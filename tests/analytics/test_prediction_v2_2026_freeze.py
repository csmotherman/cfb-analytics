import pytest

from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v2_2026_freeze import (
    FREEZE_VERSION,
    TARGET_SEASON,
    TRAINING_SEASONS,
    feature_complete,
    fit_frozen_model,
    score_rows,
    training_row_complete,
    write_immutable_json,
)
from cfb_analytics.analytics.prediction_v2_early_prior_challenger import CHALLENGER_VERSION


def _feature_row(**extra):
    row = {feature: 0.0 for feature in PREDICTION_V2_FEATURES}
    row.update(extra)
    return row


def _manifest(intercept=0.0):
    features = list(PREDICTION_V2_FEATURES)
    return {
        "schemaVersion": 1,
        "freezeVersion": FREEZE_VERSION,
        "earlyPriorVersion": CHALLENGER_VERSION,
        "matureBenchmarkVersion": "prediction-v2-site-aware-srs-hfa-v1",
        "targetSeason": TARGET_SEASON,
        "trainingSeasons": list(TRAINING_SEASONS),
        "features": features,
        "priorWeightsByGamesBefore": {
            "0": 1.0,
            "1": 0.75,
            "2": 0.5,
            "3": 0.25,
            "4": 0.0,
        },
        "model": {
            "features": features,
            "means": [0.0] * len(features),
            "scales": [1.0] * len(features),
            "weights": [float(intercept)] + [0.0] * len(features),
        },
    }


def test_prospective_feature_eligibility_does_not_require_targets():
    row = _feature_row()
    assert feature_complete(row)
    assert not training_row_complete(row)

    row["target_margin"] = 7.0
    row["target_homeWin"] = 1
    assert training_row_complete(row)


def test_fit_frozen_model_uses_exact_pre2026_training_contract():
    blend = {
        season: [
            _feature_row(
                gameId=f"{season}-1",
                target_margin=float(index - 4),
                target_homeWin=int(index >= 4),
            )
        ]
        for index, season in enumerate(TRAINING_SEASONS)
    }
    datasets = {
        "priorMap": {season: season - 1 for season in TRAINING_SEASONS},
        "blend": blend,
    }
    manifest = fit_frozen_model(datasets)

    assert manifest["targetSeason"] == 2026
    assert manifest["trainingSeasons"] == list(TRAINING_SEASONS)
    assert manifest["trainingRows"] == len(TRAINING_SEASONS)
    assert manifest["features"] == list(PREDICTION_V2_FEATURES)


def test_fit_frozen_model_rejects_training_season_drift():
    datasets = {
        "priorMap": {season: season - 1 for season in TRAINING_SEASONS[:-1]},
        "blend": {},
    }
    with pytest.raises(ValueError, match="training-season contract changed"):
        fit_frozen_model(datasets)


def test_scoring_rejects_any_outcome_bearing_2026_row():
    row = _feature_row(
        gameId="future-1",
        season=2026,
        week=1,
        homeTeam="Home",
        awayTeam="Away",
        target_margin=3.0,
    )
    with pytest.raises(ValueError, match="Outcome-bearing fields are forbidden"):
        score_rows(_manifest(), [row])


def test_scoring_emits_margin_and_winner_without_inventing_probability():
    row = _feature_row(
        gameId="future-1",
        season=2026,
        seasonType="regular",
        week=1,
        homeTeam="Home",
        awayTeam="Away",
        isNeutralSite=False,
        priorWeightHome=0.75,
        priorWeightAway=0.5,
    )
    prediction = score_rows(_manifest(intercept=3.5), [row])[0]

    assert prediction["predictedMargin"] == pytest.approx(3.5)
    assert prediction["predictedHomeWin"] == 1
    assert prediction["predictedWinner"] == "Home"
    assert "winProbability" not in prediction


def test_immutable_json_refuses_overwrite(tmp_path):
    path = tmp_path / "frozen.json"
    write_immutable_json(path, {"first": True})
    with pytest.raises(FileExistsError):
        write_immutable_json(path, {"second": True})
