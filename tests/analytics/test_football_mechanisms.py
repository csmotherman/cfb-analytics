from cfb_analytics.analytics.football_mechanisms import TEAM_FIELDS,orient_matchup


def _team(prefix, **overrides):
    base={f"{prefix}_{f}":0.5 for f in TEAM_FIELDS}
    base.update(overrides)
    return base


def test_orient_matchup_direction_and_usage_interactions():
    m={"team1":"Home","team2":"Away"}
    m.update(_team("team1"))
    m.update(_team("team2"))
    m.update({
        "team1_OffYardsPerPossession":7.0,"team1_DefYardsPerPossession":4.0,
        "team2_OffYardsPerPossession":5.0,"team2_DefYardsPerPossession":6.0,
        "team1_OffGiveawayRate":0.05,"team1_DefTakeawayRate":0.20,
        "team2_OffGiveawayRate":0.15,"team2_DefTakeawayRate":0.10,
        "team1_RushRate":0.60,"team1_RushSuccessRate":0.50,"team2_RushSuccessRateAllowed":0.40,
        "team2_RushRate":0.40,"team2_RushSuccessRate":0.40,"team1_RushSuccessRateAllowed":0.45,
        "team1_PassRate":0.40,"team1_PassSuccessRate":0.50,"team2_PassSuccessRateAllowed":0.45,
        "team2_PassRate":0.60,"team2_PassSuccessRate":0.45,"team1_PassSuccessRateAllowed":0.50,
        "team1_OffPossessionsPerGame":12.0,"team1_DefPossessionsPerGame":11.0,
        "team2_OffPossessionsPerGame":10.0,"team2_DefPossessionsPerGame":13.0,
    })
    x=orient_matchup(m,"Home","Away")
    assert x is not None
    assert x["netYardsPerPossessionEdge"]==4.0
    assert x["netTurnoverPressureEdge"]>0
    assert x["netRushMatchupImpact"]>0
    assert x["expectedPossessionsPerTeam"]==11.5


def test_orient_matchup_rejects_wrong_teams():
    assert orient_matchup({"team1":"A","team2":"B"},"A","C") is None
