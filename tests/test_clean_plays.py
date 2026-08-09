import pandas as pd

from cfb_analytics.clean.plays import clean_plays
from cfb_analytics.validate.plays import validate_plays


def _raw(rows):
    base = {
        "gameId": "g1", "driveId": "d1", "driveNumber": 1, "season": 2025, "week": 1,
        "offense": "Michigan", "defense": "Ohio State", "period": 1,
        "yardsToGoal": 75, "yardline": 25, "ppa": 0.0, "scoring": False,
        "clock": {"minutes": 12, "seconds": 34}, "playText": "normal play",
    }
    return pd.DataFrame([{**base, **row} for row in rows])


def test_success_threshold_edges():
    df = clean_plays(_raw([
        {"id":"p1","playNumber":1,"down":1,"distance":10,"yardsGained":5,"playType":"Rush"},
        {"id":"p2","playNumber":2,"down":1,"distance":10,"yardsGained":4,"playType":"Rush"},
        {"id":"p3","playNumber":3,"down":2,"distance":10,"yardsGained":7,"playType":"Pass Completion"},
        {"id":"p4","playNumber":4,"down":2,"distance":10,"yardsGained":6,"playType":"Pass Completion"},
        {"id":"p5","playNumber":5,"down":3,"distance":2,"yardsGained":2,"playType":"Rush"},
        {"id":"p6","playNumber":6,"down":3,"distance":2,"yardsGained":1,"playType":"Rush"},
    ]))
    assert df["is_success"].tolist() == [True, False, True, False, True, False]


def test_explosive_threshold_edges():
    df = clean_plays(_raw([
        {"id":"p1","playNumber":1,"down":1,"distance":10,"yardsGained":12,"playType":"Rush"},
        {"id":"p2","playNumber":2,"down":1,"distance":10,"yardsGained":11,"playType":"Rush"},
        {"id":"p3","playNumber":3,"down":1,"distance":10,"yardsGained":16,"playType":"Pass Completion"},
        {"id":"p4","playNumber":4,"down":1,"distance":10,"yardsGained":15,"playType":"Pass Completion"},
    ]))
    assert df["is_explosive"].tolist() == [True, False, True, False]


def test_kneels_and_spikes_are_not_competitive():
    df = clean_plays(_raw([
        {"id":"p1","playNumber":1,"down":1,"distance":10,"yardsGained":-1,"playType":"Rush","playText":"Quarterback kneels for loss of 1"},
        {"id":"p2","playNumber":2,"down":1,"distance":10,"yardsGained":0,"playType":"Pass Incompletion","playText":"QB spikes the ball"},
    ]))
    assert df["is_offensive_play"].all()
    assert not df["is_competitive_offensive_play"].any()
    assert not df["is_success"].any()


def test_goal_to_go_inference_uses_line_to_gain_at_or_beyond_goal():
    df = clean_plays(_raw([
        {"id":"p1","playNumber":1,"down":1,"distance":8,"yardsToGoal":8,"yardsGained":2,"playType":"Rush"},
        {"id":"p2","playNumber":2,"down":1,"distance":5,"yardsToGoal":8,"yardsGained":2,"playType":"Rush"},
        {"id":"p3","playNumber":3,"down":1,"distance":15,"yardsToGoal":15,"yardsGained":2,"playType":"Rush"},
    ]))
    assert df["is_goal_to_go"].tolist() == [True, False, True]


def test_play_validation_passes_clean_fixture():
    df = clean_plays(_raw([{
        "id":"p1","playNumber":1,"down":1,"distance":10,"yardsGained":5,"playType":"Rush"
    }]))
    report = validate_plays(df)
    assert report.ok, report.errors
