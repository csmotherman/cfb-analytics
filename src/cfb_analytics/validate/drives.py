from __future__ import annotations

import pandas as pd
from cfb_analytics.validate.base import ValidationReport

REQUIRED = {"drive_id", "game_id", "offense", "defense", "drive_points"}


def validate_drives(df: pd.DataFrame) -> ValidationReport:
    r = ValidationReport()
    r.require(REQUIRED.issubset(df.columns), f"drives missing columns: {sorted(REQUIRED - set(df.columns))}")
    if not REQUIRED.issubset(df.columns):
        return r
    r.require(df["drive_id"].notna().all(), "drives contain null drive_id")
    r.require(~df["drive_id"].duplicated().any(), "drives contain duplicate drive_id")
    r.require(df["game_id"].notna().all(), "drives contain null game_id")
    r.require((df["offense"] != df["defense"]).fillna(True).all(), "drive has identical offense and defense")
    if "plays" in df:
        r.require(df["plays"].dropna().ge(0).all(), "drive plays contains negative values")
    return r
