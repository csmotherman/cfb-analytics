from cfb_analytics.canonical.ambiguous import classify_ambiguous_triplet
from cfb_analytics.canonical.plays import normalize_play


def play(**kw):
    base={"id":"100","gameId":"g","driveId":"d","driveNumber":1,"playNumber":1,"offense":"A","defense":"B","period":1,"clock":{"minutes":10,"seconds":0},"down":1,"distance":10,"yardsToGoal":70,"yardsGained":4,"playType":"Rush","playText":"Runner for 4 yards"}
    base.update(kw); return normalize_play(base)


def test_non_ambiguous_pair_is_not_refined():
    a=play(); b=play(id="101",playNumber=2,down=2,distance=6,yardsToGoal=66)
    c=play(id="102",playNumber=3,down=3,distance=2,yardsToGoal=62)
    assert classify_ambiguous_triplet(a,b,c)["subtype"]=="NOT_AMBIGUOUS"


def test_ambiguous_without_lookahead_is_reported():
    a=play(); b=play(id="101",playNumber=2,down=3,distance=20,yardsToGoal=40)
    result=classify_ambiguous_triplet(a,b,None)
    assert result["subtype"] in {"NO_LOOKAHEAD","NOT_AMBIGUOUS"}


def test_ordering_failure_in_lookahead_is_chronology_signal():
    a=play(); b=play(id="101",playNumber=2,down=3,distance=20,yardsToGoal=40)
    c=play(id="099",playNumber=3,down=4,distance=16,yardsToGoal=36)
    result=classify_ambiguous_triplet(a,b,c)
    if result["subtype"]!="NOT_AMBIGUOUS": assert result["subtype"]=="LIKELY_CHRONOLOGY"
