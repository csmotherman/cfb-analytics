"""Unsupervised discovery of recurring historical team identities.

Clusters are analytical shapes first and fan names second.  The algorithm never
uses the hand-authored archetype rules to create clusters; those rules can be
compared later after the historical shapes are inspected.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .snapshots import DISCOVERY_DIRECTIONS

DISCOVERY_VERSION = "historical-archetype-discovery-v1-research"


def _candidate_features(rows: list[dict[str, Any]], min_coverage: float) -> list[str]:
    n = len(rows)
    fields = []
    for key in DISCOVERY_DIRECTIONS:
        field = f"current_{key}_percentile"
        coverage = sum(isinstance(r.get(field), (int, float)) for r in rows) / n if n else 0.0
        if coverage >= min_coverage:
            fields.append(field)
    return fields


def _matrix(rows: list[dict[str, Any]], features: list[str], include_trend: bool, trend_weight: float):
    kept, vectors = [], []
    for row in rows:
        vals = [row.get(f) for f in features]
        if not all(isinstance(v, (int, float)) for v in vals):
            continue
        vector = [float(v) for v in vals]
        if include_trend:
            for field in features:
                key = field.removeprefix("current_").removesuffix("_percentile")
                value = row.get(f"trend_{key}")
                vector.append(float(value) * trend_weight if isinstance(value, (int, float)) else 0.0)
        vectors.append(vector)
        kept.append(row)
    return kept, np.asarray(vectors, dtype=float)


def discover_archetypes(
    rows: list[dict[str, Any]], *, k_min: int = 6, k_max: int = 24,
    min_coverage: float = 0.85, include_trend: bool = True,
    trend_weight: float = 0.35, random_state: int = 20260815,
) -> dict[str, Any]:
    features = _candidate_features(rows, min_coverage)
    kept, x = _matrix(rows, features, include_trend, trend_weight)
    if len(features) < 4:
        raise ValueError("fewer than four sufficiently complete profile dimensions")
    if len(kept) < max(50, k_max * 5):
        raise ValueError("not enough complete historical snapshots for clustering")

    scaler = StandardScaler()
    z = scaler.fit_transform(x)
    trials = []
    upper = min(k_max, len(kept) - 1)
    for k in range(k_min, upper + 1):
        model = KMeans(n_clusters=k, n_init=20, random_state=random_state)
        labels = model.fit_predict(z)
        score = silhouette_score(z, labels, sample_size=min(5000, len(z)), random_state=random_state)
        counts = np.bincount(labels, minlength=k)
        trials.append({"k": k, "silhouette": float(score), "smallestCluster": int(counts.min()), "largestCluster": int(counts.max())})

    best_k = max(trials, key=lambda r: r["silhouette"])["k"]
    model = KMeans(n_clusters=best_k, n_init=50, random_state=random_state)
    labels = model.fit_predict(z)
    distances = model.transform(z)

    centers = []
    current_feature_count = len(features)
    for cluster in range(best_k):
        idx = np.flatnonzero(labels == cluster)
        center_z = model.cluster_centers_[cluster]
        center_raw = scaler.inverse_transform(center_z.reshape(1, -1))[0]
        center = {features[i].removeprefix("current_").removesuffix("_percentile"): float(center_raw[i]) for i in range(current_feature_count)}
        traits = sorted(center.items(), key=lambda kv: abs(kv[1] - 50.0), reverse=True)[:6]
        exemplar_idx = idx[np.argsort(distances[idx, cluster])[:5]]
        exemplars = [{"season": int(kept[i]["season"]), "team": kept[i]["team"], "week": kept[i].get("week"), "gamesPlayed": kept[i].get("gamesPlayed"), "distance": float(distances[i, cluster])} for i in exemplar_idx]
        centers.append({
            "cluster": cluster,
            "snapshotCount": int(len(idx)),
            "share": float(len(idx) / len(kept)),
            "centerPercentiles": center,
            "signatureTraits": [{"metric": k, "percentile": v} for k, v in traits],
            "exemplars": exemplars,
            "fanName": None,
            "fanDescription": None,
        })

    assignments = []
    for i, row in enumerate(kept):
        assignments.append({
            "season": row["season"], "team": row["team"], "seasonType": row.get("seasonType"),
            "week": row.get("week"), "throughGameId": row.get("throughGameId"),
            "gamesPlayed": row.get("gamesPlayed"), "cluster": int(labels[i]),
            "distanceToCenter": float(distances[i, labels[i]]),
        })

    return {
        "version": DISCOVERY_VERSION,
        "snapshotCount": len(kept),
        "availableSnapshotCount": len(rows),
        "features": features,
        "includeTrend": include_trend,
        "trendWeight": trend_weight,
        "minCoverage": min_coverage,
        "kTrials": trials,
        "selectedK": int(best_k),
        "clusters": centers,
        "assignments": assignments,
    }


def concise(report: dict[str, Any]) -> str:
    lines = [
        "HISTORICAL ARCHETYPE DISCOVERY",
        f"Snapshots used: {report['snapshotCount']:,}/{report['availableSnapshotCount']:,}",
        f"Dimensions: {len(report['features'])}",
        f"Selected clusters: {report['selectedK']}",
        "",
    ]
    for cluster in report["clusters"]:
        traits = ", ".join(f"{x['metric']}={x['percentile']:.0f}" for x in cluster["signatureTraits"][:4])
        examples = "; ".join(f"{x['season']} {x['team']} W{x['week']}" for x in cluster["exemplars"][:3])
        lines.append(f"C{cluster['cluster']:02d} | {cluster['share']:.1%} | {traits} | {examples}")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    p.add_argument("--k-min", type=int, default=6)
    p.add_argument("--k-max", type=int, default=24)
    p.add_argument("--min-coverage", type=float, default=0.85)
    p.add_argument("--no-trend", action="store_true")
    args = p.parse_args()
    source = args.processed_root / "derived" / "profiles" / "identity_snapshots_v1.json"
    if not source.exists():
        raise FileNotFoundError("build identity snapshots first: python -m cfb_analytics.profiles.snapshots")
    rows = json.loads(source.read_text())
    report = discover_archetypes(rows, k_min=args.k_min, k_max=args.k_max, min_coverage=args.min_coverage, include_trend=not args.no_trend)
    target = args.processed_root / "derived" / "profiles" / "archetype_discovery_v1.json"
    target.write_text(json.dumps(report, indent=2))
    print(concise(report))


if __name__ == "__main__":
    main()
