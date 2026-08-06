"""Ingest an entire CollegeFootballData season."""

from __future__ import annotations

import time

import pandas as pd

from src.api.schedule import get_schedule
from src.pipeline.ingest_game import ingest_game


def ingest_season(
    season: int,
    season_type: str = "regular",
    force_download: bool = False,
    delay_seconds: float = 0.25,
) -> pd.DataFrame:
    """Ingest every game in a season."""

    schedule = get_schedule(season, season_type)
    results: list[dict] = []

    for index, game in enumerate(schedule.itertuples(index=False), start=1):
        try:
            tables = ingest_game(
                game_id=str(game.game_id),
                season=season,
                force_download=force_download,
            )

            results.append(
                {
                    "season": season,
                    "week": game.week,
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
                    "week": game.week,
                    "game_id": game.game_id,
                    "status": "failed",
                    "plays": 0,
                    "error": str(exc),
                }
            )

        if index < len(schedule) and delay_seconds > 0:
            time.sleep(delay_seconds)

    return pd.DataFrame(results)
