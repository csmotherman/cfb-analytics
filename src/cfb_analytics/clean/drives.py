from __future__ import annotations

import pandas as pd
from cfb_analytics.normalize import coalesce_column, normalize_columns, to_numeric


def clean_drives(raw: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(raw)
    aliases = {
        "drive_id": ("drive_id", "id"),
        "game_id": ("game_id",),
        "offense": ("offense",),
        "defense": ("defense",),
        "drive_number": ("drive_number",),
        "start_period": ("start_period",),
        "start_yards_to_goal": ("start_yards_to_goal",),
        "end_period": ("end_period",),
        "end_yards_to_goal": ("end_yards_to_goal",),
        "plays": ("plays",),
        "yards": ("yards",),
        "start_offense_score": ("start_offense_score",),
        "end_offense_score": ("end_offense_score",),
        "drive_result": ("drive_result",),
    }
    out = pd.DataFrame(index=df.index)
    for target, candidates in aliases.items():
        coalesce_column(df, target, *candidates)
        out[target] = df[target]

    out["drive_id"] = out["drive_id"].astype("string")
    out["game_id"] = out["game_id"].astype("string")
    to_numeric(out, [
        "drive_number", "start_period", "start_yards_to_goal", "end_period",
        "end_yards_to_goal", "plays", "yards", "start_offense_score", "end_offense_score",
    ])

    out["drive_points"] = out["end_offense_score"] - out["start_offense_score"]
    result = out["drive_result"].fillna("").astype(str).str.lower()
    out["is_scoring_drive"] = out["drive_points"].fillna(0) > 0
    out["is_touchdown_drive"] = out["drive_points"].fillna(0) >= 6
    out["is_turnover_drive"] = result.str.contains("interception|fumble|turnover", regex=True)
    out["is_punt_drive"] = result.str.contains("punt")
    out["is_turnover_on_downs"] = result.str.contains("downs")
    out["is_three_and_out"] = out["is_punt_drive"] & out["plays"].fillna(999).le(3)

    return out.reset_index(drop=True)
