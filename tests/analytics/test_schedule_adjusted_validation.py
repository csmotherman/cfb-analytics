from __future__ import annotations

import pytest

from cfb_analytics.analytics.schedule_adjusted.specs import METRIC_SPECS
from cfb_analytics.analytics.schedule_adjusted.validation import (
    simple_matchup_prediction,
    validate_ridge_grid,
    walk_forward_predictions,
)


def _row(
    game: str,
    week: int,
    team_id: int,
    team: str,
    opponent_id: int,
    opponent: str,
    value: float,
    *,
    season: int = 2025,
    denominator: int = 100,
) -> dict[str, object]:
    return {
        "season": season,
        "season_type": "regular",
        "week": week,
        "gameId": game,
        "team_id": team_id,
        "opponent_id": opponent_id,
        "team": team,
        "opponent": opponent,
        "neutral_site": True,
        "gameValidationStatus": "PASS",
        "basicYardageYards": value * denominator,
        "basicYardagePlays": denominator,
        "yardsPerPlay": value,
    }


def _network(target_value: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    schedule = [
        (1, "g1", 1, "A", 2, "B", 6.2),
        (1, "g1", 2, "B", 1, "A", 4.8),
        (1, "g2", 3, "C", 4, "D", 5.8),
        (1, "g2", 4, "D", 3, "C", 4.5),
        (2, "g3", 1, "A", 3, "C", 6.5),
        (2, "g3", 3, "C", 1, "A", 5.0),
        (2, "g4", 2, "B", 4, "D", 5.2),
        (2, "g4", 4, "D", 2, "B", 4.7),
        (3, "g5", 1, "A", 4, "D", 6.8),
        (3, "g5", 4, "D", 1, "A", 4.9),
        (3, "g6", 2, "B", 3, "C", 5.3),
        (3, "g6", 3, "C", 2, "B", 5.1),
        (4, "target", 1, "A", 2, "B", target_value),
        (4, "target", 2, "B", 1, "A", 5.0),
    ]
    for week, game, team_id, team, opponent_id, opponent, value in schedule:
        rows.append(_row(game, week, team_id, team, opponent_id, opponent, value))
    return rows


def test_simple_matchup_gaussian_is_centered_offense_plus_defense() -> None:
    spec = METRIC_SPECS["yardsPerPlay"]
    assert simple_matchup_prediction(spec, 6.5, 4.8, 5.5) == pytest.approx(5.8)


def test_simple_matchup_binomial_stays_in_probability_bounds() -> None:
    spec = METRIC_SPECS["successRate"]
    prediction = simple_matchup_prediction(spec, 0.55, 0.35, 0.42)
    assert 0.0 < prediction < 1.0
    assert prediction > 0.35


def test_walk_forward_prediction_does_not_use_target_week_actual() -> None:
    low = walk_forward_predictions(
        _network(2.0),
        "yardsPerPlay",
        season=2025,
        ridge=5.0,
        min_prior_games=3,
        fit_home_field=False,
    )
    high = walk_forward_predictions(
        _network(10.0),
        "yardsPerPlay",
        season=2025,
        ridge=5.0,
        min_prior_games=3,
        fit_home_field=False,
    )
    low_target = next(row for row in low if row.game_id == "target" and row.offense_name == "A")
    high_target = next(row for row in high if row.game_id == "target" and row.offense_name == "A")
    assert low_target.raw_offense_expected == pytest.approx(high_target.raw_offense_expected, abs=1e-12)
    assert low_target.simple_matchup_expected == pytest.approx(high_target.simple_matchup_expected, abs=1e-12)
    assert low_target.adjusted_expected == pytest.approx(high_target.adjusted_expected, abs=1e-12)
    assert low_target.actual != high_target.actual


def test_ridge_grid_scores_every_method_on_same_targets() -> None:
    result = validate_ridge_grid(
        _network(6.0),
        season=2025,
        metric_names=("yardsPerPlay",),
        ridges=(1.0, 5.0),
        min_prior_games=3,
        fit_home_field=False,
    )
    metric = result["metrics"]["yardsPerPlay"]
    assert metric["predictionCount"] == metric["rawOffense"]["n"]
    assert metric["predictionCount"] == metric["simpleMatchup"]["n"]
    assert metric["predictionCount"] == metric["adjustedByRidge"]["1"]["n"]
    assert metric["predictionCount"] == metric["adjustedByRidge"]["5"]["n"]
    assert result["recommendedRidgeByMeanMAERatio"] in (1.0, 5.0)
