import pytest

from cfb_analytics.analytics.prediction_v2_adjusted_scoring_challenger import (
    ADJ_DEFENSE_FEATURE,
    ADJ_MARGIN_FEATURE,
    ADJ_OFFENSE_FEATURE,
    RAW_MARGIN_FEATURE,
    VARIANTS,
    add_scoring_features,
    fit_adjusted_scoring,
)
from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES


def _synthetic_game(home, away, offense, defense, *, base=28.0, hfa=3.0):
    home_points = base + offense[home] - defense[away] + hfa / 2.0
    away_points = base + offense[away] - defense[home] - hfa / 2.0
    return {
        "homeTeam": home,
        "awayTeam": away,
        "homePoints": home_points,
        "awayPoints": away_points,
        "isNeutralSite": False,
    }


def test_adjusted_scoring_recovers_exact_connected_synthetic_system():
    offense = {"A": 7.0, "B": 0.0, "C": -7.0}
    defense = {"A": 5.0, "B": 0.0, "C": -5.0}
    games = [
        _synthetic_game(home, away, offense, defense)
        for home in offense
        for away in offense
        if home != away
    ]

    fitted = fit_adjusted_scoring(games)

    assert fitted["converged"] is True
    assert fitted["basePoints"] == pytest.approx(28.0, abs=1e-5)
    assert fitted["homeFieldAdvantage"] == pytest.approx(3.0, abs=1e-5)
    for team in offense:
        assert fitted["offense"][team] == pytest.approx(offense[team], abs=1e-4)
        assert fitted["defense"][team] == pytest.approx(defense[team], abs=1e-4)
    assert fitted["fitRmse"] < 1e-4


def _row(game_id, week, home="A", away="B"):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": str(game_id),
        "homeTeam": home,
        "awayTeam": away,
        "isNeutralSite": False,
    }


def _raw(game_id, home_score, away_score, home="A", away="B"):
    return {
        "gameId": str(game_id),
        "homeTeam": home,
        "awayTeam": away,
        "homeScore": float(home_score),
        "awayScore": float(away_score),
    }


def test_scoring_features_use_strictly_prior_partitions_only():
    rows = [_row(1, 1), _row(2, 2)]
    raw_a = {
        "1": _raw(1, 30, 20),
        "2": _raw(2, 70, 0),
    }
    raw_b = {
        "1": _raw(1, 30, 20),
        "2": _raw(2, 0, 70),
    }

    out_a = add_scoring_features(rows, raw_a)
    out_b = add_scoring_features(rows, raw_b)

    week2_a = next(row for row in out_a if row["gameId"] == "2")
    week2_b = next(row for row in out_b if row["gameId"] == "2")

    for field in (
        RAW_MARGIN_FEATURE,
        ADJ_MARGIN_FEATURE,
        ADJ_OFFENSE_FEATURE,
        ADJ_DEFENSE_FEATURE,
        "adjustedScoringExpectedHomePoints",
        "adjustedScoringExpectedAwayPoints",
        "adjustedScoringHfa",
    ):
        assert week2_a[field] == pytest.approx(week2_b[field])

    assert week2_a["adjustedScoringGamesBefore"] == 1


def test_raw_ppg_margin_has_home_margin_orientation():
    rows = [_row(1, 1), _row(2, 2)]
    raw = {
        "1": _raw(1, 30, 20),
        "2": _raw(2, 24, 21),
    }
    out = add_scoring_features(rows, raw)
    week2 = next(row for row in out if row["gameId"] == "2")
    assert week2[RAW_MARGIN_FEATURE] == pytest.approx(10.0)


def test_adjusted_margin_equals_offense_plus_defense_plus_site_effect():
    rows = [_row(1, 1), _row(2, 2)]
    raw = {
        "1": _raw(1, 30, 20),
        "2": _raw(2, 24, 21),
    }
    out = add_scoring_features(rows, raw)
    week2 = next(row for row in out if row["gameId"] == "2")
    expected = (
        week2[ADJ_OFFENSE_FEATURE]
        + week2[ADJ_DEFENSE_FEATURE]
        + week2["adjustedScoringHfa"]
    )
    assert week2[ADJ_MARGIN_FEATURE] == pytest.approx(expected)


def test_challenger_variants_only_append_predeclared_scoring_features():
    base = tuple(PREDICTION_V2_FEATURES)
    assert VARIANTS["raw-ppg-margin"] == base + (RAW_MARGIN_FEATURE,)
    assert VARIANTS["adjusted-scoring-margin"] == base + (ADJ_MARGIN_FEATURE,)
    assert VARIANTS["adjusted-scoring-split"] == base + (
        ADJ_OFFENSE_FEATURE,
        ADJ_DEFENSE_FEATURE,
    )
