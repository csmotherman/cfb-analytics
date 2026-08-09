from __future__ import annotations

import pandas as pd
from cfb_analytics.normalize import coalesce_column, normalize_columns, to_numeric


def clean_games(raw: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(raw)

    aliases = {
        "game_id": ("game_id", "id"),
        "season": ("season",),
        "week": ("week",),
        "season_type": ("season_type",),
        "home_team": ("home_team",),
        "away_team": ("away_team",),
        "home_conference": ("home_conference",),
        "away_conference": ("away_conference",),
        "home_classification": ("home_classification",),
        "away_classification": ("away_classification",),
        "home_points": ("home_points",),
        "away_points": ("away_points",),
        "completed": ("completed",),
    }
    out = pd.DataFrame(index=df.index)
    for target, candidates in aliases.items():
        coalesce_column(df, target, *candidates)
        out[target] = df[target]

    to_numeric(out, ["season", "week", "home_points", "away_points"])
    out["game_id"] = out["game_id"].astype("string")
    out["completed"] = out["completed"].fillna(False).astype(bool)

    home = out["home_classification"].astype("string").str.lower()
    away = out["away_classification"].astype("string").str.lower()
    out["is_fbs_vs_fbs"] = home.str.contains("fbs", na=False) & away.str.contains("fbs", na=False)

    return out.reset_index(drop=True)
