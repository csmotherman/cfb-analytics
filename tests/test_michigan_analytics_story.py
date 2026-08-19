from cfb_analytics.pipelines.publish_michigan_analytics_story import build


def team(name, rush, dropbacks, points):
    return {"team": name, "rushAttempts": rush, "dropbacks": dropbacks, "rushSuccessRate": .5, "rushYardsPerAttempt": 6, "rushExplosivePlayRate": .15, "successRate": .48, "national_successRate_rank": 10, "thirdDownConversionRate": .5, "fourthDownConversionRate": .6, "pointsPerOpportunity": points, "national_pointsPerOpportunity_rank": 20, "pointsPerResolvedPossession": 2.5, "national_pointsPerResolvedPossession_rank": 15, "pointsPerResolvedPossessionAllowed": 1.8, "national_pointsPerResolvedPossessionAllowed_rank": 30, "explosivePlayRateAllowed": .1, "national_explosivePlayRateAllowed_rank": 20, "yardsPerSuccessfulPlayAllowed": 10, "national_yardsPerSuccessfulPlayAllowed_rank": 4}


def test_story_derives_run_share_from_locked_counts():
    result = build(team("Michigan", 60, 40, 3.4), team("Utah", 70, 30, 4.4))
    assert result["teams"]["michigan"]["designedBalanceRushShare"] == .6
    assert result["teams"]["utah"]["designedBalanceRushShare"] == .7
    assert result["comparisonType"] == "STAFF_CONTEXT"
