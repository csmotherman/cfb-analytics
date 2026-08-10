from cfb_analytics.canonical.forensics import _field_error, _distance_error, _ordering_signals
from cfb_analytics.canonical.plays import normalize_play


def play(**kw):
    base={"id":"100","driveId":"d1","driveNumber":1,"playNumber":1,"offense":"A","defense":"B","period":1,"clock":{"minutes":10,"seconds":0},"down":1,"distance":10,"yardsToGoal":70,"yardsGained":4,"playType":"Rush"}
    base.update(kw); return normalize_play(base)


def test_forensic_error_math():
    a=play(); b=play(id="101",playNumber=2,down=2,distance=8,yardsToGoal=40)
    assert _field_error(a,b)==-26
    assert _distance_error(a,b)==2


def test_ordering_signals_detect_clock_increase():
    a=play(); b=play(id="101",playNumber=2,clock={"minutes":11,"seconds":0})
    assert _ordering_signals(a,b)["clock_non_increasing_same_period"] is False


def test_ordering_signals_accept_candidate_sequence():
    a=play(); b=play(id="101",playNumber=2,clock={"minutes":9,"seconds":30})
    s=_ordering_signals(a,b)
    assert s["candidate_play_number_non_decreasing"] is True
    assert s["period_non_decreasing"] is True
    assert s["clock_non_increasing_same_period"] is True
    assert s["play_id_numeric_non_decreasing"] is True
