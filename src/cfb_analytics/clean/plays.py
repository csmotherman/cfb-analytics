from __future__ import annotations

import numpy as np
import pandas as pd

from cfb_analytics.config import SETTINGS
from cfb_analytics.normalize import coalesce_column, normalize_columns, to_numeric

RUN_TYPES = {"rush", "rushing touchdown"}
PASS_TYPES = {
    "pass reception", "pass completion", "pass incompletion", "passing touchdown",
    "interception", "pass interception return", "interception return touchdown", "sack",
}
PUNT_TYPES = {"punt", "punt return", "punt return touchdown", "blocked punt", "blocked punt touchdown"}
KICKOFF_TYPES = {"kickoff", "kickoff return (offense)", "kickoff return touchdown"}
FIELD_GOAL_TYPES = {"field goal good", "field goal missed", "blocked field goal", "blocked field goal touchdown", "missed field goal return"}
ADMIN_TYPES = {"timeout", "end period", "end of half", "end of game", "end of regulation"}
TURNOVER_TYPES = {
    "interception", "pass interception return", "interception return touchdown",
    "fumble recovery (opponent)", "fumble return touchdown",
}


def _family(play_type: str) -> str:
    value = (play_type or "").strip().lower()
    if value in RUN_TYPES:
        return "run"
    if value in PASS_TYPES:
        return "pass"
    if value in PUNT_TYPES:
        return "punt"
    if value in KICKOFF_TYPES:
        return "kickoff"
    if value in FIELD_GOAL_TYPES:
        return "field_goal"
    if value == "penalty":
        return "penalty"
    if value in ADMIN_TYPES:
        return "administrative"
    if "fumble" in value:
        return "turnover"
    return "other"


def _clock_parts(value):
    if isinstance(value, dict):
        return value.get("minutes"), value.get("seconds")
    return None, None


