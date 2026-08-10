from cfb_analytics.derived.seasons import derive_team_seasons

def game(week,yards,allowed,plays=10,dplays=10,poss=2,dposs=2):
 return {"season":2025,"seasonType":"regular","week":week,"gameId":f"g{week}","team":"A","opponent":"B","validatedPossessions":poss,"validatedDefensivePossessions":dposs,"offensivePlays":plays,"defensivePlays":dplays,"offensiveYards":yards,"defensiveYardsAllowed":allowed,"reviewPossessionGroups":0,"gameValidationStatus":"PASS"}

def test_aggregates_team_games_into_one_season_row():
 r=derive_team_seasons([game(1,100,80),game(2,200,120)],2025)[0]
 assert r["games"]==2 and r["offensiveYards"]==300 and r["defensiveYardsAllowed"]==200
 assert r["yardsPerGame"]==150 and r["yardsAllowedPerGame"]==100

def test_rates_are_recomputed_from_totals_not_averaged():
 r=derive_team_seasons([game(1,100,80,plays=10),game(2,200,120,plays=20)],2025)[0]
 assert r["yardsPerPlay"]==10

def test_possession_rates_reconcile_from_totals():
 r=derive_team_seasons([game(1,100,80,poss=2,dposs=4),game(2,200,120,poss=3,dposs=1)],2025)[0]
 assert r["validatedPossessions"]==5 and r["yardsPerPossession"]==60
 assert r["validatedDefensivePossessions"]==5 and r["yardsAllowedPerPossession"]==40
