"""Partitioned Parquet storage."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.config import PARQUET_DIR, TABLE_NAMES


def table_directory(
    table_name: str,
    season: int,
) -> Path:
    """Return a table's season partition directory."""

    if table_name not in TABLE_NAMES:
        raise ValueError(f"Unknown table: {table_name}")

    directory = (
        PARQUET_DIR
        / table_name
        / f"season={season}"
    )

    directory.mkdir(parents=True, exist_ok=True)

    return directory


def game_table_path(
    table_name: str,
    season: int,
    game_id: str,
) -> Path:
    """Return the Parquet path for one game's table."""

    return (
        table_directory(table_name, season)
        / f"{game_id}.parquet"
    )


def write_game_tables(
    tables: dict[str, pd.DataFrame],
    season: int,
    game_id: str,
) -> dict[str, Path]:
    """Write every non-empty normalized table for one game."""

    written: dict[str, Path] = {}

    for table_name in TABLE_NAMES:
        dataframe = tables.get(
            table_name,
            pd.DataFrame(),
        )

        if dataframe.empty:
            continue

        path = game_table_path(
            table_name,
            season,
            game_id,
        )

        dataframe.to_parquet(
            path,
            index=False,
            engine="pyarrow",
        )

        written[table_name] = path

    return written


def read_table(
    table_name: str,
    season: int | None = None,
) -> pd.DataFrame:
    """Read all available Parquet partitions for one table."""

    base = PARQUET_DIR / table_name

    if season is not None:
        pattern = base / f"season={season}" / "*.parquet"
    else:
        pattern = base / "season=*" / "*.parquet"

    files = sorted(pattern.parent.glob(pattern.name))

    if not files:
        return pd.DataFrame()

    return pd.concat(
        [pd.read_parquet(file) for file in files],
        ignore_index=True,
        sort=False,
    )