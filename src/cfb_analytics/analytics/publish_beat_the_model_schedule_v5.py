"""Beat the Model live scheduler v5 pregame team comparison stats.

This layer keeps the v4 team-logo presentation contract and the v3 market-aware
Official 15 selection unchanged. Starting in Week 3, it attaches a compact,
pregame-safe team-stat snapshot to each selected matchup. Every statistic is
restricted to completed games before the target week; current-week results are
never included.

The public comparison intentionally favors a small set of decision-useful numbers:
record and scoring context plus CFBD advanced efficiency rates. Advanced rates are
requested with garbage time excluded. The stats are presentation-only and never
feed Prediction-v2 or Official 15 selection.
"""
from __future__ import annotations

import math
from typing import Any

from cfb_analytics.analytics import publish_beat_the_model_schedule as base
from cfb_analytics.analytics import publish_beat_the_model_schedule_v4 as team_v4  # noqa: F401
from cfb_analytics.sources.cfbd.client import CfbdError

LIVE_SCHEDULE_VERSION = "beat-the-model-live-schedule-v5"
TEAM_STATS_VERSION = "cfbd-pregame-team-stats-v1"
MIN_TEAM_STATS_WEEK = 3
EXCLUDE_GARBAGE_TIME = True

_v4_build_week_rankings = base.build_week_rankings
_v4_select_slate = base.select_slate


def _finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _number(value: Any) -> float | None:
    if _finite(value):
        return float(value)
    if isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError:
            return None
        return parsed if math.isfinite(parsed) else None
    return None


def _nested_number(payload: Any, *keys: str) -> float | None:
    current = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return _number(current)


def _is_completed(raw: dict[str, Any]) -> bool:
    value = raw.get("completed")
    if isinstance(value, bool):
        return value
    status = str(raw.get("status") or raw.get("gameStatus") or "").strip().lower()
    return status in {"final", "completed", "complete"}


def _classification(raw: dict[str, Any], side: str) -> str:
    return str(
        raw.get(f"{side}Classification")
        or raw.get(f"{side}_classification")
        or ""
    ).lower()


def _team_name(raw: dict[str, Any], side: str) -> str | None:
    value = raw.get(f"{side}Team") or raw.get(f"{side}_team")
    return str(value) if value else None


def _points(raw: dict[str, Any], side: str) -> float | None:
    return _number(raw.get(f"{side}Points", raw.get(f"{side}_points")))


def _blank_record() -> dict[str, float | int]:
    return {
        "games": 0,
        "wins": 0,
        "losses": 0,
        "ties": 0,
        "pointsFor": 0.0,
        "pointsAgainst": 0.0,
    }


def pregame_records(client: Any, season: int, end_week: int) -> dict[str, dict[str, float | int]]:
    """Build records/scoring only from completed games before the target week."""
    records: dict[str, dict[str, float | int]] = {}
    for week in range(0, int(end_week) + 1):
        response = client.games(int(season), int(week), "regular")
        if not isinstance(response.payload, list):
            raise ValueError(f"Unexpected CFBD games payload for {season} Week {week}")

        for raw in response.payload:
            if not isinstance(raw, dict) or not _is_completed(raw):
                continue
            home = _team_name(raw, "home")
            away = _team_name(raw, "away")
            home_points = _points(raw, "home")
            away_points = _points(raw, "away")
            if not home or not away or home_points is None or away_points is None:
                continue

            for side, team, scored, allowed in (
                ("home", home, home_points, away_points),
                ("away", away, away_points, home_points),
            ):
                if _classification(raw, side) != "fbs":
                    continue
                row = records.setdefault(team, _blank_record())
                row["games"] = int(row["games"]) + 1
                row["pointsFor"] = float(row["pointsFor"]) + scored
                row["pointsAgainst"] = float(row["pointsAgainst"]) + allowed
                if scored > allowed:
                    row["wins"] = int(row["wins"]) + 1
                elif scored < allowed:
                    row["losses"] = int(row["losses"]) + 1
                else:
                    row["ties"] = int(row["ties"]) + 1
    return records


def advanced_stats_by_team(client: Any, season: int, end_week: int) -> dict[str, dict[str, float | None]]:
    """Normalize the CFBD advanced-season response into the public stat contract."""
    response = client.team_season_advanced_stats(
        int(season),
        start_week=0,
        end_week=int(end_week),
        exclude_garbage_time=EXCLUDE_GARBAGE_TIME,
    )
    if not isinstance(response.payload, list):
        raise ValueError("Unexpected CFBD advanced season stats payload")

    out: dict[str, dict[str, float | None]] = {}
    for raw in response.payload:
        if not isinstance(raw, dict):
            continue
        team = raw.get("team")
        if not isinstance(team, str) or not team.strip():
            continue
        out[team.strip()] = {
            "offenseSuccessRate": _nested_number(raw, "offense", "successRate"),
            "defenseSuccessRateAllowed": _nested_number(raw, "defense", "successRate"),
            "offensePPA": _nested_number(raw, "offense", "ppa"),
            "defensePPAAllowed": _nested_number(raw, "defense", "ppa"),
            "offenseExplosiveness": _nested_number(raw, "offense", "explosiveness"),
            "defenseExplosivenessAllowed": _nested_number(raw, "defense", "explosiveness"),
            "pointsPerOpportunity": _nested_number(raw, "offense", "pointsPerOpportunity"),
            "pointsPerOpportunityAllowed": _nested_number(raw, "defense", "pointsPerOpportunity"),
            "advancedPlays": _nested_number(raw, "offense", "plays"),
            "advancedDrives": _nested_number(raw, "offense", "drives"),
        }
    return out


