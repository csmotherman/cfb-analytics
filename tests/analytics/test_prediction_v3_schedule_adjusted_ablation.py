import math

import pytest

from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v3_schedule_adjusted_ablation import (
    EVIDENCE_THRESHOLDS,
    LEGACY_EXPLOSIVE,
    LEGACY_SUCCESS,
    LEGACY_YPP,
    SA_EXPLOSIVE,
    SA_PASS,
    SA_RUSH,
    SA_SUCCESS,
    SA_YPP,
    TRAIN_MIN_GAMES,
    VARIANTS,
    pooled_summary,
    validate_variants,
    variant_features,
)
from cfb_analytics.analytics.schedule_adjusted.pregame_features import (
    SCHEDULE_ADJUSTED_EDGE_FEATURES,
)


def _variant(name):
    return next(variant for variant in VARIANTS if variant.name == name)


def test_ablation_variants_are_predeclared_and_valid():
    validate_variants()
    names = [variant.name for variant in VARIANTS]
    assert len(names) == len(set(names))
    assert names[0] == "V2"
    assert set(SCHEDULE_ADJUSTED_EDGE_FEATURES) == {
        SA_SUCCESS,
        SA_RUSH,
        SA_PASS,
        SA_EXPLOSIVE,
        SA_YPP,
    }
    assert TRAIN_MIN_GAMES == 3
    assert EVIDENCE_THRESHOLDS == (3, 4, 5, 6, 7, 8)


def test_addition_variants_leave_frozen_v2_features_intact():
    base = tuple(PREDICTION_V2_FEATURES)
    assert variant_features(_variant("V2")) == base

    success = variant_features(_variant("ADD_SUCCESS"))
    assert success[:-1] == base
    assert success[-1] == SA_SUCCESS

    all5 = variant_features(_variant("ADD_ALL5"))
    assert all5[: len(base)] == base
    assert all5[len(base) :] == tuple(SCHEDULE_ADJUSTED_EDGE_FEATURES)


def test_replacement_variants_remove_only_predeclared_legacy_concepts():
    base = set(PREDICTION_V2_FEATURES)

    success = set(variant_features(_variant("REPLACE_SUCCESS")))
    assert not (success & set(LEGACY_SUCCESS))
    assert SA_SUCCESS in success
    assert (base - set(LEGACY_SUCCESS)).issubset(success)

    explosive = set(variant_features(_variant("REPLACE_EXPLOSIVE")))
    assert not (explosive & set(LEGACY_EXPLOSIVE))
    assert SA_EXPLOSIVE in explosive

    ypp = set(variant_features(_variant("REPLACE_YPP")))
    assert not (ypp & set(LEGACY_YPP))
    assert SA_YPP in ypp

    core3 = set(variant_features(_variant("REPLACE_CORE3_ADD_RUSH_PASS")))
    removed = set(LEGACY_SUCCESS + LEGACY_EXPLOSIVE + LEGACY_YPP)
    assert not (core3 & removed)
    assert {SA_SUCCESS, SA_EXPLOSIVE, SA_YPP, SA_RUSH, SA_PASS}.issubset(core3)


def test_pooled_summary_weights_games_not_seasons():
    # Two seasons with deliberately unequal sample sizes. Pooled MAE/winner must
    # weight by games; pooled RMSE must combine squared error, not average RMSE.
    rows = [
        {
            "variant": "ADD_SUCCESS",
            "group": "addition",
            "season": 2024,
            "minEvidence": 4,
            "testGames": 100,
            "v2Mae": 10.0,
            "mae": 9.0,
            "deltaMae": -1.0,
            "v2Rmse": 12.0,
            "rmse": 11.0,
            "deltaRmse": -1.0,
            "v2Winner": 0.60,
            "winner": 0.62,
            "deltaWinnerPP": 2.0,
        },
        {
            "variant": "ADD_SUCCESS",
            "group": "addition",
            "season": 2025,
            "minEvidence": 4,
            "testGames": 300,
            "v2Mae": 14.0,
            "mae": 13.5,
            "deltaMae": -0.5,
            "v2Rmse": 18.0,
            "rmse": 17.5,
            "deltaRmse": -0.5,
            "v2Winner": 0.70,
            "winner": 0.71,
            "deltaWinnerPP": 1.0,
        },
    ]

    summary = pooled_summary(rows)
    result = next(row for row in summary if row["variant"] == "ADD_SUCCESS" and row["minEvidence"] == 4)

    assert result["testGames"] == 400
    assert result["v2Mae"] == pytest.approx(13.0)
    assert result["mae"] == pytest.approx(12.375)
    assert result["deltaMae"] == pytest.approx(-0.625)
    assert result["v2Winner"] == pytest.approx(0.675)
    assert result["winner"] == pytest.approx(0.6875)
    assert result["deltaWinnerPP"] == pytest.approx(1.25)
    assert result["v2Rmse"] == pytest.approx(math.sqrt((100 * 12.0**2 + 300 * 18.0**2) / 400))
    assert result["rmse"] == pytest.approx(math.sqrt((100 * 11.0**2 + 300 * 17.5**2) / 400))
    assert result["maeSeasonWins"] == 2
    assert result["rmseSeasonWins"] == 2
    assert result["winnerSeasonWins"] == 2
    assert result["seasons"] == 2
