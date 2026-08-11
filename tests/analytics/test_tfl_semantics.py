from cfb_analytics.analytics.tfl_semantics import semantic_bucket

def p(text,typ="Rush"):return {"playText":text,"sourcePlayType":typ}
def test_kneel():assert semantic_bucket(p("Smith kneels for loss of 1"))=="KNEEL"
def test_scramble():assert semantic_bucket(p("Smith scrambles for -3 yards"))=="SCRAMBLE"
def test_bad_snap():assert semantic_bucket(p("Bad snap, Smith rush for -12 yards"))=="BAD_SNAP_ABORTED"
def test_negative_completion():assert semantic_bucket(p("Smith pass complete to Jones for -2 yards","Pass Reception"))=="NEGATIVE_COMPLETION"
def test_negative_incompletion():assert semantic_bucket(p("Smith pass incomplete for -3 yards","Pass Incompletion"))=="NEGATIVE_INCOMPLETION"
def test_ordinary_rush():assert semantic_bucket(p("Smith rush for -2 yards"))=="ORDINARY_NEGATIVE_RUSH"
