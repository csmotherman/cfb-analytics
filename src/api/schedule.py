"""CollegeFootballData game schedule functions."""

from __future__ import annotations

import pandas as pd

from src.api.client import get_json


def _season_type(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "reg": "regular",
        "regular": "regular",
        "post": "postseason",
        "postseason": "postseason",
    }
    if normalized not in aliases:
        raise ValueError("season_type must be REG, regular, POST, or postseason")
    return aliases[normalized]


def get_schedule(
    season: int,
    season_type: str = "regular",
) -> pd.DataFrame:
    """Return one row per game in a CFBD season schedule."""

    normalized_type = _season_type(season_type)
    data = get_json(
        "games",
        params={
            "year": season,
            "seasonType": normalized_type,
        },
    )

    if not isinstance(data, list):
        raise TypeError("CFBD /games response must be a JSON array")

    rows: list[dict] = []

    for game in data:
        if not isinstance(game, dict):
            continue

        row = dict(game)
        row["game_id"] = row.pop("id", None)
        row["season"] = row.get("season", season)
        row["season_type"] = row.pop("seasonType", normalized_type)
        row["scheduled"] = row.pop("startDate", None)
        row["status"] = row.pop("status", None)
        row["home_id"] = row.pop("homeId", None)
        row["home_name"] = row.pop("homeTeam", None)
        row["away_id"] = row.pop("awayId", None)
        row["away_name"] = row.pop("awayTeam", None)
        row["conference_game"] = row.pop("conferenceGame", None)
        row["neutral_site"] = row.pop("neutralSite", None)

        rows.append(row)

    return pd.DataFrame(rows)


def get_game_ids(
    season: int,
    season_type: str = "regular",
) -> list[str]:
    """Return every non-null CFBD game ID from a season schedule."""

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
    team: str,
    season_type: str = "regular",
) -> pd.DataFrame:
    """Return schedule rows involving one team name."""

    normalized_type = _season_type(season_type)
    data = get_json(
        "games",
        params={
            "year": season,
            "seasonType": normalized_type,
            "team": team,
        },
    )

    if not isinstance(data, list):
        raise TypeError("CFBD /games response must be a JSON array")

    schedule = get_schedule(season, normalized_type)

    if schedule.empty:
        return schedule

    team_lower = team.casefold()
    mask = (
        schedule["home_name"].fillna("").str.casefold().eq(team_lower)
        | schedule["away_name"].fillna("").str.casefold().eq(team_lower)
    )
    return schedule.loc[mask].reset_index(drop=True)


def get_multi_season_schedule(
    start_season: int,
    end_season: int,
    season_type: str = "regular",
) -> pd.DataFrame:
    """Return schedules for an inclusive range of seasons."""

    if end_season < start_season:
        raise ValueError("end_season must be >= start_season")

    frames = [
        get_schedule(season, season_type)
        for season in range(start_season, end_season + 1)
    ]
    nonempty = [frame for frame in frames if not frame.empty]
    return pd.concat(nonempty, ignore_index=True) if nonempty else pd.DataFrame()
