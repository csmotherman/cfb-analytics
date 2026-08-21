import math
from cfb_analytics.analytics.validate_offense_adjustment import aggregate_seasons, cross_validate
from tests.test_opponent_adjusted_offense import _sample_rows


def test_cross_validation_keeps_game_rows_together_and_scores_all_models():
    result = cross_validate(_sample_rows(), 2025, folds=3, seed="unit-test")
    assert result["games"] == 6
    assert len(result["fold_counts"]) >= 2
    for block in result["metrics"].values():
        assert block["observations"] > 0
        for model in ("raw", "one_pass", "least_squares"):
            error = block["errors"][model]
            assert math.isfinite(error["mae"])
            assert math.isfinite(error["rmse"])
            assert error["mae"] >= 0
            assert error["rmse"] >= error["mae"] - 1e-12
            assert error["weight"] > 0
            assert error["absolute_error"] >= 0
            assert error["squared_error"] >= 0


def test_cross_validation_is_deterministic_for_same_seed():
    a = cross_validate(_sample_rows(), 2025, folds=3, seed="same")
    b = cross_validate(_sample_rows(), 2025, folds=3, seed="same")
    assert a == b


def test_multi_season_pooling_uses_exact_error_sums_not_average_of_season_rmses():
    first = cross_validate(_sample_rows(), 2025, folds=3, seed="a")
    second = cross_validate(_sample_rows(), 2025, folds=3, seed="b")
    second = {**second, "season": 2024}
    pooled = aggregate_seasons([first, second])
    assert pooled["seasons"] == [2025, 2024]
    assert pooled["games"] == 12
    for metric in pooled["metrics"]:
        assert pooled["metrics"][metric]["observations"] == first["metrics"][metric]["observations"] + second["metrics"][metric]["observations"]
        for model in ("raw", "one_pass", "least_squares"):
            p = pooled["metrics"][metric]["errors"][model]
            a = first["metrics"][metric]["errors"][model]
            b = second["metrics"][metric]["errors"][model]
            assert p["weight"] == a["weight"] + b["weight"]
            assert p["absolute_error"] == a["absolute_error"] + b["absolute_error"]
            assert p["squared_error"] == a["squared_error"] + b["squared_error"]
            assert p["mae"] == (p["absolute_error"] / p["weight"])
            assert p["rmse"] == math.sqrt(p["squared_error"] / p["weight"])
