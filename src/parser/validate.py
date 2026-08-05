"""Validation for normalized SportRadar tables."""

from __future__ import annotations

import pandas as pd

from src.parser.normalize import scalar_columns_only
from src.utils.config import TABLE_NAMES


class TableValidationError(ValueError):
    """Raised when parsed tables fail validation."""


REQUIRED_COLUMNS = {
    "games": {"game_id"},
    "periods": {"game_id", "period_id"},
    "drives": {"game_id", "period_id", "drive_id"},
    "plays": {
        "game_id",
        "period_id",
        "drive_id",
        "play_id",
    },
    "play_statistics": {
        "game_id",
        "drive_id",
        "play_id",
    },
    "play_events": {
        "game_id",
        "play_id",
        "event_id",
    },
    "event_players": {
        "game_id",
        "play_id",
        "event_id",
        "player_id",
    },
}


def _validate_required_columns(
    name: str,
    df: pd.DataFrame,
) -> None:
    if df.empty:
        return

    required = REQUIRED_COLUMNS.get(name, set())
    missing = required.difference(df.columns)

    if missing:
        raise TableValidationError(
            f"{name} is missing required columns: {sorted(missing)}"
        )


def _validate_no_nested_values(
    name: str,
    df: pd.DataFrame,
) -> None:
    if df.empty:
        return

    nested = scalar_columns_only(df)

    if nested:
        raise TableValidationError(
            f"{name} still contains nested list/dict columns: {nested}"
        )


def _validate_unique_column(
    name: str,
    df: pd.DataFrame,
    column: str,
) -> None:
    if df.empty or column not in df.columns:
        return

    non_null = df[column].dropna()

    if non_null.duplicated().any():
        duplicates = (
            non_null[non_null.duplicated(keep=False)]
            .astype(str)
            .unique()
            .tolist()
        )

        raise TableValidationError(
            f"{name}.{column} contains duplicates: "
            f"{duplicates[:10]}"
        )


def validate_game_tables(
    tables: dict[str, pd.DataFrame],
) -> None:
    """Validate one parsed game's normalized tables."""

    missing_tables = set(TABLE_NAMES).difference(tables)

    if missing_tables:
        raise TableValidationError(
            f"Missing tables: {sorted(missing_tables)}"
        )

    for name in TABLE_NAMES:
        df = tables[name]

        if not isinstance(df, pd.DataFrame):
            raise TableValidationError(
                f"{name} is not a pandas DataFrame"
            )

        _validate_required_columns(name, df)
        _validate_no_nested_values(name, df)

    if len(tables["games"]) != 1:
        raise TableValidationError(
            "A parsed game must produce exactly one games row"
        )

    _validate_unique_column(
        "games",
        tables["games"],
        "game_id",
    )
    _validate_unique_column(
        "periods",
        tables["periods"],
        "period_id",
    )
    _validate_unique_column(
        "drives",
        tables["drives"],
        "drive_id",
    )
    _validate_unique_column(
        "plays",
        tables["plays"],
        "play_id",
    )
    _validate_unique_column(
        "play_events",
        tables["play_events"],
        "event_id",
    )

    play_ids = set(
        tables["plays"].get("play_id", pd.Series(dtype=str))
        .dropna()
        .astype(str)
    )

    for child_name in (
        "play_statistics",
        "play_events",
        "event_players",
    ):
        child = tables[child_name]

        if child.empty or "play_id" not in child:
            continue

        child_ids = set(
            child["play_id"].dropna().astype(str)
        )

        orphaned = child_ids.difference(play_ids)

        if orphaned:
            raise TableValidationError(
                f"{child_name} contains play IDs absent from plays: "
                f"{sorted(orphaned)[:10]}"
            )