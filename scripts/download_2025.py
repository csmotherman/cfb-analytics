"""Ingest the 2025 regular season from CollegeFootballData."""

from src.pipeline.ingest_season import ingest_season


def main() -> None:
    results = ingest_season(
        season=2025,
        season_type="regular",
    )

    print(results)
    print("\nStatus counts:")
    print(results["status"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
