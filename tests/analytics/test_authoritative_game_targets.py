import pytest

from cfb_analytics.analytics.authoritative_game_targets import (
    TARGET_SOURCE_VERSION,
    apply_authoritative_targets,
    normalize_authoritative_game,
)
from cfb_analytics.analytics.iterative_ratings import build_srs_model_dataset


def test_normalize_authoritative_cfbd_game_uses_game_endpoint_score():
    game = normalize_authoritative_game(
        {
            "id": 123,
            "homeTeam": "Home",
            "awayTeam": "Away",
            "homePoints": 31,
            "awayPoints": 30,
        }
    )
    assert game == {
        "gameId": "123",
        "homeTeam": "Home",
        "awayTeam": "Away",
        "homeScore": 31.0,
        "awayScore": 30.0,
        "scoreFields": "homePoints/awayPoints",
    }


def test_apply_authoritative_targets_repairs_score_margin_and_winner():
    rows = [
        {
            "season": 2025,
            "seasonType": "regular",
            "week": 1,
            "gameId": "g1",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "target_homeScore": 24.0,
            "target_awayScore": 30.0,
            "target_margin": -6.0,
            "target_homeWin": 0,
        }
    ]
    games = {
        "g1": {
            "gameId": "g1",
            "homeTeam": "Home",
            "awayTeam": "Away",
            "homeScore": 31.0,
            "awayScore": 30.0,
            "scoreFields": "homePoints/awayPoints",
        }
    }

    corrected, report = apply_authoritative_targets(rows, games)
    row = corrected[0]
    assert row["target_homeScore"] == 31.0
    assert row["target_awayScore"] == 30.0
    assert row["target_margin"] == 1.0
    assert row["target_homeWin"] == 1
    assert row["targetSourceVersion"] == TARGET_SOURCE_VERSION
    assert report["changedRows"] == 1


def test_apply_authoritative_targets_fails_closed_on_team_mismatch():
    rows = [{"gameId": "g1", "homeTeam": "A", "awayTeam": "B"}]
    games = {
        "g1": {
            "gameId": "g1",
            "homeTeam": "B",
            "awayTeam": "A",
            "homeScore": 10.0,
            "awayScore": 7.0,
        }
    }
    with pytest.raises(ValueError, match="Home/away mismatch"):
        apply_authoritative_targets(rows, games)


def test_srs_recomputes_from_corrected_margin_not_stale_margin():
    rows = [
        {
            "season": 2025,
            "seasonType": "regular",
            "week": 1,
            "gameId": "g1",
            "homeTeam": "A",
            "awayTeam": "B",
            "target_margin": 7.0,
            "target_homeWin": 1,
        },
        {
            "season": 2025,
            "seasonType": "regular",
            "week": 2,
            "gameId": "g2",
            "homeTeam": "A",
            "awayTeam": "B",
            "target_margin": -3.0,
            "target_homeWin": 0,
        },
    ]
    out = build_srs_model_dataset(rows, 2025)
    week2 = next(row for row in out if row["gameId"] == "g2")
    assert week2["srsGamesBefore"] == 1
    assert week2["srsEdge"] == pytest.approx(7.0)
