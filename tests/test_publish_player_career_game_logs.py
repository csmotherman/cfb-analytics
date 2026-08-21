from cfb_analytics.analytics.publish_player_career_game_logs import canonical_team_games,canonical_careers


def _game_payload():
    return [{"id":1,"teams":[{"school":"Utah","categories":[{"name":"receiving","types":[{"name":"REC","athletes":[{"id":"10","name":"Test WR","stat":"5"}]},{"name":"YDS","athletes":[{"id":"10","name":"Test WR","stat":"88"}]},{"name":"TD","athletes":[{"id":"10","name":"Test WR","stat":"1"}]}]}]}]}]


def _roster():
    return [{"id":"10","firstName":"Test","lastName":"WR","position":"WR"}]


def _schedule():
    return [{"id":1,"week":4,"homeTeam":"Utah","awayTeam":"Arizona","homePoints":31,"awayPoints":20,"startDate":"2025-09-20"}]


def test_position_aware_game_rows_keep_schedule_context():
    rows=canonical_team_games(_game_payload(),_roster(),_schedule(),2025,"Utah",{"10"},254)
    assert len(rows)==1
    row=rows[0]
    assert row["opponent"]=="Arizona"
    assert row["result"]=="W 31-20"
    assert row["teamId"]==254
    labels={(s["category"],s["stat"]):s["value"] for s in row["displayStats"]}
    assert labels[("receiving","REC")]==5
    assert labels[("receiving","YDS")]==88


def test_unwanted_players_are_filtered_by_exact_id():
    rows=canonical_team_games(_game_payload(),_roster(),_schedule(),2025,"Utah",{"999"},254)
    assert rows==[]


def test_career_rows_are_grouped_and_sorted_by_year():
    history=[{"playerId":"10","team":"Michigan","timeline":[]}]
    games=[
        {"playerId":"10","season":2024,"team":"Utah","teamId":254,"week":2,"gameId":"a","displayStats":[{"category":"receiving","stat":"REC","value":3}]},
        {"playerId":"10","season":2025,"team":"Michigan","teamId":130,"week":1,"gameId":"b","displayStats":[{"category":"receiving","stat":"REC","value":4}]},
    ]
    rows=canonical_careers(history,games,2026)
    assert [y["season"] for y in rows[0]["years"]]==[2025,2024]
    assert rows[0]["years"][0]["team"]=="Michigan"
    assert rows[0]["years"][1]["team"]=="Utah"
