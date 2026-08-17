from __future__ import annotations

import math

import pytest

from cfb_analytics.analytics.ats_logistic_prospective_freeze import (
    CONFIDENCE_THRESHOLD,
    FREEZE_VERSION,
    MODEL_FEATURES,
    add_market_context,
    artifact_sha256,
    reject_target_leakage,
    score_prospective,
    validate_artifact,
)


def _artifact(coef_value: float = 0.0, intercept: float = 0.0):
    n = len(MODEL_FEATURES)
    return {
        "freezeVersion": FREEZE_VERSION,
        "features": list(MODEL_FEATURES),
        "minGames": 3,
        "confidenceThreshold": CONFIDENCE_THRESHOLD,
        "model": {
            "C": 0.5,
            "scalerMean": [0.0] * n,
            "scalerScale": [1.0] * n,
            "coefficients": [coef_value] * n,
            "intercept": intercept,
        },
    }


def _row():
    row = {name: 0.0 for name in MODEL_FEATURES if not name.startswith("market") and name not in {"weekNumber", "neutralSite"}}
    row.update({"gameId": "1", "homeTeam": "A", "awayTeam": "B", "week": 4, "isNeutralSite": False})
    return row


def test_validate_artifact_accepts_exact_contract():
    validate_artifact(_artifact())


def test_validate_artifact_rejects_threshold_change():
    artifact = _artifact()
    artifact["confidenceThreshold"] = 0.60
    with pytest.raises(ValueError, match="confidence threshold"):
        validate_artifact(artifact)


def test_add_market_context_uses_project_spread_convention():
    out = add_market_context(_row(), 7.5)
    assert out["marketHomeMargin"] == 7.5
    assert out["marketAbsSpread"] == 7.5
    assert out["marketSpreadSquared"] == 56.25
    assert out["marketHomeFavorite"] == 1.0
    assert out["weekNumber"] == 4.0
    assert out["neutralSite"] == 0.0


def test_target_leakage_guard_rejects_outcome():
    row = _row()
    row["target_margin"] = 3.0
    with pytest.raises(ValueError, match="target/outcome"):
        reject_target_leakage(row)


def test_score_no_bet_at_fifty_percent():
    result = score_prospective(_row(), -3.0, _artifact())
    assert math.isclose(result["homeCoverProbability"], 0.5)
    assert result["pick"] == "NO_BET"


def test_score_home_when_probability_clears_frozen_threshold():
    result = score_prospective(_row(), 0.0, _artifact(intercept=1.0))
    assert result["homeCoverProbability"] > CONFIDENCE_THRESHOLD
    assert result["pick"] == "HOME"


def test_artifact_checksum_is_deterministic():
    a = _artifact()
    b = dict(reversed(list(a.items())))
    assert artifact_sha256(a) == artifact_sha256(b)