def clean_plays(raw: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(raw)

    aliases = {
        "source_play_id": ("id", "play_id"),
        "game_id": ("game_id",),
        "drive_id": ("drive_id",),
        "drive_number": ("drive_number",),
        "play_number": ("play_number",),
        "season": ("season",),
        "week": ("week",),
        "offense": ("offense",),
        "defense": ("defense",),
        "period": ("period",),
        "down": ("down",),
        "distance": ("distance",),
        "yards_to_goal": ("yards_to_goal",),
        "yardline": ("yardline",),
        "play_type": ("play_type",),
        "play_text": ("play_text",),
        "yards_gained": ("yards_gained",),
        "ppa": ("ppa",),
        "scoring": ("scoring",),
        "clock": ("clock",),
    }
    out = pd.DataFrame(index=df.index)
    for target, candidates in aliases.items():
        coalesce_column(df, target, *candidates)
        out[target] = df[target]

    for col in ["game_id", "drive_id", "source_play_id"]:
        out[col] = out[col].astype("string")
    to_numeric(out, ["drive_number", "play_number", "season", "week", "period", "down", "distance", "yards_to_goal", "yards_gained", "ppa"])

    clock_parts = out["clock"].map(_clock_parts)
    out["minutes"] = pd.to_numeric(clock_parts.map(lambda x: x[0]), errors="coerce")
    out["seconds"] = pd.to_numeric(clock_parts.map(lambda x: x[1]), errors="coerce")
    regulation_period = out["period"].clip(lower=1, upper=4)
    out["game_seconds_remaining"] = np.where(
        out["period"].between(1, 4),
        (4 - regulation_period) * 900 + out["minutes"] * 60 + out["seconds"],
        np.nan,
    )

    fallback = out["game_id"].fillna("") + "_" + out["play_number"].astype("Int64").astype("string").fillna("")
    out["play_id"] = out["source_play_id"].where(out["source_play_id"].notna() & out["source_play_id"].ne("<NA>"), fallback)

    out["play_family"] = out["play_type"].fillna("").astype(str).map(_family)
    text = out["play_text"].fillna("").astype(str).str.lower()
    ptype = out["play_type"].fillna("").astype(str).str.lower()

    out["is_run"] = out["play_family"].eq("run")
    out["is_pass"] = out["play_family"].eq("pass")
    out["is_sack"] = ptype.eq("sack")
    out["is_kneel"] = text.str.contains(r"\bkneel(?:s|ed)?\b|quarterback kneel", regex=True)
    out["is_spike"] = text.str.contains(r"\bspike(?:s|d)?\b|spiked the ball", regex=True)
    out["is_punt"] = out["play_family"].eq("punt")
    out["is_kickoff"] = out["play_family"].eq("kickoff")
    out["is_field_goal"] = out["play_family"].eq("field_goal")
    out["is_penalty"] = out["play_family"].eq("penalty")
    out["is_special_teams"] = out["play_family"].isin(["punt", "kickoff", "field_goal"])
    out["is_offensive_play"] = out["is_run"] | out["is_pass"]
    out["is_competitive_offensive_play"] = out["is_offensive_play"] & ~out["is_kneel"] & ~out["is_spike"]
    out["is_turnover"] = ptype.isin(TURNOVER_TYPES)
    out["is_scoring_play"] = out["scoring"].fillna(False).astype(bool)

    out["field_position"] = 100 - out["yards_to_goal"]
    out["is_red_zone"] = out["is_competitive_offensive_play"] & out["yards_to_goal"].between(0, 20, inclusive="both")
    out["is_goal_to_go"] = (
        out["is_competitive_offensive_play"]
        & out["yards_to_goal"].gt(0)
        & out["distance"].gt(0)
        & out["distance"].ge(out["yards_to_goal"])
    )

    valid_down = out["down"].between(1, 4, inclusive="both")
    out["is_standard_down"] = out["is_competitive_offensive_play"] & (
        out["down"].eq(1)
        | (out["down"].eq(2) & out["distance"].le(7))
        | (out["down"].isin([3, 4]) & out["distance"].le(4))
    )
    out["is_passing_down"] = out["is_competitive_offensive_play"] & valid_down & ~out["is_standard_down"]

    required = out["is_competitive_offensive_play"] & valid_down & out["distance"].notna() & out["yards_gained"].notna()
    threshold = np.select(
        [out["down"].eq(1), out["down"].eq(2), out["down"].isin([3, 4])],
        [0.50, 0.70, 1.00],
        default=np.nan,
    )
    out["is_success"] = required & out["yards_gained"].ge(out["distance"] * threshold)
    out["is_explosive"] = (
        (out["is_run"] & out["yards_gained"].ge(SETTINGS.explosive_run_yards))
        | (out["is_pass"] & out["yards_gained"].ge(SETTINGS.explosive_pass_yards))
    ) & out["is_competitive_offensive_play"]
    out["is_negative_play"] = out["is_competitive_offensive_play"] & out["yards_gained"].lt(0)

    columns = [
        "play_id", "source_play_id", "game_id", "drive_id", "drive_number", "play_number",
        "season", "week", "offense", "defense", "period", "minutes", "seconds", "game_seconds_remaining",
        "down", "distance", "yardline", "yards_to_goal", "field_position", "play_type", "play_family",
        "yards_gained", "ppa", "scoring", "play_text", "is_run", "is_pass", "is_sack", "is_kneel", "is_spike",
        "is_punt", "is_kickoff", "is_field_goal", "is_penalty", "is_special_teams", "is_offensive_play",
        "is_competitive_offensive_play", "is_turnover", "is_scoring_play", "is_success", "is_explosive",
        "is_negative_play", "is_red_zone", "is_goal_to_go", "is_standard_down", "is_passing_down",
    ]
    return out[columns].sort_values(["game_id", "drive_number", "play_number"], na_position="last").reset_index(drop=True)
