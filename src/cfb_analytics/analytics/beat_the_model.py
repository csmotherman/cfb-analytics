"""Build the model-independent rankings and weekly slates for Beat the Model.

Product rules encoded here:
- team rankings answer "how strong is this team?" and are separate from Prediction v2;
- Week 1 rankings are the previous season's final power ratings;
- after games begin, the prior-season rating fades 100/75/50/25/0 percent over
  a team's first four current-season games;
- the weekly slate is selected from team rankings only. Prediction-v2 output is
  required so The Model can participate, but its pick/confidence never affects
  which eligible matchup ranks higher;
- normal weekly slates contain the 15 strongest regular-season matchups;
- 2020 remains absent from the comparable project universe.

Power rating semantics are the existing site-aware opponent-adjusted SRS team
rating: expected neutral-field scoring strength relative to the fitted field.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    fit_site_aware_srs,
    partition_key,
)
from cfb_analytics.analytics.site_context_audit import load_raw_site_rows

BTM_VERSION = "beat-the-model-v1"
POWER_RANKING_VERSION = "btm-site-aware-srs-four-game-carryover-v1"
SLATE_SELECTION_VERSION = "btm-top-15-power-matchups-v1"
SLATE_SIZE = 15
PRIOR_WINDOW_GAMES = 4
MATCHUP_GAP_WEIGHT = 0.25
COMPARABLE_SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def prior_weight(games_before: int) -> float:
    games = max(0, int(games_before))
    return max(0.0, (PRIOR_WINDOW_GAMES - min(games, PRIOR_WINDOW_GAMES)) / PRIOR_WINDOW_GAMES)


def matchup_score(home_rank: int, away_rank: int) -> float:
    """Lower is a bigger matchup: reward quality first, then closeness in rank."""
    average = (int(home_rank) + int(away_rank)) / 2.0
    gap = abs(int(home_rank) - int(away_rank))
    return average + MATCHUP_GAP_WEIGHT * gap


def _attach_site_context(raw_root: Path, processed_root: Path, season: int) -> list[dict[str, Any]]:
    rows = load_saved_feature_store(processed_root, season)
    site_rows, _, _ = load_raw_site_rows(raw_root, season)
    attached: list[dict[str, Any]] = []
    for row in rows:
        gid = str(row.get("gameId"))
        site = site_rows.get(gid)
        if site is None or not isinstance(site.get("isNeutralSite"), bool):
            raise ValueError(f"Missing parseable site context for {season} game {gid}")
        attached.append({**row, "isNeutralSite": bool(site["isNeutralSite"])})
    return attached


def final_power_ratings(raw_root: Path, processed_root: Path, season: int) -> dict[str, float]:
    rows = _attach_site_context(raw_root, processed_root, season)
    fitted = fit_site_aware_srs(rows)
    if fitted.get("converged") is not True:
        raise RuntimeError(f"Final site-aware power rating did not converge for {season}")
    return {
        str(team): float(value)
        for team, value in dict(fitted.get("ratings", {})).items()
        if _finite(value)
    }


def _rank_rows(ratings: dict[str, float], *, source_season: int | None = None) -> list[dict[str, Any]]:
    ordered = sorted(ratings.items(), key=lambda item: (-float(item[1]), item[0]))
    return [
        {
            "rank": index,
            "team": team,
            "rating": float(rating),
            "sourceSeason": source_season,
        }
        for index, (team, rating) in enumerate(ordered, start=1)
    ]


def _team_games_before(rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        home = row.get("homeTeam")
        away = row.get("awayTeam")
        if home:
            counts[str(home)] += 1
        if away:
            counts[str(away)] += 1
    return counts


def _season_teams(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(team)
        for row in rows
        for team in (row.get("homeTeam"), row.get("awayTeam"))
        if team
    }


def blend_team_rating(
    *,
    prior_rating: float | None,
    current_rating: float | None,
    games_before: int,
) -> float | None:
    """Blend numeric ratings, never ordinal rank positions."""
    weight = prior_weight(games_before)
    prior = float(prior_rating) if _finite(prior_rating) else None
    current = float(current_rating) if _finite(current_rating) else None

    if weight >= 1.0:
        return prior
    if weight <= 0.0:
        return current
    if prior is None:
        return current
    if current is None:
        return prior
    return weight * prior + (1.0 - weight) * current


def season_weekly_rankings(
    raw_root: Path,
    processed_root: Path,
    season: int,
    *,
    prior_season: int | None,
) -> dict[int, list[dict[str, Any]]]:
    """Return rankings entering each observed regular-season week."""
    rows = _attach_site_context(raw_root, processed_root, season)
    prior_ratings = final_power_ratings(raw_root, processed_root, prior_season) if prior_season is not None else {}
    teams = _season_teams(rows) | set(prior_ratings)
    regular_weeks = sorted(
        {
            int(row.get("week") or 0)
            for row in rows
            if str(row.get("seasonType") or "regular").lower() in {"regular", "regular_season"}
        }
    )
    out: dict[int, list[dict[str, Any]]] = {}

    for week in regular_weeks:
        current_key = (0, int(week))
        history = [row for row in rows if partition_key(row) < current_key]
        fitted = fit_site_aware_srs(history)
        if fitted.get("converged") is not True:
            raise RuntimeError(f"Entering-week site-aware power rating did not converge for {season} Week {week}")
        current_ratings = {
            str(team): float(value)
            for team, value in dict(fitted.get("ratings", {})).items()
            if _finite(value)
        }
        games_before = _team_games_before(history)

        blended: dict[str, float] = {}
        for team in teams:
            value = blend_team_rating(
                prior_rating=prior_ratings.get(team),
                current_rating=current_ratings.get(team),
                games_before=games_before.get(team, 0),
            )
            if value is not None and _finite(value):
                blended[team] = float(value)
        out[int(week)] = _rank_rows(blended, source_season=prior_season)

    return out


def select_official_slate(
    games: list[dict[str, Any]],
    rankings: list[dict[str, Any]],
    *,
    slate_size: int = SLATE_SIZE,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Annotate games and select the strongest regular-season matchups.

    A game must have rankings for both teams and a valid model call so The Model
    can participate. The ordering itself uses only ranks, never the model margin,
    win probability, confidence, market line, or result.
    """
    by_team = {str(row["team"]): row for row in rankings if row.get("team") and row.get("rank") is not None}
    annotated: list[dict[str, Any]] = []
    candidates: list[tuple[float, int, int, str]] = []

    for raw in games:
        game = dict(raw)
        home = str(game.get("homeTeam"))
        away = str(game.get("awayTeam"))
        home_row = by_team.get(home)
        away_row = by_team.get(away)
        regular = str(game.get("seasonType") or "regular").lower() in {"regular", "regular_season"}
        model_available = _finite(game.get("modelHomeMargin"))

        game.update(
            {
                "beatTheModelSelected": False,
                "beatTheModelSlot": None,
                "homeRank": int(home_row["rank"]) if home_row else None,
                "awayRank": int(away_row["rank"]) if away_row else None,
                "homePowerRating": float(home_row["rating"]) if home_row and _finite(home_row.get("rating")) else None,
                "awayPowerRating": float(away_row["rating"]) if away_row and _finite(away_row.get("rating")) else None,
                "matchupScore": None,
            }
        )

        if regular and model_available and home_row and away_row:
            score = matchup_score(int(home_row["rank"]), int(away_row["rank"]))
            game["matchupScore"] = score
            candidates.append((score, min(int(home_row["rank"]), int(away_row["rank"])), max(int(home_row["rank"]), int(away_row["rank"])), str(game.get("id"))))
        annotated.append(game)

    candidates.sort()
    selected_ids = [gid for *_, gid in candidates[: max(0, int(slate_size))]]
    selected_slot = {gid: index for index, gid in enumerate(selected_ids, start=1)}
    for game in annotated:
        gid = str(game.get("id"))
        if gid in selected_slot:
            game["beatTheModelSelected"] = True
            game["beatTheModelSlot"] = selected_slot[gid]

    selected = [game for game in annotated if game.get("beatTheModelSelected") is True]
    graded = [game for game in selected if isinstance(game.get("winnerCorrect"), bool)]
    model_wins = sum(game.get("winnerCorrect") is True for game in graded)
    model_losses = sum(game.get("winnerCorrect") is False for game in graded)
    model_games = [game for game in selected if _finite(game.get("modelHomeMargin")) and _finite(game.get("modelAbsoluteError"))]

    summary = {
        "version": BTM_VERSION,
        "rankingVersion": POWER_RANKING_VERSION,
        "selectionVersion": SLATE_SELECTION_VERSION,
        "slateSize": int(slate_size),
        "eligibleGames": len(candidates),
        "selectedGames": len(selected),
        "selectedGameIds": selected_ids,
        "modelWins": model_wins,
        "modelLosses": model_losses,
        "modelAccuracy": model_wins / len(graded) if graded else None,
        "modelMae": (
            sum(float(game["modelAbsoluteError"]) for game in model_games) / len(model_games)
            if model_games
            else None
        ),
    }
    return annotated, summary


