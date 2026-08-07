import pandas as pd
import cfbd

from config.config import games_api, SEASON_TYPE


def get_games(season: int) -> pd.DataFrame:

    games = games_api.get_games(
        year=int(season),
        season_type=SEASON_TYPE
    )

    games_df = pd.DataFrame(
        [game.to_dict() for game in games]
    )

    return games_df