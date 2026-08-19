from cfb_analytics.pipelines.publish_michigan_market_lines import build, fit_logistic


def test_calibration_increases_with_favorite_margin():
    history=[{"marketHomeMargin":-7,"actualHomeMargin":-3},{"marketHomeMargin":-3,"actualHomeMargin":-7},{"marketHomeMargin":3,"actualHomeMargin":7},{"marketHomeMargin":7,"actualHomeMargin":14}]
    _, slope=fit_logistic(history)
    assert slope > 0


def test_only_sourced_games_are_published():
    source={"season":2026,"team":"Michigan","acquiredAt":"2026-08-19","source":{"name":"source","url":"https://example.com"},"lines":[{"gameId":"1","opponent":"A","sportsbook":"Book","teamSpread":-7}]}
    history=[{"marketHomeMargin":-7,"actualHomeMargin":-3},{"marketHomeMargin":-3,"actualHomeMargin":-7},{"marketHomeMargin":3,"actualHomeMargin":7},{"marketHomeMargin":7,"actualHomeMargin":14}]
    schedule=[{"id":1,"week":1,"homeId":130}]
    result=build(source,history,schedule)
    assert len(result["games"]) == 1
    assert result["games"][0]["marketWinChance"] > .5
