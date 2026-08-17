import math

import pytest

from cfb_analytics.analytics.dynamic_bayesian_offense_defense import (
    AUGMENTED_FEATURES,
    BASELINE_FEATURES,
    EXPECTED_BASELINE,
    FAMILY_FEATURES,
    FAMILIES,
    GaussianODState,
    _check_baseline,
    _rate,
)


def test_predeclared_families_and_increment_are_exact():
    assert FAMILIES == ("POINTS_OD", "YPP_OD", "SUCCESS_OD", "MULTI_OD")
    assert len(FAMILY_FEATURES["POINTS_OD"]) == 3
    assert len(FAMILY_FEATURES["YPP_OD"]) == 3
    assert len(FAMILY_FEATURES["SUCCESS_OD"]) == 3
    assert len(FAMILY_FEATURES["MULTI_OD"]) == 9
    for family in FAMILIES:
        assert AUGMENTED_FEATURES[family][: len(BASELINE_FEATURES)] == BASELINE_FEATURES
        assert AUGMENTED_FEATURES[family][len(BASELINE_FEATURES) :] == FAMILY_FEATURES[family]


def test_gaussian_od_high_offense_observation_moves_correct_directions():
    state = GaussianODState(
        center=28.0,
        initial_variance=100.0,
        process_variance=4.0,
        observation_variance=196.0,
    )
    before = state.predict("A", "B")
    state.update_partition([("A", "B", 42.0)])
    after = state.predict("A", "B")
    assert after[0] > before[0]
    assert state.offense_mean["A"] > 0.0
    # In y=center+offense-defense, allowing more than expected makes defense weaker/negative.
    assert state.defense_mean["B"] < 0.0
    assert state.offense_var["A"] < 100.0
    assert state.defense_var["B"] < 100.0


def test_period_update_uses_one_snapshot_not_sequential_result_information():
    state1 = GaussianODState(28.0, 100.0, 4.0, 196.0)
    state2 = GaussianODState(28.0, 100.0, 4.0, 196.0)
    observations = [("A", "B", 35.0), ("C", "D", 21.0)]
    state1.update_partition(observations)
    state2.update_partition(list(reversed(observations)))
    assert state1.offense_mean == pytest.approx(state2.offense_mean)
    assert state1.defense_mean == pytest.approx(state2.defense_mean)
    assert state1.offense_var == pytest.approx(state2.offense_var)
    assert state1.defense_var == pytest.approx(state2.defense_var)


def test_offseason_shrinks_means_and_restores_uncertainty():
    state = GaussianODState(0.42, 0.01, 0.0004, 0.0144)
    state.update_partition([("A", "B", 0.60)])
    mean_before = state.offense_mean["A"]
    var_before = state.offense_var["A"]
    state.offseason()
    assert state.offense_mean["A"] == pytest.approx(mean_before * 0.5)
    assert state.offense_var["A"] > var_before


def test_rate_requires_positive_finite_denominator():
    assert _rate(55, 10) == pytest.approx(5.5)
    assert _rate(4, 10) == pytest.approx(0.4)
    assert _rate(1, 0) is None
    assert _rate(float("nan"), 10) is None


def test_baseline_guard_accepts_only_locked_discovery_record():
    _check_baseline(dict(EXPECTED_BASELINE))
    broken = dict(EXPECTED_BASELINE)
    broken["wins"] += 1
    with pytest.raises(ValueError, match="baseline reproduction failed"):
        _check_baseline(broken)


def test_uncertainty_is_finite_positive():
    state = GaussianODState(5.5, 1.0, 0.04, 4.0)
    home, away, uncertainty = state.predict("A", "B")
    assert home == pytest.approx(5.5)
    assert away == pytest.approx(5.5)
    assert math.isfinite(uncertainty)
    assert uncertainty > 0.0
