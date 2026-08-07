import numpy as np
import pandas as pd

from src.utils.game_utils import attach_game_info


def build_success_features(
    pbp_df: pd.DataFrame,
    games_df: pd.DataFrame,
) -> pd.DataFrame:

    # ========================================================
    # VALID OFFENSIVE PLAYS
    # ========================================================
    
    plays = pbp_df[
        pbp_df["isOffensivePlay"]
    ].copy()

    plays["isStandardDown"] = (
            (plays["down"] == 1)
            | ((plays["down"] == 2) & (plays["distance"] <= 7))
            | ((plays["down"] == 3) & (plays["distance"] <= 4))
        )
    
    plays["isPassingDown"] = ~plays["isStandardDown"]
    # ========================================================
    # PLAY FLAGS
    # ========================================================

    plays["RushSuccess"] = (
        plays["isRun"]
        & plays["isSuccess"]
    )

    plays["PassSuccess"] = (
        plays["isPass"]
        & plays["isSuccess"]
    )

    plays["ThirdDownSuccess"] = (
        (plays["down"] == 3)
        & plays["isSuccess"]
    )

    plays["FourthDownSuccess"] = (
        (plays["down"] == 4)
        & plays["isSuccess"]
    )

    plays["StandardDownSuccess"] = (
        plays["isStandardDown"]
        & plays["isSuccess"]
    )

    plays["PassingDownSuccess"] = (
        plays["isPassingDown"]
        & plays["isSuccess"]
    )

    plays["RedZoneSuccess"] = (
        plays["isRedZone"]
        & plays["isSuccess"]
    )

    plays["GoalToGoSuccess"] = (
        plays["isGoalToGo"]
        & plays["isSuccess"]
    )

    # ========================================================
    # OFFENSIVE SUCCESS
    # ========================================================

    offense = (
        plays
        .groupby(
            ["gameId", "offense"],
            as_index=False,
        )
        .agg(
            OffensivePlays=("playUID", "count"),

            SuccessfulPlays=("isSuccess", "sum"),
            OverallSuccessRate=("isSuccess", "mean"),

            RushAttempts=("isRun", "sum"),
            RushSuccesses=("RushSuccess", "sum"),

            PassAttempts=("isPass", "sum"),
            PassSuccesses=("PassSuccess", "sum"),

            StandardDownAttempts=("isStandardDown", "sum"),
            StandardDownSuccesses=("StandardDownSuccess", "sum"),

            PassingDownAttempts=("isPassingDown", "sum"),
            PassingDownSuccesses=("PassingDownSuccess", "sum"),

            ThirdDownAttempts=("down", lambda x: (x == 3).sum()),
            ThirdDownSuccesses=("ThirdDownSuccess", "sum"),

            FourthDownAttempts=("down", lambda x: (x == 4).sum()),
            FourthDownSuccesses=("FourthDownSuccess", "sum"),

            RedZonePlays=("isRedZone", "sum"),
            RedZoneSuccesses=("RedZoneSuccess", "sum"),

            GoalToGoPlays=("isGoalToGo", "sum"),
            GoalToGoSuccesses=("GoalToGoSuccess", "sum"),
        )
        .rename(columns={"offense": "team"})
    )

    # ========================================================
    # SUCCESS RATES
    # ========================================================

    offense["OverallSuccessRate"] *= 100

    offense["RushSuccessRate"] = np.where(
        offense["RushAttempts"] > 0,
        offense["RushSuccesses"] / offense["RushAttempts"] * 100,
        np.nan,
    )

    # ...remaining rates...

    # ========================================================
    # DEFENSIVE MIRROR
    # ========================================================

    defense = (
        offense.rename(
            columns={
                "team": "opponent",
                "OverallSuccessRate": "OverallSuccessRateAllowed",
                "RushSuccessRate": "RushSuccessRateAllowed",
                # etc...
            }
        )
    )

    # ========================================================
    # MERGE
    # ========================================================

    features = offense.merge(
        defense,
        on="gameId",
    )

    features = attach_game_info(
        features,
        games_df,
    )

    return features