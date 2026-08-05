"""Rebuild DuckDB from saved Parquet game partitions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.database.duckdb import insert_tables
from src.utils.config import DUCKDB_PATH, PARQUET_DIR, TABLE_NAMES


def rebuild_database_from_parquet(
    delete_existing: bool = True,
) -> dict[str, int]:
    """Recreate DuckDB from all normalized Parquet files."""

    if delete_existing and DUCKDB_PATH.exists():
        DUCKDB_PATH.unlink()

    totals = {
        table_name: 0
        for table_name in TABLE_NAMES
    }

    game_ids: set[str] = set()

    games_directory = PARQUET_DIR / "games"

    for file in games_directory.glob(
        "season=*/*.parquet"
    ):
        game_ids.add(file.stem)

    for game_id in sorted(game_ids):
        tables: dict[str, pd.DataFrame] = {}

        for table_name in TABLE_NAMES:
            matches = list(
                (PARQUET_DIR / table_name).glob(
                    f"season=*/{game_id}.parquet"
                )
            )

            if matches:
                tables[table_name] = pd.read_parquet(
                    matches[0]
                )
            else:
                tables[table_name] = pd.DataFrame()

        counts = insert_tables(tables)

        for table_name, count in counts.items():
            totals[table_name] += count

    return totals