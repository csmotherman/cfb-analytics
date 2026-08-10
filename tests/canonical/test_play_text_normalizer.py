from cfb_analytics.canonical.play_text_normalizer import normalize_play_text


def test_normalizes_simple_rush():
    out=normalize_play_text({"playText":"Jordan Howard run for 4 yds to the UAB 44 for a 1ST down"})
    assert out["textPlayType"]=="RUSH"
    assert out["textYardsGained"]==4
    assert out["textDestinationTeam"]=="UAB"
    assert out["textDestinationYardLine"]==44
    assert out["textFirstDown"] is True
    assert out["textParseConfidence"]=="HIGH"
    assert "RUSH" in out["normalizedPlayText"]


def test_normalizes_completed_pass():
    out=normalize_play_text({"playText":"QB pass complete to WR for 12 yds to the MICH 38"})
    assert out["textPlayType"]=="PASS_COMPLETE"
    assert out["textYardsGained"]==12
    assert out["textDestinationTeam"]=="MICH"
    assert out["textDestinationYardLine"]==38


def test_penalty_declined_is_preserved_as_modifier():
    out=normalize_play_text({"playText":"Runner run for 6 yds to the OSU 40, PENALTY MICH holding declined"})
    assert out["textPenalty"] is True
    assert out["textPenaltyStatus"]=="DECLINED"
    assert out["textPenaltyType"]=="HOLDING"


def test_no_play_penalty_status():
    out=normalize_play_text({"playText":"QB run for 3 yds, PENALTY offense false start, no play"})
    assert out["textPenaltyStatus"]=="NO_PLAY"
    assert out["textNoPlay"] is True


def test_multiple_yardage_phrases_are_ambiguous():
    out=normalize_play_text({"playText":"Runner run for 8 yds to the MICH 35, PENALTY holding 10 yards"})
    assert out["textAmbiguous"] is True
    assert "MULTIPLE_YARDAGE_PHRASES" in out["textAmbiguityReasons"]
    assert out["textYardsGained"] is None


def test_multiple_destinations_are_ambiguous():
    out=normalize_play_text({"playText":"Pass complete for 5 yds to the MICH 40, returned to the OSU 20"})
    assert out["textAmbiguous"] is True
    assert "MULTIPLE_DESTINATIONS" in out["textAmbiguityReasons"]
