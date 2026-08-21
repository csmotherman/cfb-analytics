import math
from cfb_analytics.analytics.validate_offense_adjustment import cross_validate
from tests.test_opponent_adjusted_offense import _sample_rows


def test_cross_validation_keeps_game_rows_together_and_scores_all_models():
    result = cross_validate(_sample_rows(), 2025, folds=3, seed="unit-test")
    assert result["games"] == 6
    assert len(result["fold_counts"]) >= 2
    for block in result["metrics"].values():
        assert block["observations"] > 0
        for model in ("raw", "one_pass", "least_squares"):
            assert math.isfinite(block["errors"][model]["mae"])
            assert math.isfinite(block["errors"][model]["rmse"])
            assert block["errors"][model]["mae"] >= 0
            assert block["errors"][model]["rmse"] >= block["errors"][model]["mae"] - 1e-12


def test_cross_validation_is_deterministic_for_same_seed():
    a = cross_validate(_sample_rows(), 2025, folds=3, seed="same")
    b = cross_validate(_sample_rows(), 2025, folds=3, seed="same")
    assert a == b
