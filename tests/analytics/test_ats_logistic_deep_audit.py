from __future__ import annotations

import math

from cfb_analytics.analytics.ats_logistic_deep_audit import (
    BREAK_EVEN_MINUS_110,
    FEATURE_VARIANTS,
    bankroll_path,
    binomial_upper_tail,
    confidence_bucket,
    make_game_record,
    picked_side_role,
    spread_bucket,
    summarize_bets,
    week_bucket,
    wilson_interval,
)
from cfb_analytics.analytics.market_edge_model_zoo import MARKET_CONTEXT_FEATURES
from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES


def _row(actual: float, market: float, week: int = 6, neutral: bool = False) -> dict:
    return {
        "gameId": "1",
        "homeTeam": "Home",
        "awayTeam": "Away",
        "seasonType": "regular",
        "week": week,
        "isNeutralSite": neutral,
        "target_margin": actual,
        "marketHomeMargin": market,
    }


def test_feature_variants_are_predeclared_and_full_is_union() -> None:
    assert FEATURE_VARIANTS["FOOTBALL_ONLY"] == tuple(PREDICTION_V2_FEATURES)
    assert FEATURE_VARIANTS["MARKET_ONLY"] == tuple(MARKET_CONTEXT_FEATURES)
    assert FEATURE_VARIANTS["FULL"] == tuple(PREDICTION_V2_FEATURES) + tuple(MARKET_CONTEXT_FEATURES)


def test_game_record_grades_home_and_away_picks() -> None:
    home = make_game_record(_row(actual=10.0, market=7.0), min_games=3, season=2025, variant="FULL", probability_home_cover=0.61)
    assert home["pickedSide"] == "HOME"
    assert home["pickedSideRole"] == "FAVORITE"
    assert home["result"] == "WIN"
    assert math.isclose(home["confidence"], 0.61)

    away = make_game_record(_row(actual=3.0, market=7.0), min_games=3, season=2025, variant="FULL", probability_home_cover=0.38)
    assert away["pickedSide"] == "AWAY"
    assert away["pickedSideRole"] == "UNDERDOG"
    assert away["result"] == "WIN"
    assert math.isclose(away["confidence"], 0.62)


def test_market_role_handles_away_favorite_and_pickem() -> None:
    assert picked_side_role(-1, -4.0) == "FAVORITE"
    assert picked_side_role(1, -4.0) == "UNDERDOG"
    assert picked_side_role(1, 0.0) == "PICKEM"


def test_buckets_are_boundary_stable() -> None:
    assert spread_bucket(2.5) == "0-<3"
    assert spread_bucket(3.0) == "3-<7"
    assert spread_bucket(-7.0) == "7-<14"
    assert spread_bucket(14.0) == "14+"
    assert week_bucket(4) == "1-4"
    assert week_bucket(5) == "5-8"
    assert week_bucket(9) == "9-12"
    assert week_bucket(13) == "13+"
    assert confidence_bucket(0.5499) == "0.525-<0.550"
    assert confidence_bucket(0.575) == "0.575-<0.600"


def test_summary_uses_minus_110_profitability_and_wilson() -> None:
    rows = ([{"result": "WIN"}] * 55) + ([{"result": "LOSS"}] * 45) + [{"result": "PUSH"}]
    summary = summarize_bets(rows)
    assert summary["wins"] == 55
    assert summary["losses"] == 45
    assert summary["pushes"] == 1
    assert math.isclose(summary["accuracy"], 0.55)
    assert summary["roiMinus110"] > 0.0
    assert summary["wilson95Low"] < 0.55 < summary["wilson95High"]
    assert 0.0 <= summary["pValueOneSidedVsBreakEven"] <= 1.0
    assert BREAK_EVEN_MINUS_110 > 0.52


def test_binomial_tail_and_wilson_edge_cases() -> None:
    assert wilson_interval(0, 0) == (None, None)
    assert binomial_upper_tail(0, 0, 0.5) is None
    assert binomial_upper_tail(10, 10, 0.5) == 0.5 ** 10


def test_bankroll_path_tracks_drawdown_and_losing_streak() -> None:
    rows = [
        {"season": 2025, "week": 1, "gameId": "1", "confidence": 0.60, "result": "WIN"},
        {"season": 2025, "week": 2, "gameId": "2", "confidence": 0.60, "result": "LOSS"},
        {"season": 2025, "week": 3, "gameId": "3", "confidence": 0.60, "result": "LOSS"},
        {"season": 2025, "week": 4, "gameId": "4", "confidence": 0.60, "result": "WIN"},
    ]
    result = bankroll_path(rows, 0.575)
    assert result["longestLosingStreak"] == 2
    assert result["maxDrawdownUnits"] >= 2.0
    assert math.isclose(result["netUnits"], 2 * (100 / 110) - 2)
