from cfb_analytics.canonical.play_text_census import text_signature


def test_rush_run_wording_is_recognized():
    p={"playType":"Rush","playText":"Jordan Howard run for 4 yds to the UAB 44"}
    sig=text_signature(p)
    assert sig["family"]=="RUSH"
    assert "RUN" in sig["rush_cues"]
    assert "GAIN_YARDS" in sig["result_cues"]


def test_rush_scramble_wording_is_recognized():
    p={"playType":"Rush","playText":"Quarterback scrambles for 12 yards for a first down"}
    sig=text_signature(p)
    assert "SCRAMBLE" in sig["rush_cues"]
    assert "GAIN_YARDS" in sig["result_cues"]


def test_pass_completion_wording_is_recognized():
    p={"playType":"Pass Reception","playText":"Cody Clements pass complete to Kennard Backman for 8 yds"}
    sig=text_signature(p)
    assert sig["family"]=="PASS"
    assert "PASS_COMPLETE" in sig["pass_cues"]
    assert "GAIN_YARDS" in sig["result_cues"]


def test_pass_incomplete_wording_is_recognized():
    p={"playType":"Pass Incompletion","playText":"Troy Williams pass incomplete"}
    sig=text_signature(p)
    assert "PASS_INCOMPLETE" in sig["pass_cues"]


def test_sack_and_interception_are_pass_family():
    assert text_signature({"playType":"Sack","playText":"QB sacked for a loss of 7 yards"})["family"]=="PASS"
    sig=text_signature({"playType":"Interception","playText":"Pass intercepted by Smith"})
    assert sig["family"]=="PASS"
    assert "INTERCEPTION" in sig["pass_cues"]


def test_unknown_wording_remains_visible():
    sig=text_signature({"playType":"Rush","playText":"Unusual provider wording"})
    assert sig["signature"]=="NO_RECOGNIZED_CUE"
