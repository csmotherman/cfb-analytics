from cfb_analytics.analytics.finishing_drives import scoring_opportunity, possession_outcome

def drive(**kw):
 d={"isPossessionDrive":True,"driveValidationStatus":"PASS","offense":"A"};d.update(kw);return d

def play(**kw):
 p={"offense":"A","yardsToGoal":50,"eventSubtype":"RUSH"};p.update(kw);return p

def test_opportunity_when_drive_reaches_40():
 assert scoring_opportunity(drive(),[play(yardsToGoal=40)]) is True
 assert scoring_opportunity(drive(),[play(yardsToGoal=41)]) is False

def test_wrong_team_field_position_does_not_create_opportunity():
 assert scoring_opportunity(drive(),[play(offense="B",yardsToGoal=20)]) is False

def test_touchdown_outcome():
 r=possession_outcome(drive(),[play(eventSubtype="RUSH_TD")])
 assert r["outcome"]=="TOUCHDOWN" and r["possessionPointsExcludingTry"]==6

def test_passing_touchdown_outcome():
 assert possession_outcome(drive(),[play(eventSubtype="PASS_TD")])["outcome"]=="TOUCHDOWN"

def test_field_goal_outcome():
 r=possession_outcome(drive(),[play(eventSubtype="FIELD_GOAL_GOOD")])
 assert r["outcome"]=="FIELD_GOAL" and r["possessionPointsExcludingTry"]==3

def test_empty_outcome():
 assert possession_outcome(drive(),[play()])["outcome"]=="EMPTY"

def test_review_drive_not_opportunity():
 assert scoring_opportunity(drive(driveValidationStatus="REVIEW"),[play(yardsToGoal=10)]) is False
