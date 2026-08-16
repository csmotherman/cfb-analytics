import pytest

from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v2_2026_equivalence_audit import (
    _target_identity,
    compare_rows,
)
from cfb_analytics.analytics.prediction_v2_2026_features import FEATURE_MATERIALIZER_VERSION
from cfb_analytics.analytics.prediction_v2_early_prior_challenger import CHALLENGER_VERSION


def _row(game_id="1", value=1.0):
    row = {feature: value for feature in PREDICTION_V2_FEATURES}
    row.update(
        {
            "gameId": game_id,
            "priorWeightHome": 0.75,
            "priorWeightAway": 0.5,
            "earlyPriorVersion": CHALLENGER_VERSION,
            "prospectiveFeatureVersion": FEATURE_MATERIALIZER_VERSION,
        }
    )
    return row


def test_target_identity_whitelists_only_pregame_fields():
    source = {
        "season": 2025,
        "seasonType": "regular",
        "week": 2,
        "gameId": "123",
        "homeTeam": "A",
        "awayTeam": "B",
        "isNeutralSite": False,
        "target_margin": 17.0,
        "target_homeWin": 1,
        "homeScore": 31,
    }
    target = _target_identity(source)
    assert target == {
        "season": 2025,
        "seasonType": "regular",
        "week": 2,
        "gameId": "123",
        "homeTeam": "A",
        "awayTeam": "B",
        "isNeutralSite": False,
    }
    assert not any(key.startswith("target_") for key in target)


def test_compare_rows_passes_exact_and_sub_tolerance_values():
    expected = _row()
    actual = _row()
    actual[PREDICTION_V2_FEATURES[0]] += 5e-11

    result = compare_rows([expected], [actual], tolerance=1e-10)
    assert result["status"] == "PASS"
    assert result["expectedRows"] == 1
    assert result["actualRows"] == 1
    assert result["featureMismatches"] == 0
    assert result["maxAbsDiff"] == pytest.approx(5e-11)


def test_compare_rows_rejects_feature_drift():
    expected = _row()
    actual = _row()
    feature = PREDICTION_V2_FEATURES[3]
    actual[feature] += 2e-10

    result = compare_rows([expected], [actual], tolerance=1e-10)
    assert result["status"] == "FAIL"
    assert result["featureMismatches"] == 1
    assert result["maxAbsDiffByFeature"][feature] == pytest.approx(2e-10)


def test_compare_rows_rejects_missing_extra_and_outcome_bearing_rows():
    expected = [_row("1"), _row("2")]
    actual_extra = _row("3")
    actual_extra["target_margin"] = 7.0
    actual = [_row("1"), actual_extra]

    result = compare_rows(expected, actual)
    assert result["status"] == "FAIL"
    assert result["missingGameIds"] == ["2"]
    assert result["extraGameIds"] == ["3"]
    # Outcome leakage is checked on common rows, so put it on game 1 as well.
    actual[0]["target_homeWin"] = 1
    result = compare_rows(expected, actual)
    assert result["outcomeBearingRows"] == ["1"]


def test_compare_rows_rejects_prior_weight_and_version_drift():
    expected = _row()
    actual = _row()
    actual["priorWeightHome"] = 0.5
    actual["prospectiveFeatureVersion"] = "wrong-version"

    result = compare_rows([expected], [actual])
    assert result["status"] == "FAIL"
    assert result["priorWeightMismatches"] == 1
    assert result["versionMismatches"] == ["1"]


def test_compare_rows_rejects_duplicate_game_ids():
    with pytest.raises(ValueError, match="duplicate gameId"):
        compare_rows([_row("1"), _row("1")], [_row("1")])
