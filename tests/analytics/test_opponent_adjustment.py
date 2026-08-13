from cfb_analytics.analytics.opponent_adjustment import SPECS,_rate_residual,ADJUSTED_FEATURES


def test_success_adjustment_is_denominator_weighted():
    spec=next(s for s in SPECS if s[0]=="success")
    rows=[
        {"gameId":"g1","opponent":"B","successfulPlays":4,"successEligiblePlays":10,"successfulPlaysAllowed":5,"successEligiblePlaysAllowed":10},
        {"gameId":"g2","opponent":"C","successfulPlays":18,"successEligiblePlays":30,"successfulPlaysAllowed":12,"successEligiblePlaysAllowed":30},
    ]
    snaps={
        ("g1","B"):{"successRateAllowed":0.30,"successRate":0.60},
        ("g2","C"):{"successRateAllowed":0.50,"successRate":0.50},
    }
    result=_rate_residual(rows,snaps,spec)
    assert result["adjustedSuccessOffense"]==0.10
    assert result["adjustedSuccessDefense"]==0.10
    assert result["adjustedSuccessOffenseDenominator"]==40
    assert result["adjustedSuccessDefenseDenominator"]==40


def test_games_without_opponent_pregame_metric_do_not_enter_adjustment():
    spec=next(s for s in SPECS if s[0]=="success")
    rows=[{"gameId":"g1","opponent":"B","successfulPlays":9,"successEligiblePlays":10,"successfulPlaysAllowed":1,"successEligiblePlaysAllowed":10}]
    result=_rate_residual(rows,{("g1","B"):{}},spec)
    assert result["adjustedSuccessOffense"] is None
    assert result["adjustedSuccessDefense"] is None
    assert result["adjustedSuccessGames"]==0


def test_adjusted_feature_contract_has_six_directional_pairs():
    assert len(ADJUSTED_FEATURES)==12
    assert len(set(ADJUSTED_FEATURES))==12
