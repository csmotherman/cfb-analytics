import pandas as pd

from src.api.client import get


def get_schedule(year: int, season_type: str = "REG") -> pd.DataFrame:
    """
    Download a season schedule and return one row per game.
    """
    data = get(f"games/{year}/{season_type}/schedule.json")

    games = []

    for week in data["weeks"]:
        for game in week["games"]:

            games.append({
                "week": week["sequence"],
                "game_id": game["id"],
                "scheduled": game["scheduled"],

                "home_id": game["home"]["id"],
                "home_alias": game["home"]["alias"],
                "home_name": game["home"]["name"],

                "away_id": game["away"]["id"],
                "away_alias": game["away"]["alias"],
                "away_name": game["away"]["name"],
            })

    return pd.DataFrame(games)


def get_game_ids(year: int, season_type="REG"):
    """
    Return every game_id in a season.
    """
    return get_schedule(year, season_type)["game_id"].tolist()


def get_team_schedule(year: int,
                      team_alias: str,
                      season_type="REG"):
    """
    Return schedule for one team.
    """

    schedule = get_schedule(year, season_type)

    return schedule[
        (schedule.home_alias == team_alias)
        |
        (schedule.away_alias == team_alias)
    ].reset_index(drop=True)