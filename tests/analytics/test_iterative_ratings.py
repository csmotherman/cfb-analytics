import pytest

from cfb_analytics.analytics.iterative_ratings import (
    ITERATIVE_FEATURES,
    build_iterative_model_dataset,
    build_iterative_rating_snapshots,
    eligible_iterative_row,
    fit_metric_ratings,
)


def _game(team, opponent, week, game_id, made, attempts):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game_id,
        "team": team,
        "opponent": opponent,
        "successfulPlays": made,
        "successEligiblePlays": attempts,
    }


def test_iterative_solver_converges_and_centers_ratings():
    rows = [
        _game("A", "B", 1, "g1", 7, 10),
        _game("B", "A", 1, "g1", 3, 10),
        _game("A", "C", 2, "g2", 6, 10),
        _game("C", "A", 2, "g2", 4, 10),
        _game("B", "C", 3, "g3", 5, 10),
        _game("C", "B", 3, "g3", 5, 10),
    ]
    result = fit_metric_ratings(rows, ("Success", "successfulPlays", "successEligiblePlays"), shrinkage=1.0)
    assert result["converged"] is True
    assert result["iterations"] > 1
    assert sum(result["offense"].values()) == pytest.approx(0.0, abs=1e-10)
    assert sum(result["defense"].values()) == pytest.approx(0.0, abs=1e-10)
    assert result["offense"]["A"] > result["offense"]["B"]


def test_centered_ratings_preserve_fitted_game_values():
    rows = [
        _game("A", "B", 1, "g1", 8, 10),
        _game("B", "A", 1, "g1", 2, 10),
        _game("A", "C", 2, "g2", 7, 10),
        _game("C", "A", 2, "g2", 3, 10),
        _game("B", "C", 3, "g3", 6, 10),
        _game("C", "B", 3, "g3", 4, 10),
    ]
    result = fit_metric_ratings(rows, ("Success", "successfulPlays", "successEligiblePlays"), shrinkage=2.0)
    fitted = result["leagueMean"] + result["offense"]["A"] - result["defense"]["B"]
    assert result["converged"] is True
    assert 0.0 < fitted < 1.0
    assert sum(result["offense"].values()) == pytest.approx(0.0, abs=1e-10)
    assert sum(result["defense"].values()) == pytest.approx(0.0, abs=1e-10)


def test_same_partition_is_not_used_in_rating_snapshot():
    rows = [
        _game("A", "B", 1, "g1", 7, 10),
        _game("B", "A", 1, "g1", 3, 10),
        _game("A", "C", 2, "g2", 9, 10),
        _game("C", "A", 2, "g2", 1, 10),
        _game("A", "D", 2, "g3", 1, 10),
        _game("D", "A", 2, "g3", 9, 10),
    ]
    snaps = build_iterative_rating_snapshots(rows, 2025, shrinkage=1.0)
    week2 = [r for r in snaps if r["team"] == "A" and r["week"] == 2]
    assert len(week2) == 2
    assert all(r["gamesPlayedBefore"] == 1 for r in week2)
    assert week2[0]["iterativeSuccessOffense"] == pytest.approx(week2[1]["iterativeSuccessOffense"])
    assert week2[0]["iterativeSuccessDefense"] == pytest.approx(week2[1]["iterativeSuccessDefense"])


def test_future_game_does_not_change_historical_snapshot():
    base = [
        _game("A", "B", 1, "g1", 7, 10),
        _game("B", "A", 1, "g1", 3, 10),
        _game("A", "C", 2, "g2", 6, 10),
        _game("C", "A", 2, "g2", 4, 10),
    ]
    future = base + [
        _game("B", "D", 3, "g3", 0, 10),
        _game("D", "B", 3, "g3", 10, 10),
    ]
    first = build_iterative_rating_snapshots(base, 2025, shrinkage=1.0)
    second = build_iterative_rating_snapshots(future, 2025, shrinkage=1.0)
    a_g2_first = next(r for r in first if r["gameId"] == "g2" and r["team"] == "A")
    a_g2_second = next(r for r in second if r["gameId"] == "g2" and r["team"] == "A")
    assert a_g2_first["iterativeSuccessOffense"] == pytest.approx(a_g2_second["iterativeSuccessOffense"])
    assert a_g2_first["iterativeSuccessDefense"] == pytest.approx(a_g2_second["iterativeSuccessDefense"])


def test_three_and_four_game_eligibility_gates():
    row = {
        "homeIterativeGamesPlayedBefore": 3,
        "awayIterativeGamesPlayedBefore": 3,
        "target_margin": 4.0,
        "target_homeWin": 1,
    }
    row.update({feature: 0.1 for feature in ITERATIVE_FEATURES})
    assert eligible_iterative_row(row, 3) is True
    assert eligible_iterative_row(row, 4) is False
    row["homeIterativeGamesPlayedBefore"] = 4
    row["awayIterativeGamesPlayedBefore"] = 4
    assert eligible_iterative_row(row, 4) is True


def test_model_edges_use_offense_plus_opposing_defense():
    base = [{"season": 2025, "gameId": "g1", "homeTeam": "A", "awayTeam": "B", "target_margin": 7.0, "target_homeWin": 1}]
    snaps = [
        {"season": 2025, "gameId": "g1", "team": "A", "gamesPlayedBefore": 3, "iterativeSuccessOffense": 0.08, "iterativeSuccessDefense": 0.03},
        {"season": 2025, "gameId": "g1", "team": "B", "gamesPlayedBefore": 4, "iterativeSuccessOffense": -0.02, "iterativeSuccessDefense": 0.04},
    ]
    rows = build_iterative_model_dataset(base, snaps, 2025)
    assert rows[0]["home_iterativeSuccessEdge"] == pytest.approx(0.12)
    assert rows[0]["away_iterativeSuccessEdge"] == pytest.approx(0.01)
    assert rows[0]["target_margin"] == 7.0
