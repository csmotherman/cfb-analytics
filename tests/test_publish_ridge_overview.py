from cfb_analytics.analytics.publish_ridge_overview import build_overview
from tests.test_opponent_adjusted_offense import _sample_rows


def test_build_overview_has_ranked_offense_and_defense_metrics():
    artifact=build_overview(_sample_rows(),2025,team="Alpha",lam=20)
    assert artifact["season"]==2025
    assert artifact["team"]=="Alpha"
    assert artifact["lambda"]==20
    for side in ("offense","defense"):
        block=artifact[side]
        assert block["rank"]>=1
        assert block["field_size"]==3
        assert set(block["metrics"])=={"ppd","ypd","success","scoring"}
        for metric in block["metrics"].values():
            assert metric["rank"]>=1
            assert metric["field_size"]==3
            assert isinstance(metric["value"],float)
