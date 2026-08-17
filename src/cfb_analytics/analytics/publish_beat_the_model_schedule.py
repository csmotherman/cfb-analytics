"""Fetch the live CFBD schedule and publish the next Beat the Model slate.

This module owns matchup population, market context, and result refreshes. It does
not fit Prediction v2 and never uses model output to decide which games make the
Official 15.

Live product contract:

* Week 1 uses the already-published final-2025 BTM power rankings exactly.
* Week 2+ rebuilds current-season site-aware SRS strictly from completed games
  before the target week and applies the frozen 100/75/50/25/0 carryover rule.
* The Official 15 prioritizes games that combine strong BTM-ranked teams with a
  competitive consensus market line. Market data can choose interesting games;
  Prediction-v2 picks, margins, and availability cannot.
* CFBD /lines is reduced to a provider-consensus snapshot. When paired American
  moneylines are available, the public market bar uses median no-vig probability.
* Once all 15 frozen model calls exist, the slate becomes ``open``. Selected IDs,
  model calls, and the market snapshot are then preserved while schedule/results
  continue to refresh.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

from cfb_analytics.analytics.authoritative_game_targets import normalize_authoritative_game
from cfb_analytics.analytics.beat_the_model import (
    BTM_VERSION,
    MATCHUP_GAP_WEIGHT,
    POWER_RANKING_VERSION,
    SLATE_SIZE,
    blend_team_rating,
    matchup_score,
)
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import fit_site_aware_srs
from cfb_analytics.analytics.site_context_audit import extract_neutral_site
from cfb_analytics.sources.cfbd.client import CfbdClient, CfbdError

TARGET_SEASON = 2026
LIVE_SCHEDULE_VERSION = "beat-the-model-live-schedule-v2"
LIVE_SLATE_SELECTION_VERSION = "btm-top-15-ranked-market-matchups-v2"
MARKET_SOURCE_VERSION = "cfbd-lines-consensus-v1"
MODEL_VERSION = "prediction-v2-2026-prospective-freeze-v1"
MAX_REGULAR_WEEK = 16

ELITE_MAX_WORST_RANK = 40
ELITE_MAX_RANK_GAP = 15
ELITE_MAX_MARKET_SPREAD = 7.5
STRONG_MAX_WORST_RANK = 50
STRONG_MAX_RANK_GAP = 20
STRONG_MAX_MARKET_SPREAD = 10.0
COMPETITIVE_MAX_WORST_RANK = 65
COMPETITIVE_MAX_MARKET_SPREAD = 14.0

MARKET_FIELDS = (
    "marketSource",
    "marketProviderCount",
    "marketSpread",
    "marketFavorite",
    "marketLine",
    "marketHomeMoneyline",
    "marketAwayMoneyline",
    "marketHomeWinProbability",
    "marketAwayWinProbability",
    "marketSnapshotAt",
)


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
    ids = [str(game["id"]) for game in games]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate CFBD game ID in {season} Week {week}")
    return games


def _median_finite(values: list[Any]) -> float | None:
    cleaned = [float(value) for value in values if _finite(value)]
    return float(median(cleaned)) if cleaned else None


def _american_implied_probability(odds: Any) -> float | None:
    if not _finite(odds):
        return None
    value = float(odds)
    if value < 0:
        return -value / (-value + 100.0)
    if value > 0:
        return 100.0 / (value + 100.0)
    return None


def _formatted_favorite(value: Any, home: str, away: str) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().lower()
    for team in sorted((home, away), key=len, reverse=True):
        if text.startswith(team.lower()):
            return team
    return None


def market_consensus(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Reduce one CFBD BettingGame into a stable provider-consensus market view."""
    gid = raw.get("id", raw.get("gameId"))
    home = raw.get("homeTeam", raw.get("home_team"))
    away = raw.get("awayTeam", raw.get("away_team"))
    lines = raw.get("lines")
    if gid is None or not home or not away or not isinstance(lines, list):
        return None

    home_name = str(home)
    away_name = str(away)
    spreads: list[float] = []
    home_moneylines: list[float] = []
    away_moneylines: list[float] = []
    home_no_vig_probabilities: list[float] = []
    favorite_votes: list[str] = []
    providers: set[str] = set()

    for line in lines:
        if not isinstance(line, dict):
            continue
        provider = line.get("provider")
        if isinstance(provider, str) and provider.strip():
            providers.add(provider.strip())

        spread = line.get("spread")
        if _finite(spread):
            spreads.append(float(spread))

        home_ml = line.get("homeMoneyline", line.get("home_moneyline"))
        away_ml = line.get("awayMoneyline", line.get("away_moneyline"))
        if _finite(home_ml):
            home_moneylines.append(float(home_ml))
        if _finite(away_ml):
            away_moneylines.append(float(away_ml))

        home_implied = _american_implied_probability(home_ml)
        away_implied = _american_implied_probability(away_ml)
        if home_implied is not None and away_implied is not None:
            total = home_implied + away_implied
            if total > 0:
                home_no_vig_probabilities.append(home_implied / total)

        favorite = _formatted_favorite(
            line.get("formattedSpread", line.get("formatted_spread")),
            home_name,
            away_name,
        )
        if favorite:
            favorite_votes.append(favorite)

    provider_count = len(providers) if providers else sum(isinstance(line, dict) for line in lines)
    if provider_count == 0:
        return None

    signed_spread = _median_finite(spreads)
    market_spread = abs(signed_spread) if signed_spread is not None else None
    home_probability = _median_finite(home_no_vig_probabilities)
    away_probability = 1.0 - home_probability if home_probability is not None else None

    favorite: str | None = None
    if home_probability is not None:
        if home_probability > 0.5000001:
            favorite = home_name
        elif home_probability < 0.4999999:
            favorite = away_name
    if favorite is None and favorite_votes:
        home_votes = sum(vote == home_name for vote in favorite_votes)
        away_votes = sum(vote == away_name for vote in favorite_votes)
        if home_votes > away_votes:
            favorite = home_name
        elif away_votes > home_votes:
            favorite = away_name

    if market_spread is not None and market_spread <= 0.001:
        line_label = "Pick'em"
    elif market_spread is not None and favorite:
        line_label = f"{favorite} -{market_spread:g}"
    elif favorite:
        line_label = f"{favorite} favored"
    elif market_spread is not None:
        line_label = f"Consensus spread {market_spread:g}"
    else:
        line_label = "Market available"

    return {
        "marketSource": MARKET_SOURCE_VERSION,
        "marketProviderCount": int(provider_count),
        "marketSpread": market_spread,
        "marketFavorite": favorite,
        "marketLine": line_label,
        "marketHomeMoneyline": _median_finite(home_moneylines),
        "marketAwayMoneyline": _median_finite(away_moneylines),
        "marketHomeWinProbability": home_probability,
        "marketAwayWinProbability": away_probability,
    }


