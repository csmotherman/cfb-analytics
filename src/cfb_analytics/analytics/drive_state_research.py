"""Leakage-safe drive-state research rows for a semi-mechanistic simulator.

This module is intentionally a data-contract/audit step, not a final simulator.
It joins validated possession drives to the pregame football-mechanism team states
that already existed before the game and records only information available at
the start of each drive as predictors. The realized drive points are retained as
the research target.

The purpose is to establish a trustworthy state -> drive-outcome dataset before
choosing a statistical outcome model. Prediction v1 and the public simulator are
not modified.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.cfb_sandbox_systems import _points
from cfb_analytics.analytics.football_mechanisms import TEAM_FIELDS
from cfb_analytics.analytics.situational_pregame import SEASONS, partition_sort_key
from cfb_analytics.derived.drives import derived_drive_partition_dir
from cfb_analytics.raw.audit import discover_partitions

DRIVE_STATE_RESEARCH_VERSION = "drive-state-research-v1-pregame-context-contract"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_ROOT = PROJECT_ROOT / "data" / "raw"
DEFAULT_PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed"

# Keep this compact for the first mechanism experiment. These are broad team
# qualities known before kickoff; no current-drive play outcomes are predictors.
QUALITY_FIELDS = (
    "OffYardsPerPossession",
    "DefYardsPerPossession",
    "OffSuccessRate",
    "DefSuccessRateAllowed",
    "OffExplosiveRate",
    "DefExplosiveRateAllowed",
    "OffScoringOpportunityRate",
    "DefScoringOpportunityRateAllowed",
    "OffPointsPerOpportunity",
    "DefPointsPerOpportunityAllowed",
    "OffEarlyDownSuccessRate",
    "DefEarlyDownSuccessRateAllowed",
    "OffGiveawayRate",
    "DefTakeawayRate",
)


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    os.replace(tmp, path)


def matchup_path(processed_root: Path, season: int) -> Path:
    return processed_root / "derived" / "football_mechanisms" / f"season={season}" / "matchups.json"


def output_path(processed_root: Path, season: int) -> Path:
    return processed_root / "derived" / "drive_state_research" / f"season={season}" / "drives.json"


def _team_state_from_matchup(matchup: dict[str, Any], prefix: str) -> dict[str, Any]:
    state = {
        "team": matchup.get(prefix),
        "gamesPlayedBefore": matchup.get(f"{prefix}GamesPlayedBefore", 0),
    }
    for field in TEAM_FIELDS:
        state[field] = matchup.get(f"{prefix}_{field}")
    return state


def matchup_team_states(matchup: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return pregame team states keyed by team name for one matchup row."""
    out: dict[str, dict[str, Any]] = {}
    for prefix in ("team1", "team2"):
        state = _team_state_from_matchup(matchup, prefix)
        team = state.get("team")
        if team:
            out[str(team)] = state
    return out


def point_outcome_bucket(points: float | None) -> str:
    """Descriptive target bucket only; no football interpretation is imposed yet."""
    if not _num(points):
        return "missing"
    value = float(points)
    rounded = round(value)
    if abs(value - rounded) < 1e-9 and 0 <= rounded <= 8:
        return str(int(rounded))
    return "other"


def _score_margin(drive: dict[str, Any]) -> float | None:
    off = drive.get("startOffenseScore")
    deff = drive.get("startDefenseScore")
    if _num(off) and _num(deff):
        return float(off) - float(deff)
    return None


def _score_state(margin: float | None) -> str:
    if not _num(margin):
        return "unknown"
    if float(margin) > 0:
        return "leading"
    if float(margin) < 0:
        return "trailing"
    return "tied"


def build_drive_row(
    drive: dict[str, Any],
    matchup: dict[str, Any],
) -> dict[str, Any] | None:
    """Build one research row from a validated possession drive.

    Predictor fields are restricted to pregame team state and drive-start state.
    End-of-drive fields are used only to construct the target via `_points`.
    """
    if not (
        drive.get("isPossessionDrive") is True
        and drive.get("driveValidationStatus") == "PASS"
        and drive.get("offense")
        and drive.get("defense")
    ):
        return None

    points = _points(drive)
    if not _num(points):
        return None

    states = matchup_team_states(matchup)
    offense = str(drive.get("offense"))
    defense = str(drive.get("defense"))
    off_state = states.get(offense)
    def_state = states.get(defense)
    if off_state is None or def_state is None:
        return None

    margin = _score_margin(drive)
    start_ytg = drive.get("startYardsToGoal")
    start_down = drive.get("startDown")
    start_distance = drive.get("startDistance")
    period = drive.get("startPeriod")

    row: dict[str, Any] = {
        "version": DRIVE_STATE_RESEARCH_VERSION,
        "season": int(drive.get("season")),
        "seasonType": str(drive.get("seasonType")),
        "week": int(drive.get("week")),
        "gameId": str(drive.get("gameId")),
        "driveId": str(drive.get("driveId")),
        "driveNumber": drive.get("driveNumber"),
        "offense": offense,
        "defense": defense,
        "offenseGamesPlayedBefore": int(off_state.get("gamesPlayedBefore") or 0),
        "defenseGamesPlayedBefore": int(def_state.get("gamesPlayedBefore") or 0),
        "startPeriod": int(period) if _num(period) else None,
        "startYardsToGoal": float(start_ytg) if _num(start_ytg) else None,
        "startDown": int(start_down) if _num(start_down) else None,
        "startDistance": float(start_distance) if _num(start_distance) else None,
        "startScoreMargin": margin,
        "startScoreState": _score_state(margin),
        "overtime": bool(_num(period) and float(period) > 4),
        "targetPoints": float(points),
        "targetScored": int(float(points) > 0),
        "targetPointBucket": point_outcome_bucket(float(points)),
    }

    # Offense contributes offensive-quality fields; defense contributes the
    # corresponding defense-allowed / disruption fields. We still retain the
    # full compact pair below because later model selection should be empirical.
    for field in QUALITY_FIELDS:
        row[f"offense_{field}"] = off_state.get(field)
        row[f"defense_{field}"] = def_state.get(field)

    return row


