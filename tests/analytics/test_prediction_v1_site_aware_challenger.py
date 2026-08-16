import pytest

from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    FULL,
    SITE_AWARE,
    fit_site_aware_srs,
    promotion_eligible,
    site_aware_margin,
)


def test_fit_site_aware_srs_recovers_balanced_home_field_advantage():
    rows = [
        {"homeTeam": "A", "awayTeam": "B", "target_margin": 3.0, "isNeutralSite": False},
        {"homeTeam": "B", "awayTeam": "A", "target_margin": 3.0, "isNeutralSite": False},
        {"homeTeam": "A", "awayTeam": "B", "target_margin": 0.0, "isNeutralSite": True},
        {"homeTeam": "B", "awayTeam": "A", "target_margin": 0.0, "isNeutralSite": True},
    ]
    fitted = fit_site_aware_srs(rows)
    assert fitted["converged"] is True
    assert fitted["homeFieldAdvantage"] == pytest.approx(3.0, abs=1e-8)
    assert fitted["ratings"]["A"] == pytest.approx(0.0, abs=1e-8)
    assert fitted["ratings"]["B"] == pytest.approx(0.0, abs=1e-8)
    assert fitted["maxNormalResidual"] <= 1e-8
    assert fitted["hfaNormalResidual"] <= 1e-8


def test_site_aware_margin_applies_hfa_only_to_non_neutral_games():
    assert site_aware_margin(4.0, 2.5, True) == pytest.approx(4.0)
    assert site_aware_margin(4.0, 2.5, False) == pytest.approx(6.5)
    assert site_aware_margin(None, 2.5, False) is None


def test_site_aware_contract_replaces_only_srs_and_keeps_feature_count():
    assert len(SITE_AWARE) == len(FULL)
    assert "srsEdge" not in SITE_AWARE
    assert "siteAwareSrsMargin" in SITE_AWARE
    for feature in FULL:
        if feature != "srsEdge":
            assert feature in SITE_AWARE


def test_site_aware_promotion_gate_requires_broad_and_recent_stability():
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
    recent_bad["maeWins"] = 3
    assert promotion_eligible(all_good, recent_bad) is False
