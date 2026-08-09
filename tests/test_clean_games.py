import pandas as pd

from cfb_analytics.clean.games import clean_games
from cfb_analytics.validate.games import validate_games


def test_game_normalization_and_fbs_flag():
    raw = pd.DataFrame([{
        "id":"g1", "season":2025, "week":1, "seasonType":"regular",
        "homeTeam":"Michigan", "awayTeam":"Ohio State",
        "homeConference":"Big Ten", "awayConference":"Big Ten",
        "homeClassification":"fbs", "awayClassification":"fbs",
        "homePoints":24, "awayPoints":21, "completed":True,
    }])
    df = clean_games(raw)
    assert df.loc[0, "game_id"] == "g1"
    assert bool(df.loc[0, "is_fbs_vs_fbs"])
    assert validate_games(df).ok
