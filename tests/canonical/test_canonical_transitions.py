from cfb_analytics.canonical.transitions import _audit_pair, _special_context
from cfb_analytics.canonical.plays import normalize_play


def play(play_type="Rush",**kw):
    base={"id":"1","driveId":"d1","offense":"A","defense":"B","down":1,"distance":10,"yardsToGoal":70,"yardsGained":4,"period":1,"playType":play_type,"playText":"play"}
    base.update(kw); return normalize_play(base)


def test_clean_canonical_scrimmage_transition():
    assert _audit_pair(play(),play(id="2",down=2,distance=6,yardsToGoal=66))==[]


def test_canonical_transition_detects_field_and_distance_mismatch():
    flags=set(_audit_pair(play(),play(id="2",down=2,distance=8,yardsToGoal=63)))
    assert "distance_transition_mismatch" in flags
    assert "field_position_transition_mismatch" in flags


def test_administrative_record_is_not_scrimmage_transition():
    timeout=play("Timeout",yardsGained=99)
    rush=play(id="2",down=2,distance=6,yardsToGoal=66)
    assert timeout["analyticsYardsGained"]==0
    assert _audit_pair(timeout,rush)==[]


def test_penalty_record_is_not_scrimmage_transition():
    assert _audit_pair(play("Penalty"),play(id="2",down=2,distance=6,yardsToGoal=66))==[]


def test_special_context_uses_taxonomy_and_possession():
    a=play(); b=play("Kickoff",id="2",driveId="d2",offense="B",defense="A",period=2)
    tags=_special_context(a,b)
    assert {"special_teams","drive_change","period_change","possession_change"}.issubset(tags)
