"""Normalize one SportRadar game into relational DataFrames."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.parser.normalize import (
    dataframe_from_rows,
    normalize_object,
)


def parse_game(
    game_json: dict[str, Any],
) -> dict[str, pd.DataFrame]:
    """
    Convert one SportRadar play-by-play response into normalized tables.

    The parser mirrors the JSON structure and does not calculate
    football analytics.

    Returns
    -------
    dict[str, pandas.DataFrame]
        games
        periods
        drives
        plays
        play_statistics
        play_events
        event_players
    """

    if not isinstance(game_json, dict):
        raise TypeError("game_json must be a dictionary")

    game_id = game_json.get("id")

    if not game_id:
        raise ValueError("Game JSON does not contain an id")

    period_rows: list[dict] = []
    drive_rows: list[dict] = []
    play_rows: list[dict] = []
    statistic_rows: list[dict] = []
    event_rows: list[dict] = []
    event_player_rows: list[dict] = []

    # Game: remove periods because periods become their own table.
    game_row = normalize_object(
        game_json,
        remove=("periods",),
    )

    # Rename only the table's primary identifier.
    game_row["game_id"] = game_row.pop("id", game_id)

    for period in game_json.get("periods") or []:
        if not isinstance(period, dict):
            continue

        period_id = period.get("id")

        period_row = normalize_object(
            period,
            remove=("pbp",),
        )

        period_row["period_id"] = period_row.pop(
            "id",
            period_id,
        )
        period_row["game_id"] = game_id

        period_rows.append(period_row)

        for drive_index, drive in enumerate(
            period.get("pbp") or []
        ):
            if not isinstance(drive, dict):
                continue

            drive_id = drive.get("id")

            # Some feeds may include non-drive objects within pbp.
            # Preserve them rather than dropping them.
            if not drive_id:
                drive_id = (
                    f"{game_id}_period_{period_id}_pbp_{drive_index}"
                )

            drive_row = normalize_object(
                drive,
                remove=("events",),
            )

            drive_row["drive_id"] = drive_row.pop(
                "id",
                drive_id,
            )
            drive_row["game_id"] = game_id
            drive_row["period_id"] = period_id

            drive_rows.append(drive_row)

            for play_index, play in enumerate(
                drive.get("events") or []
            ):
                if not isinstance(play, dict):
                    continue

                play_id = play.get("id")

                if not play_id:
                    play_id = (
                        f"{drive_id}_event_{play_index}"
                    )

                play_row = normalize_object(
                    play,
                    remove=("statistics", "details"),
                )

                play_row["play_id"] = play_row.pop(
                    "id",
                    play_id,
                )
                play_row["game_id"] = game_id
                play_row["period_id"] = period_id
                play_row["drive_id"] = drive_id

                play_rows.append(play_row)

                for statistic_index, statistic in enumerate(
                    play.get("statistics") or []
                ):
                    if not isinstance(statistic, dict):
                        continue

                    statistic_row = normalize_object(statistic)

                    statistic_row["statistic_index"] = statistic_index
                    statistic_row["game_id"] = game_id
                    statistic_row["period_id"] = period_id
                    statistic_row["drive_id"] = drive_id
                    statistic_row["play_id"] = play_id

                    statistic_rows.append(statistic_row)

                for detail_index, detail in enumerate(
                    play.get("details") or []
                ):
                    if not isinstance(detail, dict):
                        continue

                    detail_sequence = detail.get(
                        "sequence",
                        detail_index,
                    )

                    event_id = (
                        f"{play_id}_{detail_sequence}_{detail_index}"
                    )

                    event_row = normalize_object(
                        detail,
                        remove=("players",),
                    )

                    event_row["event_id"] = event_id
                    event_row["detail_index"] = detail_index
                    event_row["game_id"] = game_id
                    event_row["period_id"] = period_id
                    event_row["drive_id"] = drive_id
                    event_row["play_id"] = play_id

                    event_rows.append(event_row)

                    for player_index, player in enumerate(
                        detail.get("players") or []
                    ):
                        if not isinstance(player, dict):
                            continue

                        player_row = normalize_object(player)

                        player_row["player_id"] = player_row.pop(
                            "id",
                            player.get("id"),
                        )
                        player_row["event_player_index"] = player_index
                        player_row["event_id"] = event_id
                        player_row["game_id"] = game_id
                        player_row["period_id"] = period_id
                        player_row["drive_id"] = drive_id
                        player_row["play_id"] = play_id

                        event_player_rows.append(player_row)

    return {
        "games": dataframe_from_rows([game_row]),
        "periods": dataframe_from_rows(period_rows),
        "drives": dataframe_from_rows(drive_rows),
        "plays": dataframe_from_rows(play_rows),
        "play_statistics": dataframe_from_rows(statistic_rows),
        "play_events": dataframe_from_rows(event_rows),
        "event_players": dataframe_from_rows(event_player_rows),
    }