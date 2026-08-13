import pytest

from cfb_analytics.analytics.opponent_adjustment import SPECS,_rate_residual,build_adjusted_model_dataset,build_adjusted_snapshots
from cfb_analytics.derived.pregame import build_pregame_snapshots


def tg(team,opp,week,gid,s,sa):
 return {"season":2025,"seasonType":"regular","week":week,"gameId":gid,"team":team,"opponent":opp,"validatedPossessions":2,"validatedDefensivePossessions":2,"offensivePlays":10,"defensivePlays":10,"offensiveYards":50,"defensiveYardsAllowed":50,"reviewPossessionGroups":0,"gameValidationStatus":"PASS","successEligiblePlays":10,"successfulPlays":s,"successEligiblePlaysAllowed":10,"successfulPlaysAllowed":sa}


def test_success_adjustment_sign_convention():
 spec=next(x for x in SPECS if x[0]=="success")
 good=_rate_residual([{"gameId":"g","opponent":"B","successfulPlays":6,"successEligiblePlays":10,"successfulPlaysAllowed":3,"successEligiblePlaysAllowed":10}],{("g","B"):{"successRateAllowed":.4,"successRate":.5}},spec)
 bad=_rate_residual([{"gameId":"g","opponent":"B","successfulPlays":3,"successEligiblePlays":10,"successfulPlaysAllowed":7,"successEligiblePlaysAllowed":10}],{("g","B"):{"successRateAllowed":.5,"successRate":.5}},spec)
 assert good["adjustedSuccessOffense"]==pytest.approx(.2)
 assert good["adjustedSuccessDefense"]==pytest.approx(.2)
 assert bad["adjustedSuccessOffense"]==pytest.approx(-.2)
 assert bad["adjustedSuccessDefense"]==pytest.approx(-.2)


def test_same_week_games_share_identical_prior_adjustment_cutoff():
 rows=[tg("B","F",0,"g0",5,5),tg("F","B",0,"g0",5,5),tg("A","B",1,"g1",6,4),tg("B","A",1,"g1",4,6),tg("A","C",2,"g2",8,2),tg("C","A",2,"g2",2,8),tg("A","D",2,"g3",1,9),tg("D","A",2,"g3",9,1)]
 snaps=build_pregame_snapshots(rows,2025);adj=build_adjusted_snapshots(rows,snaps,2025);a=[r for r in adj if r["team"]=="A" and r["week"]==2]
 assert len(a)==2
 assert all(r["adjustedSuccessGames"]==1 for r in a)
 assert a[0]["adjustedSuccessOffense"]==pytest.approx(a[1]["adjustedSuccessOffense"])
 assert a[0]["adjustedSuccessDefense"]==pytest.approx(a[1]["adjustedSuccessDefense"])


def test_historical_opponent_strength_is_frozen_at_historical_game():
 rows=[tg("B","C",1,"g0",5,5),tg("C","B",1,"g0",5,5),tg("A","B",2,"g1",6,4),tg("B","A",2,"g1",4,6),tg("B","D",3,"g2",0,10),tg("D","B",3,"g2",10,0),tg("A","E",4,"g3",5,5),tg("E","A",4,"g3",5,5)]
 snaps=build_pregame_snapshots(rows,2025)
 b_g1=next(s for s in snaps if s["gameId"]=="g1" and s["team"]=="B");b_g2=next(s for s in snaps if s["gameId"]=="g2" and s["team"]=="B")
 assert b_g1["successRateAllowed"]==pytest.approx(.5)
 assert b_g2["successRateAllowed"]==pytest.approx(.55)
 adj=build_adjusted_snapshots(rows,snaps,2025);a4=next(r for r in adj if r["team"]=="A" and r["week"]==4)
 assert a4["adjustedSuccessOffense"]==pytest.approx(.1)


def test_adjusted_matchup_edge_is_offense_plus_opposing_defense():
 base=[{"season":2025,"gameId":"g1","homeTeam":"A","awayTeam":"B","target_margin":7.0,"target_homeWin":1}]
 adj=[{"season":2025,"gameId":"g1","team":"A","adjustedSuccessOffense":.08,"adjustedSuccessDefense":.03},{"season":2025,"gameId":"g1","team":"B","adjustedSuccessOffense":-.02,"adjustedSuccessDefense":.04}]
 row=build_adjusted_model_dataset(base,adj,2025)[0]
 assert row["home_adjustedSuccessEdge"]==pytest.approx(.12)
 assert row["away_adjustedSuccessEdge"]==pytest.approx(.01)
 assert row["target_margin"]==7.0 and row["target_homeWin"]==1
