from src.api.download_season import download_season

# ============================================================
# SEASONS TO BUILD
# ============================================================

SEASONS = [
    2023,
    2024,
]

# ============================================================
# BUILD SEASONS
# ============================================================

for season in SEASONS:

    print()
    print("=" * 80)
    print(f"BUILDING {season}")
    print("=" * 80)

    (
        games_df,
        drives_df,
        plays_df,
        plays_clean
    ) = download_season(season)

    print()
    print("-" * 60)
    print(f"{season} SUMMARY")
    print("-" * 60)

    print(f"Games       : {len(games_df):,}")
    print(f"Drives      : {len(drives_df):,}")
    print(f"Raw Plays   : {len(plays_df):,}")
    print(f"Clean Plays : {len(plays_clean):,}")

print()
print("=" * 80)
print("ALL SEASONS COMPLETE")
print("=" * 80)