def fetch_market_consensus(client: CfbdClient, season: int, week: int) -> dict[str, dict[str, Any]]:
    """Fetch CFBD /lines and index consensus snapshots by authoritative game ID."""
    response = client.lines(int(season), int(week), "regular")
    if not isinstance(response.payload, list):
        raise ValueError(f"Unexpected CFBD lines payload for {season} Week {week}")
    out: dict[str, dict[str, Any]] = {}
    for raw in response.payload:
        if not isinstance(raw, dict):
            continue
        consensus = market_consensus(raw)
        if consensus is None:
            continue
        gid = raw.get("id", raw.get("gameId"))
        if gid is None:
            continue
        key = str(gid)
        if key in out:
            raise ValueError(f"Duplicate CFBD betting game ID in {season} Week {week}: {key}")
        out[key] = consensus
    return out


def _seed_rankings_path(data_root: Path, season: int) -> Path:
    return data_root / "beat-the-model" / "rankings" / f"season={season}" / "week=1.json"


def _ranking_path(data_root: Path, season: int, week: int) -> Path:
    return data_root / "beat-the-model" / "rankings" / f"season={season}" / f"week={week}.json"


def _current_path(data_root: Path) -> Path:
    return data_root / "beat-the-model" / "current.json"


def _slate_snapshot_path(data_root: Path, season: int, week: int) -> Path:
    return data_root / "beat-the-model" / "slates" / f"season={season}" / f"week={week}.json"


def _prediction_rows(data_root: Path) -> dict[str, dict[str, Any]]:
    """Load already-published model calls without making them selection inputs."""
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
    cleaned = [
        row
        for row in teams
        if isinstance(row, dict) and row.get("team") and _finite(row.get("rating"))
    ]
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


def _selection_tier(home_rank: int, away_rank: int, market: dict[str, Any] | None) -> int:
    worst_rank = max(int(home_rank), int(away_rank))
    rank_gap = abs(int(home_rank) - int(away_rank))
    spread = market.get("marketSpread") if market else None

    if _finite(spread):
        value = float(spread)
        if worst_rank <= ELITE_MAX_WORST_RANK and rank_gap <= ELITE_MAX_RANK_GAP and value <= ELITE_MAX_MARKET_SPREAD:
            return 0
        if worst_rank <= STRONG_MAX_WORST_RANK and rank_gap <= STRONG_MAX_RANK_GAP and value <= STRONG_MAX_MARKET_SPREAD:
            return 1
        if worst_rank <= COMPETITIVE_MAX_WORST_RANK and value <= COMPETITIVE_MAX_MARKET_SPREAD:
            return 2

    # Lines are sometimes not posted when the slate first appears. Strong,
    # close-ranked games remain preferable to a weak mismatch while waiting.
    if worst_rank <= STRONG_MAX_WORST_RANK and rank_gap <= STRONG_MAX_RANK_GAP:
        return 3
    return 4


