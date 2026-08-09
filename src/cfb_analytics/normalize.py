from __future__ import annotations

import re
import pandas as pd


def snake_case(name: str) -> str:
    value = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name))
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").lower()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [snake_case(c) for c in out.columns]
    return out


def coalesce_column(df: pd.DataFrame, target: str, *candidates: str, default=pd.NA):
    for candidate in candidates:
        if candidate in df.columns:
            df[target] = df[candidate]
            return
    df[target] = default


def to_numeric(df: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
