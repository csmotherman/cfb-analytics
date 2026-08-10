from cfb_analytics.raw.transitions import _audit_pair


def play(**kw):
    base = {"driveId": "d1", "offense": "A", "defense": "B", "down": 1, "distance": 10, "yardsToGoal": 70, "yardsGained": 4, "scoring": False, "playType": "Rush", "playText": "Runner gains 4 yards", "offenseScore": 0, "defenseScore": 0}
    base.update(kw)
    return base


def test_clean_scrimmage_transition():
    a = play()
    b = play(down=2, distance=6, yardsToGoal=66, yardsGained=3)
    assert _audit_pair(a, b) == []


def test_detects_subtle_transition_mismatch():
    a = play()
    b = play(down=3, distance=7, yardsToGoal=65)
    flags = set(_audit_pair(a, b))
    assert "expected_next_down_mismatch" in flags
    assert "distance_transition_mismatch" in flags
    assert "field_position_transition_mismatch" in flags


def test_penalty_is_not_naively_reconstructed():
    a = play(playType="Penalty", playText="Penalty on A, holding")
    b = play(down=1, distance=20, yardsToGoal=80)
    assert _audit_pair(a, b) == []
