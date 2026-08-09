import pandas as pd

from cfb_analytics.validate.relations import validate_relations


def test_cross_table_relationships():
    games = pd.DataFrame({"game_id":["g1"]})
    drives = pd.DataFrame({"drive_id":["d1"], "game_id":["g1"]})
    plays = pd.DataFrame({"game_id":["g1"], "drive_id":["d1"]})
    report = validate_relations(games, drives, plays)
    assert report.ok
    assert not report.warnings
