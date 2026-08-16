from cfb_analytics.analytics.prediction_v1_lean_challenger import (
    DEVELOPMENT_FOLDS,
    MIN_DEVELOPMENT_WINS,
    MIN_VALIDATION_WINS,
    VALIDATION_FOLDS,
    promotion_eligible,
    select_prunes,
)


def row(feature, mae, rmse, mae_wins, rmse_wins, folds=DEVELOPMENT_FOLDS):
    return {
        "feature": feature,
        "folds": folds,
        "meanDeltaMae": mae,
        "meanDeltaRmse": rmse,
        "maeWins": mae_wins,
        "rmseWins": rmse_wins,
    }


def test_select_prunes_requires_both_mean_metrics_and_stable_fold_wins():
    summaries = [
        row("good", -0.01, -0.02, MIN_DEVELOPMENT_WINS, MIN_DEVELOPMENT_WINS),
        row("mae_only", -0.01, 0.01, 8, 8),
        row("rmse_only", 0.01, -0.01, 8, 8),
        row("too_few_mae_wins", -0.01, -0.01, MIN_DEVELOPMENT_WINS - 1, 8),
        row("too_few_rmse_wins", -0.01, -0.01, 8, MIN_DEVELOPMENT_WINS - 1),
        row("wrong_fold_count", -0.01, -0.01, 8, 8, folds=7),
    ]
    assert select_prunes(summaries) == ("good",)


def test_promotion_gate_requires_both_recent_metrics_and_four_of_six_wins():
    passing = {
        "folds": VALIDATION_FOLDS,
        "meanDeltaMae": -0.01,
        "meanDeltaRmse": -0.01,
        "maeWins": MIN_VALIDATION_WINS,
        "rmseWins": MIN_VALIDATION_WINS,
    }
    assert promotion_eligible(passing)

    failing_rmse = dict(passing, meanDeltaRmse=0.001)
    assert not promotion_eligible(failing_rmse)

    failing_wins = dict(passing, maeWins=MIN_VALIDATION_WINS - 1)
    assert not promotion_eligible(failing_wins)