def decorate_archive(
    *,
    raw_root: Path,
    processed_root: Path,
    archive_root: Path,
) -> dict[str, Any]:
    """Add rankings and Official 15 metadata to generated historical archive files."""
    ranking_cache: dict[int, dict[int, list[dict[str, Any]]]] = {}
    total_slates = 0
    total_selected = 0

    for season in COMPARABLE_SEASONS:
        prior = season - 1 if season - 1 in COMPARABLE_SEASONS else None
        ranking_cache[season] = season_weekly_rankings(
            raw_root,
            processed_root,
            season,
            prior_season=prior,
        )
        season_dir = archive_root / f"season={season}"
        if not season_dir.exists():
            continue
        for path in sorted(season_dir.glob("week=*.json")):
            payload = json.loads(path.read_text())
            if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
                continue
            week = int(payload.get("week") or 0)
            rankings = ranking_cache[season].get(week, [])
            annotated, btm = select_official_slate(payload["games"], rankings)
            payload["games"] = annotated
            payload["beatTheModel"] = btm
            path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            if btm["selectedGames"]:
                total_slates += 1
                total_selected += int(btm["selectedGames"])

    return {
        "version": BTM_VERSION,
        "rankingVersion": POWER_RANKING_VERSION,
        "selectionVersion": SLATE_SELECTION_VERSION,
        "historicalSlates": total_slates,
        "historicalSelectedGames": total_selected,
    }


