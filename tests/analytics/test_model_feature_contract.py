import pytest

from cfb_analytics.analytics.model_feature_contract import (
    HIGHER_IS_BETTER,
    HIGHER_IS_WORSE,
    MODEL_FEATURE_CONTRACT,
    MATCHUP_FAMILIES,
    TURNOVER_CONTRACT,
    iterative_matchup_value,
    raw_matchup_value,
)
from cfb_analytics.derived.pregame import build_matchup_features


def test_all_six_matchup_families_have_explicit_direction_contracts():
    assert len(MATCHUP_FAMILIES) == 6
    assert set(MODEL_FEATURE_CONTRACT) == {x[0] for x in MATCHUP_FAMILIES}
    for contract in MODEL_FEATURE_CONTRACT.values():
        assert contract["raw_offense_direction"] == HIGHER_IS_BETTER
        assert contract["raw_defense_direction"] == HIGHER_IS_WORSE
        assert contract["iterative_offense_direction"] == HIGHER_IS_BETTER
        assert contract["iterative_defense_direction"] == HIGHER_IS_BETTER
    assert TURNOVER_CONTRACT["direction"] == HIGHER_IS_BETTER


def test_raw_matchup_monotonicity_matches_football_meaning():
    baseline = raw_matchup_value(0.50, 0.40)
    assert raw_matchup_value(0.55, 0.40) > baseline
    assert raw_matchup_value(0.50, 0.45) > baseline
    assert raw_matchup_value(0.50, 0.35) < baseline


def test_iterative_matchup_monotonicity_matches_strength_ratings():
    baseline = iterative_matchup_value(0.08, 0.04)
    assert iterative_matchup_value(0.10, 0.04) > baseline
    assert iterative_matchup_value(0.08, 0.06) < baseline
    assert iterative_matchup_value(0.08, 0.02) > baseline


def test_raw_matchup_builder_treats_more_allowed_as_weaker_defense():
    common = {
        "season": 2025,
        "seasonType": "regular",
        "week": 5,
        "gameId": "g1",
        "gamesPlayedBefore": 4,
        "historyAvailable": True,
        "turnoverMargin": 0,
        "explosivePlayRate": 0.10,
        "explosivePlayRateAllowed": 0.10,
        "yardsPerPlay": 6.0,
        "yardsAllowedPerPlay": 6.0,
        "yardsPerPossession": 35.0,
        "yardsAllowedPerPossession": 35.0,
        "pointsPerOpportunity": 4.0,
        "pointsPerOpportunityAllowed": 4.0,
        "averageStartOwnYardLine": 30.0,
        "averageStartOwnYardLineAllowed": 30.0,
    }
    a = {**common, "team": "A", "opponent": "B", "successRate": 0.50, "successRateAllowed": 0.40}
    b = {**common, "team": "B", "opponent": "A", "successRate": 0.50, "successRateAllowed": 0.45}
    row = build_matchup_features([a, b], 2025)[0]
    assert row["team1_successRateEdge"] == pytest.approx(0.95)
    assert row["team2_successRateEdge"] == pytest.approx(0.90)
