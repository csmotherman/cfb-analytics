from __future__ import annotations

import pandas as pd
from cfb_analytics.validate.base import ValidationReport

REQUIRED = {"game_id", "season", "week", "home_team", "away_team", "is_fbs_vs_fbs"}


def validate_games(df: pd.DataFrame) -> ValidationReport:
    r = ValidationReport()
    r.require(REQUIRED.issubset(df.columns), f"games missing columns: {sorted(REQUIRED - set(df.columns))}")
    if not REQUIRED.issubset(df.columns):
        return r
    r.require(df["game_id"].notna().all(), "games contain null game_id")
    r.require(~df["game_id"].duplicated().any(), "games contain duplicate game_id")
    r.require((df["home_team"] != df["away_team"]).all(), "game has identical home and away team")
    r.require(df["week"].dropna().ge(0).all(), "game week contains negative values")
    return r
