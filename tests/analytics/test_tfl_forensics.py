from cfb_analytics.analytics.tfl_forensics import tfl_forensics

def p(y,typ="Rush",**kw):
 x={"isScrimmagePlay":True,"analyticsYardsGained":y,"sourcePlayType":typ,"eventSubtype":"RUSH","hasNoPlayContext":False};x.update(kw);return x

def test_negative_rush_is_censused_not_asserted_as_tfl():
 r=tfl_forensics([p(-3)]);assert r["counts"]["negative_non_sack"]==1 and r["families"]["RUSH"]==1

def test_sack_excluded_from_candidate_pool():
 r=tfl_forensics([p(-8,"Sack",eventSubtype="SACK")]);assert r["counts"].get("negative_non_sack",0)==0

def test_positive_play_excluded():
 r=tfl_forensics([p(4)]);assert r["counts"].get("negative_non_sack",0)==0
