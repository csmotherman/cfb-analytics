from __future__ import annotations

import pandas as pd
from cfb_analytics.validate.base import ValidationReport

REQUIRED = {
    "play_id", "game_id", "drive_id", "play_number", "period", "down", "distance",
    "yards_to_goal", "is_run", "is_pass", "is_offensive_play", "is_competitive_offensive_play",
    "is_success", "is_explosive", "is_red_zone", "is_goal_to_go",
}


def validate_plays(df: pd.DataFrame) -> ValidationReport:
    r = ValidationReport()
    r.require(REQUIRED.issubset(df.columns), f"plays missing columns: {sorted(REQUIRED - set(df.columns))}")
    if not REQUIRED.issubset(df.columns):
        return r

    r.require(df["play_id"].notna().all(), "plays contain null play_id")
    r.require(~df["play_id"].duplicated().any(), "plays contain duplicate play_id")
    r.require(df["game_id"].notna().all(), "plays contain null game_id")
    r.require(~(df["is_run"] & df["is_pass"]).any(), "play cannot be both run and pass")
    r.require((df["is_offensive_play"] == (df["is_run"] | df["is_pass"])).all(), "is_offensive_play does not match run/pass flags")
    r.require((~df["is_success"] | df["is_competitive_offensive_play"]).all(), "non-competitive play marked successful")
    r.require((~df["is_explosive"] | df["is_competitive_offensive_play"]).all(), "non-competitive play marked explosive")
    r.require(df["down"].dropna().between(0, 4).all(), "down outside 0..4")
    r.require(df["distance"].dropna().ge(0).all(), "distance contains negative values")
    r.require(df["yards_to_goal"].dropna().between(0, 100).all(), "yards_to_goal outside 0..100")
    if "seconds" in df:
        r.require(df["seconds"].dropna().between(0, 59).all(), "clock seconds outside 0..59")
    return r
