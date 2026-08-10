from cfb_analytics.derived.games import derive_team_games

def drive(offense,defense,yards=50,status="PASS",possession=True):
 return {"gameId":"g1","offense":offense,"defense":defense,"analyticsYardsGained":yards,"offensivePlayCount":8,"driveValidationStatus":status,"isPossessionDrive":possession}
def play(offense="A",defense="B"): return {"gameId":"g1","offense":offense,"defense":defense}

def test_two_rows_per_game_and_mirrored_yards():
 rows=derive_team_games([play()],[drive("A","B",70),drive("B","A",40)],2025,"regular",1)
 assert len(rows)==2
 a=next(r for r in rows if r["team"]=="A"); b=next(r for r in rows if r["team"]=="B")
 assert a["opponent"]=="B" and a["offensiveYards"]==70 and a["defensiveYardsAllowed"]==40
 assert b["offensiveYards"]==40 and b["defensiveYardsAllowed"]==70

def test_review_possession_is_quarantined_from_metrics():
 rows=derive_team_games([play()],[drive("A","B",70),drive("A","B",999,"REVIEW"),drive("B","A",40)],2025,"regular",1)
 a=next(r for r in rows if r["team"]=="A")
 assert a["offensiveYards"]==70 and a["validatedPossessions"]==1

def test_non_possession_group_does_not_create_possession():
 rows=derive_team_games([play()],[drive("A","B",70),drive(None,None,999,possession=False),drive("B","A",40)],2025,"regular",1)
 a=next(r for r in rows if r["team"]=="A")
 assert a["validatedPossessions"]==1
