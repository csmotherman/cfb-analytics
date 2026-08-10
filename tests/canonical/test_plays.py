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


def test_scrimmage_penalty_keeps_base_type_and_adds_modifier():
    out=normalize_play({"playType":"Rush","yardsGained":6,"playText":"Runner gains 6 yards. MICHIGAN Penalty, Offensive Holding (10 Yards)."})
    assert out["eventCategory"]=="SCRIMMAGE"
    assert out["isScrimmagePlay"] is True
    assert out["hasPenaltyContext"] is True
    assert out["hasStateTransitionModifier"] is True


def test_context_modifiers_are_independent():
    out=normalize_play({"playType":"Pass Reception","playText":"Pass complete, fumbled; play reviewed. Penalty declined."})
    assert out["hasPenaltyContext"] is True
    assert out["hasReviewContext"] is True
    assert out["hasFumbleContext"] is True
    assert out["hasInterceptionContext"] is False


def test_no_play_context_detected():
    out=normalize_play({"playType":"Rush","playText":"False start, no play"})
    assert out["hasNoPlayContext"] is True
    assert out["hasStateTransitionModifier"] is True


def test_play_text_evidence_is_materialized_without_overwriting_structured_yards():
    source={
        "playType":"Rush",
        "yardsGained":9,
        "playText":"Runner run for 4 yds to the MICH 36",
    }
    out=normalize_play(source)
    assert out["sourceYardsGained"]==9
    assert out["analyticsYardsGained"]==9
    assert out["textYardsGained"]==4
    assert out["textDestinationTeam"]=="MICH"
    assert out["textDestinationYardLine"]==36
    assert out["textParseVersion"]=="v1"
    assert out["textParseConfidence"]=="HIGH"
    assert source["yardsGained"]==9


def test_ambiguous_text_evidence_is_persisted_but_not_promoted():
    out=normalize_play({
        "playType":"Rush",
        "yardsGained":8,
        "playText":"Runner run for 8 yds to the MICH 35, PENALTY holding 10 yards",
    })
    assert out["analyticsYardsGained"]==8
    assert out["textAmbiguous"] is True
    assert "MULTIPLE_YARDAGE_PHRASES" in out["textAmbiguityReasons"]
    assert out["textYardsGained"] is None


def test_unclassified_play_type_fails_closed():
    with pytest.raises(KeyError):
        classify_play_type("Made Up Play Type")
