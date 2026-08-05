"""SportRadar season schedule functions."""

from __future__ import annotations

import pandas as pd

from src.api.client import get_json


def get_schedule(
    season: int,
    season_type: str = "REG",
) -> pd.DataFrame:
    """Return one row per game in a SportRadar season schedule."""

    season_type = season_type.upper()

    data = get_json(
        f"games/{season}/{season_type}/schedule.json"
    )

    rows: list[dict] = []

    for week in data.get("weeks", []):
        week_number = week.get("sequence")
        week_id = week.get("id")
        week_title = week.get("title")

        for game in week.get("games", []):
            home = game.get("home") or {}
            away = game.get("away") or {}

            row = {
                "season": season,
                "season_type": season_type,
                "week": week_number,
                "week_id": week_id,
                "week_title": week_title,
                "game_id": game.get("id"),
                "scheduled": game.get("scheduled"),
                "status": game.get("status"),
                "game_type": game.get("game_type"),
                "conference_game": game.get("conference_game"),
                "neutral_site": game.get("neutral_site"),
                "home_id": home.get("id"),
                "home_alias": home.get("alias"),
                "home_market": home.get("market"),
                "home_name": home.get("name"),
                "away_id": away.get("id"),
                "away_alias": away.get("alias"),
                "away_market": away.get("market"),
                "away_name": away.get("name"),
            }

            rows.append(row)

    return pd.DataFrame(rows)


def get_game_ids(
    season: int,
    season_type: str = "REG",
) -> list[str]:
    """Return every non-null game ID from a season schedule."""

    schedule = get_schedule(season, season_type)

    if schedule.empty:
        return []

    return (
        schedule["game_id"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )


def get_team_schedule(
    season: int,
    team_alias: str,
    season_type: str = "REG",
) -> pd.DataFrame:
    """Return schedule rows involving one team alias."""

    schedule = get_schedule(season, season_type)

    if schedule.empty:
        return schedule

    alias = team_alias.upper()

    mask = (
        schedule["home_alias"].eq(alias)
        | schedule["away_alias"].eq(alias)
    )

    return schedule.loc[mask].reset_index(drop=True)


def get_multi_season_schedule(
    start_season: int,
    end_season: int,
    season_type: str = "REG",
) -> pd.DataFrame:
    """Return schedules for an inclusive range of seasons."""

    if end_season < start_season:
        raise ValueError("end_season must be >= start_season")

    frames = [
        get_schedule(season, season_type)
        for season in range(start_season, end_season + 1)
    ]

    nonempty = [frame for frame in frames if not frame.empty]

    if not nonempty:
        return pd.DataFrame()

    return pd.concat(nonempty, ignore_index=True)