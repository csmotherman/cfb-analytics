from cfb_analytics.analytics.drive_outcome_model import (
    OUTCOME_CLASSES,
    normalized_outcome_family,
    semantic_rows,
)


def test_other_is_preserved_but_not_a_modeled_football_class():
    assert "OTHER" not in OUTCOME_CLASSES
    rows = [
        {"modelOutcomeFamily": normalized_outcome_family("TD")},
        {"modelOutcomeFamily": normalized_outcome_family("Uncategorized")},
        {"modelOutcomeFamily": normalized_outcome_family("FG")},
    ]
    kept = semantic_rows(rows)
    assert [row["modelOutcomeFamily"] for row in kept] == ["TOUCHDOWN", "FIELD_GOAL"]
