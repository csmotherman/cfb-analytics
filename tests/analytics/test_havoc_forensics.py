from cfb_analytics.analytics.havoc_forensics import _tfl_text,_forced_fumble_text

def test_explicit_tackle_for_loss():assert _tfl_text({"playText":"Smith tackled for a loss of 3 yards"})
def test_loss_phrase():assert _tfl_text({"playText":"Jones rush for loss of 2 yards"})
def test_plain_negative_not_automatically_tfl():assert not _tfl_text({"playText":"Jones rush for -2 yards"})
def test_forced_fumble_phrase():assert _forced_fumble_text({"playText":"Smith forced fumble recovered by Michigan"})
def test_fumble_without_force_is_not_forced():assert not _forced_fumble_text({"playText":"Smith fumbles, recovered by Michigan"})
