"""Fetch the live CFBD schedule and publish the next Beat the Model slate.

This module owns *matchup population*, not model fitting.  The selection is kept
independent of Prediction v2:

* Week 1 uses the already-published final-2025 BTM power rankings exactly.
* Week 2+ rebuilds a current-season site-aware SRS from completed games strictly
  before the target week and blends the numeric rating with the Week 1 seed using
  the frozen 100/75/50/25/0 four-game carryover rule.
* The Official 15 is the 15 lowest matchup scores, where
  score = average(rank) + .25 * rank gap.
* Model picks are attached only if a separately frozen prediction record already
  exists.  Missing model picks never influence which games are selected.
* Once every selected game has a model pick, the slate becomes ``open`` and the
  selected game IDs are treated as frozen; later refreshes may update kickoff and
  final-score fields but may not silently reselect the slate.

The command is intentionally cheap enough for GitHub Actions: only the CFBD games
endpoint is needed for rankings, schedules, and results.  Play-by-play remains the
responsibility of the frozen Prediction-v2 production pipeline.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.authoritative_game_targets import normalize_authoritative_game
from cfb_analytics.analytics.beat_the_model import (
    BTM_VERSION,
    MATCHUP_GAP_WEIGHT,
    POWER_RANKING_VERSION,
    SLATE_SELECTION_VERSION,
    SLATE_SIZE,
    blend_team_rating,
    matchup_score,
)
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import fit_site_aware_srs
from cfb_analytics.analytics.site_context_audit import extract_neutral_site
from cfb_analytics.sources.cfbd.client import CfbdClient

TARGET_SEASON = 2026
LIVE_SCHEDULE_VERSION = "beat-the-model-live-schedule-v1"
MODEL_VERSION = "prediction-v2-2026-prospective-freeze-v1"
MAX_REGULAR_WEEK = 16


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _read_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _fbs_vs_fbs(raw: dict[str, Any]) -> bool:
    return (
        str(raw.get("homeClassification") or raw.get("home_classification") or "").lower() == "fbs"
        and str(raw.get("awayClassification") or raw.get("away_classification") or "").lower() == "fbs"
    )


def _kickoff(raw: dict[str, Any]) -> str | None:
    for field in ("startDate", "start_date", "startTime", "start_time", "kickoff"):
        value = raw.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _completed(raw: dict[str, Any]) -> bool:
    for field in ("completed", "isCompleted", "is_completed"):
        value = raw.get(field)
        if isinstance(value, bool):
            return value
    status = str(raw.get("status") or raw.get("gameStatus") or "").strip().lower()
    return status in {"final", "completed", "complete"}


def _normalize_live_game(raw: dict[str, Any], season: int, week: int) -> dict[str, Any] | None:
    if not _fbs_vs_fbs(raw):
        return None
    normalized = normalize_authoritative_game(raw)
    if normalized is None or not normalized.get("homeTeam") or not normalized.get("awayTeam"):
        return None
    _, neutral = extract_neutral_site(raw)
    return {
        "id": str(normalized["gameId"]),
        "season": int(season),
        "week": int(week),
        "seasonType": "regular",
        "kickoff": _kickoff(raw),
        "homeTeam": str(normalized["homeTeam"]),
        "awayTeam": str(normalized["awayTeam"]),
        "isNeutralSite": neutral,
        "completed": _completed(raw),
        "actualHomeScore": normalized.get("homeScore"),
        "actualAwayScore": normalized.get("awayScore"),
    }


def fetch_week(client: CfbdClient, season: int, week: int) -> list[dict[str, Any]]:
    response = client.games(int(season), int(week), "regular")
    if not isinstance(response.payload, list):
        raise ValueError(f"Unexpected CFBD games payload for {season} Week {week}")
    games = [
        game
        for raw in response.payload
        if isinstance(raw, dict)
        for game in [_normalize_live_game(raw, season, week)]
        if game is not None
    ]
    # A duplicated upstream game ID is a hard failure.  Silent deduplication can
    # change the ranked slate and therefore the public contest.
    ids = [str(game["id"]) for game in games]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate CFBD game ID in {season} Week {week}")
    return games


def _seed_rankings_path(data_root: Path, season: int) -> Path:
    return data_root / "beat-the-model" / "rankings" / f"season={season}" / "week=1.json"


def _ranking_path(data_root: Path, season: int, week: int) -> Path:
    return data_root / "beat-the-model" / "rankings" / f"season={season}" / f"week={week}.json"


def _current_path(data_root: Path) -> Path:
    return data_root / "beat-the-model" / "current.json"


def _slate_snapshot_path(data_root: Path, season: int, week: int) -> Path:
    return data_root / "beat-the-model" / "slates" / f"season={season}" / f"week={week}.json"


def _prediction_rows(data_root: Path) -> dict[str, dict[str, Any]]:
    """Load any already-published model calls without making them selection inputs."""
    rows: list[dict[str, Any]] = []

    prediction_payload = _read_object(data_root / "predictions.json")
    for key in ("current", "results"):
        value = prediction_payload.get(key)
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, dict))

    snapshot_root = data_root / "beat-the-model" / "model-snapshots"
    if snapshot_root.exists():
        for path in snapshot_root.glob("season=*/week=*.json"):
            payload = _read_object(path)
            value = payload.get("predictions")
            if isinstance(value, list):
                rows.extend(row for row in value if isinstance(row, dict))

    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        gid = row.get("gameId", row.get("id"))
        if gid is not None:
            out[str(gid)] = row
    return out


def _seed_teams(data_root: Path, season: int) -> list[dict[str, Any]]:
    path = _seed_rankings_path(data_root, season)
    payload = _read_object(path)
    teams = payload.get("teams")
    if not isinstance(teams, list) or not teams:
        raise FileNotFoundError(
            f"Week 1 ranking seed is missing or empty: {path}. "
            "Publish final prior-season BTM rankings before running the live scheduler."
        )
    cleaned = [row for row in teams if isinstance(row, dict) and row.get("team") and _finite(row.get("rating"))]
    if not cleaned:
        raise ValueError(f"Week 1 ranking seed has no finite team ratings: {path}")
    return cleaned


def _history_rows(client: CfbdClient, season: int, target_week: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    games_played: dict[str, int] = {}
    for week in range(0, int(target_week)):
        for game in fetch_week(client, season, week):
            if not game["completed"]:
                continue
            hs = game.get("actualHomeScore")
            as_ = game.get("actualAwayScore")
            neutral = game.get("isNeutralSite")
            if not _finite(hs) or not _finite(as_) or not isinstance(neutral, bool):
                continue
            home = str(game["homeTeam"])
            away = str(game["awayTeam"])
            rows.append(
                {
                    "homeTeam": home,
                    "awayTeam": away,
                    "target_margin": float(hs) - float(as_),
                    "isNeutralSite": neutral,
                }
            )
            games_played[home] = games_played.get(home, 0) + 1
            games_played[away] = games_played.get(away, 0) + 1
    return rows, games_played


def build_week_rankings(
    client: CfbdClient,
    data_root: Path,
    *,
    season: int,
    week: int,
) -> dict[str, Any]:
    seed = _seed_teams(data_root, season)
    # The product contract is explicit: Week 1 is exactly the prior-season final
    # ranking.  Week 0 results do not retroactively alter the published Week 1 seed.
    if int(week) == 1:
        payload = _read_object(_seed_rankings_path(data_root, season))
        payload["liveScheduleVersion"] = LIVE_SCHEDULE_VERSION
        return payload

    seed_rating = {str(row["team"]): float(row["rating"]) for row in seed}
    history, games_played = _history_rows(client, season, week)
    fitted = fit_site_aware_srs(history)
    if fitted.get("converged") is not True:
        raise RuntimeError(f"Current-season site-aware SRS failed for {season} Week {week}")
    current = {
        str(team): float(value)
        for team, value in dict(fitted.get("ratings", {})).items()
        if _finite(value)
    }

    teams = sorted(set(seed_rating) | set(current))
    blended: dict[str, float] = {}
    for team in teams:
        value = blend_team_rating(
            prior_rating=seed_rating.get(team),
            current_rating=current.get(team),
            games_before=games_played.get(team, 0),
        )
        if _finite(value):
            blended[team] = float(value)

    ordered = sorted(blended.items(), key=lambda item: (-item[1], item[0]))
    ranking_rows = [
        {
            "rank": index,
            "team": team,
            "rating": rating,
            "sourceSeason": season - 1,
            "gamesBefore": games_played.get(team, 0),
        }
        for index, (team, rating) in enumerate(ordered, start=1)
    ]
    return {
        "schemaVersion": 2,
        "version": BTM_VERSION,
        "rankingVersion": POWER_RANKING_VERSION,
        "liveScheduleVersion": LIVE_SCHEDULE_VERSION,
        "season": int(season),
        "week": int(week),
        "sourceSeason": int(season) - 1,
        "historyGames": len(history),
        "method": (
            "Week 2+ blends final prior-season site-aware power rating with current-season "
            "pregame site-aware SRS using the frozen four-game carryover rule."
        ),
        "teams": ranking_rows,
    }


def _attach_model(game: dict[str, Any], model_by_id: dict[str, dict[str, Any]], existing: dict[str, Any] | None) -> None:
    source = model_by_id.get(str(game["id"])) or existing or {}
    winner = source.get("predictedWinner", source.get("modelWinner"))
    margin = source.get("predictedMargin", source.get("modelMargin"))
    game["modelWinner"] = str(winner) if winner and str(winner) != "TIE" else None
    game["modelMargin"] = float(margin) if _finite(margin) else None
    for source_field, target_field in (
        ("homeWinProbability", "modelHomeWinProbability"),
        ("modelHomeWinProbability", "modelHomeWinProbability"),
        ("projectedHomeScore", "modelProjectedHomeScore"),
        ("modelProjectedHomeScore", "modelProjectedHomeScore"),
        ("projectedAwayScore", "modelProjectedAwayScore"),
        ("modelProjectedAwayScore", "modelProjectedAwayScore"),
    ):
        if target_field in game and game[target_field] is not None:
            continue
        value = source.get(source_field)
        if _finite(value):
            game[target_field] = float(value)


def select_slate(
    schedule: list[dict[str, Any]],
    rankings: dict[str, Any],
    *,
    existing_current: dict[str, Any],
    model_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    ranking_by_team = {
        str(row["team"]): row
        for row in rankings.get("teams", [])
        if isinstance(row, dict) and row.get("team") and row.get("rank") is not None
    }
    existing_by_id = {
        str(row.get("id")): row
        for row in existing_current.get("games", [])
        if isinstance(row, dict) and row.get("id") is not None
    }

    frozen_ids: list[str] = []
    if existing_current.get("status") in {"open", "locked", "final"}:
        frozen_ids = [str(row.get("id")) for row in existing_current.get("games", []) if isinstance(row, dict)]

    by_id = {str(game["id"]): game for game in schedule}
    selected_raw: list[dict[str, Any]] = []
    if frozen_ids:
        missing = [gid for gid in frozen_ids if gid not in by_id]
        if missing:
            raise ValueError(
                "A frozen Beat the Model slate contains game IDs missing from the refreshed CFBD schedule: "
                + ", ".join(missing)
            )
        selected_raw = [by_id[gid] for gid in frozen_ids]
    else:
        candidates: list[tuple[float, int, int, str, dict[str, Any]]] = []
        for game in schedule:
            home_row = ranking_by_team.get(str(game["homeTeam"]))
            away_row = ranking_by_team.get(str(game["awayTeam"]))
            if not home_row or not away_row:
                continue
            hr = int(home_row["rank"])
            ar = int(away_row["rank"])
            score = matchup_score(hr, ar)
            candidates.append((score, min(hr, ar), max(hr, ar), str(game["id"]), game))
        candidates.sort(key=lambda item: item[:4])
        selected_raw = [item[4] for item in candidates[:SLATE_SIZE]]

    out: list[dict[str, Any]] = []
    for slot, raw in enumerate(selected_raw, start=1):
        home_row = ranking_by_team.get(str(raw["homeTeam"]))
        away_row = ranking_by_team.get(str(raw["awayTeam"]))
        if not home_row or not away_row:
            raise ValueError(f"Frozen selected game lost a team ranking: {raw['id']}")
        game = {
            "id": str(raw["id"]),
            "season": int(raw["season"]),
            "week": int(raw["week"]),
            "slot": slot,
            "kickoff": raw.get("kickoff"),
            "homeTeam": raw["homeTeam"],
            "awayTeam": raw["awayTeam"],
            "homeRank": int(home_row["rank"]),
            "awayRank": int(away_row["rank"]),
            "homePowerRating": float(home_row["rating"]),
            "awayPowerRating": float(away_row["rating"]),
            "matchupScore": matchup_score(int(home_row["rank"]), int(away_row["rank"])),
            "status": "final" if raw.get("completed") else "upcoming",
            "actualHomeScore": raw.get("actualHomeScore") if raw.get("completed") else None,
            "actualAwayScore": raw.get("actualAwayScore") if raw.get("completed") else None,
        }
        _attach_model(game, model_by_id, existing_by_id.get(str(raw["id"])))
        out.append(game)
    return out


def _refresh_existing_results(
    client: CfbdClient,
    current: dict[str, Any],
) -> dict[str, Any]:
    games = current.get("games")
    if not isinstance(games, list) or not games:
        return current
    season = int(current.get("season", TARGET_SEASON))
    week = int(current.get("week", 1))
    refreshed = {str(game["id"]): game for game in fetch_week(client, season, week)}
    updated = dict(current)
    next_games: list[dict[str, Any]] = []
    for old in games:
        if not isinstance(old, dict):
            continue
        game = dict(old)
        live = refreshed.get(str(game.get("id")))
        if live:
            game["kickoff"] = live.get("kickoff") or game.get("kickoff")
            if live.get("completed"):
                game["status"] = "final"
                game["actualHomeScore"] = live.get("actualHomeScore")
                game["actualAwayScore"] = live.get("actualAwayScore")
        next_games.append(game)
    updated["games"] = next_games
    if next_games and all(game.get("status") == "final" for game in next_games):
        updated["status"] = "final"
    return updated


def _archive_final_current(data_root: Path, current: dict[str, Any]) -> None:
    if current.get("status") != "final" or not current.get("games"):
        return
    season = int(current["season"])
    week = int(current["week"])
    path = _slate_snapshot_path(data_root, season, week)
    if path.exists():
        existing = _read_object(path)
        if existing.get("games") != current.get("games"):
            raise ValueError(f"Immutable BTM slate snapshot already differs: {path}")
        return
    snapshot = dict(current)
    snapshot["archivedAt"] = datetime.now(timezone.utc).isoformat()
    _write_json(path, snapshot)


def publish(
    *,
    data_root: Path,
    season: int,
    week: int | None,
    advance: bool,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    current_path = _current_path(data_root)
    existing = _read_object(current_path)

    with CfbdClient() as client:
        if existing.get("games"):
            existing = _refresh_existing_results(client, existing)
            _write_json(current_path, existing)
            _archive_final_current(data_root, existing)

        if week is None:
            current_week = int(existing.get("week", 1)) if existing else 1
            if advance and existing.get("status") == "final":
                week = current_week + 1
            else:
                week = current_week
        week = int(week)
        if week < 1 or week > MAX_REGULAR_WEEK:
            raise ValueError(f"Target regular-season week must be 1-{MAX_REGULAR_WEEK}; got {week}")

        # When moving to another week, never carry frozen IDs/model calls from the
        # previous contest into the new selection.
        same_week = int(existing.get("season", season)) == int(season) and int(existing.get("week", week)) == week
        selection_context = existing if same_week else {}

        rankings = build_week_rankings(client, data_root, season=season, week=week)
        ranking_path = _ranking_path(data_root, season, week)
        _write_json(ranking_path, rankings)

        schedule = fetch_week(client, season, week)
        if not schedule:
            raise RuntimeError(f"CFBD returned no FBS-vs-FBS schedule for {season} Week {week}")
        model_by_id = _prediction_rows(data_root)
        games = select_slate(
            schedule,
            rankings,
            existing_current=selection_context,
            model_by_id=model_by_id,
        )
        if not games:
            raise RuntimeError(f"No rankable Beat the Model games for {season} Week {week}")

        model_ready = len(games) == SLATE_SIZE and all(game.get("modelWinner") for game in games)
        all_final = games and all(game.get("status") == "final" for game in games)
        status = "final" if all_final else "open" if model_ready else "awaiting-model"
        published_at = selection_context.get("publishedAt") or now
        payload = {
            "schemaVersion": 2,
            "version": BTM_VERSION,
            "liveScheduleVersion": LIVE_SCHEDULE_VERSION,
            "season": int(season),
            "week": week,
            "updatedAt": now,
            "publishedAt": published_at,
            "status": status,
            "slateSize": SLATE_SIZE,
            "selectedGames": len(games),
            "rankingVersion": POWER_RANKING_VERSION,
            "selectionVersion": SLATE_SELECTION_VERSION,
            "modelVersion": MODEL_VERSION,
            "modelReady": model_ready,
            "selectionFrozen": status in {"open", "locked", "final"},
            "matchupGapWeight": MATCHUP_GAP_WEIGHT,
            "games": games,
        }
        _write_json(current_path, payload)
        if status == "final":
            _archive_final_current(data_root, payload)
        return payload


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Fetch and publish the live Beat the Model Official 15")
    parser.add_argument("--season", type=int, default=TARGET_SEASON)
    parser.add_argument("--week", type=int, help="Explicit target week; omit to refresh/advance current.json")
    parser.add_argument(
        "--advance",
        action="store_true",
        help="When the current slate is final and --week is omitted, advance to the next week",
    )
    parser.add_argument("--data-root", type=Path, default=root / "website" / "data")
    args = parser.parse_args()

    payload = publish(
        data_root=args.data_root,
        season=args.season,
        week=args.week,
        advance=args.advance,
    )
    print("BEAT THE MODEL LIVE SCHEDULE: PUBLISHED")
    print(f"Season/week: {payload['season']} Week {payload['week']}")
    print(f"Official slate: {payload['selectedGames']}/{payload['slateSize']}")
    print(f"Model ready: {payload['modelReady']}")
    print(f"Status: {payload['status']}")
    print(f"Selection frozen: {payload['selectionFrozen']}")
    print(f"Output: {args.data_root / 'beat-the-model' / 'current.json'}")


if __name__ == "__main__":
    main()