def load_matchups(processed_root: Path, season: int) -> dict[str, dict[str, Any]]:
    path = matchup_path(processed_root, season)
    if not path.exists():
        raise FileNotFoundError(
            f"Missing football-mechanism matchups for {season}: {path}. "
            "Run python -m cfb_analytics.analytics.football_mechanisms --all"
        )
    rows = json.loads(path.read_text())
    return {str(r.get("gameId")): r for r in rows if r.get("gameId") is not None}


def materialize_season(raw_root: Path, processed_root: Path, season: int) -> tuple[Path, list[dict[str, Any]]]:
    matchups = load_matchups(processed_root, season)
    out: list[dict[str, Any]] = []

    for season_type, week in sorted(discover_partitions(raw_root, season), key=partition_sort_key):
        drive_file = derived_drive_partition_dir(processed_root, season, season_type, week) / "drives.json"
        if not drive_file.exists():
            raise FileNotFoundError(f"Missing derived drives: {drive_file}")
        for drive in json.loads(drive_file.read_text()):
            matchup = matchups.get(str(drive.get("gameId")))
            if matchup is None:
                continue
            row = build_drive_row(drive, matchup)
            if row is not None:
                out.append(row)

    path = output_path(processed_root, season)
    _atomic(path, out)
    return path, out


def audit_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    points = Counter(r.get("targetPointBucket") for r in rows)
    starts = Counter(r.get("startDown") for r in rows)
    periods = Counter(r.get("startPeriod") for r in rows)
    score_states = Counter(r.get("startScoreState") for r in rows)
    ytg_present = sum(_num(r.get("startYardsToGoal")) for r in rows)
    score_present = sum(_num(r.get("startScoreMargin")) for r in rows)
    zero_history = sum(
        int(r.get("offenseGamesPlayedBefore", 0)) == 0 or int(r.get("defenseGamesPlayedBefore", 0)) == 0
        for r in rows
    )
    quality_total = len(rows) * len(QUALITY_FIELDS) * 2
    quality_present = sum(
        _num(r.get(f"{side}_{field}"))
        for r in rows
        for side in ("offense", "defense")
        for field in QUALITY_FIELDS
    )
    return {
        "rows": len(rows),
        "teams": len({r.get("offense") for r in rows} | {r.get("defense") for r in rows}),
        "games": len({r.get("gameId") for r in rows}),
        "pointBuckets": dict(sorted(points.items(), key=lambda x: str(x[0]))),
        "startDowns": dict(sorted(starts.items(), key=lambda x: str(x[0]))),
        "startPeriods": dict(sorted(periods.items(), key=lambda x: str(x[0]))),
        "scoreStates": dict(sorted(score_states.items(), key=lambda x: str(x[0]))),
        "yardsToGoalCoverage": ytg_present / len(rows) if rows else 0.0,
        "scoreMarginCoverage": score_present / len(rows) if rows else 0.0,
        "qualityCoverage": quality_present / quality_total if quality_total else 0.0,
        "zeroHistoryRows": zero_history,
        "overtimeRows": sum(bool(r.get("overtime")) for r in rows),
    }


def concise_audit(season: int, path: Path, report: dict[str, Any]) -> str:
    lines = [
        f"DRIVE STATE RESEARCH AUDIT — {season}",
        "=" * 72,
        f"Rows: {report['rows']:,}",
        f"Games: {report['games']:,}",
        f"Teams: {report['teams']:,}",
        f"Start yards-to-goal coverage: {report['yardsToGoalCoverage']*100:.2f}%",
        f"Start score-margin coverage: {report['scoreMarginCoverage']*100:.2f}%",
        f"Pregame quality-field coverage: {report['qualityCoverage']*100:.2f}%",
        f"Rows with either team at zero prior games: {report['zeroHistoryRows']:,}",
        f"Overtime rows: {report['overtimeRows']:,}",
        "",
        "POINT OUTCOME BUCKETS",
    ]
    for key, value in report["pointBuckets"].items():
        lines.append(f"  {str(key):>7s}: {value:>8,}")
    lines.append("")
    lines.append("DRIVE START DOWN")
    for key, value in report["startDowns"].items():
        lines.append(f"  {str(key):>7s}: {value:>8,}")
    lines.append("")
    lines.append("START SCORE STATE")
    for key, value in report["scoreStates"].items():
        lines.append(f"  {str(key):>9s}: {value:>8,}")
    lines.append("")
    lines.append(f"Wrote: {path}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--processed-root", type=Path, default=DEFAULT_PROCESSED_ROOT)
    args = parser.parse_args()

    seasons = SEASONS if args.all else ((args.season,) if args.season else ())
    if not seasons:
        parser.error("pass --season YYYY or --all")

    for season in seasons:
        path, rows = materialize_season(args.raw_root, args.processed_root, season)
        print(concise_audit(season, path, audit_rows(rows)))


if __name__ == "__main__":
    main()
