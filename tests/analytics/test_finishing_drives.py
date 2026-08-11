from cfb_analytics.analytics.finishing_drives import scoring_opportunity, possession_outcome

def drive(**kw):
 d={"gameId":"g1","driveId":"d1","isPossessionDrive":True,"driveValidationStatus":"PASS","offense":"A"};d.update(kw);return d

def play(**kw):
 p={"id":"p1","gameId":"g1","driveId":"d1","offense":"A","defense":"B","yardsToGoal":50,"eventSubtype":"RUSH","offenseScore":10,"defenseScore":3,"period":1,"clock":{"minutes":10,"seconds":0}};p.update(kw);return p

def test_opportunity_when_drive_reaches_40():
 assert scoring_opportunity(drive(),[play(yardsToGoal=40)]) is True
 assert scoring_opportunity(drive(),[play(yardsToGoal=41)]) is False

def test_wrong_team_field_position_does_not_create_opportunity():
 assert scoring_opportunity(drive(),[play(offense="B",yardsToGoal=20)]) is False

def test_touchdown_uses_adjudicated_score_delta():
 before=play(id="p0",driveId="d0",offenseScore=10,clock={"minutes":11,"seconds":0})
 td=play(id="p1",eventSubtype="RUSH_TD",yardsToGoal=0,offenseScore=17)
 r=possession_outcome(drive(),[td],[before,td])
 assert r["outcome"]=="TOUCHDOWN" and r["points"]==7 and r["pointsResolved"] is True

def test_passing_touchdown_can_resolve_six():
 before=play(id="p0",driveId="d0",offenseScore=10,clock={"minutes":11,"seconds":0})
 td=play(id="p1",eventSubtype="PASS_TD",yardsToGoal=0,offenseScore=16)
 assert possession_outcome(drive(),[td],[before,td])["points"]==6

def test_field_goal_outcome():
 fg=play(eventSubtype="FIELD_GOAL_GOOD")
 r=possession_outcome(drive(),[fg],[fg])
 assert r["outcome"]=="FIELD_GOAL" and r["points"]==3 and r["pointsResolved"] is True

def test_empty_outcome():
 p=play();r=possession_outcome(drive(),[p],[p])
 assert r["outcome"]=="EMPTY" and r["points"]==0 and r["pointsResolved"] is True

def test_review_drive_not_opportunity():
 assert scoring_opportunity(drive(driveValidationStatus="REVIEW"),[play(yardsToGoal=10)]) is False
