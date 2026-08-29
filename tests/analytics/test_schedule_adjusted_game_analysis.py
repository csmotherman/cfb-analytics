from __future__ import annotations

import pytest

from cfb_analytics.analytics.schedule_adjusted.game_analysis import analyze_game


def _row(
    game: str,
    week: int,
    team_id: int,
    team: str,
    opponent_id: int,
    opponent: str,
    ypp: float,
    ypp_allowed: float,
) -> dict[str, object]:
    return {
        "season": 2025,
        "week": week,
        "gameId": game,
        "team_id": team_id,
        "opponent_id": opponent_id,
        "team": team,
        "opponent": opponent,
        "team_slug": team.lower(),
        "neutral_site": True,
        "gameValidationStatus": "PASS",
        "basicYardageYards": ypp * 100,
        "basicYardagePlays": 100,
        "yardsPerPlay": ypp,
        "yardsPerPlayAllowed": ypp_allowed,
    }


def _network(target_ypp: float) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows = [
        _row("g1", 1, 1, "A", 3, "C", 6.2, 5.0),
        _row("g1", 1, 3, "C", 1, "A", 5.0, 6.2),
        _row("g2", 1, 2, "B", 4, "D", 5.1, 4.7),
        _row("g2", 1, 4, "D", 2, "B", 4.7, 5.1),
        _row("g3", 2, 1, "A", 4, "D", 6.5, 4.8),
        _row("g3", 2, 4, "D", 1, "A", 4.8, 6.5),
        _row("g4", 2, 2, "B", 3, "C", 5.3, 5.2),
        _row("g4", 2, 3, "C", 2, "B", 5.2, 5.3),
        _row("g5", 3, 1, "A", 2, "B", 6.7, 5.0),
        _row("g5", 3, 2, "B", 1, "A", 5.0, 6.7),
        _row("g6", 3, 3, "C", 4, "D", 5.4, 4.9),
        _row("g6", 3, 4, "D", 3, "C", 4.9, 5.4),
    ]
    target = _row("target", 4, 1, "A", 2, "B", target_ypp, 4.2)
    counterpart = _row("target", 4, 2, "B", 1, "A", 4.2, target_ypp)
    rows.extend((target, counterpart))
    return rows, target


def test_retrospective_game_analysis_excludes_target_game_from_expectation() -> None:
    low_rows, low_target = _network(3.0)
    high_rows, high_target = _network(9.0)

    low = analyze_game(
        low_rows,
        low_target,
        metric_names=("yardsPerPlay",),
        ridge=5.0,
        fit_home_field=False,
    )
    high = analyze_game(
        high_rows,
        high_target,
        metric_names=("yardsPerPlay",),
        ridge=5.0,
        fit_home_field=False,
    )

    low_metric = low.metrics[0]
    high_metric = high.metrics[0]
    assert low_metric.offense is not None and high_metric.offense is not None
    assert low_metric.defense is not None and high_metric.defense is not None
    assert low_metric.offense.expected == pytest.approx(high_metric.offense.expected, abs=1e-12)
    assert low_metric.defense.expected == pytest.approx(high_metric.defense.expected, abs=1e-12)
    assert low_metric.offense.actual != high_metric.offense.actual
    assert low_metric.offense.network_supported
    assert low_metric.defense.network_supported


def test_positive_defense_poe_means_allowed_less_than_expected() -> None:
    rows, target = _network(6.0)
    result = analyze_game(
        rows,
        target,
        metric_names=("yardsPerPlay",),
        ridge=5.0,
        fit_home_field=False,
    )
    defense = result.metrics[0].defense
    assert defense is not None
    assert defense.actual == pytest.approx(4.2)
    if defense.actual < defense.expected:
        assert defense.performance_over_expected > 0
    else:
        assert defense.performance_over_expected <= 0
