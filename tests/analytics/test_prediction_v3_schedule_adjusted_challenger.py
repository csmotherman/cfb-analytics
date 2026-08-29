from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v3_schedule_adjusted_challenger import (
    PREDICTION_V3_FEATURES,
)
from cfb_analytics.analytics.schedule_adjusted.pregame_features import (
    SCHEDULE_ADJUSTED_EDGE_FEATURES,
    VALIDATED_PREGAME_METRICS,
)


def test_v3_appends_only_validated_schedule_adjusted_edges_to_v2():
    assert PREDICTION_V3_FEATURES[: len(PREDICTION_V2_FEATURES)] == tuple(PREDICTION_V2_FEATURES)
    assert PREDICTION_V3_FEATURES[len(PREDICTION_V2_FEATURES) :] == SCHEDULE_ADJUSTED_EDGE_FEATURES
    assert len(SCHEDULE_ADJUSTED_EDGE_FEATURES) == len(VALIDATED_PREGAME_METRICS) == 5


def test_v3_feature_contract_contains_no_outcome_fields():
    forbidden = ("target", "score", "margin", "win", "result")
    for feature in SCHEDULE_ADJUSTED_EDGE_FEATURES:
        lowered = feature.lower()
        assert not any(token in lowered for token in forbidden)
