import pandas as pd

from cfb_analytics.clean.drives import clean_drives
from cfb_analytics.validate.drives import validate_drives


def test_drive_flags_and_points():
    raw = pd.DataFrame([{
        "id":"d1", "gameId":"g1", "offense":"Michigan", "defense":"Ohio State",
        "driveNumber":1, "plays":3, "yards":-2, "startOffenseScore":0, "endOffenseScore":0,
        "driveResult":"Punt",
    }, {
        "id":"d2", "gameId":"g1", "offense":"Ohio State", "defense":"Michigan",
        "driveNumber":2, "plays":8, "yards":75, "startOffenseScore":0, "endOffenseScore":7,
        "driveResult":"Touchdown",
    }])
    df = clean_drives(raw)
    assert df.loc[0, "drive_points"] == 0
    assert bool(df.loc[0, "is_three_and_out"])
    assert df.loc[1, "drive_points"] == 7
    assert bool(df.loc[1, "is_touchdown_drive"])
    assert validate_drives(df).ok
