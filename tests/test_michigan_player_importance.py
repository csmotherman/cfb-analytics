from cfb_analytics.pipelines.publish_michigan_player_importance import build


def test_bryce_underwood_is_first_and_starters_lead_depth():
    roster=[{"id":"1","firstName":"Depth","lastName":"Player","position":"QB"},{"id":"2","firstName":"Bryce","lastName":"Underwood","position":"QB"},{"id":"3","firstName":"Jordan","lastName":"Marshall","position":"RB"}]
    rows=build(roster,[])
    assert rows[0]["playerId"]=="2"
    assert rows[0]["rank"]==1
    assert rows[1]["depth"]==1
