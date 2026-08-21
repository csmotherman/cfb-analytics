import math
import pytest

np = pytest.importorskip("numpy")

from cfb_analytics.analytics.least_squares_offense import (
    _solve_metric,
    calculate_least_squares_offense,
    compare_methods,
)
from tests.test_opponent_adjusted_offense import _sample_rows


def test_least_squares_outputs_all_four_metrics_and_zero_centered_effects():
    rows = _sample_rows()
    result = calculate_least_squares_offense(rows, 2025)
    assert {r["team"] for r in result} == {"Alpha", "Beta", "Gamma"}
    alpha = next(r for r in result if r["team"] == "Alpha")
    for key in (
        "ls_adjusted_points_per_drive",
        "ls_adjusted_yards_per_drive",
        "ls_adjusted_success_rate",
        "ls_adjusted_scoring_drive_rate",
    ):
        assert math.isfinite(alpha[key])

    solved = _solve_metric(rows, "ppd")
    assert sum(solved["offense_effect"].values()) == pytest.approx(0.0, abs=1e-9)
    assert sum(solved["defense_effect"].values()) == pytest.approx(0.0, abs=1e-9)


def test_clear_best_offense_stays_best_under_least_squares():
    result = calculate_least_squares_offense(_sample_rows(), 2025)
    assert result[0]["team"] == "Alpha"


def test_weighting_changes_solution_when_game_opportunities_change():
    rows = _sample_rows()
    baseline = _solve_metric(rows, "ppd")["adjusted"][1]
    # Give Alpha's strongest scoring game far more possessions; weighted LS
    # should move Alpha's estimated neutral-defense PPD upward.
    for r in rows:
        if r["gameId"] == "4" and r["team"] == "Alpha":
            r["resolvedPointPossessions"] = 100
            r["possessionPoints"] = 380
    weighted = _solve_metric(rows, "ppd")["adjusted"][1]
    assert weighted > baseline


def test_compare_methods_returns_correlations_and_team_differences():
    result = compare_methods(_sample_rows(), 2025)
    assert set(result["correlations"]) == {"ppd", "ypd", "success", "scoring"}
    assert len(result["teams"]) == 3
    assert all(math.isfinite(v) for v in result["correlations"].values())


def test_matrix_is_identifiable_with_constraints():
    solved = _solve_metric(_sample_rows(), "ppd")
    # Two sum-to-zero constraints should eliminate the two additive null
    # directions in separate offense/defense effects for a connected schedule.
    assert solved["matrix_rank"] == solved["parameter_count"]
