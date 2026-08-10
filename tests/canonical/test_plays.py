import pytest

from cfb_analytics.canonical.play_types import classify_play_type
from cfb_analytics.canonical.plays import normalize_play


def test_timeout_zeroes_analytics_yards_but_preserves_source():
    source={"id":1,"playType":"Timeout","yardsGained":37}
    out=normalize_play(source)
    assert out["sourceYardsGained"]==37
    assert out["analyticsYardsGained"]==0
    assert out["yardsGainedWasNormalized"] is True
    assert out["isAdministrative"] is True
    assert source["yardsGained"]==37


def test_end_period_zeroes_analytics_yards():
    out=normalize_play({"playType":"End Period","yardsGained":12})
    assert out["analyticsYardsGained"]==0
    assert out["eventSubtype"]=="END_PERIOD"


def test_rush_preserves_yards():
    out=normalize_play({"playType":"Rush","yardsGained":8})
    assert out["analyticsYardsGained"]==8
    assert out["isScrimmagePlay"] is True
    assert out["isOffensivePlay"] is True


def test_kickoff_is_not_blanket_zeroed():
    out=normalize_play({"playType":"Kickoff","yardsGained":65})
    assert out["analyticsYardsGained"]==65
    assert out["isSpecialTeams"] is True


def test_unclassified_play_type_fails_closed():
    with pytest.raises(KeyError):
        classify_play_type("Made Up Play Type")
