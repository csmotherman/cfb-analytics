from cfb_analytics.analytics.tfl_residuals import residual_audit

def base(typ,y=-3,**kw):
 p={"isScrimmagePlay":True,"sourcePlayType":typ,"analyticsYardsGained":y,"yardsGained":y};p.update(kw);return p

def test_negative_incompletion_is_residual():
 r=residual_audit([base("Pass Incompletion")]);assert r["counts"]["residual"]==1

def test_negative_rush_not_residual():
 r=residual_audit([base("Rush")]);assert r["counts"].get("residual",0)==0

def test_negative_completion_not_residual():
 r=residual_audit([base("Pass Reception")]);assert r["counts"].get("residual",0)==0

def test_other_negative_type_is_residual():
 r=residual_audit([base("Fumble")]);assert r["counts"]["residual"]==1
