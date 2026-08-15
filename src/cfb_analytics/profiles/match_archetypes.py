"""Match historical team-state snapshots to the 2,000-name archetype ontology.

The matcher is descriptive and post-partition. It scores every eligible v3
snapshot from 2014-2024 against the catalog and keeps the closest candidates.

v3 matching is root-first and salience-aware. A narrow trait can be an excellent
secondary descriptor without becoming the team's headline identity merely
because it matches two fields almost perfectly. Primary roots are rewarded for
explaining the strongest deviations in the team's whole profile.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from .archetype_catalog import CATALOG, CATALOG_VERSION, ArchetypeCandidate

MATCH_VERSION = "historical-archetype-match-v3-salience-2014-2024"
DEFAULT_SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024)
SIGNED_FIELDS = {
    "identity_explosive_vs_methodical",
    "identity_offense_vs_defense",
    "identity_run_vs_pass_off",
    "identity_run_vs_pass_def",
    "identity_playcalling_fit",
}
ROOTS_BY_NAME = {x.root_name: x for x in CATALOG if x.modifier is None}

# Profile-coverage weights intentionally span quality, style and scheme. They are
# not prediction weights; they only stop a sparse two-field template from
# becoming the headline when it ignores more distinctive parts of the profile.
SALIENCE_WEIGHTS: dict[str, float] = {
    "identity_rushing_attack": 1.00,
    "identity_passing_attack": 1.00,
    "identity_rushing_defense": 0.90,
    "identity_passing_defense": 0.90,
    "identity_offense_quality": 0.80,
    "identity_defense_quality": 0.80,
    "rush_rate": 1.00,
    "plays_per_possession": 0.55,
    "identity_explosive_vs_methodical": 0.65,
    "identity_offense_vs_defense": 0.55,
    "identity_run_vs_pass_off": 0.75,
    "identity_run_vs_pass_def": 0.55,
    "identity_predictability": 0.55,
    "identity_one_dimensionality": 0.55,
    "identity_playcalling_fit": 0.40,
    "identity_scheme_constraint": 0.55,
}


def _value(row: dict[str, Any], key: str) -> float | None:
    if key == "rush_rate":
        raw = row.get("current_rush_rate_percentile")
    elif key == "plays_per_possession":
        raw = row.get("current_plays_per_possession_percentile")
    else:
        raw = row.get(key)
    return float(raw) if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None


def _neutral(key: str) -> float:
    return 0.0 if key in SIGNED_FIELDS else 50.0


def _salience(key: str, actual: float) -> float:
    scale = 100.0 if key in SIGNED_FIELDS else 50.0
    return SALIENCE_WEIGHTS.get(key, 0.0) * min(1.0, abs(actual - _neutral(key)) / scale)


def _profile_coverage(row: dict[str, Any], target_keys: set[str]) -> float:
    total = 0.0
    covered = 0.0
    for key, weight in SALIENCE_WEIGHTS.items():
        actual = _value(row, key)
        if actual is None:
            continue
        contribution = _salience(key, actual)
        total += contribution
        if key in target_keys:
            covered += contribution
    if total <= 1e-12:
        return 0.0
    return min(1.0, covered / total)


def _specificity_factor(dimensions: int) -> float:
    # Sparse roots remain valid, but must explain a very salient slice of the
    # profile to beat a richer identity. Five or more fields receive no penalty.
    return min(1.0, 0.60 + 0.08 * max(0, dimensions))


def _tolerance(key: str) -> float:
    return 36.0 if key in SIGNED_FIELDS else 24.0


def _contradiction(key: str, actual: float, target: float) -> bool:
    if key in SIGNED_FIELDS:
        return (target >= 25.0 and actual <= -10.0) or (target <= -25.0 and actual >= 10.0)
    return (target >= 70.0 and actual <= 40.0) or (target <= 30.0 and actual >= 60.0)


def score_candidate(
    row: dict[str, Any],
    candidate: ArchetypeCandidate,
    *,
    min_dimensions: int = 3,
) -> dict[str, Any] | None:
    weighted_sq = 0.0
    weight_sum = 0.0
    used: list[dict[str, float]] = []
    contradictions = 0
    for key, target in candidate.targets.items():
        actual = _value(row, key)
        if actual is None:
            continue
        tolerance = _tolerance(key)
        weight = float(candidate.weights.get(key, 1.0))
        standardized = (actual - float(target)) / tolerance
        weighted_sq += weight * standardized * standardized
        weight_sum += weight
        if _contradiction(key, actual, float(target)):
            contradictions += 1
        used.append({
            "attribute": key,
            "actual": actual,
            "target": float(target),
            "delta": actual - float(target),
            "standardizedDelta": standardized,
        })
    if len(used) < min_dimensions or weight_sum <= 0:
        return None

    rms = math.sqrt(weighted_sq / weight_sum)
    fit_similarity = 100.0 * math.exp(-0.5 * rms * rms)
    if contradictions:
        fit_similarity *= 0.72 ** contradictions

    coverage = _profile_coverage(row, {x["attribute"] for x in used})
    specificity = _specificity_factor(len(used))
    # A perfect local fit is not a perfect team identity unless it explains a
    # meaningful share of what is distinctive about the whole team state.
    identity_similarity = fit_similarity * (0.45 + 0.55 * coverage) * specificity

    used.sort(key=lambda x: abs(x["standardizedDelta"]))
    return {
        "id": candidate.id,
        "name": candidate.name,
        "family": candidate.family,
        "rootName": candidate.root_name,
        "modifier": candidate.modifier,
        "similarity": identity_similarity,
        "localFitSimilarity": fit_similarity,
        "profileCoverage": coverage,
        "specificityFactor": specificity,
        "dimensionsUsed": len(used),
        "contradictions": contradictions,
        "closestAttributes": used[:4],
        "largestMismatches": list(reversed(used[-3:])),
    }


def match_snapshot(row: dict[str, Any], *, top_n: int = 5, min_dimensions: int = 3) -> list[dict[str, Any]]:
    root_scores: dict[str, dict[str, Any]] = {}
    for root_name, root in ROOTS_BY_NAME.items():
        score = score_candidate(row, root, min_dimensions=min(2, min_dimensions))
        if score is not None:
            root_scores[root_name] = score

    scored = []
    for candidate in CATALOG:
        score = score_candidate(row, candidate, min_dimensions=min_dimensions)
        if score is None:
            continue
        root = root_scores.get(candidate.root_name)
        if root is None:
            continue
        root_similarity = float(root["similarity"])
        variant_similarity = float(score["similarity"])
        # Root identity dominates. Modifier refinements can improve presentation,
        # but they cannot turn a weak root into the headline identity.
        blended = 0.82 * root_similarity + 0.18 * variant_similarity
        score["variantSimilarity"] = variant_similarity
        score["rootSimilarity"] = root_similarity
        score["rootLocalFitSimilarity"] = root["localFitSimilarity"]
        score["rootProfileCoverage"] = root["profileCoverage"]
        score["similarity"] = blended
        scored.append(score)

    scored.sort(key=lambda x: (-x["similarity"], x["contradictions"], -x["rootProfileCoverage"], -x["dimensionsUsed"], x["id"]))

    best_by_root: dict[str, dict[str, Any]] = {}
    for score in scored:
        best_by_root.setdefault(str(score["rootName"]), score)
    distinct = sorted(
        best_by_root.values(),
        key=lambda x: (-x["similarity"], x["contradictions"], -x["rootProfileCoverage"], -x["dimensionsUsed"], x["id"]),
    )
    return distinct[:top_n]


def match_history(
    rows: list[dict[str, Any]],
    *,
    seasons: tuple[int, ...] = DEFAULT_SEASONS,
    top_n: int = 5,
    min_dimensions: int = 3,
) -> dict[str, Any]:
    wanted = {int(s) for s in seasons}
    matched = []
    for row in rows:
        season = int(row.get("season", -1))
        if season not in wanted:
            continue
        top = match_snapshot(row, top_n=top_n, min_dimensions=min_dimensions)
        if not top:
            continue
        matched.append({
            "season": season,
            "team": row.get("team"),
            "seasonType": row.get("seasonType"),
            "week": row.get("week"),
            "throughGameId": row.get("throughGameId"),
            "gamesPlayed": row.get("gamesPlayed"),
            "topMatches": top,
        })

    by_team_season: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for item in matched:
        by_team_season[(int(item["season"]), str(item["team"]))].append(item)

    season_summaries = []
    for (season, team), items in sorted(by_team_season.items()):
        items.sort(key=lambda x: (str(x.get("seasonType") or "regular"), int(x.get("week") or 0), int(x.get("gamesPlayed") or 0)))
        primary = [x["topMatches"][0] for x in items]

        exact_counts = Counter(x["id"] for x in primary)
        dominant_id, dominant_count = exact_counts.most_common(1)[0]
        dominant_rows = [x for x in primary if x["id"] == dominant_id]
        dominant = max(dominant_rows, key=lambda x: x["similarity"])

        root_counts = Counter(x["rootName"] for x in primary)
        dominant_root, dominant_root_count = root_counts.most_common(1)[0]
        root_rows = [x for x in primary if x["rootName"] == dominant_root]
        best_root_variant = max(root_rows, key=lambda x: x["similarity"])

        final = items[-1]["topMatches"][0]
        avg_similarity = mean(x["similarity"] for x in primary)
        season_summaries.append({
            "season": season,
            "team": team,
            "snapshotCount": len(items),
            "dominantArchetype": dominant,
            "dominantShare": dominant_count / len(items),
            "dominantRootName": dominant_root,
            "dominantRootShare": dominant_root_count / len(items),
            "bestDominantRootVariant": best_root_variant,
            "finalArchetype": final,
            "meanPrimarySimilarity": avg_similarity,
            "primaryArchetypeCounts": dict(exact_counts),
            "primaryRootCounts": dict(root_counts),
        })

    return {
        "version": MATCH_VERSION,
        "catalogVersion": CATALOG_VERSION,
        "catalogSize": len(CATALOG),
        "seasons": sorted(wanted),
        "snapshotCount": len(matched),
        "teamSeasonCount": len(season_summaries),
        "topN": top_n,
        "matches": matched,
        "teamSeasonSummaries": season_summaries,
    }


def concise(report: dict[str, Any], *, examples: int = 20) -> str:
    lines = [
        "HISTORICAL 2K ARCHETYPE MATCHING",
        f"Catalog: {report['catalogSize']:,} candidates",
        f"Seasons: {report['seasons'][0]}-{report['seasons'][-1]} (2020 absent by corpus design)",
        f"Matched snapshots: {report['snapshotCount']:,}",
        f"Team-seasons: {report['teamSeasonCount']:,}",
        "",
        "Sample team-season dominant builds:",
    ]
    for x in report["teamSeasonSummaries"][:examples]:
        a = x["bestDominantRootVariant"]
        lines.append(
            f"{x['season']} {x['team']} | root={x['dominantRootName']} "
            f"({x['dominantRootShare']:.0%}) | build={a['name']} | "
            f"score={a['similarity']:.1f} | coverage={a['rootProfileCoverage']:.0%}"
        )
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    p.add_argument("--top-n", type=int, default=5)
    p.add_argument("--min-dimensions", type=int, default=3)
    p.add_argument("--seasons", nargs="+", type=int, default=list(DEFAULT_SEASONS))
    p.add_argument("--examples", type=int, default=20)
    args = p.parse_args()

    source = args.processed_root / "derived" / "profiles" / "identity_snapshots_v3_attack_scheme.json"
    if not source.exists():
        raise FileNotFoundError("build v3 attack/scheme snapshots first: python -m cfb_analytics.profiles.snapshots")
    rows = json.loads(source.read_text())
    report = match_history(rows, seasons=tuple(args.seasons), top_n=args.top_n, min_dimensions=args.min_dimensions)
    target = args.processed_root / "derived" / "profiles" / "historical_archetype_matches_2014_2024.json"
    target.write_text(json.dumps(report, separators=(",", ":")))
    print(concise(report, examples=args.examples))


if __name__ == "__main__":
    main()
