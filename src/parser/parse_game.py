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

    SportRadar period-level ``pbp`` arrays may contain:

    - Drives containing an ``events`` list
    - Standalone plays containing ``statistics`` and/or ``details``
    - Clock markers such as TV timeouts

    A drive may also span multiple periods. Repeated drive objects are
    therefore merged by drive_id before normalized tables are created.

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

    period_rows: list[dict[str, Any]] = []
    drive_rows: list[dict[str, Any]] = []
    play_rows: list[dict[str, Any]] = []
    statistic_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    event_player_rows: list[dict[str, Any]] = []

    # Stores one merged record per drive.
    merged_drives: dict[str, dict[str, Any]] = {}

    # Standalone plays found directly in period["pbp"].
    standalone_plays: list[dict[str, Any]] = []

    # Prevent duplicate plays when feeds repeat or update objects.
    seen_play_ids: set[str] = set()

    # ------------------------------------------------------------------
    # Game row
    # ------------------------------------------------------------------

    game_row = normalize_object(
        game_json,
        remove=("periods",),
    )

    game_row["game_id"] = game_row.pop("id", game_id)

    # ------------------------------------------------------------------
    # First pass:
    #   1. Build period rows
    #   2. Classify each PBP object
    #   3. Merge drives that span multiple periods
    #   4. Collect standalone plays
    # ------------------------------------------------------------------

    for period_index, period in enumerate(
        game_json.get("periods") or []
    ):
        if not isinstance(period, dict):
            continue

        period_id = period.get("id")

        if not period_id:
            period_id = f"{game_id}_period_{period_index}"

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

        for pbp_index, item in enumerate(
            period.get("pbp") or []
        ):
            if not isinstance(item, dict):
                continue

            # ----------------------------------------------------------
            # Drive object
            # ----------------------------------------------------------

            if isinstance(item.get("events"), list):
                drive_id = item.get("id")

                if not drive_id:
                    drive_id = (
                        f"{game_id}_period_{period_id}"
                        f"_drive_{pbp_index}"
                    )

                if drive_id not in merged_drives:
                    merged_drives[drive_id] = {
                        "drive_id": drive_id,
                        "first_period_id": period_id,
                        "last_period_id": period_id,
                        "first_period_index": period_index,
                        "last_period_index": period_index,
                        "data": dict(item),
                        "plays": [],
                        "seen_play_ids": set(),
                    }

                merged = merged_drives[drive_id]

                # A continued drive may contain updated totals or status.
                # Prefer later non-null values from the feed.
                for key, value in item.items():
                    if key == "events":
                        continue

                    if value is not None:
                        merged["data"][key] = value

                merged["last_period_id"] = period_id
                merged["last_period_index"] = period_index

                for play_index, play in enumerate(
                    item.get("events") or []
                ):
                    if not isinstance(play, dict):
                        continue

                    play_id = play.get("id")

                    if not play_id:
                        play_id = (
                            f"{drive_id}_period_{period_id}"
                            f"_play_{play_index}"
                        )

                    # Protect against repeated plays in updated feeds.
                    if play_id in merged["seen_play_ids"]:
                        continue

                    merged["seen_play_ids"].add(play_id)

                    merged["plays"].append(
                        {
                            "play": play,
                            "play_id": play_id,
                            "period_id": period_id,
                            "play_index": play_index,
                        }
                    )

                continue

            # ----------------------------------------------------------
            # Standalone play object
            # ----------------------------------------------------------

            is_standalone_play = (
                "statistics" in item
                or "details" in item
                or "play_type" in item
            )

            if is_standalone_play:
                play_id = item.get("id")

                if not play_id:
                    play_id = (
                        f"{game_id}_period_{period_id}"
                        f"_standalone_play_{pbp_index}"
                    )

                standalone_plays.append(
                    {
                        "play": item,
                        "play_id": play_id,
                        "period_id": period_id,
                        "play_index": pbp_index,
                    }
                )

                continue

            # ----------------------------------------------------------
            # Clock marker or unknown period-level object
            # ----------------------------------------------------------
            #
            # Objects such as TV timeouts contain event_type, clock,
            # description, and wall_clock. They are intentionally not
            # written to the drives or plays tables.
            # ----------------------------------------------------------

    # ------------------------------------------------------------------
    # Helper: normalize one play and all child records
    # ------------------------------------------------------------------

    def append_play_records(
        play: dict[str, Any],
        play_id: str,
        period_id: str,
        drive_id: str | None,
        play_index: int,
    ) -> None:
        if play_id in seen_play_ids:
            return

        seen_play_ids.add(play_id)

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
        play_row["play_index"] = play_index

        play_rows.append(play_row)

        # --------------------------------------------------------------
        # Play statistics
        # --------------------------------------------------------------

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

        # --------------------------------------------------------------
        # Play details/events
        # --------------------------------------------------------------

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

            # ----------------------------------------------------------
            # Event players
            # ----------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Second pass: create one row per merged drive and parse its plays
    # ------------------------------------------------------------------

    for drive_id, merged in merged_drives.items():
        drive_data = merged["data"]

        drive_row = normalize_object(
            drive_data,
            remove=(
                "events",
                "statistics",
                "details",
            ),
        )

        drive_row["drive_id"] = drive_row.pop(
            "id",
            drive_id,
        )
        drive_row["game_id"] = game_id

        # period_id remains the first period of the drive so the current
        # validation and schema continue to work.
        drive_row["period_id"] = merged["first_period_id"]

        # These fields explicitly preserve quarter-spanning information.
        drive_row["start_period_id"] = merged["first_period_id"]
        drive_row["end_period_id"] = merged["last_period_id"]
        drive_row["start_period_index"] = merged[
            "first_period_index"
        ]
        drive_row["end_period_index"] = merged[
            "last_period_index"
        ]
        drive_row["spans_periods"] = (
            merged["first_period_id"]
            != merged["last_period_id"]
        )

        drive_rows.append(drive_row)

        for play_record in merged["plays"]:
            append_play_records(
                play=play_record["play"],
                play_id=play_record["play_id"],
                period_id=play_record["period_id"],
                drive_id=drive_id,
                play_index=play_record["play_index"],
            )

    # ------------------------------------------------------------------
    # Parse standalone plays
    # ------------------------------------------------------------------

    for play_record in standalone_plays:
        append_play_records(
            play=play_record["play"],
            play_id=play_record["play_id"],
            period_id=play_record["period_id"],
            drive_id=None,
            play_index=play_record["play_index"],
        )

    # ------------------------------------------------------------------
    # Return normalized relational tables
    # ------------------------------------------------------------------

    return {
        "games": dataframe_from_rows([game_row]),
        "periods": dataframe_from_rows(period_rows),
        "drives": dataframe_from_rows(drive_rows),
        "plays": dataframe_from_rows(play_rows),
        "play_statistics": dataframe_from_rows(statistic_rows),
        "play_events": dataframe_from_rows(event_rows),
        "event_players": dataframe_from_rows(event_player_rows),
    }