def _selection_score(home_rank: int, away_rank: int, market: dict[str, Any] | None) -> float:
    average_rank = (int(home_rank) + int(away_rank)) / 2.0
    rank_gap = abs(int(home_rank) - int(away_rank))
    spread = market.get("marketSpread") if market else None
    market_penalty = float(spread) if _finite(spread) else 8.0
    return average_rank + 0.50 * rank_gap + market_penalty


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


def _attach_market(
    game: dict[str, Any],
    market_by_id: dict[str, dict[str, Any]],
    existing: dict[str, Any] | None,
    *,
    market_snapshot_at: str | None,
    preserve_existing: bool,
) -> None:
    existing = existing or {}
    current = market_by_id.get(str(game["id"]), {})
    existing_has_market = bool(existing.get("marketSource") or existing.get("marketProviderCount"))
    source = existing if preserve_existing and existing_has_market else current or existing

    for field in MARKET_FIELDS:
        if field == "marketSnapshotAt":
            continue
        game[field] = source.get(field)
    if source.get("marketSource"):
        game["marketSnapshotAt"] = source.get("marketSnapshotAt") or market_snapshot_at
    else:
        game["marketSnapshotAt"] = None


def select_slate(
    schedule: list[dict[str, Any]],
    rankings: dict[str, Any],
    *,
    existing_current: dict[str, Any],
    model_by_id: dict[str, dict[str, Any]],
    market_by_id: dict[str, dict[str, Any]] | None = None,
    market_snapshot_at: str | None = None,
) -> list[dict[str, Any]]:
    market_by_id = market_by_id or {}
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
        frozen_ids = [
            str(row.get("id"))
            for row in existing_current.get("games", [])
            if isinstance(row, dict) and row.get("id") is not None
        ]

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
        candidates: list[tuple[int, float, float, int, int, str, dict[str, Any]]] = []
        for game in schedule:
            home_row = ranking_by_team.get(str(game["homeTeam"]))
            away_row = ranking_by_team.get(str(game["awayTeam"]))
            if not home_row or not away_row:
                continue
            hr = int(home_row["rank"])
            ar = int(away_row["rank"])
            market = market_by_id.get(str(game["id"]))
            tier = _selection_tier(hr, ar, market)
            score = _selection_score(hr, ar, market)
            market_spread = float(market["marketSpread"]) if market and _finite(market.get("marketSpread")) else 999.0
            candidates.append(
                (
                    tier,
                    score,
                    market_spread,
                    min(hr, ar),
                    max(hr, ar),
                    str(game["id"]),
                    game,
                )
            )
        candidates.sort(key=lambda item: item[:6])
        selected_raw = [item[6] for item in candidates[:SLATE_SIZE]]

    out: list[dict[str, Any]] = []
    for slot, raw in enumerate(selected_raw, start=1):
        home_row = ranking_by_team.get(str(raw["homeTeam"]))
        away_row = ranking_by_team.get(str(raw["awayTeam"]))
        if not home_row or not away_row:
            raise ValueError(f"Frozen selected game lost a team ranking: {raw['id']}")
        hr = int(home_row["rank"])
        ar = int(away_row["rank"])
        market = market_by_id.get(str(raw["id"]))
        existing_game = existing_by_id.get(str(raw["id"]))
        game = {
            "id": str(raw["id"]),
            "season": int(raw["season"]),
            "week": int(raw["week"]),
            "slot": slot,
            "kickoff": raw.get("kickoff"),
            "homeTeam": raw["homeTeam"],
            "awayTeam": raw["awayTeam"],
            "homeRank": hr,
            "awayRank": ar,
            "homePowerRating": float(home_row["rating"]),
            "awayPowerRating": float(away_row["rating"]),
            "matchupScore": matchup_score(hr, ar),
            "selectionTier": _selection_tier(hr, ar, market if not frozen_ids else existing_game or market),
            "selectionScore": _selection_score(hr, ar, market if not frozen_ids else existing_game or market),
            "status": "final" if raw.get("completed") else "upcoming",
            "actualHomeScore": raw.get("actualHomeScore") if raw.get("completed") else None,
            "actualAwayScore": raw.get("actualAwayScore") if raw.get("completed") else None,
        }
        _attach_market(
            game,
            market_by_id,
            existing_game,
            market_snapshot_at=market_snapshot_at,
            preserve_existing=bool(frozen_ids),
        )
        _attach_model(game, model_by_id, existing_game)
        out.append(game)
    return out


