"""
Project-wide configuration.

Every other module should import paths and constants from here.
"""
from dotenv import load_dotenv

load_dotenv()
from pathlib import Path
import os

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ==========================================================
# Data Directories
# ==========================================================

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw" / "sportradar"

PARQUET_DIR = DATA_DIR / "parquet"

CACHE_DIR = DATA_DIR / "cache"

EXPORT_DIR = DATA_DIR / "exports"

LOG_DIR = DATA_DIR / "logs"

# ==========================================================
# Database
# ==========================================================

DATABASE_DIR = PROJECT_ROOT / "database"

DUCKDB_PATH = DATABASE_DIR / "cfb.duckdb"

BACKUP_DIR = DATABASE_DIR / "backups"

# ==========================================================
# Documentation / Notebooks
# ==========================================================

DOCS_DIR = PROJECT_ROOT / "docs"

NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

# ==========================================================
# API
# ==========================================================

API_KEY = os.getenv("SPORTRADAR_API_KEY", "")

BASE_URL = "https://api.sportradar.com/ncaafb/trial/v7/en"

HEADERS = {
    "accept": "application/json",
    "x-api-key": API_KEY,
}

# ==========================================================
# Ensure Directories Exist
# ==========================================================

for directory in [
    RAW_DIR,
    PARQUET_DIR,
    CACHE_DIR,
    EXPORT_DIR,
    LOG_DIR,
    DATABASE_DIR,
    BACKUP_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)