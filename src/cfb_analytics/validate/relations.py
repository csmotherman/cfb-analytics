from __future__ import annotations

import pandas as pd
from cfb_analytics.validate.base import ValidationReport


def validate_relations(games: pd.DataFrame, drives: pd.DataFrame, plays: pd.DataFrame) -> ValidationReport:
    r = ValidationReport()
    game_ids = set(games["game_id"].dropna().astype(str))
    drive_ids = set(drives["drive_id"].dropna().astype(str))

    missing_drive_games = ~drives["game_id"].astype(str).isin(game_ids)
    r.require(not missing_drive_games.any(), f"{int(missing_drive_games.sum())} drives reference unknown games")

    missing_play_games = ~plays["game_id"].astype(str).isin(game_ids)
    r.require(not missing_play_games.any(), f"{int(missing_play_games.sum())} plays reference unknown games")

    play_drive = plays["drive_id"].notna() & ~plays["drive_id"].astype(str).isin(drive_ids)
    r.warn(not play_drive.any(), f"{int(play_drive.sum())} plays reference drive IDs absent from drive data")

    return r
