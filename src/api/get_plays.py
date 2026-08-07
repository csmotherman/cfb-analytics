import time
import pandas as pd

from config.config import (
    plays_api,
    SEASON_TYPE,
    REQUEST_DELAY
)


def get_plays(season: int, weeks: list[int]) -> pd.DataFrame:

    all_plays = []

    for week in weeks:

        week = int(week)

        print(f"Downloading {season} Week {week}...")

        plays = plays_api.get_plays(
            year=int(season),
            week=week,
            season_type=SEASON_TYPE
        )

        week_df = pd.DataFrame(
            [play.to_dict() for play in plays]
        )

        week_df["season"] = int(season)
        week_df["week"] = week

        all_plays.append(week_df)

        time.sleep(REQUEST_DELAY)

    plays_df = pd.concat(
        all_plays,
        ignore_index=True
    )

    return plays_df