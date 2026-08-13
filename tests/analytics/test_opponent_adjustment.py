import pytest

from cfb_analytics.analytics.opponent_adjustment import (
    ADJUSTED_FEATURES,
    SPECS,
    _rate_residual,
    build_adjusted_model_dataset,
    build_adjusted_snapshots,
)
from cfb_analytics.derived.pregame import build_pregame_snapshots


def _success_spec():
    return next(s for s in SPECS if s[0] == "success")


def _team_game(team, opponent, week, game_id, successful, eligible, successful_allowed, eligible_allowed):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game_id,
        "team": team,
        "opponent": opponent,
        "validatedPossessions": 2,
        "validatedDefensivePossessions": 2,
        "offensivePlays": eligible,
        "defensivePlays": eligible_allowed,
        "offensiveYards": 50,
        "defensiveYardsAllowed": 50,
        "reviewPossessionGroups": 0,
        "gameValidationStatus": "PASS",
        "successEligiblePlays": eligible,
        "successfulPlays": successful,
        "successEligiblePlaysAllowed": eligible_allowed,
        "successfulPlaysAllowed": successful_allowed,
    }


def test_success_adjustment_is_denominator_weighted():
    rows = [
        {"gameId": "g1", "opponent": "B", "successfulPlays": 4, "successEligiblePlays": 10, "successfulPlaysAllowed": 5, "successEligiblePlaysAllowed": 10},
        {"gameId": "g2", "opponent": "C", "successfulPlays": 18, "successEligiblePlays": 30, "successfulPlaysAllowed": 12, "successEligiblePlaysAllowed": 30},
    ]
    snaps = {
        ("g1", "B"): {"successRateAllowed": 0.30, "successRate": 0.60},
        ("g2", "C"): {"successRateAllowed": 0.50, "successRate": 0.50},
    }
    result = _rate_residual(rows, snaps, _success_spec())
    assert result["adjustedSuccessOffense"] == pytest.approx(0.10)
    assert result["adjustedSuccessDefense"] == pytest.approx(0.10)
    assert result["adjustedSuccessOffenseDenominator"] == 40
    assert result["adjustedSuccessDefenseDenominator"] == 40


def test_adjustment_sign_is_positive_for_better_than_expected_play():
    rows = [{"gameId": "g1", "opponent": "B", "successfulPlays": 6, "successEligiblePlays": 10, "successfulPlaysAllowed": 3, "successEligiblePlaysAllowed": 10}]
    snaps = {("g1", "B"): {"successRateAllowed": 0.40, "successRate": 0.50}}
    result = _rate_residual(rows, snaps, _success_spec())
    assert result["adjustedSuccessOffense"] == pytest.approx(0.20)
    assert result["adjustedSuccessDefense"] == pytest.approx(0.20)


def test_adjustment_sign_is_negative_for_worse_than_expected_play():
    rows = [{"gameId": "g1", "opponent": "B", "successfulPlays": 3, "successEligiblePlays": 10, "successfulPlaysAllowed": 7, "successEligiblePlaysAllowed": 10}]
    snaps = {("g1", "B"): {"successRateAllowed": 0.50, "successRate": 0.50}}
    result = _rate_residual(rows, snaps, _success_spec())
    assert result["adjustedSuccessOffense"] == pytest.approx(-0.20)
    assert result["adjustedSuccessDefense"] == pytest.approx(-0.20)


def test_games_without_opponent_pregame_metric_do_not_enter_adjustment():
    rows = [{"gameId": "g1", "opponent": "B", "successfulPlays": 9, "successEligiblePlays": 10, "successfulPlaysAllowed": 1, "successEligiblePlaysAllowed": 10}]
    result = _rate_residual(rows, {("g1", "B"): {}}, _success_spec())
    assert result["adjustedSuccessOffense"] is None
    assert result["adjustedSuccessDefense"] is None
    assert result["adjustedSuccessGames"] == 0


