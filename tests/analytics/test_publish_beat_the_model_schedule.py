import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from cfb_analytics.analytics.publish_beat_the_model_schedule import (
    build_week_rankings,
    market_consensus,
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


def _schedule_game(game_id: str, home: str, away: str) -> dict:
    return {
        "id": game_id,
        "season": 2026,
        "week": 1,
        "homeTeam": home,
        "awayTeam": away,
        "kickoff": None,
        "completed": False,
        "actualHomeScore": None,
        "actualAwayScore": None,
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
            1: [_game("g1", "Beta", "Alpha", home_points=90, away_points=10, completed=True, neutral=True)],
        }
    )

    payload = build_week_rankings(client, tmp_path, season=2026, week=2)
    by_team = {row["team"]: row for row in payload["teams"]}

    assert by_team["Alpha"]["gamesBefore"] == 1
    assert by_team["Beta"]["gamesBefore"] == 1
    assert by_team["Beta"]["rating"] > by_team["Alpha"]["rating"]
    assert payload["historyGames"] == 1


def test_market_consensus_uses_median_spread_and_no_vig_moneyline_probability():
    payload = market_consensus(
        {
            "id": 123,
            "homeTeam": "Alpha",
            "awayTeam": "Beta",
            "lines": [
                {
                    "provider": "Book A",
                    "spread": -2.5,
                    "formattedSpread": "Alpha -2.5",
                    "homeMoneyline": -120,
                    "awayMoneyline": 110,
                },
                {
                    "provider": "Book B",
                    "spread": -3.0,
                    "formattedSpread": "Alpha -3",
                    "homeMoneyline": -130,
                    "awayMoneyline": 115,
                },
            ],
        }
    )

    assert payload is not None
    assert payload["marketProviderCount"] == 2
    assert payload["marketSpread"] == pytest.approx(2.75)
    assert payload["marketFavorite"] == "Alpha"
    assert payload["marketLine"] == "Alpha -2.75"
    assert payload["marketHomeWinProbability"] > 0.5
    assert payload["marketHomeWinProbability"] + payload["marketAwayWinProbability"] == pytest.approx(1.0)


def test_live_official_15_selection_does_not_require_or_rank_by_model_calls():
    rankings = {
        "teams": [
            {"rank": rank, "team": f"T{rank}", "rating": 100 - rank}
            for rank in range(1, 33)
        ]
    }
    schedule = [
        _schedule_game(f"g{index}", f"T{2 * index - 1}", f"T{2 * index}")
        for index in range(1, 17)
    ]

    selected = select_slate(
        schedule,
        rankings,
        existing_current={},
        model_by_id={"g16": {"predictedWinner": "T31", "predictedMargin": 99.0}},
    )

    assert len(selected) == 15
    assert [game["id"] for game in selected] == [f"g{i}" for i in range(1, 16)]
    assert all(game["modelWinner"] is None for game in selected)


def test_market_competitiveness_keeps_a_big_ranked_mismatch_out_of_official_15():
    rankings = {
        "teams": [
            {"rank": rank, "team": f"T{rank}", "rating": 100 - rank}
            for rank in range(1, 51)
        ]
    }
    schedule = []
    market_by_id = {}
    for index in range(15):
        home_rank = 2 + index * 2
        away_rank = home_rank + 1
        gid = f"close-{index}"
        schedule.append(_schedule_game(gid, f"T{home_rank}", f"T{away_rank}"))
        market_by_id[gid] = {
            "marketProviderCount": 3,
            "marketSpread": 3.0,
            "marketFavorite": f"T{home_rank}",
        }

    schedule.append(_schedule_game("mismatch", "T1", "T50"))
    market_by_id["mismatch"] = {
        "marketProviderCount": 3,
        "marketSpread": 24.0,
        "marketFavorite": "T1",
    }

    selected = select_slate(
        schedule,
        rankings,
        existing_current={},
        model_by_id={"mismatch": {"predictedWinner": "T1", "predictedMargin": 30.0}},
        market_by_id=market_by_id,
        market_snapshot_at="2026-08-17T18:48:06+00:00",
    )

    assert len(selected) == 15
    assert "mismatch" not in {game["id"] for game in selected}
    assert all(game["marketSpread"] == 3.0 for game in selected)


def test_open_slate_keeps_frozen_game_ids_when_schedule_is_refreshed():
    rankings = {
        "teams": [
            {"rank": rank, "team": f"T{rank}", "rating": 100 - rank}
            for rank in range(1, 9)
        ]
    }
    schedule = [
        _schedule_game(gid, home, away)
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
            {
                "id": "frozen-a",
                "modelWinner": "T3",
                "marketSource": "cfbd-lines-consensus-v1",
                "marketProviderCount": 2,
                "marketSpread": 2.5,
                "marketFavorite": "T3",
                "marketSnapshotAt": "2026-08-17T18:00:00+00:00",
            },
            {
                "id": "frozen-b",
                "modelWinner": "T5",
                "marketSource": "cfbd-lines-consensus-v1",
                "marketProviderCount": 2,
                "marketSpread": 4.0,
                "marketFavorite": "T5",
                "marketSnapshotAt": "2026-08-17T18:00:00+00:00",
            },
        ],
    }

    selected = select_slate(
        schedule,
        rankings,
        existing_current=existing,
        model_by_id={},
        market_by_id={
            "frozen-a": {"marketProviderCount": 5, "marketSpread": 8.0, "marketFavorite": "T4"},
            "frozen-b": {"marketProviderCount": 5, "marketSpread": 9.0, "marketFavorite": "T6"},
        },
        market_snapshot_at="2026-08-18T18:00:00+00:00",
    )

    assert [game["id"] for game in selected] == ["frozen-a", "frozen-b"]
    assert [game["modelWinner"] for game in selected] == ["T3", "T5"]
    assert [game["marketSpread"] for game in selected] == [2.5, 4.0]
    assert all(game["marketSnapshotAt"] == "2026-08-17T18:00:00+00:00" for game in selected)