def write_current_week1_rankings(
    *,
    raw_root: Path,
    processed_root: Path,
    website_data_root: Path,
    target_season: int = 2026,
) -> dict[str, Any]:
    """Seed Week 1 exactly from the immediately previous season's final ratings."""
    source_season = int(target_season) - 1
    ratings = final_power_ratings(raw_root, processed_root, source_season)
    teams = _rank_rows(ratings, source_season=source_season)
    payload = {
        "schemaVersion": 1,
        "version": BTM_VERSION,
        "rankingVersion": POWER_RANKING_VERSION,
        "season": int(target_season),
        "week": 1,
        "sourceSeason": source_season,
        "method": "Week 1 equals the previous season's final site-aware power ratings.",
        "teams": teams,
    }
    destination = website_data_root / "beat-the-model" / "rankings" / f"season={target_season}" / "week=1.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def write_current_game_data(
    *,
    website_data_root: Path,
    rankings_payload: dict[str, Any],
) -> dict[str, Any]:
    """Create the current Beat the Model slate from ranked live predictions when available."""
    predictions_path = website_data_root / "predictions.json"
    prediction_payload: dict[str, Any] = {}
    if predictions_path.exists():
        parsed = json.loads(predictions_path.read_text())
        if isinstance(parsed, dict):
            prediction_payload = parsed

    season = int(rankings_payload["season"])
    week = int(rankings_payload["week"])
    current = prediction_payload.get("current") if isinstance(prediction_payload.get("current"), list) else []
    current = [row for row in current if isinstance(row, dict) and int(row.get("season", season)) == season and int(row.get("week", week)) == week]

    ranking_by_team = {str(row["team"]): row for row in rankings_payload.get("teams", []) if isinstance(row, dict) and row.get("team")}
    candidates: list[tuple[float, str, dict[str, Any]]] = []
    for row in current:
        home = str(row.get("homeTeam"))
        away = str(row.get("awayTeam"))
        home_rank = ranking_by_team.get(home)
        away_rank = ranking_by_team.get(away)
        if not home_rank or not away_rank or not row.get("predictedWinner"):
            continue
        score = matchup_score(int(home_rank["rank"]), int(away_rank["rank"]))
        candidates.append((score, str(row.get("id")), row))
    candidates.sort(key=lambda item: (item[0], item[1]))

    games: list[dict[str, Any]] = []
    for slot, (score, _, row) in enumerate(candidates[:SLATE_SIZE], start=1):
        home = str(row.get("homeTeam"))
        away = str(row.get("awayTeam"))
        home_rank = ranking_by_team[home]
        away_rank = ranking_by_team[away]
        games.append(
            {
                "id": str(row.get("id")),
                "season": season,
                "week": week,
                "slot": slot,
                "kickoff": row.get("kickoff"),
                "homeTeam": home,
                "awayTeam": away,
                "homeRank": int(home_rank["rank"]),
                "awayRank": int(away_rank["rank"]),
                "homePowerRating": float(home_rank["rating"]),
                "awayPowerRating": float(away_rank["rating"]),
                "matchupScore": score,
                "modelWinner": row.get("predictedWinner"),
                "modelHomeWinProbability": row.get("homeWinProbability"),
                "modelProjectedHomeScore": row.get("projectedHomeScore"),
                "modelProjectedAwayScore": row.get("projectedAwayScore"),
                "status": row.get("status", "upcoming"),
                "actualHomeScore": row.get("actualHomeScore"),
                "actualAwayScore": row.get("actualAwayScore"),
            }
        )

    payload = {
        "schemaVersion": 1,
        "version": BTM_VERSION,
        "season": season,
        "week": week,
        "updatedAt": prediction_payload.get("updatedAt"),
        "status": "open" if games else "awaiting-slate",
        "slateSize": SLATE_SIZE,
        "rankingVersion": POWER_RANKING_VERSION,
        "selectionVersion": SLATE_SELECTION_VERSION,
        "modelVersion": prediction_payload.get("modelVersion", "prediction-v2-2026-prospective-freeze-v1"),
        "games": games,
    }
    destination = website_data_root / "beat-the-model" / "current.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def publish_beat_the_model(
    *,
    raw_root: Path,
    processed_root: Path,
    archive_root: Path,
    website_data_root: Path,
    target_season: int = 2026,
) -> dict[str, Any]:
    archive_report = decorate_archive(
        raw_root=raw_root,
        processed_root=processed_root,
        archive_root=archive_root,
    )
    rankings = write_current_week1_rankings(
        raw_root=raw_root,
        processed_root=processed_root,
        website_data_root=website_data_root,
        target_season=target_season,
    )
    current = write_current_game_data(
        website_data_root=website_data_root,
        rankings_payload=rankings,
    )
    return {
        **archive_report,
        "currentSeason": int(current["season"]),
        "currentWeek": int(current["week"]),
        "currentRankedTeams": len(rankings["teams"]),
        "currentSlateGames": len(current["games"]),
        "currentStatus": current["status"],
    }
