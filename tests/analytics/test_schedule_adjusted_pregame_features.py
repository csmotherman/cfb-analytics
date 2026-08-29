from __future__ import annotations

import copy

import pytest

from cfb_analytics.analytics.schedule_adjusted.pregame_features import (
    PREGAME_RIDGE,
    attach_schedule_adjusted_pregame_features,
    edge_feature_name,
    partition_key,
)


def _row(game, week, team_id, team, opponent_id, opponent, ypp):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game,
        "team_id": team_id,
        "team": team,
        "opponent_id": opponent_id,
        "opponent": opponent,
        "neutral_site": True,
        "gameValidationStatus": "PASS",
        "basicYardageYards": ypp * 100.0,
        "basicYardagePlays": 100,
    }


def _game(game, week, a_id, a, b_id, b, a_ypp, b_ypp):
    return [
        _row(game, week, a_id, a, b_id, b, a_ypp),
        _row(game, week, b_id, b, a_id, a, b_ypp),
    ]


def _network():
    rows = []
    rows += _game("g1", 1, 1, "A", 3, "C", 6.2, 5.0)
    rows += _game("g2", 1, 2, "B", 4, "D", 5.1, 4.7)
    rows += _game("g3", 2, 1, "A", 4, "D", 6.5, 4.8)
    rows += _game("g4", 2, 2, "B", 3, "C", 5.3, 5.2)
    rows += _game("target", 3, 1, "A", 2, "B", 9.0, 2.0)
    rows += _game("future", 4, 3, "C", 4, "D", 8.0, 3.0)
    target = {
        "season": 2025,
        "seasonType": "regular",
        "week": 3,
        "gameId": "target",
        "homeTeam": "A",
        "awayTeam": "B",
        "isNeutralSite": True,
        "target_margin": 99.0,
        "target_homeWin": 1,
    }
    return rows, target


def _feature(rows, target):
    result = attach_schedule_adjusted_pregame_features(
        [target],
        rows,
        season=2025,
        metric_names=("yardsPerPlay",),
        ridge=5.0,
        fit_home_field=False,
        home_ridge=5.0,
    )
    assert len(result) == 1
    assert result[0]["scheduleAdjustedNetworkSupported"] is True
    return result[0][edge_feature_name("yardsPerPlay")]


def test_target_game_stats_and_label_cannot_change_its_pregame_feature():
    rows, target = _network()
    baseline = _feature(rows, target)

    mutated_rows = copy.deepcopy(rows)
    for row in mutated_rows:
        if row["gameId"] == "target":
            row["basicYardageYards"] *= 20.0
    mutated_target = {**target, "target_margin": -200.0, "target_homeWin": 0}

    assert _feature(mutated_rows, mutated_target) == pytest.approx(baseline, abs=1e-12)


def test_future_game_cannot_change_earlier_pregame_feature():
    rows, target = _network()
    baseline = _feature(rows, target)

    mutated = copy.deepcopy(rows)
    for row in mutated:
        if row["gameId"] == "future":
            row["basicYardageYards"] *= 50.0

    assert _feature(mutated, target) == pytest.approx(baseline, abs=1e-12)


def test_prior_game_can_change_later_pregame_feature():
    rows, target = _network()
    baseline = _feature(rows, target)

    mutated = copy.deepcopy(rows)
    for row in mutated:
        if row["gameId"] == "g1" and row["team"] == "A":
            row["basicYardageYards"] = 950.0

    assert abs(_feature(mutated, target) - baseline) > 1e-6


def test_postseason_partition_orders_after_regular_season_even_when_week_resets():
    regular = {"seasonType": "regular", "week": 14}
    postseason = {"seasonType": "postseason", "week": 1}
    assert partition_key(regular) < partition_key(postseason)


def test_validated_default_uses_multi_season_selected_ridge_40():
    assert PREGAME_RIDGE == 40.0
