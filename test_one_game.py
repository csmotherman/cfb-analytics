from pathlib import Path

from src.pipeline.ingest_game import ingest_game

paths = sorted(
    Path("data/raw/sportradar/2025").glob("*.json")
)

print(f"Testing {len(paths)} games...\n")

failures = []

for path in paths:
    game_id = path.stem

    try:
        tables = ingest_game(
            game_id=game_id,
            season=2025,
            force_download=False,
            write_parquet=False,
            write_duckdb=False,
        )

        spanning = (
            tables["drives"]
            .get("spans_periods", False)
            .sum()
        )

        standalone = (
            tables["plays"]["drive_id"]
            .isna()
            .sum()
        )

        print(
            f"✓ {game_id}"
            f"  drives={len(tables['drives'])}"
            f"  plays={len(tables['plays'])}"
            f"  spanning={spanning}"
            f"  standalone={standalone}"
        )

    except Exception as e:
        failures.append((game_id, str(e)))
        print(f"✗ {game_id}: {e}")

print("\n")

if failures:
    print("Failures:")
    for game_id, error in failures:
        print(game_id, error)
else:
    print("All cached games passed.")