from __future__ import annotations

import math

from cfb_analytics.analytics.dynamic_market_edge_zoo import (
    ELO_HFA,
    EloState,
    GlickoState,
    KalmanState,
    build_dynamic_signals,
)


def test_classic_elo_home_win_moves_ratings_correct_direction():
    state = EloState(mov=False)
    before, _ = state.predict("A", "B", False)
    state.update("A", "B", 7.0, False)
    after, _ = state.predict("A", "B", False)
    assert before == ELO_HFA
    assert after > before


def test_mov_elo_reacts_more_to_blowout_than_classic_elo():
    classic = EloState(mov=False)
    mov = EloState(mov=True)
    classic.update("A", "B", 35.0, True)
    mov.update("A", "B", 35.0, True)
    assert mov.ratings["A"] - 1500.0 > classic.ratings["A"] - 1500.0


def test_glicko_uncertainty_shrinks_after_observed_game():
    state = GlickoState()
    _, before = state.predict("A", "B", True)
    state.update_partition([("A", "B", 3.0, True)])
    _, after = state.predict("A", "B", True)
    assert after < before


def test_kalman_updates_latent_strength_toward_result():
    state = KalmanState()
    before, _ = state.predict("A", "B", True)
    state.update("A", "B", 21.0, True)
    after, _ = state.predict("A", "B", True)
    assert before == 0.0
    assert after > 0.0


def test_same_partition_results_do_not_leak_into_same_partition_predictions():
    data = {
        2014: [
            {"season": 2014, "seasonType": "regular", "week": 1, "gameId": "1", "homeTeam": "A", "awayTeam": "B", "target_margin": 40.0, "isNeutralSite": False},
            {"season": 2014, "seasonType": "regular", "week": 1, "gameId": "2", "homeTeam": "A", "awayTeam": "C", "target_margin": -10.0, "isNeutralSite": False},
            {"season": 2014, "seasonType": "regular", "week": 2, "gameId": "3", "homeTeam": "A", "awayTeam": "D", "target_margin": 1.0, "isNeutralSite": False},
        ]
    }
    signals = build_dynamic_signals(data)
    # Both week-1 A home games are scored from the untouched initial Elo state.
    assert signals["ELO"]["1"][0] == ELO_HFA
    assert signals["ELO"]["2"][0] == ELO_HFA
    # Week 2 sees the completed week-1 information.
    assert not math.isclose(signals["ELO"]["3"][0], ELO_HFA)


def test_offseason_regresses_elo_halfway_to_mean():
    state = EloState(ratings={"A": 1600.0}, mov=False)
    state.offseason()
    assert state.ratings["A"] == 1550.0
