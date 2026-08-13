"""Validated team-game behavioral/system metrics built from canonical plays and drives.

System Metrics v1 intentionally exposes auditable components rather than arbitrary
weighted composites. These metrics are research inputs until corpus audits pass and
predictive value is tested separately.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.explosiveness import classify_explosive
from cfb_analytics.analytics.success import classify_success
from cfb_analytics.canonical.materialize import canonical_partition_dir
from cfb_analytics.derived.drives import derived_drive_partition_dir
from cfb_analytics.raw.audit import discover_partitions

SYSTEM_METRICS_VERSION = "system-metrics-v1"
NEUTRAL_SCORE_MARGIN = 14
SECOND_AND_LONG_DISTANCE = 7
SHORT_YARDAGE_DISTANCE = 2
FOURTH_SHORT_DISTANCE = 3


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def _rate(n: float, d: float) -> float | None:
    return float(n) / float(d) if d else None


def _family(play: dict[str, Any]) -> str | None:
    subtype = str(play.get("eventSubtype") or "").lower()
    if "rush" in subtype:
        return "rush"
    if "pass" in subtype or "sack" in subtype:
        return "pass"
    return None


def _is_sack(play: dict[str, Any]) -> bool:
    return "sack" in str(play.get("eventSubtype") or "").lower()


def _is_field_goal(play: dict[str, Any]) -> bool:
    s = str(play.get("eventSubtype") or "").lower().replace("_", " ")
    return "field goal" in s or "fieldgoal" in s


def _is_punt(play: dict[str, Any]) -> bool:
    return "punt" in str(play.get("eventSubtype") or "").lower()


def _eligible_scrimmage(play: dict[str, Any], team: str, role: str) -> bool:
    return (
        play.get(role) == team
        and play.get("isScrimmagePlay") is True
        and play.get("hasNoPlayContext", False) is not True
        and _family(play) in {"rush", "pass"}
    )


def _offense_margin(play: dict[str, Any]) -> float | None:
    a, b = play.get("offenseScore"), play.get("defenseScore")
    if not _num(a) or not _num(b):
        return None
    return float(a) - float(b)


def _period(play: dict[str, Any]) -> int | None:
    v = play.get("period")
    return int(v) if _num(v) else None


def _drive_points(drive: dict[str, Any]) -> float | None:
    start, end = drive.get("startOffenseScore"), drive.get("endOffenseScoreObserved")
    if not _num(start) or not _num(end):
        return None
    # Offensive possessions should not receive credit for defensive/special-team
    # scores outside the possession. Clamp to the legal single-possession range.
    return min(8.0, max(0.0, float(end) - float(start)))


def _side_components(plays: list[dict[str, Any]], drives: list[dict[str, Any]], team: str, role: str) -> dict[str, Any]:
    selected = [p for p in plays if _eligible_scrimmage(p, team, role)]
    pass_plays = [p for p in selected if _family(p) == "pass"]
    rush_plays = [p for p in selected if _family(p) == "rush"]

    def yards(rows: list[dict[str, Any]]) -> float:
        return sum(float(p["analyticsYardsGained"]) for p in rows if _num(p.get("analyticsYardsGained")))

    def success_counts(rows: list[dict[str, Any]]) -> tuple[int, int]:
        vals = [classify_success(p) for p in rows]
        vals = [v for v in vals if v is not None]
        return sum(bool(v) for v in vals), len(vals)

    def explosive_counts(rows: list[dict[str, Any]]) -> tuple[int, int]:
        vals = [classify_explosive(p) for p in rows]
        vals = [v for v in vals if v is not None]
        return sum(bool(v) for v in vals), len(vals)

    p_succ, p_succ_n = success_counts(pass_plays)
    r_succ, r_succ_n = success_counts(rush_plays)
    p_exp, p_exp_n = explosive_counts(pass_plays)
    r_exp, r_exp_n = explosive_counts(rush_plays)
    sacks = sum(_is_sack(p) for p in pass_plays)
    pass_yards, rush_yards = yards(pass_plays), yards(rush_plays)
    stuffs = sum(_num(p.get("analyticsYardsGained")) and float(p["analyticsYardsGained"]) <= 0 for p in rush_plays)

    early = [p for p in selected if p.get("down") in (1, 2)]
    first = [p for p in selected if p.get("down") == 1]
    second_long = [p for p in selected if p.get("down") == 2 and _num(p.get("distance")) and float(p["distance"]) >= SECOND_AND_LONG_DISTANCE]
    short = [p for p in selected if p.get("down") in (3, 4) and _num(p.get("distance")) and float(p["distance"]) <= SHORT_YARDAGE_DISTANCE]
    neutral = [
        p for p in early
        if (_period(p) or 99) <= 3
        and _offense_margin(p) is not None
        and abs(float(_offense_margin(p))) <= NEUTRAL_SCORE_MARGIN
    ]

    third = [p for p in selected if p.get("down") == 3]
    fourth_go = [p for p in selected if p.get("down") == 4]
    red_zone = [p for p in selected if _num(p.get("yardsToGoal")) and 0 < float(p["yardsToGoal"]) <= 20]

    def conv_rate(rows: list[dict[str, Any]]) -> tuple[int, int, float | None]:
        successes = 0
        eligible = 0
        for p in rows:
            v = classify_success(p)
            if v is None:
                continue
            eligible += 1
            successes += int(bool(v))
        return successes, eligible, _rate(successes, eligible)

    third_conv, third_n, third_rate = conv_rate(third)
    fourth_conv, fourth_n, fourth_rate = conv_rate(fourth_go)
    short_conv, short_n, short_rate = conv_rate(short)
    rz_succ, rz_n, rz_rate = conv_rate(red_zone)

    half = {}
    for label, periods in (("H1", {1, 2}), ("H2", {3, 4})):
        hp = [p for p in selected if _period(p) in periods]
        hs, hn = success_counts(hp)
        hy = yards(hp)
        hds = [
            d for d in drives
            if d.get(role) == team
            and d.get("isPossessionDrive") is True
            and d.get("driveValidationStatus") == "PASS"
            and _num(d.get("startPeriod"))
            and int(d["startPeriod"]) in periods
            and _drive_points(d) is not None
        ]
        hpts = sum(float(_drive_points(d)) for d in hds)
        half[label] = {
            "plays": len(hp), "successes": hs, "successEligible": hn, "yards": hy,
            "possessions": len(hds), "points": hpts,
            "successRate": _rate(hs, hn), "yardsPerPlay": _rate(hy, len(hp)),
            "pointsPerPossession": _rate(hpts, len(hds)),
        }

    out = {
        "scrimmageRunPassPlays": len(selected),
        "passDropbacks": len(pass_plays),
        "passAttemptsExcludingSacks": len(pass_plays) - sacks,
        "sacksTaken": sacks,
        "passYards": pass_yards,
        "yardsPerDropback": _rate(pass_yards, len(pass_plays)),
        "passSuccessEligiblePlays": p_succ_n,
        "passSuccessfulPlays": p_succ,
        "passSuccessRate": _rate(p_succ, p_succ_n),
        "passExplosiveEligiblePlays": p_exp_n,
        "passExplosivePlays": p_exp,
        "passExplosiveRate": _rate(p_exp, p_exp_n),
        "sackRate": _rate(sacks, len(pass_plays)),
        "rushAttempts": len(rush_plays),
        "rushYards": rush_yards,
        "yardsPerRush": _rate(rush_yards, len(rush_plays)),
        "rushSuccessEligiblePlays": r_succ_n,
        "rushSuccessfulPlays": r_succ,
        "rushSuccessRate": _rate(r_succ, r_succ_n),
        "rushExplosiveEligiblePlays": r_exp_n,
        "rushExplosivePlays": r_exp,
        "rushExplosiveRate": _rate(r_exp, r_exp_n),
        "stuffedRushes": stuffs,
        "stuffRate": _rate(stuffs, len(rush_plays)),
        "earlyDownPlays": len(early),
        "earlyDownPasses": sum(_family(p) == "pass" for p in early),
        "earlyDownPassRate": _rate(sum(_family(p) == "pass" for p in early), len(early)),
        "firstDownPlays": len(first),
        "firstDownPasses": sum(_family(p) == "pass" for p in first),
        "firstDownPassRate": _rate(sum(_family(p) == "pass" for p in first), len(first)),
        "secondAndLongPlays": len(second_long),
        "secondAndLongPasses": sum(_family(p) == "pass" for p in second_long),
        "secondAndLongPassRate": _rate(sum(_family(p) == "pass" for p in second_long), len(second_long)),
        "neutralSituationPlays": len(neutral),
        "neutralSituationPasses": sum(_family(p) == "pass" for p in neutral),
        "neutralSituationPassRate": _rate(sum(_family(p) == "pass" for p in neutral), len(neutral)),
        "thirdDownAttempts": third_n,
        "thirdDownConversions": third_conv,
        "thirdDownConversionRate": third_rate,
        "fourthDownGoAttempts": fourth_n,
        "fourthDownConversions": fourth_conv,
        "fourthDownConversionRate": fourth_rate,
        "shortYardageAttempts": short_n,
        "shortYardageConversions": short_conv,
        "shortYardageConversionRate": short_rate,
        "redZonePlayAttempts": rz_n,
        "redZoneSuccessfulPlays": rz_succ,
        "redZoneSuccessRate": rz_rate,
    }
    for label in ("H1", "H2"):
        for key, value in half[label].items():
            out[f"{label}{key[0].upper()}{key[1:]}"] = value
    for metric in ("successRate", "yardsPerPlay", "pointsPerPossession"):
        a, b = half["H1"][metric], half["H2"][metric]
        out[f"secondHalf{metric[0].upper()}{metric[1:]}Delta"] = float(b) - float(a) if _num(a) and _num(b) else None
    return out


def _aggressiveness(plays: list[dict[str, Any]], team: str) -> dict[str, Any]:
    decisions = []
    short_decisions = []
    for p in plays:
        if p.get("offense") != team or p.get("down") != 4 or p.get("hasNoPlayContext", False) is True:
            continue
        fam = _family(p)
        if fam not in {"rush", "pass"} and not _is_punt(p) and not _is_field_goal(p):
            continue
        decisions.append(p)
        if _num(p.get("distance")) and float(p["distance"]) <= FOURTH_SHORT_DISTANCE:
            short_decisions.append(p)
    goes = sum(_family(p) in {"rush", "pass"} for p in decisions)
    short_goes = sum(_family(p) in {"rush", "pass"} for p in short_decisions)
    return {
        "fourthDownDecisionOpportunities": len(decisions),
        "fourthDownGoDecisions": goes,
        "fourthDownGoRate": _rate(goes, len(decisions)),
        "fourthAndShortDecisionOpportunities": len(short_decisions),
        "fourthAndShortGoDecisions": short_goes,
        "fourthAndShortGoRate": _rate(short_goes, len(short_decisions)),
    }


_ALLOWED_PERFORMANCE_KEYS = {
    "passDropbacks", "passAttemptsExcludingSacks", "sacksTaken", "passYards", "yardsPerDropback",
    "passSuccessEligiblePlays", "passSuccessfulPlays", "passSuccessRate", "passExplosiveEligiblePlays",
    "passExplosivePlays", "passExplosiveRate", "sackRate", "rushAttempts", "rushYards", "yardsPerRush",
    "rushSuccessEligiblePlays", "rushSuccessfulPlays", "rushSuccessRate", "rushExplosiveEligiblePlays",
    "rushExplosivePlays", "rushExplosiveRate", "stuffedRushes", "stuffRate", "thirdDownAttempts",
    "thirdDownConversions", "thirdDownConversionRate", "fourthDownGoAttempts", "fourthDownConversions",
    "fourthDownConversionRate", "shortYardageAttempts", "shortYardageConversions", "shortYardageConversionRate",
    "redZonePlayAttempts", "redZoneSuccessfulPlays", "redZoneSuccessRate",
}
_ALLOWED_PERFORMANCE_KEYS |= {f"H{h}{name}" for h in (1, 2) for name in (
    "Plays", "Successes", "SuccessEligible", "Yards", "Possessions", "Points", "SuccessRate", "YardsPerPlay", "PointsPerPossession"
)}
_ALLOWED_PERFORMANCE_KEYS |= {
    "secondHalfSuccessRateDelta", "secondHalfYardsPerPlayDelta", "secondHalfPointsPerPossessionDelta"
}


def derive_system_team_games(plays: list[dict[str, Any]], drives: list[dict[str, Any]], season: int, season_type: str, week: int) -> list[dict[str, Any]]:
    by_game_plays: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_game_drives: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in plays:
        by_game_plays[str(p.get("gameId"))].append(p)
    for d in drives:
        by_game_drives[str(d.get("gameId"))].append(d)
    out = []
    for gid in sorted(set(by_game_plays) | set(by_game_drives)):
        gp, gd = by_game_plays.get(gid, []), by_game_drives.get(gid, [])
        teams = {x for p in gp for x in (p.get("offense"), p.get("defense")) if x}
        teams |= {x for d in gd for x in (d.get("offense"), d.get("defense")) if x}
        if len(teams) != 2:
            continue
        for team in sorted(teams):
            opponent = next(t for t in teams if t != team)
            offense = _side_components(gp, gd, team, "offense")
            defense = _side_components(gp, gd, team, "defense")
            row = {
                "season": season, "seasonType": season_type, "week": week, "gameId": gid,
                "team": team, "opponent": opponent, "systemMetricsVersion": SYSTEM_METRICS_VERSION,
                **offense, **_aggressiveness(gp, team),
            }
            for key in _ALLOWED_PERFORMANCE_KEYS:
                if key in defense:
                    row[f"{key}Allowed"] = defense[key]
            out.append(row)
    return out


def system_metrics_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_game = Counter(str(r.get("gameId")) for r in rows)
    by_key = {(str(r.get("gameId")), str(r.get("team"))) for r in rows}
    checks = {
        "exactly_two_rows_per_game": bool(rows) and all(v == 2 for v in by_game.values()),
        "unique_team_game_rows": len(by_key) == len(rows),
        "version_present": all(r.get("systemMetricsVersion") == SYSTEM_METRICS_VERSION for r in rows),
        "run_pass_partition_reconciles": all(r.get("scrimmageRunPassPlays") == r.get("passDropbacks", 0) + r.get("rushAttempts", 0) for r in rows),
        "pass_attempt_sack_partition_reconciles": all(r.get("passDropbacks") == r.get("passAttemptsExcludingSacks", 0) + r.get("sacksTaken", 0) for r in rows),
        "early_down_pass_bounds": all(0 <= r.get("earlyDownPasses", 0) <= r.get("earlyDownPlays", 0) for r in rows),
        "fourth_down_go_bounds": all(0 <= r.get("fourthDownGoDecisions", 0) <= r.get("fourthDownDecisionOpportunities", 0) for r in rows),
        "pass_offense_defense_reconciles": sum(r.get("passDropbacks", 0) for r in rows) == sum(r.get("passDropbacksAllowed", 0) for r in rows),
        "rush_offense_defense_reconciles": sum(r.get("rushAttempts", 0) for r in rows) == sum(r.get("rushAttemptsAllowed", 0) for r in rows),
        "pass_yards_reconcile": abs(sum(r.get("passYards", 0.0) for r in rows) - sum(r.get("passYardsAllowed", 0.0) for r in rows)) < 1e-8,
        "rush_yards_reconcile": abs(sum(r.get("rushYards", 0.0) for r in rows) - sum(r.get("rushYardsAllowed", 0.0) for r in rows)) < 1e-8,
        "third_down_reconciles": sum(r.get("thirdDownAttempts", 0) for r in rows) == sum(r.get("thirdDownAttemptsAllowed", 0) for r in rows),
        "half_play_reconciles": sum(r.get("H1Plays", 0) + r.get("H2Plays", 0) for r in rows) == sum(r.get("H1PlaysAllowed", 0) + r.get("H2PlaysAllowed", 0) for r in rows),
        "rates_bounded": all(
            not _num(v) or 0.0 <= float(v) <= 1.0
            for r in rows for k, v in r.items()
            if k.endswith("Rate") and not k.startswith("secondHalf")
        ),
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "games": len(by_game), "teamGameRows": len(rows),
        "passDropbacks": sum(r.get("passDropbacks", 0) for r in rows),
        "rushAttempts": sum(r.get("rushAttempts", 0) for r in rows),
        "fourthDownDecisions": sum(r.get("fourthDownDecisionOpportunities", 0) for r in rows),
        "neutralSituationPlays": sum(r.get("neutralSituationPlays", 0) for r in rows),
        "checks": checks,
    }


def _load_partition(processed_root: Path, season: int, season_type: str, week: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pp = canonical_partition_dir(processed_root, season, season_type, week) / "plays.json"
    dp = derived_drive_partition_dir(processed_root, season, season_type, week) / "drives.json"
    if not pp.exists() or not dp.exists():
        raise FileNotFoundError(f"Missing canonical plays or derived drives for {season} {season_type} week {week}")
    return json.loads(pp.read_text()), json.loads(dp.read_text())


def build_system_metrics_season(raw_root: Path, processed_root: Path, season: int) -> list[dict[str, Any]]:
    out = []
    for season_type, week in discover_partitions(raw_root, season):
        plays, drives = _load_partition(processed_root, season, season_type, week)
        out.extend(derive_system_team_games(plays, drives, season, season_type, week))
    return out


def concise(audit: dict[str, Any]) -> str:
    lines = [
        f"SYSTEM METRICS v1 AUDIT: {audit['status']}",
        f"Games: {audit['games']:,}", f"Team-game rows: {audit['teamGameRows']:,}",
        f"Pass dropbacks: {audit['passDropbacks']:,}", f"Rush attempts: {audit['rushAttempts']:,}",
        f"Fourth-down decision opportunities: {audit['fourthDownDecisions']:,}",
        f"Neutral-situation plays: {audit['neutralSituationPlays']:,}", "", "Checks:",
    ]
    lines += [f"{k}: {'PASS' if v else 'FAIL'}" for k, v in audit["checks"].items()]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows = build_system_metrics_season(args.raw_root, args.processed_root, args.season)
    audit = system_metrics_audit(rows)
    if args.write:
        path = args.processed_root / "derived" / "system_metrics" / f"season={args.season}" / "team_games.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
        print(f"Wrote: {path}")
    print(concise(audit))


if __name__ == "__main__":
    main()
