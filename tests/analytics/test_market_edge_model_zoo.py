from __future__ import annotations

import numpy as np

from cfb_analytics.analytics.market_edge_model_zoo import (
    BREAK_EVEN_MINUS_110,
    CLASSIFIER_SPECS,
    CONFIDENCE_THRESHOLDS,
    FIXED_BLEND_WEIGHTS,
    MODEL_FEATURES,
    REGRESSION_SPECS,
    attach_market,
    feature_matrix,
    grade_classifier,
    grade_margin_predictions,
)


def _base_row() -> dict:
    row = {feature: 0.1 for feature in MODEL_FEATURES if feature not in {
        "marketHomeMargin", "marketAbsSpread", "marketSpreadSquared",
        "marketHomeFavorite", "marketPickem", "weekNumber", "neutralSite",
    }}
    row.update(
        {
            "gameId": "1",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "week": 5,
            "isNeutralSite": False,
            "target_margin": 10.0,
        }
    )
    return row


def test_attach_market_uses_project_sign_convention_and_transforms() -> None:
    row = attach_market(
        _base_row(),
        {
            "gameId": "1",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "marketHomeMargin": 7.5,
        },
    )
    assert row["marketHomeMargin"] == 7.5
    assert row["marketAbsSpread"] == 7.5
    assert row["marketSpreadSquared"] == 56.25
    assert row["marketHomeFavorite"] == 1.0
    assert row["marketPickem"] == 0.0
    assert row["weekNumber"] == 5.0
    assert row["neutralSite"] == 0.0
    assert feature_matrix([row]).shape == (1, len(MODEL_FEATURES))


def test_margin_grading_matches_ats_and_minus_110_roi() -> None:
    rows = [
        {"target_margin": 10.0, "marketHomeMargin": 7.0},  # home covers
        {"target_margin": 3.0, "marketHomeMargin": 7.0},   # away covers
        {"target_margin": 7.0, "marketHomeMargin": 7.0},   # push
    ]
    # Pick home, away, home respectively.
    pred = np.asarray([9.0, 5.0, 8.0])
    scored = grade_margin_predictions(rows, pred)
    assert scored["atsWins"] == 2
    assert scored["atsLosses"] == 0
    assert scored["atsPushes"] == 1
    assert scored["atsAccuracy"] == 1.0
    assert scored["roiMinus110"] == 100.0 / 110.0


def test_classifier_confidence_threshold_can_abstain() -> None:
    rows = [
        {"target_margin": 10.0, "marketHomeMargin": 7.0},
        {"target_margin": 3.0, "marketHomeMargin": 7.0},
    ]
    scored = grade_classifier(rows, np.asarray([0.80, 0.52]), 0.55)
    assert scored["wins"] == 1
    assert scored["losses"] == 0
    assert scored["noBet"] == 1


def test_discovery_registry_is_predeclared_and_unique() -> None:
    regression_names = [spec.name for spec in REGRESSION_SPECS]
    classifier_names = [spec.name for spec in CLASSIFIER_SPECS]
    assert len(regression_names) == len(set(regression_names))
    assert len(classifier_names) == len(set(classifier_names))
    assert not set(regression_names) & set(classifier_names)
    assert FIXED_BLEND_WEIGHTS == (0.10, 0.25, 0.50, 0.75)
    assert CONFIDENCE_THRESHOLDS == (0.50, 0.55, 0.575, 0.60)
    assert abs(BREAK_EVEN_MINUS_110 - 0.5238095238095238) < 1e-15


def test_registry_covers_linear_robust_tree_kernel_neural_and_direct_ats() -> None:
    regression_names = {spec.name for spec in REGRESSION_SPECS}
    classifier_names = {spec.name for spec in CLASSIFIER_SPECS}
    assert {
        "RESIDUAL_RIDGE",
        "RESIDUAL_HUBER",
        "RESIDUAL_MEDIAN_QUANTILE",
        "RESIDUAL_HIST_GB",
        "RESIDUAL_EXTRA_TREES",
        "RESIDUAL_RBF_SVR",
        "RESIDUAL_MLP",
        "DIRECT_RIDGE",
    } <= regression_names
    assert {"ATS_LOGISTIC", "ATS_HIST_GB", "ATS_EXTRA_TREES", "ATS_MLP"} <= classifier_names
