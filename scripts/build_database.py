from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]

DATABASE = ROOT / "database"
DATABASE.mkdir(exist_ok=True)

DB_FILE = DATABASE / "cfb.duckdb"

con = duckdb.connect(str(DB_FILE))

print("=" * 60)
print("BUILDING DUCKDB")
print("=" * 60)

# ============================================================
# RAW TABLES
# ============================================================

print("Creating games table...")

con.execute("""
CREATE OR REPLACE TABLE games AS
SELECT *
FROM read_parquet('data/raw/*/games.parquet');
""")

print("Creating drives table...")

con.execute("""
CREATE OR REPLACE TABLE drives AS
SELECT *
FROM read_parquet('data/raw/*/drives.parquet');
""")

print("Creating plays table...")

con.execute("""
CREATE OR REPLACE TABLE plays AS
SELECT *
FROM read_parquet('data/raw/*/plays.parquet');
""")

# ============================================================
# CLEAN TABLES
# ============================================================

print("Creating plays_clean table...")

con.execute("""
CREATE OR REPLACE TABLE plays_clean AS
SELECT *
FROM read_parquet('data/cleaned/*/plays_clean.parquet');
""")

# ============================================================
# INFORMATION
# ============================================================

print()

for table in [
    "games",
    "drives",
    "plays",
    "plays_clean",
]:

    rows = con.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table:<15} {rows:,}")

con.close()

print()
print(f"Database saved to:\n{DB_FILE}")