def test_same_week_games_do_not_enter_opponent_adjustment_history():
    rows = [
        _team_game("A", "B", 1, "g1", 6, 10, 4, 10),
        _team_game("B", "A", 1, "g1", 4, 10, 6, 10),
        _team_game("A", "C", 2, "g2", 8, 10, 2, 10),
        _team_game("C", "A", 2, "g2", 2, 10, 8, 10),
        _team_game("A", "D", 2, "g3", 1, 10, 9, 10),
        _team_game("D", "A", 2, "g3", 9, 10, 1, 10),
        _team_game("A", "E", 3, "g4", 5, 10, 5, 10),
        _team_game("E", "A", 3, "g4", 5, 10, 5, 10),
    ]
    snapshots = build_pregame_snapshots(rows, 2025)
    adjusted = build_adjusted_snapshots(rows, snapshots, 2025)
    a_week2 = [r for r in adjusted if r["team"] == "A" and r["week"] == 2]
    a_week3 = next(r for r in adjusted if r["team"] == "A" and r["week"] == 3)
    assert len(a_week2) == 2
    assert all(r["adjustedSuccessGames"] == 0 for r in a_week2)
    assert a_week3["adjustedSuccessGames"] == 2


def test_historical_opponent_uses_snapshot_from_that_game_not_future_strength():
    rows = [
        _team_game("B", "C", 1, "g0", 5, 10, 5, 10),
        _team_game("C", "B", 1, "g0", 5, 10, 5, 10),
        _team_game("A", "B", 2, "g1", 6, 10, 4, 10),
        _team_game("B", "A", 2, "g1", 4, 10, 6, 10),
        _team_game("B", "D", 3, "g2", 0, 10, 10, 10),
        _team_game("D", "B", 3, "g2", 10, 10, 0, 10),
        _team_game("A", "E", 4, "g3", 5, 10, 5, 10),
        _team_game("E", "A", 4, "g3", 5, 10, 5, 10),
    ]
    snapshots = build_pregame_snapshots(rows, 2025)
    b_at_g1 = next(s for s in snapshots if s["gameId"] == "g1" and s["team"] == "B")
    b_at_g2 = next(s for s in snapshots if s["gameId"] == "g2" and s["team"] == "B")
    assert b_at_g1["successRateAllowed"] == pytest.approx(0.50)
    assert b_at_g2["successRateAllowed"] == pytest.approx(0.55)
    adjusted = build_adjusted_snapshots(rows, snapshots, 2025)
    a_week4 = next(r for r in adjusted if r["team"] == "A" and r["week"] == 4)
    assert a_week4["adjustedSuccessOffense"] == pytest.approx(0.10)


def test_adjusted_model_edges_combine_offense_and_opposing_defense():
    base = [{
        "season": 2025,
        "gameId": "g1",
        "homeTeam": "A",
        "awayTeam": "B",
        "target_margin": 7.0,
        "target_homeWin": 1,
    }]
    adjusted = [
        {"season": 2025, "gameId": "g1", "team": "A", "adjustedSuccessOffense": 0.08, "adjustedSuccessDefense": 0.03},
        {"season": 2025, "gameId": "g1", "team": "B", "adjustedSuccessOffense": -0.02, "adjustedSuccessDefense": 0.04},
    ]
    rows = build_adjusted_model_dataset(base, adjusted, 2025)
    assert len(rows) == 1
    assert rows[0]["home_adjustedSuccessEdge"] == pytest.approx(0.12)
    assert rows[0]["away_adjustedSuccessEdge"] == pytest.approx(0.01)
    assert rows[0]["target_margin"] == 7.0
    assert rows[0]["target_homeWin"] == 1


def test_adjusted_feature_contract_has_six_directional_pairs():
    assert len(ADJUSTED_FEATURES) == 12
    assert len(set(ADJUSTED_FEATURES)) == 12
