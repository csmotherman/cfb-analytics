"""Match historical team-state snapshots to the 2,000-name archetype ontology.

The matcher is descriptive and post-partition.  It scores every eligible v3
snapshot from 2014-2024 against the catalog and keeps the closest candidates.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from .archetype_catalog import ATTR_RANGES, CATALOG, CATALOG_VERSION, ArchetypeCandidate

MATCH_VERSION = "historical-archetype-match-v1-2014-2024"
DEFAULT_SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024)


def _value(row: dict[str, Any], key: str) -> float | None:
    if key == "rush_rate":
        raw = row.get("current_rush_rate_percentile")
    elif key == "plays_per_possession":
        raw = row.get("current_plays_per_possession_percentile")
    else:
        raw = row.get(key)
    return float(raw) if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None


def score_candidate(row: dict[str, Any], candidate: ArchetypeCandidate, *, min_dimensions: int = 3) -> dict[str, Any] | None:
    weighted_sq = 0.0
    weight_sum = 0.0
    used: list[dict[str, float]] = []
    for key, target in candidate.targets.items():
        actual = _value(row, key)
        if actual is None:
            continue
        scale = ATTR_RANGES.get(key, 100.0)
        weight = float(candidate.weights.get(key, 1.0))
        delta = (actual - float(target)) / scale
        weighted_sq += weight * delta * delta
        weight_sum += weight
        used.append({"attribute": key, "actual": actual, "target": float(target), "delta": actual - float(target)})
    if len(used) < min_dimensions or weight_sum <= 0:
        return None
    distance = math.sqrt(weighted_sq / weight_sum)
    similarity = max(0.0, 100.0 * (1.0 - distance))
    used.sort(key=lambda x: abs(x["delta"]) / ATTR_RANGES.get(x["attribute"], 100.0))
    return {
        "id": candidate.id,
        "name": candidate.name,
        "family": candidate.family,
        "rootName": candidate.root_name,
        "modifier": candidate.modifier,
        "similarity": similarity,
        "dimensionsUsed": len(used),
        "closestAttributes": used[:4],
        "largestMismatches": list(reversed(used[-3:])),
    }


def match_snapshot(row: dict[str, Any], *, top_n: int = 5, min_dimensions: int = 3) -> list[dict[str, Any]]:
    scored = []
    for candidate in CATALOG:
        score = score_candidate(row, candidate, min_dimensions=min_dimensions)
        if score is not None:
            scored.append(score)
    scored.sort(key=lambda x: (-x["similarity"], -x["dimensionsUsed"], x["id"]))
    return scored[:top_n]


def match_history(rows: list[dict[str, Any]], *, seasons: tuple[int, ...] = DEFAULT_SEASONS, top_n: int = 5, min_dimensions: int = 3) -> dict[str, Any]:
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
        counts = Counter(x["id"] for x in primary)
        dominant_id, dominant_count = counts.most_common(1)[0]
        dominant_rows = [x for x in primary if x["id"] == dominant_id]
        dominant = max(dominant_rows, key=lambda x: x["similarity"])
        final = items[-1]["topMatches"][0]
        avg_similarity = mean(x["similarity"] for x in primary)
        season_summaries.append({
            "season": season,
            "team": team,
            "snapshotCount": len(items),
            "dominantArchetype": dominant,
            "dominantShare": dominant_count / len(items),
            "finalArchetype": final,
            "meanPrimarySimilarity": avg_similarity,
            "primaryArchetypeCounts": dict(counts),
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
        a = x["dominantArchetype"]
        lines.append(
            f"{x['season']} {x['team']} | {a['name']} | "
            f"share={x['dominantShare']:.0%} | sim={a['similarity']:.1f}"
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
