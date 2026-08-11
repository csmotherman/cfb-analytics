from cfb_analytics.analytics.tfl_kneel_audit import candidate,kneel_audit

def play(**kw):
 p={"isScrimmagePlay":True,"analyticsYardsGained":-2,"sourcePlayType":"Rush","period":4,"clock":{"minutes":1,"seconds":0}};p.update(kw);return p

def test_negative_rush_candidate():assert candidate(play())
def test_negative_completion_candidate():assert candidate(play(sourcePlayType="Pass Reception"))
def test_incompletion_not_candidate():assert not candidate(play(sourcePlayType="Pass Incompletion"))
def test_late_small_loss_rush_enters_risk_bucket():
 r=kneel_audit([play()]);assert r["counts"]["kneel_risk_window"]==1 and r["counts"]["kneel_risk_small_loss"]==1
