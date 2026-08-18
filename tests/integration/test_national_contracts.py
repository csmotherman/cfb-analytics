import json
from pathlib import Path

from cfb_analytics.canonical.team_games import build_team_games
from cfb_analytics.canonical.teams import build_season_teams
from cfb_analytics.validation.integrity import IntegrityError, validate_team_games


def test_team_game_enrichment_uses_ids_and_is_symmetric():
    games = [{"id": 1, "season": 2025, "week": 1, "seasonType": "regular", "homeId": 10, "homeTeam": "A", "homeConference": "X", "homeClassification": "fbs", "homePoints": 7, "awayId": 20, "awayTeam": "B", "awayConference": "Y", "awayClassification": "fbs", "awayPoints": 3, "neutralSite": False}]
    derived = [{"season": 2025, "week": 1, "gameId": "1", "team": "A", "opponent": "B"}, {"season": 2025, "week": 1, "gameId": "1", "team": "B", "opponent": "A"}]
    rows = build_team_games(derived, games, build_season_teams(games, 2025))
    assert validate_team_games(rows)["status"] == "PASS"
    assert {(row["team_id"], row["opponent_id"]) for row in rows} == {(10, 20), (20, 10)}


def test_duplicate_team_game_fails_closed():
    row = {"game_id": "1", "team_id": 1, "opponent_id": 2, "points_for": 1, "points_against": 0}
    try:
        validate_team_games([row, row])
    except IntegrityError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate team-game did not fail")

