"""Project-wide configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "sportradar"
PARQUET_DIR = DATA_DIR / "parquet"
CACHE_DIR = DATA_DIR / "cache"
EXPORT_DIR = DATA_DIR / "exports"
LOG_DIR = DATA_DIR / "logs"

DATABASE_DIR = PROJECT_ROOT / "database"
DUCKDB_PATH = DATABASE_DIR / "cfb.duckdb"
BACKUP_DIR = DATABASE_DIR / "backups"

DOCS_DIR = PROJECT_ROOT / "docs"
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

SPORTRADAR_API_KEY = os.getenv("SPORTRADAR_API_KEY", "").strip()
SPORTRADAR_BASE_URL = (
    "https://api.sportradar.com/ncaafb/trial/v7/en"
)

REQUEST_TIMEOUT_SECONDS = 30

TABLE_NAMES = (
    "games",
    "periods",
    "drives",
    "plays",
    "play_statistics",
    "play_events",
    "event_players",
)

for directory in (
    RAW_DIR,
    PARQUET_DIR,
    CACHE_DIR,
    EXPORT_DIR,
    LOG_DIR,
    DATABASE_DIR,
    BACKUP_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)