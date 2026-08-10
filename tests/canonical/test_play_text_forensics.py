from cfb_analytics.canonical.play_text_forensics import _penalty_profile, _yardage_profile, _destination_profile, _semantic_text_label


def test_penalty_statuses_and_complexity():
    p=_penalty_profile("Runner for 8 yds. PENALTY MICH Holding accepted; PENALTY OSU declined")
    assert p["has_penalty"] is True
    assert set(p["statuses"])=={"ACCEPTED","DECLINED"}
    assert p["penalty_count"]==2


def test_multiple_yardage_phrases_are_exposed():
    p=_yardage_profile("Runner for 8 yds, penalty for 10 yards")
    assert p["count"]==2
    assert p["values"]==[8,10]


def test_destination_extraction():
    d=_destination_profile("Runner for 8 yds to the MICH 42")
    assert d[0]["team"]=="MICH"
    assert d[0]["yard"]==42


def test_semantic_labels():
    assert _semantic_text_label("QB pass complete to WR for 9 yds") == "PASS_COMPLETE"
    assert _semantic_text_label("QB pass incomplete") == "PASS_INCOMPLETE"
    assert _semantic_text_label("QB sacked for a loss of 7 yards") == "SACK"
    assert _semantic_text_label("RB run for 5 yards") == "RUSH"
