from pathlib import Path

import pandas as pd

from config.config import (
    RAW_DIR,
    CLEAN_DIR,
    FEATURE_DIR,
    SAVE_FORMAT
)


# ============================================================
# INTERNAL
# ============================================================

def _get_path(base_dir: Path, season: int, name: str) -> Path:
    """
    Build the full file path.
    """

    season_dir = base_dir / str(season)
    season_dir.mkdir(parents=True, exist_ok=True)

    return season_dir / f"{name}.{SAVE_FORMAT}"


# ============================================================
# RAW
# ============================================================

def save_raw(df: pd.DataFrame, season: int, name: str) -> None:
    """
    Save raw dataframe.
    """

    path = _get_path(RAW_DIR, season, name)

    df.to_parquet(path, index=False)

    print(f"Saved: {path}")


def load_raw(season: int, name: str) -> pd.DataFrame:
    """
    Load raw dataframe.
    """

    path = _get_path(RAW_DIR, season, name)

    return pd.read_parquet(path)


# ============================================================
# CLEANED
# ============================================================

def save_clean(df: pd.DataFrame, season: int, name: str) -> None:
    """
    Save cleaned dataframe.
    """

    path = _get_path(CLEAN_DIR, season, name)

    df.to_parquet(path, index=False)

    print(f"Saved: {path}")


def load_clean(season: int, name: str) -> pd.DataFrame:
    """
    Load cleaned dataframe.
    """

    path = _get_path(CLEAN_DIR, season, name)

    return pd.read_parquet(path)


# ============================================================
# FEATURES
# ============================================================

def save_feature(df: pd.DataFrame, season: int, name: str) -> None:
    """
    Save feature dataframe.
    """

    path = _get_path(FEATURE_DIR, season, name)

    df.to_parquet(path, index=False)

    print(f"Saved: {path}")


def load_feature(season: int, name: str) -> pd.DataFrame:
    """
    Load feature dataframe.
    """

    path = _get_path(FEATURE_DIR, season, name)

    return pd.read_parquet(path)
def raw_exists(season: int, name: str) -> bool:
    return _get_path(RAW_DIR, season, name).exists()


def clean_exists(season: int, name: str) -> bool:
    return _get_path(CLEAN_DIR, season, name).exists()


def feature_exists(season: int, name: str) -> bool:
    return _get_path(FEATURE_DIR, season, name).exists()