def _refresh_existing_results(client: CfbdClient, current: dict[str, Any]) -> dict[str, Any]:
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

        same_week = (
            int(existing.get("season", season)) == int(season)
            and int(existing.get("week", week)) == week
        )
        selection_context = existing if same_week else {}
        frozen_existing = selection_context.get("status") in {"open", "locked", "final"}

        rankings = build_week_rankings(client, data_root, season=season, week=week)
        ranking_path = _ranking_path(data_root, season, week)
        _write_json(ranking_path, rankings)

        schedule = fetch_week(client, season, week)
        if not schedule:
            raise RuntimeError(f"CFBD returned no FBS-vs-FBS schedule for {season} Week {week}")

        market_fetch_status = "ok"
        try:
            market_by_id = fetch_market_consensus(client, season, week)
            if not market_by_id:
                market_fetch_status = "no-lines"
        except CfbdError:
            # The contest must remain playable if the secondary market feed is
            # unavailable. Ranking-only fallbacks are explicit in the tier rules.
            market_by_id = {}
            market_fetch_status = "unavailable"

        market_snapshot_at = (
            selection_context.get("marketSnapshotAt")
            if frozen_existing and selection_context.get("marketSnapshotAt")
            else now
        )
        model_by_id = _prediction_rows(data_root)
        games = select_slate(
            schedule,
            rankings,
            existing_current=selection_context,
            model_by_id=model_by_id,
            market_by_id=market_by_id,
            market_snapshot_at=market_snapshot_at,
        )
        if not games:
            raise RuntimeError(f"No rankable Beat the Model games for {season} Week {week}")

        model_ready = len(games) == SLATE_SIZE and all(game.get("modelWinner") for game in games)
        all_final = bool(games) and all(game.get("status") == "final" for game in games)
        status = "final" if all_final else "open" if model_ready else "awaiting-model"
        same_selection_version = selection_context.get("selectionVersion") == LIVE_SLATE_SELECTION_VERSION
        published_at = selection_context.get("publishedAt") if same_selection_version else None
        published_at = published_at or now
        market_selected = sum(bool(game.get("marketProviderCount")) for game in games)

        payload = {
            "schemaVersion": 3,
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
            "selectionVersion": LIVE_SLATE_SELECTION_VERSION,
            "modelVersion": MODEL_VERSION,
            "modelReady": model_ready,
            "selectionFrozen": status in {"open", "locked", "final"},
            "matchupGapWeight": MATCHUP_GAP_WEIGHT,
            "marketSource": MARKET_SOURCE_VERSION,
            "marketSnapshotAt": market_snapshot_at,
            "marketFetchStatus": market_fetch_status,
            "marketAvailableGames": len(market_by_id),
            "marketSelectedGames": market_selected,
            "marketSelectionRules": {
                "elite": {
                    "maxWorstRank": ELITE_MAX_WORST_RANK,
                    "maxRankGap": ELITE_MAX_RANK_GAP,
                    "maxSpread": ELITE_MAX_MARKET_SPREAD,
                },
                "strong": {
                    "maxWorstRank": STRONG_MAX_WORST_RANK,
                    "maxRankGap": STRONG_MAX_RANK_GAP,
                    "maxSpread": STRONG_MAX_MARKET_SPREAD,
                },
                "competitive": {
                    "maxWorstRank": COMPETITIVE_MAX_WORST_RANK,
                    "maxSpread": COMPETITIVE_MAX_MARKET_SPREAD,
                },
                "modelUsedForSelection": False,
            },
            "games": games,
        }
        _write_json(current_path, payload)
        if status == "final":
            _archive_final_current(data_root, payload)
        return payload


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(
        description="Fetch rankings, market consensus, and publish the live Beat the Model Official 15"
    )
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
    print(f"Market coverage: {payload['marketSelectedGames']}/{payload['selectedGames']}")
    print(f"Market fetch: {payload['marketFetchStatus']}")
    print(f"Model ready: {payload['modelReady']}")
    print(f"Status: {payload['status']}")
    print(f"Selection frozen: {payload['selectionFrozen']}")
    print(f"Output: {args.data_root / 'beat-the-model' / 'current.json'}")


if __name__ == "__main__":
    main()
