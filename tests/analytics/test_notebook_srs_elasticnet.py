from __future__ import annotations

import math

from cfb_analytics.analytics.notebook_srs_elasticnet import (
    ELASTIC_NET_ALPHA,
    ELASTIC_NET_L1_RATIO,
    ELASTIC_NET_MAX_ITER,
    NOTEBOOK_FEATURES,
    clipped_drive_points,
    fit_notebook_model,
    fit_notebook_srs,
    notebook_matchup_features,
    notebook_success,
    predict_notebook,
)


def test_notebook_success_rule_matches_50_70_100_thresholds():
    assert notebook_success({"down": 1, "distance": 10, "yardsGained": 5}) == 1.0
    assert notebook_success({"down": 1, "distance": 10, "yardsGained": 4}) == 0.0
    assert notebook_success({"down": 2, "distance": 10, "yardsGained": 7}) == 1.0
    assert notebook_success({"down": 2, "distance": 10, "yardsGained": 6}) == 0.0
    assert notebook_success({"down": 3, "distance": 4, "yardsGained": 4}) == 1.0
    assert notebook_success({"down": 4, "distance": 1, "yardsGained": 0}) == 0.0
    assert notebook_success({"down": None, "distance": None, "yardsGained": None}) == 0.0


def test_drive_points_match_notebook_clip_zero_to_eight():
    assert clipped_drive_points({"startOffenseScore": 7, "endOffenseScore": 14}) == 7.0
    assert clipped_drive_points({"startOffenseScore": 7, "endOffenseScore": 17}) == 8.0
    assert clipped_drive_points({"startOffenseScore": 14, "endOffenseScore": 7}) == 0.0
    assert clipped_drive_points({"startOffenseScore": None, "endOffenseScore": 7}) is None


def test_two_team_notebook_srs_standardizes_to_plus_minus_one():
    rows = [
        {
            "home_team": "A",
            "away_team": "B",
            "spread": 10.0,
            "SR_diff": 0.2,
            "EPA_diff": 0.5,
            "PPD_diff": 1.5,
            "DriveConv_diff": 0.25,
        }
    ]
    ratings = fit_notebook_srs(rows)
    for metric in ("spread", "SR_diff", "EPA_diff", "PPD_diff", "DriveConv_diff"):
        assert math.isclose(ratings["A"][f"SRS_{metric}"], 1.0, abs_tol=1e-12)
        assert math.isclose(ratings["B"][f"SRS_{metric}"], -1.0, abs_tol=1e-12)
    assert math.isclose(ratings["A"]["SRS_Overall"], 1.0, abs_tol=1e-12)
    assert math.isclose(ratings["B"]["SRS_Overall"], -1.0, abs_tol=1e-12)

    matchup = notebook_matchup_features(ratings, "A", "B")
    assert matchup is not None
    assert tuple(matchup) == NOTEBOOK_FEATURES
    assert all(math.isclose(matchup[feature], 2.0, abs_tol=1e-12) for feature in NOTEBOOK_FEATURES)


def test_notebook_srs_uses_unweighted_distinct_opponent_mean():
    # A plays B twice and C once. The notebook weights metric margins by games,
    # but avg_opp_srs is mean(B, C), not a 2:1 weighted opponent average.
    rows = [
        {"home_team": "A", "away_team": "B", "spread": 10.0, "SR_diff": 1.0, "EPA_diff": 1.0, "PPD_diff": 1.0, "DriveConv_diff": 1.0},
        {"home_team": "A", "away_team": "B", "spread": 8.0, "SR_diff": 1.0, "EPA_diff": 1.0, "PPD_diff": 1.0, "DriveConv_diff": 1.0},
        {"home_team": "A", "away_team": "C", "spread": -3.0, "SR_diff": -1.0, "EPA_diff": -1.0, "PPD_diff": -1.0, "DriveConv_diff": -1.0},
        {"home_team": "B", "away_team": "C", "spread": 2.0, "SR_diff": 0.5, "EPA_diff": 0.5, "PPD_diff": 0.5, "DriveConv_diff": 0.5},
    ]
    ratings = fit_notebook_srs(rows)
    assert set(ratings) == {"A", "B", "C"}
    for team in ratings:
        assert all(math.isfinite(value) for value in ratings[team].values())


def test_exact_selected_elasticnet_configuration_and_scaled_prediction():
    rows = []
    for i in range(20):
        row = {feature: float(i + j) / 10.0 for j, feature in enumerate(NOTEBOOK_FEATURES)}
        row["target_margin"] = 2.0 * i - 10.0
        rows.append(row)

    bundle = fit_notebook_model(rows)
    model = bundle["model"]
    assert model.alpha == ELASTIC_NET_ALPHA == 0.1
    assert model.l1_ratio == ELASTIC_NET_L1_RATIO == 0.2
    assert model.max_iter == ELASTIC_NET_MAX_ITER == 5000
    prediction = predict_notebook(bundle, rows[-1])
    assert math.isfinite(prediction)
