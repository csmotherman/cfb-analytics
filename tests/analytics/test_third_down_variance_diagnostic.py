import math

from cfb_analytics.analytics.third_down_variance_diagnostic import (
    fit_residual_effects_separate,
    prior_sd,
    select_penalty,
)


def test_prior_sd_matches_ridge_gaussian_scale():
    assert math.isclose(prior_sd(25.0), 0.2)


def test_offense_only_fit_does_not_manufacture_defense_effects():
    rows = []
    for i in range(40):
        rows.append({"offense": "A", "defense": "X" if i % 2 == 0 else "Y", "converted": 1 if i < 30 else 0})
        rows.append({"offense": "B", "defense": "X" if i % 2 == 0 else "Y", "converted": 1 if i < 10 else 0})
    baseline_logits = [0.0] * len(rows)

    offense, defense = fit_residual_effects_separate(
        rows,
        baseline_logits,
        offense_penalty=10.0,
        defense_penalty=10.0,
        fit_offense=True,
        fit_defense=False,
    )

    assert offense["A"] > 0
    assert offense["B"] < 0
    # defaultdict lookups can materialize disabled-side keys at exactly zero.
    # The invariant that matters is that no nonzero defense effect was fit.
    assert all(value == 0.0 for value in defense.values())


def test_defense_only_fit_does_not_manufacture_offense_effects():
    rows = []
    for i in range(40):
        rows.append({"offense": "A" if i % 2 == 0 else "B", "defense": "X", "converted": 1 if i < 30 else 0})
        rows.append({"offense": "A" if i % 2 == 0 else "B", "defense": "Y", "converted": 1 if i < 10 else 0})
    baseline_logits = [0.0] * len(rows)

    offense, defense = fit_residual_effects_separate(
        rows,
        baseline_logits,
        offense_penalty=10.0,
        defense_penalty=10.0,
        fit_offense=False,
        fit_defense=True,
    )

    assert all(value == 0.0 for value in offense.values())
    assert defense["X"] > 0
    assert defense["Y"] < 0


def test_select_penalty_uses_only_supplied_inner_seasons():
    penalties = (2.0, 100.0)
    reports = {
        2018: {
            "baseline": {"n": 100, "logLoss": 0.60, "brier": 0.21},
            "offense": {
                2.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
                100.0: {"n": 100, "logLoss": 0.60, "brier": 0.210},
            },
            "defense": {
                2.0: {"n": 100, "logLoss": 0.60, "brier": 0.210},
                100.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
            },
        },
        2019: {
            "baseline": {"n": 100, "logLoss": 0.60, "brier": 0.21},
            "offense": {
                2.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
                100.0: {"n": 100, "logLoss": 0.60, "brier": 0.210},
            },
            "defense": {
                2.0: {"n": 100, "logLoss": 0.60, "brier": 0.210},
                100.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
            },
        },
        2021: {
            "baseline": {"n": 100, "logLoss": 0.60, "brier": 0.21},
            "offense": {
                2.0: {"n": 100, "logLoss": 0.70, "brier": 0.250},
                100.0: {"n": 100, "logLoss": 0.50, "brier": 0.180},
            },
            "defense": {
                2.0: {"n": 100, "logLoss": 0.50, "brier": 0.180},
                100.0: {"n": 100, "logLoss": 0.70, "brier": 0.250},
            },
        },
    }

    choice = select_penalty(reports, (2018, 2019), "offense", penalties)
    assert choice["penalty"] == 2.0
    assert choice["deltaLogLoss"] < 0


def test_select_penalty_prefers_stronger_shrinkage_on_exact_tie():
    penalties = (2.0, 100.0)
    reports = {
        2019: {
            "baseline": {"n": 100, "logLoss": 0.60, "brier": 0.21},
            "offense": {
                2.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
                100.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
            },
            "defense": {
                2.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
                100.0: {"n": 100, "logLoss": 0.59, "brier": 0.205},
            },
        }
    }

    choice = select_penalty(reports, (2019,), "offense", penalties)
    assert choice["penalty"] == 100.0
