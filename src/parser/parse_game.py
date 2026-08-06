"""Normalize one CFBD game bundle into relational DataFrames."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.parser.normalize import dataframe_from_rows, normalize_object


def _period_id(game_id: str, period: Any) -> str:
    return f"{game_id}_period_{period}"


def parse_game(
    game_json: dict[str, Any],
) -> dict[str, pd.DataFrame]:
    """Convert one CFBD game, drive, and play bundle into project tables."""

    if not isinstance(game_json, dict):
        raise TypeError("game_json must be a dictionary")

    game_id = str(game_json.get("id") or "").strip()
    game = game_json.get("game")
    drives = game_json.get("drives") or []
    plays = game_json.get("plays") or []

    if not game_id:
        raise ValueError("Game JSON does not contain an id")
    if not isinstance(game, dict):
        raise TypeError("game_json['game'] must be a dictionary")
    if not isinstance(drives, list) or not isinstance(plays, list):
        raise TypeError("game_json drives and plays must be lists")

    game_row = normalize_object(game)
    game_row["game_id"] = str(game_row.pop("id", game_id))

    period_values: set[Any] = set()
    for play in plays:
        if isinstance(play, dict) and play.get("period") is not None:
            period_values.add(play.get("period"))
    for drive in drives:
        if not isinstance(drive, dict):
            continue
        for key in ("startPeriod", "endPeriod"):
            if drive.get(key) is not None:
                period_values.add(drive.get(key))

    period_rows = [
        {
            "game_id": game_id,
            "period_id": _period_id(game_id, period),
            "period": period,
        }
        for period in sorted(period_values, key=lambda value: int(value))
    ]

    drive_rows: list[dict[str, Any]] = []
    for drive in drives:
        if not isinstance(drive, dict):
            continue

        row = normalize_object(drive)
        drive_id = str(row.pop("id", "")).strip()
        if not drive_id:
            continue

        start_period = row.get("startPeriod")
        row["drive_id"] = drive_id
        row["game_id"] = game_id
        row["period_id"] = _period_id(game_id, start_period)
        drive_rows.append(row)

    play_rows: list[dict[str, Any]] = []
    for play_index, play in enumerate(plays):
        if not isinstance(play, dict):
            continue

        row = normalize_object(play)
        play_id = str(row.pop("id", "")).strip()
        if not play_id:
            play_id = f"{game_id}_play_{play_index}"

        period = row.get("period")
        drive_id = row.pop("driveId", None)

        row["play_id"] = play_id
        row["game_id"] = game_id
        row["period_id"] = _period_id(game_id, period)
        row["drive_id"] = str(drive_id) if drive_id is not None else None
        row["play_index"] = play_index
        play_rows.append(row)

    return {
        "games": dataframe_from_rows([game_row]),
        "periods": dataframe_from_rows(period_rows),
        "drives": dataframe_from_rows(drive_rows),
        "plays": dataframe_from_rows(play_rows),
        "play_statistics": dataframe_from_rows([]),
        "play_events": dataframe_from_rows([]),
        "event_players": dataframe_from_rows([]),
    }
