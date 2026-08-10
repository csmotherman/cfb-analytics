from cfb_analytics.raw.anomalies import _flag_play, _flag_drive


def test_play_anomaly_rules():
    flags = _flag_play({"offenseScore": -1, "defenseScore": 7, "down": 5, "distance": -2, "yardsToGoal": 103, "yardsGained": 561})
    assert set(flags) == {"negative-score", "down-outside-0-4", "negative-distance", "yards-to-goal-outside-0-100", "extreme-play-yards"}


def test_drive_anomaly_rules():
    flags = _flag_drive({"startYardsToGoal": 80, "endYardsToGoal": -5, "yards": -4957, "startPeriod": 0, "endPeriod": 0})
    assert set(flags) == {"drive-yards-to-goal-outside-0-100", "extreme-drive-yards", "drive-period-outside-game-period"}
