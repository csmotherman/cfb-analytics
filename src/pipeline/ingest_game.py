"""End-to-end ingestion for one CollegeFootballData game."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.api.pbp import get_game_pbp
from src.database.duckdb import insert_tables
from src.database.parquet import write_game_tables
from src.parser.parse_game import parse_game
from src.parser.validate import validate_game_tables
from src.utils.config import RAW_DIR


def raw_game_path(
    season: int,
    game_id: str,
) -> Path:
    """Return the raw JSON path for one game."""

    directory = RAW_DIR / str(season)
    directory.mkdir(parents=True, exist_ok=True)

    return directory / f"{game_id}.json"


def save_raw_game(
    game_json: dict[str, Any],
    season: int,
    game_id: str,
) -> Path:
    """Save the original CFBD response bundle without transformation."""

    path = raw_game_path(season, game_id)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            game_json,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return path


def load_raw_game(
    season: int,
    game_id: str,
) -> dict[str, Any]:
    """Load a previously saved raw CFBD response bundle."""

    path = raw_game_path(season, game_id)

    if not path.exists():
        raise FileNotFoundError(
            f"Raw game JSON does not exist: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def ingest_game(
    game_id: str,
    season: int,
    force_download: bool = False,
    write_parquet: bool = True,
    write_duckdb: bool = True,
) -> dict[str, pd.DataFrame]:
    """Download, save, parse, validate, and store one CFBD game."""

    game_id_text = str(game_id)
    path = raw_game_path(season, game_id_text)

    if path.exists() and not force_download:
        game_json = load_raw_game(season, game_id_text)
    else:
        game_json = get_game_pbp(game_id_text)
        save_raw_game(game_json, season, game_id_text)

    returned_game_id = str(game_json.get("id"))

    if returned_game_id != game_id_text:
        raise ValueError(
            f"Requested game {game_id_text}, "
            f"but API returned {returned_game_id}"
        )

    tables = parse_game(game_json)
    validate_game_tables(tables)

    if write_parquet:
        write_game_tables(tables, season, game_id_text)

    if write_duckdb:
        insert_tables(tables)

    return tables
