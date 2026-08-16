from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v2_early_prior_challenger import (
    CHALLENGER_VERSION,
    PRIOR_WINDOW_GAMES,
    blend_value,
    is_early_regular,
    prior_weight,
)


def test_four_game_prior_decay_is_fixed():
    assert CHALLENGER_VERSION == "prediction-v2-early-prior-four-game-linear-v1"
    assert PRIOR_WINDOW_GAMES == 4
    assert [prior_weight(games) for games in range(6)] == [1.0, 0.75, 0.5, 0.25, 0.0, 0.0]


def test_blend_value_reverts_to_current_after_four_games():
    assert blend_value(10.0, 2.0, 0) == 10.0
    assert blend_value(10.0, 2.0, 2) == 6.0
    assert blend_value(10.0, 2.0, 4) == 2.0
    assert blend_value(None, 2.0, 4) == 2.0
    assert blend_value(10.0, None, 0) == 10.0


def test_early_scope_is_regular_week_four_or_earlier():
    assert is_early_regular({"seasonType": "regular", "week": 0})
    assert is_early_regular({"seasonType": "regular", "week": 4})
    assert not is_early_regular({"seasonType": "regular", "week": 5})
    assert not is_early_regular({"seasonType": "postseason", "week": 1})


def test_prediction_v2_feature_count_stays_fixed():
    assert len(PREDICTION_V2_FEATURES) == 19
