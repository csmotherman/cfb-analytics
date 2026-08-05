"""Ingest and store the complete 2025 regular season."""

from __future__ import annotations

from pathlib import Path

from src.database.duckdb import table_counts
from src.pipeline.ingest_season import ingest_season


def main() -> None:
    results_path = Path("data/logs/ingest_2025_reg.csv")

    results = ingest_season(
        season=2025,
        season_type="REG",
        force_download=False,
        delay_seconds=1.1,
        results_path=results_path,
    )

    status_counts = results["status"].value_counts(dropna=False)
    succeeded = int(status_counts.get("success", 0))
    failed = int(status_counts.get("failed", 0))

    print("\n" + "=" * 72)
    print("2025 REGULAR-SEASON INGEST COMPLETE")
    print(f"Games processed: {len(results)}")
    print(f"Succeeded:       {succeeded}")
    print(f"Failed:          {failed}")
    print(f"Plays loaded:    {int(results['plays'].sum())}")
    print(f"Results log:     {results_path}")

    print("\nDuckDB table counts:")
    print(table_counts().to_string(index=False))

    if failed:
        print("\nFailed games:")
        print(
            results.loc[
                results["status"].eq("failed"),
                ["week", "matchup", "game_id", "error"],
            ].to_string(index=False)
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()
