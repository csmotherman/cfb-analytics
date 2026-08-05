"""Ingest an entire SportRadar season."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from src.api.schedule import get_schedule
from src.pipeline.ingest_game import ingest_game


def ingest_season(
    season: int,
    season_type: str = "REG",
    force_download: bool = False,
    delay_seconds: float = 1.1,
    results_path: str | Path | None = None,
) -> pd.DataFrame:
    """
    Ingest every game in a season.

    Raw JSON is reused unless force_download=True. Each successful game is
    written to Parquet and DuckDB by ingest_game. Progress is printed as the
    run proceeds, and results may optionally be checkpointed to CSV.
    """

    schedule = (
        get_schedule(season, season_type)
        .dropna(subset=["game_id"])
        .drop_duplicates(subset=["game_id"])
        .sort_values(["week", "scheduled", "game_id"], na_position="last")
        .reset_index(drop=True)
    )

    if schedule.empty:
        return pd.DataFrame(
            columns=[
                "season",
                "season_type",
                "week",
                "game_id",
                "matchup",
                "status",
                "plays",
                "elapsed_seconds",
                "error",
            ]
        )

    checkpoint = Path(results_path) if results_path else None

    if checkpoint:
        checkpoint.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    total_games = len(schedule)

    for index, game in enumerate(
        schedule.itertuples(index=False),
        start=1,
    ):
        away = getattr(game, "away_alias", None) or "AWAY"
        home = getattr(game, "home_alias", None) or "HOME"
        matchup = f"{away} @ {home}"

        print(
            f"[{index}/{total_games}] "
            f"Week {game.week}: {matchup} ({game.game_id})"
        )

        started = time.monotonic()

        try:
            tables = ingest_game(
                game_id=game.game_id,
                season=season,
                force_download=force_download,
                write_parquet=True,
                write_duckdb=True,
            )

            result = {
                "season": season,
                "season_type": season_type.upper(),
                "week": game.week,
                "game_id": game.game_id,
                "matchup": matchup,
                "status": "success",
                "plays": len(tables["plays"]),
                "elapsed_seconds": round(
                    time.monotonic() - started,
                    2,
                ),
                "error": None,
            }

            print(
                f"  Success: {result['plays']} plays "
                f"in {result['elapsed_seconds']}s"
            )

        except Exception as exc:
            result = {
                "season": season,
                "season_type": season_type.upper(),
                "week": game.week,
                "game_id": game.game_id,
                "matchup": matchup,
                "status": "failed",
                "plays": 0,
                "elapsed_seconds": round(
                    time.monotonic() - started,
                    2,
                ),
                "error": str(exc),
            }

            print(f"  Failed: {exc}")

        results.append(result)

        if checkpoint:
            pd.DataFrame(results).to_csv(
                checkpoint,
                index=False,
            )

        successes = sum(
            item["status"] == "success"
            for item in results
        )
        failures = len(results) - successes

        print(
            f"  Progress: success={successes}, failed={failures}\n"
        )

        if index < total_games and delay_seconds > 0:
            time.sleep(delay_seconds)

    return pd.DataFrame(results)
