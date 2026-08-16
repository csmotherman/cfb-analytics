import math

from cfb_analytics.analytics.drive_outcome_model import (
    OUTCOME_CLASSES,
    fit_quality_means,
    global_class_probabilities,
    model_feature_dict,
    multiclass_metrics,
    normalized_outcome_family,
)
from cfb_analytics.analytics.drive_state_research import (
    DEFENSE_QUALITY_FIELDS,
    OFFENSE_QUALITY_FIELDS,
)


def _row(label="TD"):
    row = {
        "targetDriveResult": label,
        "modelOutcomeFamily": normalized_outcome_family(label),
        "startYardsToGoal": 75.0,
        "startClockSeconds": 600,
        "startScoreMargin": -3.0,
        "startScoreState": "trailing",
        "startPeriod": 2,
        "isHomeOffense": True,
        "offenseGamesPlayedBefore": 3,
        "defenseGamesPlayedBefore": 4,
    }
    for field in OFFENSE_QUALITY_FIELDS:
        row[f"offense_{field}"] = 0.5
    for field in DEFENSE_QUALITY_FIELDS:
        row[f"defense_{field}"] = 0.4
    return row


def test_normalized_outcome_family_handles_cross_season_aliases():
    assert normalized_outcome_family("TD") == "TOUCHDOWN"
    assert normalized_outcome_family("RUSHING TD") == "TOUCHDOWN"
    assert normalized_outcome_family("PASSING TD") == "TOUCHDOWN"
    assert normalized_outcome_family("END OF HALF TD") == "TOUCHDOWN"
    assert normalized_outcome_family("FG GOOD") == "FIELD_GOAL"
    assert normalized_outcome_family("FG MISSED") == "MISSED_FIELD_GOAL"
    assert normalized_outcome_family("INT RETURN TOUCH") == "RETURN_TOUCHDOWN"
    assert normalized_outcome_family("Uncategorized") == "OTHER"


def test_quality_means_use_only_finite_training_values():
    a = _row()
    b = _row()
    key = f"offense_{OFFENSE_QUALITY_FIELDS[0]}"
    a[key] = 0.2
    b[key] = None
    means = fit_quality_means([a, b])
    assert math.isclose(means[key], 0.2)


def test_full_features_impute_missing_quality_and_add_indicator_without_targets():
    row = _row()
    key = f"offense_{OFFENSE_QUALITY_FIELDS[0]}"
    row[key] = None
    means = fit_quality_means([_row()])
    features = model_feature_dict(row, means, include_quality=True)
    assert features[key] == means[key]
    assert features[f"{key}_missing"] == 1.0
    assert "targetDriveResult" not in features
    assert "modelOutcomeFamily" not in features
    assert "offense" not in features
    assert "defense" not in features
    assert "gameId" not in features


def test_global_probabilities_sum_to_one_and_cover_every_class():
    rows = [_row("TD"), _row("TD"), _row("FG"), _row("PUNT")]
    probs = global_class_probabilities(rows)
    assert len(probs) == len(OUTCOME_CLASSES)
    assert math.isclose(sum(probs), 1.0)
    assert all(p > 0 for p in probs)


def test_multiclass_metrics_reward_perfect_predictions():
    rows = [_row("TD"), _row("FG")]
    probs = []
    for row in rows:
        p = [0.0] * len(OUTCOME_CLASSES)
        p[OUTCOME_CLASSES.index(row["modelOutcomeFamily"])] = 1.0
        probs.append(p)
    metrics = multiclass_metrics(rows, probs)
    assert metrics["logLoss"] < 1e-9
    assert metrics["brier"] < 1e-9
    assert metrics["accuracy"] == 1.0
