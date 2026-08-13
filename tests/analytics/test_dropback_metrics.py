from cfb_analytics.analytics.dropbacks import DROPBACKS_VERSION, team_dropback_metrics


def test_dropback_metrics_basic_counts():
    plays = [
        {"gameId": "g", "driveId": "d", "offense": "A", "defense": "B", "isScrimmagePlay": True, "isOffensivePlay": True, "eventSubtype": "PASS_COMPLETION"},
        {"gameId": "g", "driveId": "d", "offense": "A", "defense": "B", "isScrimmagePlay": True, "isOffensivePlay": True, "eventSubtype": "SACK"},
    ]
    off = team_dropback_metrics("A", plays, [])
    deff = team_dropback_metrics("B", plays, [])
    assert off["dropbacks"] == 2
    assert off["sacksAllowed"] == 1
    assert off["sackRate"] == 0.5
    assert deff["defensiveDropbacks"] == 2
    assert deff["sacks"] == 1
    assert deff["defensiveSackRate"] == 0.5
    assert off["dropbacksDefinitionVersion"] == DROPBACKS_VERSION


def test_zero_denominator_rates_are_null():
    result = team_dropback_metrics("A", [], [])
    assert result["dropbacks"] == 0
    assert result["sackRate"] is None
    assert result["defensiveDropbacks"] == 0
    assert result["defensiveSackRate"] is None
