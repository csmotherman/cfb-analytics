from cfb_analytics.analytics.score_transition_forensics import team_score,touchdown_score_delta

def play(offense="A",defense="B",offenseScore=0,defenseScore=0,subtype="RUSH"):
 return {"offense":offense,"defense":defense,"offenseScore":offenseScore,"defenseScore":defenseScore,"eventSubtype":subtype}

def test_team_score_maps_across_possession_change():
 assert team_score(play("A","B",14,7),"A")==14
 assert team_score(play("B","A",7,14),"A")==14

def test_td_delta_uses_later_opponent_possession_score():
 rows=[play("A","B",14,7),play("A","B",20,7,"RUSH_TD"),play("B","A",7,21)]
 r=touchdown_score_delta(rows,1)
 assert r["status"]=="RESOLVED" and r["delta"]==7

def test_two_point_delta():
 rows=[play("A","B",14,7),play("A","B",20,7,"PASS_TD"),play("B","A",7,22)]
 assert touchdown_score_delta(rows,1)["delta"]==8

def test_missing_after_is_unresolved():
 rows=[play("A","B",14,7),play("A","B",20,7,"RUSH_TD")]
 assert touchdown_score_delta(rows,1)["status"]=="NO_AFTER_SCORE"
