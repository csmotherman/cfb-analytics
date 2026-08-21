from cfb_analytics.analytics.publish_player_stats import canonical_season, canonical_games


def _roster():
    return [
        {"id":1,"firstName":"Q","lastName":"One","position":"QB"},
        {"id":2,"firstName":"R","lastName":"Two","position":"RB"},
        {"id":3,"firstName":"D","lastName":"Three","position":"LB"},
        {"id":4,"firstName":"O","lastName":"Four","position":"OL"},
    ]


def test_season_stats_are_position_aware():
    payload=[
        {"playerId":1,"player":"Q One","category":"passing","statType":"YDS","stat":"2500"},
        {"playerId":1,"player":"Q One","category":"passing","statType":"TD","stat":"20"},
        {"playerId":1,"player":"Q One","category":"receiving","statType":"YDS","stat":"5"},
        {"playerId":2,"player":"R Two","category":"rushing","statType":"YDS","stat":"1000"},
        {"playerId":2,"player":"R Two","category":"receiving","statType":"REC","stat":"30"},
        {"playerId":3,"player":"D Three","category":"defensive","statType":"TFL","stat":"9.5"},
        {"playerId":3,"player":"D Three","category":"defensive","statType":"SACKS","stat":"4"},
        {"playerId":4,"player":"O Four","category":"defensive","statType":"TOT","stat":"1"},
    ]
    rows=canonical_season(payload,_roster(),2025,"Michigan")
    by={r["playerId"]:r for r in rows}
    assert by["1"]["positionFamily"]=="QB"
    assert any(x["stat"]=="YDS" and x["category"]=="passing" for x in by["1"]["displayStats"])
    assert not any(x["category"]=="receiving" for x in by["1"]["displayStats"])
    assert by["2"]["positionFamily"]=="RB"
    assert any(x["category"]=="receiving" for x in by["2"]["displayStats"])
    assert by["3"]["side"]=="DEFENSE"
    assert any(x["stat"]=="SACKS" for x in by["3"]["displayStats"])
    assert by["4"]["positionFamily"]=="OL"
    assert by["4"]["displayStats"]==[]
    assert by["4"]["hasBoxScoreStats"] is False


def test_game_logs_include_opponent_and_result():
    games=[{"id":100,"teams":[{"school":"Michigan","categories":[{"name":"rushing","types":[{"name":"YDS","athletes":[{"id":2,"name":"R Two","stat":"88"}]}]}]}]}]
    schedule=[{"id":100,"week":2,"seasonType":"regular","homeTeam":"Michigan","awayTeam":"Oklahoma","homePoints":24,"awayPoints":20,"startDate":"2025-09-06T00:00:00Z"}]
    rows=canonical_games(games,_roster(),schedule,2025,"Michigan")
    assert len(rows)==1
    row=rows[0]
    assert row["playerId"]=="2"
    assert row["opponent"]=="Oklahoma"
    assert row["result"]=="W 24-20"
    assert row["week"]==2
    assert row["stats"]["rushing"]["YDS"]==88


def test_return_stats_are_added_when_present():
    payload=[
        {"playerId":2,"player":"R Two","category":"kickReturns","statType":"NO","stat":"3"},
        {"playerId":2,"player":"R Two","category":"kickReturns","statType":"YDS","stat":"72"},
    ]
    rows=canonical_season(payload,_roster(),2025,"Michigan")
    stats=rows[0]["displayStats"]
    assert {x["stat"] for x in stats} >= {"NO","YDS"}
