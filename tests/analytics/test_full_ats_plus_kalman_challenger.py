from __future__ import annotations

import pytest

from cfb_analytics.analytics.full_ats_plus_kalman_challenger import (
    BASELINE_FEATURES,
    CHALLENGER_FEATURES,
    EXPECTED_BASELINE,
    KALMAN_FEATURES,
    MIN_GAMES,
    THRESHOLD,
    _check_baseline,
    selection_overlap,
)


def _row(
    game_id: str,
    variant: str,
    confidence: float,
    side: int,
    result: str,
    season: int = 2025,
) -> dict:
    return {
        "season": season,
        "gameId": game_id,
        "variant": variant,
        "confidence": confidence,
        "pickedSideSign": side,
        "result": result,
    }


def test_contract_is_exactly_two_added_features() -> None:
    assert MIN_GAMES == 3
    assert THRESHOLD == pytest.approx(0.575)
    assert KALMAN_FEATURES == ("KALMAN_strength", "KALMAN_uncertainty")
    assert CHALLENGER_FEATURES[:-2] == BASELINE_FEATURES
    assert CHALLENGER_FEATURES[-2:] == KALMAN_FEATURES
    assert len(CHALLENGER_FEATURES) == len(BASELINE_FEATURES) + 2
    assert len(set(CHALLENGER_FEATURES)) == len(CHALLENGER_FEATURES)


def test_baseline_guard_accepts_selected_discovery_record() -> None:
    _check_baseline(dict(EXPECTED_BASELINE))


def test_baseline_guard_rejects_shifted_sample() -> None:
    wrong = dict(EXPECTED_BASELINE)
    wrong["wins"] += 1
    with pytest.raises(ValueError, match="baseline reproduction failed"):
        _check_baseline(wrong)


def test_selection_overlap_counts_fixed_threshold_sets() -> None:
    baseline = [
        _row("1", "FULL_BASELINE", 0.60, 1, "WIN"),       # both same side
        _row("2", "FULL_BASELINE", 0.59, 1, "LOSS"),      # baseline only
        _row("3", "FULL_BASELINE", 0.54, -1, "WIN"),      # challenger only
        _row("4", "FULL_BASELINE", 0.61, 1, "LOSS"),      # both opposite
        _row("5", "FULL_BASELINE", 0.52, 1, "WIN"),       # neither
    ]
    challenger = [
        _row("1", "FULL_PLUS_KALMAN", 0.62, 1, "WIN"),
        _row("2", "FULL_PLUS_KALMAN", 0.53, 1, "LOSS"),
        _row("3", "FULL_PLUS_KALMAN", 0.58, -1, "WIN"),
        _row("4", "FULL_PLUS_KALMAN", 0.60, -1, "WIN"),
        _row("5", "FULL_PLUS_KALMAN", 0.51, 1, "WIN"),
    ]
    out = selection_overlap(baseline, challenger)
    assert out["allGames"] == 5
    assert out["baselineBets"] == 3
    assert out["challengerBets"] == 3
    assert out["bothBet"] == 2
    assert out["bothSameSide"] == 1
    assert out["bothOppositeSide"] == 1
    assert out["baselineOnly"] == 1
    assert out["challengerOnly"] == 1
    assert out["baselineOnlyPerformance"]["losses"] == 1
    assert out["challengerOnlyPerformance"]["wins"] == 1


def test_selection_overlap_rejects_game_mismatch() -> None:
    baseline = [_row("1", "FULL_BASELINE", 0.60, 1, "WIN")]
    challenger = [_row("2", "FULL_PLUS_KALMAN", 0.60, 1, "WIN")]
    with pytest.raises(ValueError, match="key mismatch"):
        selection_overlap(baseline, challenger)
