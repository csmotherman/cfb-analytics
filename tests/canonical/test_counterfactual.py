from cfb_analytics.canonical.counterfactual import _candidate_repairs, _expected_field
from cfb_analytics.canonical.plays import normalize_play


def play(**kw):
    base={"id":"100","gameId":"g","driveId":"d","driveNumber":1,"playNumber":1,"offense":"A","defense":"B","period":1,"clock":{"minutes":10,"seconds":0},"down":1,"distance":10,"yardsToGoal":70,"yardsGained":4,"playType":"Rush","playText":"Runner for 4 yards"}
    base.update(kw); return normalize_play(base)


def test_expected_field_uses_previous_gain():
    assert _expected_field(play())==66


def test_candidates_include_forward_field_repair():
    a=play(); b=play(id="101",playNumber=2,down=2,distance=6,yardsToGoal=40); c=play(id="102",playNumber=3,down=3,distance=2,yardsToGoal=36)
    candidates=_candidate_repairs(a,b,c)
    assert ("yardsToGoal",66,"A state + A analyticsYardsGained") in candidates


def test_candidates_include_text_yardage_repair():
    a=play(); b=play(id="101",playNumber=2,yardsGained=9,playText="Runner gains 4 yards"); c=play(id="102",playNumber=3)
    candidates=_candidate_repairs(a,b,c)
    assert any(field=="analyticsYardsGained" and value==4 for field,value,_ in candidates)
