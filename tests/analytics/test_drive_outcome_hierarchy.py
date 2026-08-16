import math

from cfb_analytics.analytics.drive_outcome_hierarchy import (
    NON_SCORING_CLASSES,
    OFFENSIVE_SCORE_CLASSES,
    OPPONENT_SCORE_CLASSES,
    ROOT_CLASSES,
    combine_branch_probabilities,
    root_outcome,
)
from cfb_analytics.analytics.drive_outcome_model import OUTCOME_CLASSES


def test_root_outcome_maps_every_semantic_class_once():
    expected = {
        "TOUCHDOWN": "OFFENSIVE_SCORE",
        "FIELD_GOAL": "OFFENSIVE_SCORE",
        "PUNT": "NON_SCORING_END",
        "TURNOVER": "NON_SCORING_END",
        "DOWNS": "NON_SCORING_END",
        "MISSED_FIELD_GOAL": "NON_SCORING_END",
        "PERIOD_END": "PERIOD_END",
        "RETURN_TOUCHDOWN": "OPPONENT_SCORE",
        "SAFETY": "OPPONENT_SCORE",
    }
    assert set(expected) == set(OUTCOME_CLASSES)
    assert {label: root_outcome(label) for label in OUTCOME_CLASSES} == expected


def test_hierarchy_contract_partitions_modeled_outcomes():
    leaves = (
        set(OFFENSIVE_SCORE_CLASSES)
        | set(NON_SCORING_CLASSES)
        | set(OPPONENT_SCORE_CLASSES)
        | {"PERIOD_END"}
    )
    assert leaves == set(OUTCOME_CLASSES)
    assert set(ROOT_CLASSES) == {
        "OFFENSIVE_SCORE",
        "NON_SCORING_END",
        "OPPONENT_SCORE",
        "PERIOD_END",
    }


def test_combined_probabilities_sum_to_one_and_preserve_products():
    root = {
        "OFFENSIVE_SCORE": 0.40,
        "NON_SCORING_END": 0.50,
        "OPPONENT_SCORE": 0.02,
        "PERIOD_END": 0.08,
    }
    offense = {"TOUCHDOWN": 0.70, "FIELD_GOAL": 0.30}
    non_scoring = {
        "PUNT": 0.60,
        "TURNOVER": 0.20,
        "DOWNS": 0.15,
        "MISSED_FIELD_GOAL": 0.05,
    }
    opponent = {"RETURN_TOUCHDOWN": 0.90, "SAFETY": 0.10}

    probs = combine_branch_probabilities(root, offense, non_scoring, opponent)
    mapped = dict(zip(OUTCOME_CLASSES, probs))

    assert math.isclose(sum(probs), 1.0)
    assert math.isclose(mapped["TOUCHDOWN"], 0.40 * 0.70)
    assert math.isclose(mapped["FIELD_GOAL"], 0.40 * 0.30)
    assert math.isclose(mapped["PUNT"], 0.50 * 0.60)
    assert math.isclose(mapped["TURNOVER"], 0.50 * 0.20)
    assert math.isclose(mapped["DOWNS"], 0.50 * 0.15)
    assert math.isclose(mapped["MISSED_FIELD_GOAL"], 0.50 * 0.05)
    assert math.isclose(mapped["PERIOD_END"], 0.08)
    assert math.isclose(mapped["RETURN_TOUCHDOWN"], 0.02 * 0.90)
    assert math.isclose(mapped["SAFETY"], 0.02 * 0.10)


def test_root_outcome_rejects_unresolved_target():
    try:
        root_outcome("OTHER")
    except ValueError as exc:
        assert "Unsupported semantic outcome" in str(exc)
    else:
        raise AssertionError("OTHER must not enter the hierarchy")
