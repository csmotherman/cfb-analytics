from cfb_analytics.analytics.possession_volume import orient_matchup


def test_orient_matchup_expected_volume_and_edges():
    matchup={
        "team1":"A","team2":"B",
        "team1_OffPossessionsPerGame":12.0,"team1_DefPossessionsPerGame":11.0,
        "team1_OffPlaysPerPossession":6.0,"team1_DefPlaysPerPossession":5.5,
        "team2_OffPossessionsPerGame":10.0,"team2_DefPossessionsPerGame":13.0,
        "team2_OffPlaysPerPossession":5.0,"team2_DefPlaysPerPossession":4.5,
    }
    r=orient_matchup(matchup,"A","B")
    assert r["expectedHomePossessions"]==12.5
    assert r["expectedAwayPossessions"]==10.5
    assert r["expectedPossessionsPerTeam"]==11.5
    assert r["expectedTotalPlays"]==127.5
    assert r["homePlaysPerPossessionEdge"]==1.5
    assert r["awayPlaysPerPossessionEdge"]==-0.5


def test_orient_matchup_rejects_wrong_teams():
    assert orient_matchup({"team1":"A","team2":"B"},"A","C") is None
