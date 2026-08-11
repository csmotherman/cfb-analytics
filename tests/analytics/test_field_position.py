from cfb_analytics.analytics.field_position import valid_start_yards_to_goal,team_field_position_metrics

def d(off="A",deff="B",y=75,status="PASS",pos=True):return {"offense":off,"defense":deff,"startYardsToGoal":y,"driveValidationStatus":status,"isPossessionDrive":pos}
def test_valid_start():assert valid_start_yards_to_goal(d(y=75))==75.0
def test_invalid_start_excluded():
 assert valid_start_yards_to_goal(d(y=101)) is None
 assert valid_start_yards_to_goal(d(y=None)) is None
 assert valid_start_yards_to_goal(d(y=50,status="REVIEW")) is None
def test_team_metrics_offense_and_defense():
 m=team_field_position_metrics("A",[d(y=75),d(off="B",deff="A",y=60)])
 assert m["fieldPositionPossessions"]==1 and m["averageStartYardsToGoal"]==75
 assert m["averageStartOwnYardLine"]==25
 assert m["fieldPositionPossessionsAllowed"]==1 and m["averageStartOwnYardLineAllowed"]==40
