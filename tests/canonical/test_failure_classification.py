from cfb_analytics.canonical.failure_classification import classify_failure
from cfb_analytics.canonical.plays import normalize_play


def play(**kw):
    base={"id":"100","driveId":"d1","driveNumber":1,"playNumber":1,"offense":"A","defense":"B","period":1,"clock":{"minutes":10,"seconds":0},"down":1,"distance":10,"yardsToGoal":70,"yardsGained":4,"playType":"Rush","playText":"Runner gains 4 yards"}
    base.update(kw); return normalize_play(base)


def test_classifies_chronology_suspect_on_clock_regression():
    a=play(); b=play(id="101",playNumber=2,clock={"minutes":11,"seconds":0},down=2,distance=6,yardsToGoal=66)
    result=classify_failure(a,b,["field_position_transition_mismatch"])
    assert result["classification"]=="CHRONOLOGY_SUSPECT"


def test_classifies_structured_yards_suspect_when_text_disagrees():
    a=play(yardsGained=9,playText="Runner gains 4 yards"); b=play(id="101",playNumber=2,down=2,distance=6,yardsToGoal=66)
    result=classify_failure(a,b,["field_position_transition_mismatch"])
    assert result["classification"]=="YARDS_GAINED_SUSPECT"


def test_classifies_field_position_suspect_when_down_distance_reconcile():
    a=play(); b=play(id="101",playNumber=2,down=2,distance=6,yardsToGoal=40)
    result=classify_failure(a,b,["field_position_transition_mismatch"])
    assert result["classification"]=="FIELD_POSITION_SUSPECT"


def test_classifies_down_distance_suspect_when_field_reconciles():
    a=play(); b=play(id="101",playNumber=2,down=2,distance=9,yardsToGoal=66)
    result=classify_failure(a,b,["distance_transition_mismatch"])
    assert result["classification"]=="DOWN_DISTANCE_SUSPECT"
