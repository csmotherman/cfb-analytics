"""Stats-first layered archetype matching for historical team profiles.

A team is not forced into one label. The same measured profile is compared
separately against whole-team, offense, defense, and scheme/style vocabularies.
Only names supported by fields that actually exist in the current profile are
eligible for presentation. The full 2,000-name catalog remains a research
vocabulary for future metrics.

v4 is root-first inside every lane: canonical football roots compete using their
own evidence before any modifier is considered. Modifiers may refine the winning
root but cannot make a weaker root win. Weak scores are reported as NO CLEAR
MATCH rather than being presented as confident archetype assignments.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from .archetype_catalog import CATALOG
from .match_archetypes import DEFAULT_SEASONS, PROFILE_FIELDS, _profile_row, score_candidate

LAYERED_VERSION = "historical-archetype-layers-v4-root-first-confidence-2014-2024"

LANE_FAMILIES = {
    "team": {"whole_team", "survival"},
    "offense": {"run_offense", "pass_offense", "offensive_shape", "tempo"},
    "defense": {"run_defense", "pass_defense", "defense"},
    "scheme": {"scheme"},
}

# Research presentation thresholds on the current salience-aware score scale.
# These do not change the ranking or underlying stats; they only prevent weak
# nearest-neighbor results from being presented as actual assignments.
LANE_ASSIGNMENT_THRESHOLDS = {
    "team": 45.0,
    "offense": 50.0,
    "defense": 50.0,
    "scheme": 45.0,
}

EVIDENCE_ROOTS = {
    "team": {
        "Complete Team", "Offense First", "Defense First", "Defense or Bust",
        "Outscore the Problem", "Paper Tiger", "One-Sided Contender",
        "Searching for Answers", "Low Ceiling", "Ugly but Effective",
    },
    "offense": {
        "Ground & Pound", "Run or Die", "Possession Vampire",
        "Three Yards and a Cloud", "Run Into a Wall", "Air It Out",
        "Bombs Away", "Pass to Control", "Sling and Pray",
        "Broken Passing Game", "Death by a Thousand Cuts", "Metronome",
        "Home Run Hunter", "Boom or Bust", "Efficient but Toothless",
        "Pretty but Empty", "Stuck in Mud", "Three-and-Out Factory",
        "All Gas", "Slow Cooker", "Clock Eater", "Possession Roulette",
    },
    "defense": {
        "Run Wall", "Run Funnel", "Open Highway", "No Fly Zone",
        "Coverage Blanket", "Pass Funnel", "Open Skies", "Brick Wall",
        "Paper Wall", "Defense in Name Only",
    },
    "scheme": {
        "Predictable Grinder", "Constraint Master", "Tendency Breaker",
        "Playcalling Prison", "Identity Crisis",
    },
}

# Root-specific modifier vocabulary. None means the canonical root name itself.
ROOT_MODIFIERS: dict[str, set[str | None]] = {
    "Complete Team": {None, "Elite", "Strong"},
    "Offense First": {None, "Strong", "Elite", "Offense-Led"},
    "Defense First": {None, "Strong", "Elite", "Defense-Led"},
    "Defense or Bust": {None, "Defense-Led"},
    "Outscore the Problem": {None, "Offense-Led", "Explosive"},
    "Paper Tiger": {None, "Offense-Led"},
    "One-Sided Contender": {None, "Offense-Led", "Defense-Led"},
    "Searching for Answers": {None, "Limited", "Broken"},
    "Low Ceiling": {None, "Limited"},
    "Ugly but Effective": {None, "Strong", "Defense-Led", "Possession"},

    "Ground & Pound": {None, "Elite", "Strong", "Run-Leaning", "Run-Dependent", "Predictable", "Possession", "Methodical"},
    "Run or Die": {None, "Elite", "Strong", "Predictable", "One-Dimensional", "Run-Dependent", "Possession"},
    "Possession Vampire": {None, "Elite", "Strong", "Run-Leaning", "Possession", "Methodical", "Control"},
    "Three Yards and a Cloud": {None, "Run-Leaning", "Run-Dependent", "Predictable", "Methodical", "Limited"},
    "Run Into a Wall": {None, "Broken", "Limited", "Run-Dependent", "Predictable", "One-Dimensional"},

    "Air It Out": {None, "Elite", "Strong", "Pass-Leaning", "Pass-Dependent", "Explosive", "Volatile"},
    "Bombs Away": {None, "Elite", "Strong", "Pass-Leaning", "Pass-Dependent", "Explosive", "Volatile"},
    "Pass to Control": {None, "Elite", "Strong", "Pass-Leaning", "Pass-Dependent", "Methodical", "Control", "Possession"},
    "Sling and Pray": {None, "Broken", "Limited", "Pass-Leaning", "Pass-Dependent", "Predictable", "One-Dimensional", "Volatile"},
    "Broken Passing Game": {None, "Broken", "Limited", "One-Dimensional", "Run-Dependent"},

    "Death by a Thousand Cuts": {None, "Elite", "Strong", "Methodical", "Possession", "Control"},
    "Metronome": {None, "Elite", "Strong", "Methodical", "Stable", "Control"},
    "Home Run Hunter": {None, "Elite", "Strong", "Explosive", "Volatile"},
    "Boom or Bust": {None, "Explosive", "Volatile", "Predictable"},
    "Efficient but Toothless": {None, "Methodical", "Stable"},
    "Pretty but Empty": {None, "Explosive", "Volatile", "Limited"},
    "Stuck in Mud": {None, "Broken", "Limited", "Methodical"},
    "Three-and-Out Factory": {None, "Broken", "Limited", "Predictable"},
    "All Gas": {None, "Elite", "Strong", "Explosive", "Volatile", "Adaptive"},
    "Slow Cooker": {None, "Strong", "Methodical", "Possession", "Control"},
    "Clock Eater": {None, "Strong", "Run-Leaning", "Possession", "Control", "Methodical"},
    "Possession Roulette": {None, "Volatile", "Broken", "Limited"},

    "Run Wall": {None, "Elite", "Strong"},
    "Run Funnel": {None},
    "Open Highway": {None, "Limited", "Broken"},
    "No Fly Zone": {None, "Elite", "Strong"},
    "Coverage Blanket": {None, "Elite", "Strong"},
    "Pass Funnel": {None},
    "Open Skies": {None, "Limited", "Broken"},
    "Brick Wall": {None, "Elite", "Strong"},
    "Paper Wall": {None, "Limited", "Broken"},
    "Defense in Name Only": {None, "Broken"},

    "Predictable Grinder": {None, "Predictable", "One-Dimensional"},
    "Constraint Master": {None, "Adaptive", "Well-Fit"},
    "Tendency Breaker": {None, "Adaptive", "Well-Fit"},
    "Playcalling Prison": {None, "Predictable", "Miscast", "One-Dimensional"},
    "Identity Crisis": {None, "Miscast", "One-Dimensional"},
}


def _value(row: dict[str, Any], key: str) -> float | None:
    if key == "rush_rate":
        raw = row.get("current_rush_rate_percentile", row.get("rush_rate"))
    elif key == "plays_per_possession":
        raw = row.get("current_plays_per_possession_percentile", row.get("plays_per_possession"))
    else:
        raw = row.get(key)
    return float(raw) if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None


def season_profile(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for key in PROFILE_FIELDS:
        vals = [_value(r, key) for r in rows]
        vals = [float(v) for v in vals if isinstance(v, (int, float))]
        out[key] = mean(vals) if vals else None
    return out


def _lane_candidates(lane: str):
    families = LANE_FAMILIES[lane]
    roots = EVIDENCE_ROOTS[lane]
    return [
        c for c in CATALOG
        if c.family in families
        and c.root_name in roots
        and c.modifier in ROOT_MODIFIERS.get(c.root_name, {None})
    ]


def _confidence(score: float, threshold: float) -> str:
    if score >= max(65.0, threshold + 15.0):
        return "HIGH"
    if score >= max(55.0, threshold + 5.0):
        return "MODERATE"
    if score >= threshold:
        return "LOW"
    return "NO_CLEAR_MATCH"


def match_lane(profile: dict[str, float | None], lane: str, *, top_n: int = 3) -> list[dict[str, Any]]:
    if lane not in LANE_FAMILIES:
        raise ValueError(f"unknown lane: {lane}")
    row = _profile_row(profile)
    candidates = _lane_candidates(lane)

    by_root: dict[str, list[Any]] = defaultdict(list)
    for candidate in candidates:
        by_root[candidate.root_name].append(candidate)

    # Step 1: canonical roots compete without modifiers.
    roots_ranked: list[tuple[str, dict[str, Any]]] = []
    for root_name, root_candidates in by_root.items():
        canonical = next((c for c in root_candidates if c.modifier is None), None)
        if canonical is None:
            continue
        root_score = score_candidate(row, canonical, min_dimensions=2)
        if root_score is not None:
            roots_ranked.append((root_name, root_score))
    roots_ranked.sort(
        key=lambda item: (
            -item[1]["similarity"],
            item[1]["contradictions"],
            -item[1]["profileCoverage"],
            -item[1]["dimensionsUsed"],
            item[0],
        )
    )

    # Step 2: only after a root is ranked do its legal modifiers compete.
    out: list[dict[str, Any]] = []
    threshold = LANE_ASSIGNMENT_THRESHOLDS[lane]
    for root_name, root_score in roots_ranked[:top_n]:
        variants: list[dict[str, Any]] = []
        for candidate in by_root[root_name]:
            variant = score_candidate(row, candidate, min_dimensions=2)
            if variant is None:
                continue
            variant["variantSimilarity"] = float(variant["similarity"])
            variant["rootSimilarity"] = float(root_score["similarity"])
            variants.append(variant)
        variants.sort(
            key=lambda x: (
                -x["variantSimilarity"],
                x["contradictions"],
                -x["profileCoverage"],
                -x["dimensionsUsed"],
                x["id"],
            )
        )
        best = variants[0] if variants else dict(root_score)
        # Modifier quality refines presentation but cannot alter root ranking.
        best["similarity"] = 0.90 * float(root_score["similarity"]) + 0.10 * float(best.get("variantSimilarity", root_score["similarity"]))
        best["assignmentThreshold"] = threshold
        best["confidence"] = _confidence(float(root_score["similarity"]), threshold)
        best["isClearMatch"] = float(root_score["similarity"]) >= threshold
        out.append(best)
    return out


def match_team_season(rows: list[dict[str, Any]], *, season: int, team: str, top_n: int = 3) -> dict[str, Any]:
    selected = [r for r in rows if int(r.get("season", -1)) == int(season) and str(r.get("team")) == team]
    if not selected:
        return {"season": season, "team": team, "status": "NO_DATA"}
    profile = season_profile(selected)
    return {
        "season": season,
        "team": team,
        "status": "OK",
        "snapshotCount": len(selected),
        "profile": profile,
        "lanes": {lane: match_lane(profile, lane, top_n=top_n) for lane in LANE_FAMILIES},
    }


def match_history(rows: list[dict[str, Any]], *, seasons: tuple[int, ...] = DEFAULT_SEASONS, top_n: int = 3) -> dict[str, Any]:
    wanted = {int(x) for x in seasons}
    groups: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        season = int(row.get("season", -1))
        team = str(row.get("team") or "")
        if season in wanted and team:
            groups[(season, team)].append(row)
    items = []
    for (season, team), selected in sorted(groups.items()):
        profile = season_profile(selected)
        items.append({
            "season": season,
            "team": team,
            "snapshotCount": len(selected),
            "profile": profile,
            "lanes": {lane: match_lane(profile, lane, top_n=top_n) for lane in LANE_FAMILIES},
        })
    return {
        "version": LAYERED_VERSION,
        "seasons": sorted(wanted),
        "teamSeasonCount": len(items),
        "eligibleRootCounts": {lane: len(EVIDENCE_ROOTS[lane]) for lane in EVIDENCE_ROOTS},
        "assignmentThresholds": dict(LANE_ASSIGNMENT_THRESHOLDS),
        "teamSeasons": items,
    }


def _fmt(v: Any) -> str:
    return "NA" if not isinstance(v, (int, float)) else f"{float(v):.0f}"


def _match_text(items: list[dict[str, Any]]) -> str:
    if not items:
        return "NO MATCH"
    x = items[0]
    if not x.get("isClearMatch"):
        return (
            f"NO CLEAR MATCH | best={x['rootName']} "
            f"rootScore={x['rootSimilarity']:.1f} confidence={x['confidence']}"
        )
    return (
        f"{x['name']} (root={x['rootName']}, rootScore={x['rootSimilarity']:.1f}, "
        f"confidence={x['confidence']})"
    )


def concise(report: dict[str, Any], *, examples: int = 20) -> str:
    lines = [
        "HISTORICAL ARCHETYPE LAYERS — ROOT FIRST + CONFIDENCE",
        f"Seasons: {report['seasons'][0]}-{report['seasons'][-1]} (2020 absent by corpus design)",
        f"Team-seasons: {report['teamSeasonCount']:,}",
        "Eligible roots: " + ", ".join(f"{k}={v}" for k, v in report["eligibleRootCounts"].items()),
        "Assignment thresholds: " + ", ".join(f"{k}={v:.0f}" for k, v in report["assignmentThresholds"].items()),
        "",
    ]
    for x in report["teamSeasons"][:examples]:
        p = x["profile"]
        lines.append(f"{x['season']} {x['team']}")
        lines.append(
            "  STATS | "
            f"RushAtk={_fmt(p.get('identity_rushing_attack'))} PassAtk={_fmt(p.get('identity_passing_attack'))} "
            f"OffQ={_fmt(p.get('identity_offense_quality'))} | "
            f"RunDef={_fmt(p.get('identity_rushing_defense'))} PassDef={_fmt(p.get('identity_passing_defense'))} "
            f"DefQ={_fmt(p.get('identity_defense_quality'))}"
        )
        lines.append(
            "        | "
            f"RushTend={_fmt(p.get('rush_rate'))} DriveLen={_fmt(p.get('plays_per_possession'))} "
            f"Expl-v-Method={_fmt(p.get('identity_explosive_vs_methodical'))} "
            f"Predict={_fmt(p.get('identity_predictability'))} Constraint={_fmt(p.get('identity_scheme_constraint'))}"
        )
        lines.append(f"  TEAM   | {_match_text(x['lanes']['team'])}")
        lines.append(f"  OFFENSE| {_match_text(x['lanes']['offense'])}")
        lines.append(f"  DEFENSE| {_match_text(x['lanes']['defense'])}")
        lines.append(f"  SCHEME | {_match_text(x['lanes']['scheme'])}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    p.add_argument("--seasons", nargs="+", type=int, default=list(DEFAULT_SEASONS))
    p.add_argument("--top-n", type=int, default=3)
    p.add_argument("--examples", type=int, default=20)
    args = p.parse_args()

    source = args.processed_root / "derived" / "profiles" / "identity_snapshots_v3_attack_scheme.json"
    if not source.exists():
        raise FileNotFoundError("build v3 snapshots first: python -m cfb_analytics.profiles.snapshots")
    rows = json.loads(source.read_text())
    report = match_history(rows, seasons=tuple(args.seasons), top_n=args.top_n)
    target = args.processed_root / "derived" / "profiles" / "historical_archetype_layers_2014_2024.json"
    target.write_text(json.dumps(report, separators=(",", ":")))
    print(concise(report, examples=args.examples))


if __name__ == "__main__":
    main()
