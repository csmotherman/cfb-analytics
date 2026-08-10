from cfb_analytics.raw.transitions import _audit_pair, _penalty_context, _penalty_signal, _football_context


def play(**kw):
    base = {"driveId": "d1", "offense": "A", "defense": "B", "down": 1, "distance": 10, "yardsToGoal": 70, "yardsGained": 4, "scoring": False, "playType": "Rush", "playText": "Runner gains 4 yards", "offenseScore": 0, "defenseScore": 0, "period": 1}
    base.update(kw)
    return base


def test_clean_scrimmage_transition():
    a = play()
    b = play(down=2, distance=6, yardsToGoal=66, yardsGained=3)
    assert _audit_pair(a, b) == []


def test_detects_wrong_next_down_without_cascading_distance_flag():
    a = play()
    b = play(down=3, distance=7, yardsToGoal=66)
    flags = set(_audit_pair(a, b))
    assert "expected_next_down_mismatch" in flags
    assert "distance_transition_mismatch" not in flags


def test_detects_distance_and_field_position_mismatch_when_down_reconciles():
    a = play()
    b = play(down=2, distance=8, yardsToGoal=63)
    flags = set(_audit_pair(a, b))
    assert "distance_transition_mismatch" in flags
    assert "field_position_transition_mismatch" in flags


def test_penalty_is_not_naively_reconstructed():
    a = play(playType="Penalty", playText="Penalty on A, holding")
    b = play(down=1, distance=20, yardsToGoal=80)
    assert _audit_pair(a, b) == []


def test_penalty_signal_distinguishes_type_and_text():
    assert _penalty_signal(play(playType="Penalty", playText="Holding")) == "playtype_only"
    assert _penalty_signal(play(playType="Rush", playText="Runner gains 8, PENALTY holding")) == "text_only"
    assert _penalty_signal(play(playType="Penalty", playText="Penalty on A")) == "playtype_and_text"
    assert _penalty_signal(play()) is None


def test_penalty_context_checks_both_sides_of_flagged_pair():
    a = play()
    b = play(playType="Penalty", playText="Penalty on B, offside")
    context = _penalty_context(a, b)
    assert context["location"] == "next"
    assert context["previous_signal"] is None
    assert context["next_signal"] == "playtype_and_text"


def test_football_context_tags_special_situations():
    a = play(playType="Pass Incompletion", playText="Pass incomplete")
    b = play(driveId="d2", offense="B", defense="A", playType="Kickoff", playText="Kickoff after touchdown", scoring=True, period=2)
    tags = _football_context(a, b)
    assert {"incomplete_pass", "special_teams", "scoring", "possession_change", "drive_change", "period_change"}.issubset(tags)
    assert "ordinary_unexplained" not in tags


def test_football_context_marks_ordinary_pair():
    assert _football_context(play(), play(down=2, distance=6, yardsToGoal=66)) == {"ordinary_unexplained"}
