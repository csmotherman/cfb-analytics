from cfb_analytics.analytics.tfl import structural_candidate,high_confidence_kneel_ids,classify_tfl,team_tfl_metrics

def p(**kw):
    x={"gameId":"1","isScrimmagePlay":True,"analyticsYardsGained":-2,"sourcePlayType":"Rush","eventSubtype":"RUSH","period":1,"clock":{"minutes":10,"seconds":0},"offense":"A","defense":"B"};x.update(kw);return x

def test_negative_rush_is_structural_candidate():assert structural_candidate(p())
def test_negative_completion_is_structural_candidate():assert structural_candidate(p(sourcePlayType="Pass Reception"))
def test_sack_not_structural_candidate():assert not structural_candidate(p(sourcePlayType="Sack",eventSubtype="SACK"))
def test_high_confidence_kneel_excluded():
    a=p(period=4,clock={"minutes":1,"seconds":10},down=1)
    b=p(period=4,clock={"minutes":0,"seconds":40},down=2)
    c=p(period=4,clock={"minutes":0,"seconds":10},down=3)
    rows=[a,b,c];ids=high_confidence_kneel_ids(rows)
    assert id(a) in ids and not classify_tfl(a,ids)
def test_team_metrics_reconcile_one_tfl():
    mA=team_tfl_metrics("A",[p()]);mB=team_tfl_metrics("B",[p()])
    assert mA["tacklesForLossAllowed"]==1 and mB["tacklesForLoss"]==1