def build_pregame_team_stats(client: Any, season: int, target_week: int) -> dict[str, dict[str, Any]]:
    """Return a frozen-through-prior-week comparison snapshot for all FBS teams."""
    if int(target_week) < MIN_TEAM_STATS_WEEK:
        return {}

    through_week = int(target_week) - 1
    records = pregame_records(client, int(season), through_week)
    advanced = advanced_stats_by_team(client, int(season), through_week)
    teams = sorted(set(records) | set(advanced))
    out: dict[str, dict[str, Any]] = {}

    for team in teams:
        record = records.get(team, _blank_record())
        games = int(record["games"])
        stats: dict[str, Any] = {
            "version": TEAM_STATS_VERSION,
            "season": int(season),
            "throughWeek": through_week,
            "games": games,
            "wins": int(record["wins"]),
            "losses": int(record["losses"]),
            "ties": int(record["ties"]),
            "pointsPerGame": float(record["pointsFor"]) / games if games else None,
            "pointsAllowedPerGame": float(record["pointsAgainst"]) / games if games else None,
            "excludeGarbageTime": EXCLUDE_GARBAGE_TIME,
        }
        stats.update(advanced.get(team, {}))
        if games or team in advanced:
            out[team] = stats
    return out


def build_week_rankings(
    client: Any,
    data_root: Any,
    *,
    season: int,
    week: int,
) -> dict[str, Any]:
    rankings = _v4_build_week_rankings(
        client,
        data_root,
        season=season,
        week=week,
    )

    if int(week) < MIN_TEAM_STATS_WEEK:
        team_stats: dict[str, dict[str, Any]] = {}
        status = "not-yet"
    else:
        try:
            team_stats = build_pregame_team_stats(client, int(season), int(week))
            status = "ok" if team_stats else "empty"
        except (CfbdError, ValueError, AttributeError):
            # Team comparison is valuable context but must never block the weekly
            # contest. If the secondary stats feed is unavailable, fail open.
            team_stats = {}
            status = "unavailable"

    payload = dict(rankings)
    rows: list[dict[str, Any]] = []
    for raw in rankings.get("teams", []):
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        stats = team_stats.get(str(row.get("team")))
        if stats:
            row["pregameStats"] = stats
        rows.append(row)

    payload["teams"] = rows
    payload["teamStatsVersion"] = TEAM_STATS_VERSION
    payload["teamStatsStatus"] = status
    payload["teamStatsThroughWeek"] = int(week) - 1 if int(week) >= MIN_TEAM_STATS_WEEK else None
    payload["teamStatsExcludeGarbageTime"] = EXCLUDE_GARBAGE_TIME
    return payload


def select_slate(
    schedule: list[dict[str, Any]],
    rankings: dict[str, Any],
    *,
    existing_current: dict[str, Any],
    model_by_id: dict[str, dict[str, Any]],
    market_by_id: dict[str, dict[str, Any]] | None = None,
    market_snapshot_at: str | None = None,
) -> list[dict[str, Any]]:
    games = _v4_select_slate(
        schedule,
        rankings,
        existing_current=existing_current,
        model_by_id=model_by_id,
        market_by_id=market_by_id,
        market_snapshot_at=market_snapshot_at,
    )

    by_team = {
        str(row.get("team")): row
        for row in rankings.get("teams", [])
        if isinstance(row, dict) and row.get("team")
    }
    existing_by_id = {
        str(row.get("id")): row
        for row in existing_current.get("games", [])
        if isinstance(row, dict) and row.get("id") is not None
    }
    preserve_existing = existing_current.get("status") in {"open", "locked", "final"}

    out: list[dict[str, Any]] = []
    for raw in games:
        game = dict(raw)
        existing = existing_by_id.get(str(game.get("id")), {})
        home_stats = by_team.get(str(game.get("homeTeam")), {}).get("pregameStats")
        away_stats = by_team.get(str(game.get("awayTeam")), {}).get("pregameStats")

        if preserve_existing and existing.get("homePregameStats"):
            home_stats = existing.get("homePregameStats")
        if preserve_existing and existing.get("awayPregameStats"):
            away_stats = existing.get("awayPregameStats")

        game["homePregameStats"] = home_stats if isinstance(home_stats, dict) else None
        game["awayPregameStats"] = away_stats if isinstance(away_stats, dict) else None
        out.append(game)
    return out


def install() -> None:
    base.LIVE_SCHEDULE_VERSION = LIVE_SCHEDULE_VERSION
    base.build_week_rankings = build_week_rankings
    base.select_slate = select_slate


install()


def main() -> None:
    base.main()


if __name__ == "__main__":
    main()
