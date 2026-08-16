from cfb_analytics.analytics.prediction_v1_integrity_audit import FULL
from cfb_analytics.analytics.prediction_v2 import (
    PREDICTION_V2_FEATURES,
    PREDICTION_V2_SITE_FEATURE,
    PREDICTION_V2_VERSION,
)


def test_prediction_v2_replaces_only_srs_with_site_aware_margin():
    assert PREDICTION_V2_VERSION == "prediction-v2-site-aware-srs-hfa-v1"
    assert len(PREDICTION_V2_FEATURES) == len(FULL) == 19
    assert PREDICTION_V2_SITE_FEATURE == "siteAwareSrsMargin"
    assert "srsEdge" not in PREDICTION_V2_FEATURES
    assert "siteAwareSrsMargin" in PREDICTION_V2_FEATURES
    for feature in FULL:
        if feature != "srsEdge":
            assert feature in PREDICTION_V2_FEATURES
