import math

from cfb_analytics.analytics.third_down_residual_skill import (
    context_feature_dict,
    distance_basis,
    fit_residual_effects,
    residual_probabilities,
    shrunken_rate,
)


def test_shrunken_rate_returns_prior_with_no_history_and_moves_with_evidence():
    assert shrunken_rate(0, 0, 0.42, 100) == 0.42
    high = shrunken_rate(80, 100, 0.42, 100)
    low = shrunken_rate(20, 100, 0.42, 100)
    assert 0.42 < high < 0.80
    assert 0.20 < low < 0.42


def test_distance_basis_uses_exact_distance_continuously():
    d4 = distance_basis(4)
    d5 = distance_basis(5)
    d10 = distance_basis(10)
    assert d4["distance_10"] < d5["distance_10"] < d10["distance_10"]
    assert d4["distance_hinge_3"] < d5["distance_hinge_3"]
    assert d5["distance_hinge_6"] == 0.0
    assert d10["distance_hinge_6"] > 0.0


def test_context_features_do_not_include_team_identity():
    row = {
        "distance": 7,
        "yardsToGoal": 55,
        "scoreMargin": -3,
        "goalToGo": False,
        "quarter": "2",
        "scoreState": "trailing",
        "offAllPlaySuccessShrunk": 0.48,
        "defAllPlaySuccessAllowedShrunk": 0.41,
    }
    features = context_feature_dict(row)
    assert features["quarter"] == "2"
    assert features["score_state"] == "trailing"
    assert math.isclose(features["yards_to_goal"], 0.55)
    assert not any("team" in key.lower() for key in features)


def test_partial_pooling_finds_directional_offense_and_defense_residuals():
    # Baseline believes every attempt is a 50/50 conversion. Team A repeatedly
    # over-converts and Team B repeatedly under-converts against both defenses.
    rows = []
    for i in range(40):
        rows.append({"offense": "A", "defense": "X" if i % 2 == 0 else "Y", "converted": 1 if i < 30 else 0})
        rows.append({"offense": "B", "defense": "X" if i % 2 == 0 else "Y", "converted": 1 if i < 10 else 0})
    baseline_logits = [0.0] * len(rows)

    offense, defense = fit_residual_effects(rows, baseline_logits, penalty=10.0)

    assert offense["A"] > 0
    assert offense["B"] < 0
    assert abs(defense["X"]) < 0.25
    assert abs(defense["Y"]) < 0.25

    probabilities = residual_probabilities(rows, baseline_logits, offense, defense)
    a_probs = [p for r, p in zip(rows, probabilities) if r["offense"] == "A"]
    b_probs = [p for r, p in zip(rows, probabilities) if r["offense"] == "B"]
    assert sum(a_probs) / len(a_probs) > 0.5
    assert sum(b_probs) / len(b_probs) < 0.5


def test_stronger_penalty_shrinks_team_effects_toward_zero():
    rows = [{"offense": "A", "defense": "X", "converted": 1}] * 12
    baseline_logits = [0.0] * len(rows)

    weak_off, _ = fit_residual_effects(rows, baseline_logits, penalty=2.0)
    strong_off, _ = fit_residual_effects(rows, baseline_logits, penalty=50.0)

    assert weak_off["A"] > strong_off["A"] > 0
