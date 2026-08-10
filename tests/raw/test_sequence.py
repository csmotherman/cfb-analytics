from cfb_analytics.raw.sequence import _game_summary


def test_sequence_detects_source_order_conflicts():
    plays = [
        {"id": "2", "driveId": "d1", "driveNumber": 1, "playNumber": 2, "period": 1, "clock": {"minutes": 10, "seconds": 0}, "wallclock": "2025-09-01T12:00:02Z"},
        {"id": "1", "driveId": "d1", "driveNumber": 1, "playNumber": 1, "period": 1, "clock": {"minutes": 10, "seconds": 30}, "wallclock": "2025-09-01T12:00:01Z"},
    ]
    result = _game_summary(plays)
    assert result["source_play_number_regression_same_drive"] == 1
    assert result["source_clock_regression_same_period"] == 1
    assert result["source_wallclock_regression"] == 1
    assert result["source_play_id_regression"] == 1
