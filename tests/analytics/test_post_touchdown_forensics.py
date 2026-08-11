from cfb_analytics.analytics.post_touchdown_forensics import _conversion_signal

def test_pat_good_text():
 assert _conversion_signal({"playText":"Touchdown, Smith kick is good"})=="PAT_GOOD_TEXT"

def test_pat_failed_text():
 assert _conversion_signal({"playText":"Jones PAT no good"})=="PAT_FAILED_TEXT"

def test_two_point_taxonomy():
 assert _conversion_signal({"eventSubtype":"TWO_POINT_PASS","playText":""})=="TWO_POINT_ATTEMPT"

def test_defensive_two_point_taxonomy():
 assert _conversion_signal({"eventSubtype":"DEFENSIVE_TWO_POINT","playText":""})=="DEFENSIVE_TWO_POINT"

def test_unrelated_play_has_no_signal():
 assert _conversion_signal({"eventSubtype":"KICKOFF","playText":"Smith kicks 65 yards"}) is None
