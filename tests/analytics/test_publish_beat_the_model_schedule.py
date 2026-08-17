import json
from pathlib import Path
from types import SimpleNamespace

from cfb_analytics.analytics.publish_beat_the_model_schedule import (
    build_week_rankings,
    select_slate,
)


class FakeClient:
    def __init__(self, by_week: dict[int, list[dict]]):
        self.by_week = by_week

    def games(self, season: int, week: int, season_type: str):
        assert season == 2026
        assert season_type == "regular"
        return SimpleNamespace(payload=self.by_week.get(week, []))


def _write_week1_seed(root: Path, teams: list[tuple[str, float]]) -> dict:
    rows = [
        {"rank": index, "team": team, "rating": rating, "sourceSeason": 2025}
        for index, (team, rating) in enumerate(teams, start=1)
    ]
    payload = {
        "schemaVersion": 1,
        "version": "beat-the-model-v1",
        "rankingVersion": "btm-site-aware-srs-four-game-carryover-v1",
        "season": 2026,
        "week": 1,
        "sourceSeason": 2025,
        "method": "Week 1 equals the previous season's final site-aware power ratings.",
        "teams": rows,
    }
    path = root / "beat-the-model" / "rankings" / "season=2026" / "week=1.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload))
    return payload


def _game(
    game_id: str,
    home: str,
    away: str,
    *,
    home_points=None,
    away_points=None,
    completed=False,
    neutral=False,
):
    return {
        "id": game_id,
        "homeTeam": home,
        "awayTeam": away,
        "homeClassification": "fbs",
        "awayClassification": "fbs",
        "homePoints": home_points,
        "awayPoints": away_points,
        "completed": completed,
        "neutralSite": neutral,
        "startDate": "2026-09-05T16:00:00.000Z",
    }


def test_week1_rankings_reuse_previous_season_final_seed_exactly(tmp_path):
    expected = _write_week1_seed(tmp_path, [("Alpha", 12.5), ("Beta", 8.0)])
    actual = build_week_rankings(FakeClient({}), tmp_path, season=2026, week=1)

    assert actual["teams"] == expected["teams"]
    assert actual["sourceSeason"] == 2025
    assert actual["week"] == 1


def test_week2_rankings_blend_numeric_seed_with_completed_current_season_games(tmp_path):
    _write_week1_seed(tmp_path, [("Alpha", 20.0), ("Beta", 10.0)])
    client = FakeClient(
        {
            # A large neutral-site result makes the 25% current-season component
            # easy to distinguish from the Week 1 seed in this two-team fixture.
            1: [_game("g1", "Beta", "Alpha", home_points=90, away_points=10, completed=True, neutral=True)],
        }
    )

    payload = build_week_rankings(client, tmp_path, season=2026, week=2)
    by_team = {row["team"]: row for row in payload["teams"]}

    # One game played means 75% previous-season rating and 25% current SRS.
    assert by_team["Alpha"]["gamesBefore"] == 1
    assert by_team["Beta"]["gamesBefore"] == 1
    assert by_team["Beta"]["rating"] > by_team["Alpha"]["rating"]
    assert payload["historyGames"] == 1


def test_live_official_15_selection_does_not_require_or_rank_by_model_calls():
    rankings = {
        "teams": [
            {"rank": rank, "team": f"T{rank}", "rating": 100 - rank}
            for rank in range(1, 33)
        ]
    }
    schedule = [
        {
            "id": f"g{index}",
            "season": 2026,
            "week": 1,
            "homeTeam": f"T{2 * index - 1}",
            "awayTeam": f"T{2 * index}",
            "kickoff": None,
            "completed": False,
            "actualHomeScore": None,
            "actualAwayScore": None,
        }
        for index in range(1, 17)
    ]

    # Give only the lowest-ranked matchup a model call. It still must not jump
    # into the Official 15 because model availability is not a selection input.
    selected = select_slate(
        schedule,
        rankings,
        existing_current={},
        model_by_id={"g16": {"predictedWinner": "T31", "predictedMargin": 99.0}},
    )

    assert len(selected) == 15
    assert [game["id"] for game in selected] == [f"g{i}" for i in range(1, 16)]
    assert all(game["modelWinner"] is None for game in selected)


def test_open_slate_keeps_frozen_game_ids_when_schedule_is_refreshed():
    rankings = {
        "teams": [
            {"rank": rank, "team": f"T{rank}", "rating": 100 - rank}
            for rank in range(1, 9)
        ]
    }
    schedule = [
        {
            "id": gid,
            "season": 2026,
            "week": 1,
            "homeTeam": home,
            "awayTeam": away,
            "kickoff": None,
            "completed": False,
            "actualHomeScore": None,
            "actualAwayScore": None,
        }
        for gid, home, away in (
            ("top", "T1", "T2"),
            ("frozen-a", "T3", "T4"),
            ("frozen-b", "T5", "T6"),
            ("other", "T7", "T8"),
        )
    ]
    existing = {
        "status": "open",
        "games": [
            {"id": "frozen-a", "modelWinner": "T3"},
            {"id": "frozen-b", "modelWinner": "T5"},
        ],
    }

    selected = select_slate(
        schedule,
        rankings,
        existing_current=existing,
        model_by_id={},
    )

    assert [game["id"] for game in selected] == ["frozen-a", "frozen-b"]
    assert [game["modelWinner"] for game in selected] == ["T3", "T5"]
