import pytest

from cfb_analytics.analytics.adjusted_scoring_model import _metrics
from cfb_analytics.analytics.prediction_v2_adjusted_scoring_challenger import fit_adjusted_scoring


def test_direct_margin_is_expected_home_minus_away_points():
    games = [
        {
            "homeTeam": "A",
            "awayTeam": "B",
            "homePoints": 35.0,
            "awayPoints": 21.0,
            "isNeutralSite": False,
        },
        {
            "homeTeam": "B",
            "awayTeam": "A",
            "homePoints": 24.0,
            "awayPoints": 28.0,
            "isNeutralSite": False,
        },
    ]
    fitted = fit_adjusted_scoring(games)
    base = fitted["basePoints"]
    hfa = fitted["homeFieldAdvantage"]
    offense = fitted["offense"]
    defense = fitted["defense"]

    home_points = base + offense["A"] - defense["B"] + hfa / 2.0
    away_points = base + offense["B"] - defense["A"] - hfa / 2.0
    margin = home_points - away_points

    expected = (
        offense["A"] - offense["B"]
        + defense["A"] - defense["B"]
        + hfa
    )
    assert margin == pytest.approx(expected)


def test_metrics_score_both_margin_error_and_winner_accuracy():
    rows = [
        {"actualHomeMargin": 7.0, "actualHomeWin": True, "pred": 3.0},
        {"actualHomeMargin": -4.0, "actualHomeWin": False, "pred": -6.0},
        {"actualHomeMargin": 10.0, "actualHomeWin": True, "pred": -2.0},
    ]
    metrics = _metrics(rows, "pred")
    assert metrics["n"] == 3
    assert metrics["mae"] == pytest.approx((4.0 + 2.0 + 12.0) / 3.0)
    assert metrics["rmse"] == pytest.approx(((16.0 + 4.0 + 144.0) / 3.0) ** 0.5)
    assert metrics["winnerAccuracy"] == pytest.approx(2.0 / 3.0)
