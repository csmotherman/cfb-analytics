"""Human-in-the-loop validation harness for fan-facing team archetypes.

This tool is intentionally diagnostic. It reads the opponent-adjusted historical
identity snapshots and hierarchical cluster assignments, summarizes one team's
season-by-season identity, and attaches transparent *provisional* fan names.

The purpose is calibration: a knowledgeable fan can agree/disagree with labels
before any nickname rules are promoted into the production profile contract.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from .grades import grade_percentile

DEFAULT_SEASONS = (2021, 2022, 2023, 2024, 2025)

QUALITY_FIELDS = (
    "oa_run_efficiency_off", "oa_pass_efficiency_off", "oa_success_off",
    "oa_explosiveness_off", "oa_third_down_off", "oa_finishing_off",
    "oa_run_efficiency_def", "oa_pass_efficiency_def", "oa_success_def",
    "oa_explosiveness_def", "oa_third_down_def", "oa_finishing_def",
)
STYLE_FIELDS = ("rush_rate", "pass_rate", "plays_per_possession")
SHAPE_FIELDS = (
    "identity_run_vs_pass_off", "identity_run_vs_pass_def",
    "identity_explosive_vs_methodical", "identity_finishing_vs_foundation",
    "identity_offense_vs_defense", "identity_rush_vs_pass_tendency",
)


def _avg(rows: list[dict[str, Any]], field: str) -> float | None:
    vals = [float(r[field]) for r in rows if isinstance(r.get(field), (int, float))]
    return mean(vals) if vals else None


def _pct(row: dict[str, Any], key: str) -> float | None:
    value = row.get(f"current_{key}_percentile")
    return float(value) if isinstance(value, (int, float)) else None


def provisional_name(row: dict[str, Any]) -> tuple[str, str]:
    run_o = _pct(row, "oa_run_efficiency_off") or 50.0
    pass_o = _pct(row, "oa_pass_efficiency_off") or 50.0
    success_o = _pct(row, "oa_success_off") or 50.0
    explosive_o = _pct(row, "oa_explosiveness_off") or 50.0
    finish_o = _pct(row, "oa_finishing_off") or 50.0
    run_d = _pct(row, "oa_run_efficiency_def") or 50.0
    pass_d = _pct(row, "oa_pass_efficiency_def") or 50.0
    success_d = _pct(row, "oa_success_def") or 50.0
    explosive_d = _pct(row, "oa_explosiveness_def") or 50.0
    rush = _pct(row, "rush_rate") or 50.0
    pass_rate = _pct(row, "pass_rate") or 50.0
    drive_len = _pct(row, "plays_per_possession") or 50.0
    off_quality = mean((run_o, pass_o, success_o, explosive_o, finish_o))
    def_quality = mean((run_d, pass_d, success_d, explosive_d))
    run_pass_gap = run_o - pass_o
    explosive_gap = explosive_o - success_o

    if def_quality >= 78 and off_quality <= 42:
        return "Defense or Bust", "Elite opponent-adjusted defense carrying an offense that gives it very little help."
    if def_quality >= 82 and run_d >= 75 and pass_d >= 75:
        return "Brick Wall", "High-end defense with very few obvious ways for opponents to attack it."
    if rush >= 78 and run_o >= 65 and run_pass_gap >= 18 and pass_o < 50:
        return "Run or Die", "The ground game is the clear strength and the passing game is a major limitation."
    if rush >= 72 and run_o >= 65 and drive_len >= 65:
        return "Possession Vampire", "Run-leaning, efficient and built to keep stacking plays and possessions on offense."
    if rush >= 68 and run_o >= 62:
        return "Ground & Pound", "Leans on an opponent-adjusted rushing advantage as the foundation of the offense."
    if pass_rate >= 78 and pass_o >= 65 and pass_o - run_o >= 18:
        return "Air It Out", "Passing is both the preferred mode and the clear opponent-adjusted offensive strength."
    if explosive_gap >= 20 and success_o <= 55:
        return "Boom or Bust", "Explosive upside is much stronger than the offense's down-to-down consistency."
    if success_o >= 78 and explosive_o <= 62 and drive_len >= 62:
        return "Death by a Thousand Cuts", "Wins with repeatable efficiency and sustained drives more than chunk-play dependence."
    if success_o >= 82 and run_o >= 70 and pass_o >= 70:
        return "Pick Your Poison", "Opponent-adjusted efficiency is strong enough both running and passing that defenses lack an easy answer."
    if success_o >= 70 and finish_o <= 38:
        return "Between-the-20s Merchant", "The offense moves the ball better than it finishes scoring opportunities."
    if off_quality >= 75 and def_quality >= 70:
        return "Complete Team", "Strong opponent-adjusted performance on both sides without one extreme stylistic dependency."
    if off_quality >= 72:
        return "Offensive Machine", "Broad opponent-adjusted offensive quality matters more than any single stylistic extreme."
    if def_quality >= 72:
        return "Defense First", "The defense is the team's clearest opponent-adjusted strength."
    if off_quality <= 30 and def_quality <= 30:
        return "Searching for Answers", "Both sides grade poorly after opponent adjustment, with no stable strength to lean on."
    return "No Single Identity", "The snapshot is relatively balanced or does not cross a strong calibration threshold."


def _cluster_lookup(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for family in report.get("families", []):
        for archetype in family.get("archetypes", []):
            out[str(archetype["id"])] = archetype
    return out


def _resolve_team(snapshots: list[dict[str, Any]], requested: str) -> str:
    names = sorted({str(r.get("team")) for r in snapshots if r.get("team")})
    exact = [n for n in names if n == requested]
    if exact:
        return exact[0]
    ci = [n for n in names if n.lower() == requested.lower()]
    if len(ci) == 1:
        return ci[0]
    contains = [n for n in names if requested.lower() in n.lower()]
    if len(contains) == 1:
        return contains[0]
    return requested


def validate_team(snapshots: list[dict[str, Any]], discovery: dict[str, Any], *, team: str, seasons: tuple[int, ...] = DEFAULT_SEASONS) -> dict[str, Any]:
    wanted = {int(s) for s in seasons}
    resolved_team = _resolve_team(snapshots, team)
    team_snaps = [
        r for r in snapshots
        if int(r.get("season", -1)) in wanted and str(r.get("team")) == resolved_team
    ]
    by_full = {
        (int(r["season"]), str(r.get("throughGameId"))): r
        for r in team_snaps if r.get("throughGameId") is not None
    }
    by_fallback = {
        (int(r["season"]), int(r.get("week") or 0), int(r.get("gamesPlayed") or 0)): r
        for r in team_snaps
    }
    assignments = [
        a for a in discovery.get("assignments", [])
        if int(a.get("season", -1)) in wanted and str(a.get("team")) == resolved_team
    ]
    by_season: dict[int, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for a in assignments:
        snap = None
        if a.get("throughGameId") is not None:
            snap = by_full.get((int(a["season"]), str(a.get("throughGameId"))))
        if snap is None:
            snap = by_fallback.get((int(a["season"]), int(a.get("week") or 0), int(a.get("gamesPlayed") or 0)))
        if snap is not None:
            by_season[int(a["season"])].append((a, snap))

    clusters = _cluster_lookup(discovery)
    seasons_out = []
    for season in sorted(wanted):
        pairs = sorted(by_season.get(season, []), key=lambda x: (int(x[1].get("week") or 0), str(x[1].get("throughGameId"))))
        if not pairs:
            seasons_out.append({"season": season, "status": "NO_DATA"})
            continue
        names = [provisional_name(s)[0] for _, s in pairs]
        name_counts = Counter(names)
        dominant_name, dominant_count = name_counts.most_common(1)[0]
        cluster_counts = Counter(str(a.get("archetype")) for a, _ in pairs)
        dominant_cluster, cluster_count = cluster_counts.most_common(1)[0]
        summary: dict[str, Any] = {}
        for key in QUALITY_FIELDS + STYLE_FIELDS:
            summary[key] = _avg([s for _, s in pairs], f"current_{key}_percentile")
            summary[f"{key}_grade"] = grade_percentile(summary[key])
        for key in SHAPE_FIELDS:
            summary[key] = _avg([s for _, s in pairs], key)

        timeline = []
        last = None
        for a, snap in pairs:
            name, why = provisional_name(snap)
            state = {"week": snap.get("week"), "gamesPlayed": snap.get("gamesPlayed"), "archetype": a.get("archetype"), "candidateName": name, "why": why}
            if last != (a.get("archetype"), name):
                timeline.append(state)
                last = (a.get("archetype"), name)

        cluster_info = clusters.get(dominant_cluster, {})
        seasons_out.append({
            "season": season, "status": "OK", "snapshotCount": len(pairs),
            "dominantCandidateName": dominant_name, "dominantCandidateShare": dominant_count / len(pairs),
            "dominantCluster": dominant_cluster, "dominantClusterShare": cluster_count / len(pairs),
            "candidateNameCounts": dict(name_counts), "clusterCounts": dict(cluster_counts),
            "summary": summary, "timeline": timeline, "clusterExemplars": cluster_info.get("exemplars", [])[:4],
        })
    return {"team": resolved_team, "requestedTeam": team, "seasons": seasons_out, "labelStatus": "CALIBRATION_ONLY"}


def concise(report: dict[str, Any]) -> str:
    title = f"TEAM ARCHETYPE VALIDATION — {report['team']}"
    if report.get("requestedTeam") != report.get("team"):
        title += f" (matched from {report['requestedTeam']})"
    lines = [title, "Labels are calibration-only, not production archetype names.", ""]
    for season in report["seasons"]:
        if season["status"] != "OK":
            lines.append(f"{season['season']}: NO DATA")
            continue
        s = season["summary"]
        lines.append(f"{season['season']}: {season['dominantCandidateName']} ({season['dominantCandidateShare']:.0%} of snapshots) | cluster {season['dominantCluster']} ({season['dominantClusterShare']:.0%})")
        lines.append("  OA grades: " f"Run O {s['oa_run_efficiency_off_grade']} ({s['oa_run_efficiency_off']:.0f}) | " f"Pass O {s['oa_pass_efficiency_off_grade']} ({s['oa_pass_efficiency_off']:.0f}) | " f"Success O {s['oa_success_off_grade']} ({s['oa_success_off']:.0f}) | " f"Run D {s['oa_run_efficiency_def_grade']} ({s['oa_run_efficiency_def']:.0f}) | " f"Pass D {s['oa_pass_efficiency_def_grade']} ({s['oa_pass_efficiency_def']:.0f})")
        lines.append("  Style: " f"Rush tendency {s['rush_rate']:.0f} | Pass tendency {s['pass_rate']:.0f} | " f"Drive length {s['plays_per_possession']:.0f}")
        lines.append("  Shape: " f"Run-vs-pass O {s['identity_run_vs_pass_off']:+.0f} | " f"Offense-vs-defense {s['identity_offense_vs_defense']:+.0f} | " f"Explosive-vs-methodical {s['identity_explosive_vs_methodical']:+.0f}")
        if season["timeline"]:
            changes = " -> ".join(f"W{x['week']} {x['candidateName']} [{x['archetype']}]" for x in season["timeline"])
            lines.append(f"  Timeline: {changes}")
        if season["clusterExemplars"]:
            ex = "; ".join(f"{x['season']} {x['team']} W{x['week']}" for x in season["clusterExemplars"][:3])
            lines.append(f"  Cluster examples: {ex}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    p.add_argument("--team", default="Michigan")
    p.add_argument("--seasons", nargs="+", type=int, default=list(DEFAULT_SEASONS))
    args = p.parse_args()
    profile_root = args.processed_root / "derived" / "profiles"
    snapshot_path = profile_root / "identity_snapshots_v2_oa.json"
    discovery_path = profile_root / "archetype_discovery_v2_oa.json"
    if not snapshot_path.exists() or not discovery_path.exists():
        raise FileNotFoundError("build OA snapshots and archetype discovery before validation")
    report = validate_team(json.loads(snapshot_path.read_text()), json.loads(discovery_path.read_text()), team=args.team, seasons=tuple(args.seasons))
    print(concise(report))


if __name__ == "__main__":
    main()
