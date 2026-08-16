from cfb_analytics.analytics.prediction_v1_symmetric_challenger import (
    SYMMETRIC,
    add_symmetric_features,
    promotion_eligible,
)


def test_add_symmetric_features_builds_net_iterative_and_mwdr_edges():
    row = {
        "home_iterativeSuccessEdge": 0.30,
        "away_iterativeSuccessEdge": 0.10,
        "home_iterativeExplosiveEdge": 0.20,
        "away_iterativeExplosiveEdge": -0.05,
        "home_iterativeYardsPerPlayEdge": 1.1,
        "away_iterativeYardsPerPlayEdge": 0.4,
        "home_iterativeYardsPerPossessionEdge": 4.0,
        "away_iterativeYardsPerPossessionEdge": 1.5,
        "home_iterativeFinishingEdge": 0.8,
        "away_iterativeFinishingEdge": 0.2,
        "home_iterativeFieldPositionEdge": 2.0,
        "away_iterativeFieldPositionEdge": 0.5,
        "home_MWDR_OffenseEdge": 0.35,
        "home_MWDR_DefenseEdge": 0.25,
    }
    out = add_symmetric_features(row)
    assert out["netIterativeSuccessEdge"] == 0.20
    assert out["netIterativeExplosiveEdge"] == 0.25
    assert out["netIterativeYardsPerPlayEdge"] == 0.7
    assert out["netIterativeYardsPerPossessionEdge"] == 2.5
    assert out["netIterativeFinishingEdge"] == 0.6
    assert out["netIterativeFieldPositionEdge"] == 1.5
    assert out["netMwdrEdge"] == 0.60


def test_symmetric_contract_reduces_feature_count_without_duplicates():
    assert len(SYMMETRIC) == 12
    assert len(set(SYMMETRIC)) == len(SYMMETRIC)
    assert "srsEdge" in SYMMETRIC
    assert "mwdrXExpectedPossessions" in SYMMETRIC
    assert "successVolumeEdge" in SYMMETRIC
    assert "explosiveVolumeEdge" in SYMMETRIC
    assert "turnoverVolumeEdge" in SYMMETRIC


def test_promotion_gate_requires_broad_and_recent_stability():
    all_good = {
        "folds": 14,
        "meanDeltaMae": -0.02,
        "meanDeltaRmse": -0.01,
        "maeWins": 9,
        "rmseWins": 9,
    }
    recent_good = {
        "folds": 6,
        "meanDeltaMae": -0.01,
        "meanDeltaRmse": -0.01,
        "maeWins": 4,
        "rmseWins": 4,
    }
    assert promotion_eligible(all_good, recent_good) is True

    recent_bad = dict(recent_good)
    recent_bad["rmseWins"] = 3
    assert promotion_eligible(all_good, recent_bad) is False
