import pytest

from cfb_analytics.analytics.prediction_v2_2026_pipeline import (
    _assert_outputs_new,
    validate_as_of,
    validate_history_alignment,
)


def test_history_alignment_requires_exact_two_team_game_sample():
    team_history = [
        {"gameId": "1", "team": "A"},
        {"gameId": "1", "team": "B"},
        {"gameId": "2", "team": "C"},
        {"gameId": "2", "team": "D"},
    ]
    site_history = [{"gameId": "1"}, {"gameId": "2"}]

    result = validate_history_alignment(team_history, site_history)
    assert result["status"] == "PASS"
    assert result["derivedGames"] == 2
    assert result["siteScoreGames"] == 2


def test_history_alignment_rejects_raw_score_only_game():
    team_history = [
        {"gameId": "1", "team": "A"},
        {"gameId": "1", "team": "B"},
    ]
    site_history = [{"gameId": "1"}, {"gameId": "2"}]

    with pytest.raises(ValueError, match="raw-score-only"):
        validate_history_alignment(team_history, site_history)


def test_history_alignment_rejects_derived_only_game():
    team_history = [
        {"gameId": "1", "team": "A"},
        {"gameId": "1", "team": "B"},
        {"gameId": "2", "team": "C"},
        {"gameId": "2", "team": "D"},
    ]
    site_history = [{"gameId": "1"}]

    with pytest.raises(ValueError, match="derived-only"):
        validate_history_alignment(team_history, site_history)


def test_history_alignment_rejects_malformed_team_game_count():
    team_history = [{"gameId": "1", "team": "A"}]
    site_history = []

    with pytest.raises(ValueError, match="non-two-team"):
        validate_history_alignment(team_history, site_history)


def test_as_of_must_be_offset_aware():
    assert validate_as_of("2026-08-29T09:00:00-04:00") == "2026-08-29T09:00:00-04:00"
    with pytest.raises(ValueError, match="offset-aware"):
        validate_as_of("2026-08-29T09:00:00")


def test_pipeline_outputs_are_preflighted_as_immutable(tmp_path):
    feature = tmp_path / "features.json"
    audit = tmp_path / "audit.json"
    predictions = tmp_path / "predictions.json"
    _assert_outputs_new([feature, audit, predictions])

    audit.write_text("{}")
    with pytest.raises(FileExistsError, match="immutable"):
        _assert_outputs_new([feature, audit, predictions])
