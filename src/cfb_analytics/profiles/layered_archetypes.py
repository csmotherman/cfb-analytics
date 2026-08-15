"""Stats-first layered archetype matching for historical team profiles.

A team is not forced into one label.  The same measured profile is compared
separately against whole-team, offense, defense, and scheme/style vocabularies.
This prevents a narrow defensive trait from becoming the headline identity of
an offense-driven team (or vice versa).
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from .archetype_catalog import CATALOG
from .match_archetypes import DEFAULT_SEASONS, PROFILE_FIELDS, PROFILE_LABELS, _profile_row, score_candidate

LAYERED_VERSION = "historical-archetype-layers-v1-stats-first-2014-2024"

LANE_FAMILIES = {
    "team": {"whole_team", "survival"},
    "offense": {"run_offense", "pass_offense", "offensive_shape", "tempo"},
    "defense": {"run_defense", "pass_defense", "defense"},
    "scheme": {"scheme"},
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
    return [c for c in CATALOG if c.family in families]


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
        "HISTORICAL ARCHETYPE LAYERS — STATS FIRST",
        f"Seasons: {report['seasons'][0]}-{report['seasons'][-1]} (2020 absent by corpus design)",
        f"Team-seasons: {report['teamSeasonCount']:,}",
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
