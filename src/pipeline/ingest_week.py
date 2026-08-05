"""Ingest one week of a season."""

from __future__ import annotations

import pandas as pd

from src.api.schedule import get_schedule
from src.pipeline.ingest_game import ingest_game


def ingest_week(
    season: int,
    week: int,
    season_type: str = "REG",
    force_download: bool = False,
) -> pd.DataFrame:
    """Ingest every scheduled game in one week."""

    schedule = get_schedule(
        season,
        season_type,
    )

    games = schedule.loc[
        schedule["week"].eq(week)
    ]

    results: list[dict] = []

    for game in games.itertuples(index=False):
        try:
            tables = ingest_game(
                game_id=game.game_id,
                season=season,
                force_download=force_download,
            )

            results.append(
                {
                    "season": season,
                    "week": week,
                    "game_id": game.game_id,
                    "status": "success",
                    "plays": len(tables["plays"]),
                    "error": None,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "season": season,
                    "week": week,
                    "game_id": game.game_id,
                    "status": "failed",
                    "plays": 0,
                    "error": str(exc),
                }
            )

    return pd.DataFrame(results)