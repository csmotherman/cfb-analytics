from cfb_analytics.pipelines.publish_michigan_player_profiles import build


def test_freshmen_lead_with_prospect_and_veterans_with_production():
    roster=[{"id":"1","position":"QB","stars":5,"compositeRating":.99},{"id":"2","position":"RB","stars":3,"compositeRating":.85}]
    statuses=[{"playerId":"1","rosterStatus":"FRESHMAN"},{"playerId":"2","rosterStatus":"RETURNING"}]
    grades=[{"playerId":"2","grade":"A","positionFamily":"RB","nationalPositionPercentile":88,"productionPercentile":90,"usagePercentile":84}]
    snapshot={"payload":[{"playerId":"2","season":2025,"team":"Michigan","category":"rushing","statType":"YDS","stat":"800"}]}
    recruits=[{"playerId":"1","grade":"S","stars":5,"compositeRating":.99}]
    rows=build(roster,statuses,grades,[snapshot],recruits)
    assert rows[0]["focus"]["kind"] == "PROSPECT"
    assert rows[0]["focus"]["stars"] == 5
    assert rows[1]["focus"]["kind"] == "PRODUCTION"
    assert rows[1]["pastSeasons"][0]["stats"][0]["value"] == 800


def test_zero_stats_remain_an_explicit_empty_state():
    row=build([{"id":"1","position":"OL"}],[{"playerId":"1","rosterStatus":"RETURNING"}],[],[])[0]
    assert row["pastSeasons"] == []
    assert "No non-zero" in row["growthAreas"][-1]
