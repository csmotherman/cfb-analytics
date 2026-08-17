from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cfb_analytics.analytics.publish_beat_the_model_schedule_v5 import (
    MIN_TEAM_STATS_WEEK,
    TEAM_STATS_VERSION,
    build_pregame_team_stats,
)


@dataclass
class _Response:
    payload: Any


class _NoCallClient:
    def __getattr__(self, name: str):
        raise AssertionError(f"unexpected API call: {name}")


class _FakeClient:
    def __init__(self) -> None:
        self.game_weeks: list[int] = []
        self.advanced_args: dict[str, Any] | None = None

    def games(self, season: int, week: int, season_type: str) -> _Response:
        assert season == 2026
        assert season_type == "regular"
        self.game_weeks.append(week)
        payloads = {
            0: [],
            1: [
                {
                    "completed": True,
                    "homeTeam": "Alpha",
                    "awayTeam": "Beta",
                    "homeClassification": "fbs",
                    "awayClassification": "fbs",
                    "homePoints": 31,
                    "awayPoints": 21,
                }
            ],
            2: [
                {
                    "completed": True,
                    "homeTeam": "FCS State",
                    "awayTeam": "Alpha",
                    "homeClassification": "fcs",
                    "awayClassification": "fbs",
                    "homePoints": 10,
                    "awayPoints": 40,
                },
                {
                    "completed": False,
                    "homeTeam": "Beta",
                    "awayTeam": "Gamma",
                    "homeClassification": "fbs",
                    "awayClassification": "fbs",
                    "homePoints": None,
                    "awayPoints": None,
                },
            ],
        }
        return _Response(payloads.get(week, []))

    def team_season_advanced_stats(
        self,
        season: int,
        *,
        start_week: int | None = None,
        end_week: int | None = None,
        exclude_garbage_time: bool = True,
    ) -> _Response:
        self.advanced_args = {
            "season": season,
            "start_week": start_week,
            "end_week": end_week,
            "exclude_garbage_time": exclude_garbage_time,
        }
        return _Response(
            [
                {
                    "season": 2026,
                    "team": "Alpha",
                    "conference": "Test",
                    "offense": {
                        "successRate": 0.51,
                        "ppa": 0.29,
                        "explosiveness": 1.21,
                        "pointsPerOpportunity": 4.8,
                        "plays": 142,
                        "drives": 22,
                    },
                    "defense": {
                        "successRate": 0.37,
                        "ppa": -0.08,
                        "explosiveness": 0.94,
                        "pointsPerOpportunity": 2.9,
                    },
                },
                {
                    "season": 2026,
                    "team": "Beta",
                    "conference": "Test",
                    "offense": {
                        "successRate": 0.43,
                        "ppa": 0.11,
                        "explosiveness": 1.04,
                        "pointsPerOpportunity": 3.7,
                        "plays": 68,
                        "drives": 11,
                    },
                    "defense": {
                        "successRate": 0.46,
                        "ppa": 0.18,
                        "explosiveness": 1.16,
                        "pointsPerOpportunity": 4.1,
                    },
                },
            ]
        )


def test_stats_do_not_exist_before_week_three() -> None:
    assert MIN_TEAM_STATS_WEEK == 3
    assert build_pregame_team_stats(_NoCallClient(), 2026, 1) == {}
    assert build_pregame_team_stats(_NoCallClient(), 2026, 2) == {}


def test_week_three_snapshot_uses_only_weeks_zero_through_two() -> None:
    client = _FakeClient()
    stats = build_pregame_team_stats(client, 2026, 3)

    assert client.game_weeks == [0, 1, 2]
    assert client.advanced_args == {
        "season": 2026,
        "start_week": 0,
        "end_week": 2,
        "exclude_garbage_time": True,
    }

    alpha = stats["Alpha"]
    assert alpha["version"] == TEAM_STATS_VERSION
    assert alpha["throughWeek"] == 2
    assert alpha["games"] == 2
    assert alpha["wins"] == 2
    assert alpha["losses"] == 0
    assert alpha["pointsPerGame"] == 35.5
    assert alpha["pointsAllowedPerGame"] == 15.5
    assert alpha["offenseSuccessRate"] == 0.51
    assert alpha["defenseSuccessRateAllowed"] == 0.37
    assert alpha["offensePPA"] == 0.29
    assert alpha["defensePPAAllowed"] == -0.08
    assert alpha["pointsPerOpportunity"] == 4.8

    beta = stats["Beta"]
    assert beta["games"] == 1
    assert beta["wins"] == 0
    assert beta["losses"] == 1
    assert beta["pointsPerGame"] == 21.0
    assert beta["pointsAllowedPerGame"] == 31.0
