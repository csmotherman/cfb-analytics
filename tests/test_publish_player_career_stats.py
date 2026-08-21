from cfb_analytics.analytics.publish_player_career_stats import canonical_careers


def test_transfer_career_keeps_team_seasons_and_team_ids():
    history=[{"playerId":"1","team":"Michigan","timeline":[{"season":2024,"team":"Utah State","position":"RB"},{"season":2025,"team":"Michigan","position":"RB"},{"season":2026,"team":"Michigan","position":"RB"}]}]
    seasons={
        2024:[{"playerId":"1","player":"Test Back","team":"Utah State","category":"rushing","statType":"CAR","stat":"100"},{"playerId":"1","player":"Test Back","team":"Utah State","category":"rushing","statType":"YDS","stat":"650"}],
        2025:[{"playerId":"1","player":"Test Back","team":"Michigan","category":"rushing","statType":"CAR","stat":"120"},{"playerId":"1","player":"Test Back","team":"Michigan","category":"rushing","statType":"YDS","stat":"800"}],
    }
    teams=[{"id":328,"school":"Utah State"},{"id":130,"school":"Michigan"}]
    rows=canonical_careers(history,seasons,teams)
    assert len(rows)==1
    assert [(s["season"],s["team"],s["teamId"]) for s in rows[0]["seasons"]]==[(2024,"Utah State",328),(2025,"Michigan",130)]
    assert rows[0]["seasons"][0]["displayStats"][0]["stat"]=="CAR"


def test_mismatched_team_row_is_rejected_by_timeline():
    history=[{"playerId":"1","team":"Michigan","timeline":[{"season":2025,"team":"Michigan","position":"QB"},{"season":2026,"team":"Michigan","position":"QB"}]}]
    seasons={2025:[{"playerId":"1","team":"Other School","category":"passing","statType":"YDS","stat":"9999"}]}
    rows=canonical_careers(history,seasons,[{"id":130,"school":"Michigan"}])
    assert rows[0]["seasons"]==[]


def test_players_without_prior_stats_are_preserved():
    history=[{"playerId":"9","team":"Michigan","timeline":[{"season":2026,"team":"Michigan","position":"WR"}]}]
    rows=canonical_careers(history,{},[{"id":130,"school":"Michigan"}])
    assert rows==[{"playerId":"9","currentTeam":"Michigan","currentPosition":"WR","seasons":[]}]
