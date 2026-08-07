"""
Run Success Rate feature generation.
"""

from src.features.success import build_success_features
from src.utils.io import (
    load_raw,
    load_clean,
    save_feature,
)


def run(season: int) -> None:
    """
    Build and save success features for a season.
    """

    print(f"\nBuilding Success Features ({season})...")

    # ========================================================
    # LOAD DATA
    # ========================================================

    games = load_raw(season, "games")
    plays = load_clean(season, "plays_clean")

    # ========================================================
    # BUILD FEATURES
    # ========================================================

    success = build_success_features(
        pbp_df=plays,
        games_df=games,
    )

    # ========================================================
    # SAVE
    # ========================================================

    save_feature(
        success,
        season,
        "success",
    )

    print(f"Built {len(success):,} team-game rows.")


if __name__ == "__main__":

    run(2025)