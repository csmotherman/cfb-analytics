from cfb_analytics.analytics.touchdown_points import adjudicate_touchdown_points

def p(offense="A",defense="B",offenseScore=None,defenseScore=None,eventSubtype="RUSH"):
 return {"offense":offense,"defense":defense,"offenseScore":offenseScore,"defenseScore":defenseScore,"eventSubtype":eventSubtype}

def test_td_record_plus_7_is_primary():
 rows=[p(offenseScore=10,defenseScore=3),p(offenseScore=17,defenseScore=3,eventSubtype="RUSH_TD"),p(offense="B",defense="A",offenseScore=3,defenseScore=17)]
 r=adjudicate_touchdown_points(rows,1);assert r["points"]==7 and r["source"]=="TD_RECORD_SCORE"

def test_td_record_plus_6_is_valid():
 rows=[p(offenseScore=10),p(offenseScore=16,eventSubtype="PASS_TD")]
 assert adjudicate_touchdown_points(rows,1)["points"]==6

def test_td_record_plus_8_is_valid():
 rows=[p(offenseScore=10),p(offenseScore=18,eventSubtype="PASS_TD")]
 assert adjudicate_touchdown_points(rows,1)["points"]==8

def test_abnormal_td_record_can_use_immediate_standard_fallback():
 rows=[p(offenseScore=10),p(offenseScore=10,eventSubtype="RUSH_TD"),p(offense="B",defense="A",offenseScore=7,defenseScore=17)]
 r=adjudicate_touchdown_points(rows,1);assert r["points"]==7 and r["source"]=="NEXT_RECORD_SCORE"

def test_abnormal_states_are_not_coerced():
 rows=[p(offenseScore=10),p(offenseScore=24,eventSubtype="RUSH_TD"),p(offense="B",defense="A",offenseScore=7,defenseScore=24)]
 assert adjudicate_touchdown_points(rows,1)["status"]=="UNRESOLVED"
