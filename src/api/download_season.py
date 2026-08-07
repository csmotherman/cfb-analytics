import pandas as pd
import cfbd
from src.cleaning.clean_plays import clean_plays

from src.utils.io import (
    save_raw,
    save_clean
)
from src.api.get_games import get_games
from src.api.get_drives import get_drives
from src.api.get_plays import get_plays

from src.utils.io import save_raw


def download_season(season: int):

    print("=" * 60)
    print(f"DOWNLOADING {season} SEASON")
    print("=" * 60)

    # ============================================================
    # DOWNLOAD GAMES
    # ============================================================

    print("\nDownloading games...")

    games_df = get_games(season)

    # ============================================================
    # FILTER FBS VS FBS
    # ============================================================

    games_df = games_df[
        (games_df["homeClassification"] == cfbd.DivisionClassification.FBS) &
        (games_df["awayClassification"] == cfbd.DivisionClassification.FBS)
    ].copy()

    game_ids = set(games_df["id"])

    weeks = (
        games_df["week"]
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
        .tolist()
    )

    print(f"FBS Games : {len(games_df):,}")
    print(f"Weeks     : {weeks}")

    # ============================================================
    # DOWNLOAD PLAYS
    # ============================================================

    print("\nDownloading plays...")

    plays_df = get_plays(
        season=season,
        weeks=weeks
    )

    plays_df = plays_df[
        plays_df["gameId"].isin(game_ids)
    ].copy()

    # ============================================================
    # DOWNLOAD DRIVES
    # ============================================================

    print("\nDownloading drives...")

    drives_df = get_drives(season)

    drives_df = drives_df[
        drives_df["gameId"].isin(game_ids)
    ].copy()

    # ============================================================
    # SAVE RAW DATA
    # ============================================================

    print("\nSaving raw datasets...")

    save_raw(games_df, season, "games")
    save_raw(drives_df, season, "drives")
    save_raw(plays_df, season, "plays")
    # ============================================================
    # CLEAN PLAYS
    # ============================================================

    print("\nCleaning plays...")

    plays_clean = clean_plays(plays_df)

    # ============================================================
    # SAVE CLEAN DATA
    # ============================================================

    print("\nSaving cleaned data...")

    save_clean(
        plays_clean,
        season,
        "plays_clean"
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)

    print(f"Games : {len(games_df):,}")
    print(f"Drives: {len(drives_df):,}")
    print(f"Plays : {len(plays_df):,}")

    return (
        games_df,
        drives_df,
        plays_df,
        plays_clean
    )