import pandas as pd
from config.constants import (
    PLAY_FAMILY,
    SUCCESS_RATE,
    EXPLOSIVE_RUN,
    EXPLOSIVE_PASS
)


# ============================================================
# Clean Play-by-Play
# ============================================================

def clean_plays(plays_df):

    df = plays_df.copy()

    # ============================================================
    # CLOCK
    # ============================================================

    df["minutes"] = df["clock"].apply(lambda x: x["minutes"])
    df["seconds"] = df["clock"].apply(lambda x: x["seconds"])

    df["secondsRemainingQuarter"] = (
        df["minutes"] * 60 +
        df["seconds"]
    )

    df["gameSecondsRemaining"] = (
        (4 - df["period"]) * 900 +
        df["secondsRemainingQuarter"]
    )

    # ============================================================
    # FIELD POSITION
    # ============================================================

    # 0 = Own Goal Line
    # 50 = Midfield
    # 100 = Opponent Goal Line

    df["fieldPosition"] = 100 - df["yardsToGoal"]

    df["fieldSide"] = pd.cut(
        df["fieldPosition"],
        bins=[-1, 49.999, 100],
        labels=["Own", "Opponent"]
    )

    # ============================================================
    # PLAY FAMILY
    # ============================================================

    df["playFamily"] = df["playType"].map(PLAY_FAMILY)

    df["playFamily"] = df["playFamily"].fillna("Other")

    # ============================================================
    # PLAY FLAGS
    # ============================================================

    df["isRun"] = df["playFamily"] == "Run"

    df["isPass"] = df["playFamily"] == "Pass"

    df["isPunt"] = df["playFamily"] == "Punt"

    df["isKickoff"] = df["playFamily"] == "Kickoff"

    df["isFieldGoal"] = df["playFamily"] == "Field Goal"

    df["isPenalty"] = df["playFamily"] == "Penalty"

    df["isSpecialTeams"] = df["playFamily"].isin([
        "Kickoff",
        "Punt",
        "Field Goal"
    ])

    df["isOffensivePlay"] = df["playFamily"].isin([
        "Run",
        "Pass"
    ])

    df["isTurnover"] = df["playType"].isin([
        "Interception",
        "Pass Interception Return",
        "Interception Return Touchdown",
        "Fumble Recovery (Opponent)",
        "Fumble Return Touchdown"
    ])

    df["isScoringPlay"] = df["scoring"]

    df["isRedZone"] = df["yardsToGoal"] <= 20

    df["isGoalToGo"] = (
        (df["yardsToGoal"] <= 10) &
        (df["distance"] <= df["yardsToGoal"])
    )

    # ============================================================
    # DOWN / DISTANCE
    # ============================================================

    df["downCategory"] = df["down"].map({
        1: "1st",
        2: "2nd",
        3: "3rd",
        4: "4th"
    })

    df["distanceCategory"] = pd.cut(
        df["distance"],
        bins=[-1, 2, 6, 10, 100],
        labels=[
            "Short",
            "Medium",
            "Long",
            "Very Long"
        ]
    )

    # ============================================================
    # SUCCESS
    # ============================================================

    df["isSuccess"] = (
        (
            (df["down"] == 1) &
            (df["yardsGained"] >= df["distance"] * SUCCESS_RATE[1])
        )
        |
        (
            (df["down"] == 2) &
            (df["yardsGained"] >= df["distance"] * SUCCESS_RATE[2])
        )
        |
        (
            (df["down"] >= 3) &
            (df["yardsGained"] >= df["distance"])
        )
    )

    # ============================================================
    # EXPLOSIVE
    # ============================================================

    df["isExplosive"] = (
        (
            df["isRun"] &
            (df["yardsGained"] >= EXPLOSIVE_RUN)
        )
        |
        (
            df["isPass"] &
            (df["yardsGained"] >= EXPLOSIVE_PASS)
        )
    )

    # ============================================================
    # NEGATIVE PLAY
    # ============================================================

    df["isNegativePlay"] = df["yardsGained"] < 0

    # ============================================================
    # DRIVE PLAY NUMBER
    # ============================================================

    df["drivePlay"] = (
        df
        .groupby("driveId")
        .cumcount() + 1
    )

    # ============================================================
    # RED ZONE ENTRY
    # ============================================================

    previous = (
        df.groupby("driveId")["yardsToGoal"]
        .shift(1)
        .fillna(99)
    )

    df["enteredRedZone"] = (
        (previous > 20) &
        (df["yardsToGoal"] <= 20)
    )

    # ============================================================
    # UNIQUE PLAY ID
    # ============================================================

    df["playUID"] = (
        df["gameId"].astype(str)
        + "_"
        + df["playNumber"].astype(str)
    )

    # ============================================================
    # REMOVE ADMINISTRATIVE PLAYS
    # ============================================================

    df = df[
        df["playFamily"] != "Administrative"
    ].copy()

    # ============================================================
    # SORT
    # ============================================================

    df = (
        df
        .sort_values(
            [
                "gameId",
                "driveNumber",
                "playNumber"
            ]
        )
        .reset_index(drop=True)
    )

    # ============================================================
    # COLUMN ORDER
    # ============================================================

    cols = [

        "playUID",

        "gameId",
        "driveId",
        "driveNumber",
        "drivePlay",
        "playNumber",

        "season",
        "week",

        "offense",
        "defense",

        "period",
        "minutes",
        "seconds",
        "secondsRemainingQuarter",
        "gameSecondsRemaining",

        "down",
        "downCategory",

        "distance",
        "distanceCategory",

        "yardline",
        "yardsToGoal",
        "fieldPosition",
        "fieldSide",

        "playType",
        "playFamily",

        "yardsGained",
        "ppa",

        "scoring",
        "isScoringPlay",

        "isRun",
        "isPass",
        "isPunt",
        "isKickoff",
        "isFieldGoal",
        "isPenalty",
        "isSpecialTeams",
        "isOffensivePlay",

        "isSuccess",
        "isExplosive",
        "isNegativePlay",
        "isTurnover",

        "isRedZone",
        "enteredRedZone",
        "isGoalToGo",

        "playText"
    ]

    return df[cols]