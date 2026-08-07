import pandas as pd

from src.utils.io import load_feature


def test_success(season: int = 2025) -> None:
    """
    Validate success feature output.
    """

    success = load_feature(season, "success")

    print("\n==============================")
    print("SUCCESS FEATURE VALIDATION")
    print("==============================")

    # =========================================================
    # Shape
    # =========================================================

    print(f"Rows: {len(success):,}")
    print(f"Columns: {len(success.columns)}")

    # =========================================================
    # Game Counts
    # =========================================================

    rows_per_game = (
        success.groupby("gameId")
        .size()
        .rename("rows")
        .reset_index()
    )

    print(f"Unique games: {len(rows_per_game):,}")

    good_games = rows_per_game[
        rows_per_game["rows"] == 2
    ]

    bad_games = rows_per_game[
        rows_per_game["rows"] != 2
    ]

    print(f"Games with exactly 2 rows: {len(good_games):,}")
    print(f"Games with != 2 rows: {len(bad_games):,}")

    if not bad_games.empty:
        print("\nFirst 10 bad games:")
        print(bad_games.head(10))
    else:
        print("✓ Every game has exactly 2 team rows.")

    # =========================================================
    # Duplicate Team-Game Rows
    # =========================================================

    duplicates = success.duplicated(
        ["gameId", "team"]
    )

    if duplicates.any():
        print(f"✗ {duplicates.sum()} duplicate team-game rows.")
    else:
        print("✓ No duplicate team-game rows.")

    # =========================================================
    # Success Rates
    # =========================================================

    rate_columns = [
        c
        for c in success.columns
        if c.endswith("Rate")
        or c.endswith("RateAllowed")
    ]

    print("\nRate Validation")

    for col in rate_columns:

        bad = success[
            (success[col] < 0)
            | (success[col] > 100)
        ]

        if len(bad):
            print(f"✗ {col}: {len(bad)} invalid values")
        else:
            print(f"✓ {col}")

    # =========================================================
    # Successes <= Attempts
    # =========================================================

    print("\nAttempt Validation")

    checks = [
        ("RushSuccesses", "RushAttempts"),
        ("PassSuccesses", "PassAttempts"),
        ("ThirdDownSuccesses", "ThirdDownAttempts"),
        ("FourthDownSuccesses", "FourthDownAttempts"),
        ("RedZoneSuccesses", "RedZonePlays"),
        ("GoalToGoSuccesses", "GoalToGoPlays"),
        ("SuccessfulPlays", "OffensivePlays"),
    ]

    for successes, attempts in checks:

        if successes not in success.columns:
            print(f"• Skipping {successes} (column not found)")
            continue

        if attempts not in success.columns:
            print(f"• Skipping {attempts} (column not found)")
            continue

        bad = success[
            success[successes] > success[attempts]
        ]

        if len(bad):
            print(f"✗ {successes}: {len(bad)} invalid rows")
        else:
            print(f"✓ {successes}")

    print("\nValidation complete.")


if __name__ == "__main__":
    test_success()