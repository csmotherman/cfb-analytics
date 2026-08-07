import pandas as pd

from config.config import drives_api, SEASON_TYPE


def get_drives(season: int) -> pd.DataFrame:

    drives = drives_api.get_drives(
        year=int(season),
        season_type=SEASON_TYPE
    )

    drives_df = pd.DataFrame(
        [drive.to_dict() for drive in drives]
    )

    return drives_df