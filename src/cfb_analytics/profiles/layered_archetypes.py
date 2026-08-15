"""Stats-first layered archetype matching for historical team profiles.

A team is not forced into one label. The same measured profile is compared
separately against whole-team, offense, defense, and scheme/style vocabularies.
Only names supported by fields that actually exist in the current profile are
eligible for presentation. The full 2,000-name catalog remains a research
vocabulary for future metrics.
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

LAYERED_VERSION = "historical-archetype-layers-v2-evidence-backed-2014-2024"

LANE_FAMILIES = {
    "team": {"whole_team", "survival"},
    "offense": {"run_offense", "pass_offense", "offensive_shape", "tempo"},
    "defense": {"run_defense", "pass_defense", "defense"},
    "scheme": {"scheme"},
}

# These names are eligible because every concept in the label is supported by
# fields presently available in the profile. Names requiring YAC, personnel,
# front structure, route concepts, talent, or coaching intent remain in the 2K
# research vocabulary but cannot be assigned yet.
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

# Modifier semantics are lane-specific. This prevents nonsense combinations such
# as "Finesse Complete Team" or "One-Dimensional Open Skies".
ALLOWED_MODIFIERS = {
    "team": {None, "Elite", "Strong", "Limited", "Broken", "Defense-Led", "Offense-Led"},
    "offense": {
        None, "Elite", "Strong", "Limited", "Broken", "Explosive", "Methodical",
        "Volatile", "Stable", "Predictable", "Adaptive", "Run-Leaning",
        "Pass-Leaning", "Possession", "Control", "One-Dimensional",
        "Run-Dependent", "Pass-Dependent",
    },
    "defense": {None, "Elite", "Strong", "Limited", "Broken"},
    "scheme": {None, "Predictable", "Adaptive", "Stable", "Miscast", "Well-Fit", "One-Dimensional"},
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
    modifiers = ALLOWED_MODIFIERS[lane]
    return [
        c for c in CATALOG
        if c.family in families
        and c.root_name in roots
        and c.modifier in modifiers
    ]


def match_lane(profile: dict[str, float | None], lane: str, *, top_n: int = 3) -> list[dict[str, Any]]:
    if lane not in LANE_FAMILIES:
        raise ValueError(f"unknown lane: {lane}")
    row = _profile_row(profile)
    scored = []
    for candidate in _lane_candidates(lane):
        score = score_candidate(row, candidate, min_dimensions=2)
        if score is not None:
            scored.append(score)
    scored.sort(key=lambda x: (-x["similarity"], x["contradictions"], -x["profileCoverage"], -x["dimensionsUsed"], x["id"]))
    best_by_root: dict[str, dict[str, Any]] = {}
    for score in scored:
        best_by_root.setdefault(str(score["rootName"]), score)
    return list(best_by_root.values())[:top_n]


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
        "teamSeasons": items,
    }


def _fmt(v: Any) -> str:
    return "NA" if not isinstance(v, (int, float)) else f"{float(v):.0f}"


def _match_text(items: list[dict[str, Any]]) -> str:
    if not items:
        return "NO MATCH"
    x = items[0]
    return f"{x['name']} (root={x['rootName']}, score={x['similarity']:.1f})"


def concise(report: dict[str, Any], *, examples: int = 20) -> str:
    lines = [
        "HISTORICAL ARCHETYPE LAYERS — EVIDENCE BACKED",
        f"Seasons: {report['seasons'][0]}-{report['seasons'][-1]} (2020 absent by corpus design)",
        f"Team-seasons: {report['teamSeasonCount']:,}",
        "Eligible roots: " + ", ".join(f"{k}={v}" for k, v in report["eligibleRootCounts"].items()),
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
