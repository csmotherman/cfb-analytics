import pandas as pd


def build_passing_matchups(
    plays_df: pd.DataFrame,
    drives_df: pd.DataFrame,
    season: int = 2025,
) -> pd.DataFrame:

    # -----------------------------------------------------
    # Regular Season Only (Weeks 1-14)
    # -----------------------------------------------------

    plays = plays_df[
        (plays_df["season"] == season)
        & (plays_df["week"] <= 14)
        & (plays_df["isPass"])
    ].copy()

    drives = drives_df.copy()

    # -----------------------------------------------------
    # Home / Away
    # -----------------------------------------------------

    home_lookup = (
        drives[
            [
                "gameId",
                "offense",
                "isHomeOffense",
            ]
        ]
        .drop_duplicates()
        .assign(
            homeAway=lambda x: x["isHomeOffense"].map(
                {
                    True: "Home",
                    False: "Away",
                }
            )
        )
        .drop(columns="isHomeOffense")
    )

    # -----------------------------------------------------
    # Aggregate Passing
    # -----------------------------------------------------

    passing = (
        plays
        .groupby(
            [
                "season",
                "week",
                "gameId",
                "offense",
                "defense",
            ],
            as_index=False,
        )
        .agg(
            offenseConference=("offenseConference", "first"),
            defenseConference=("defenseConference", "first"),

            PassAttempts=("isPass", "sum"),

            PassSuccesses=("isSuccess", "sum"),

            PassYards=("yardsGained", "sum"),

            YardsPerAttempt=("yardsGained", "mean"),

            PassPPA=("ppa", "sum"),

            PPAPerDropback=("ppa", "mean"),

            ExplosivePasses=("isExplosive", "sum"),

            ExplosivePassRate=("isExplosive", "mean"),

            SacksAllowed=("playType", lambda x: (x == "Sack").sum()),

            InterceptionsThrown=(
                "isTurnover",
                "sum",
            ),
        )
    )
    passing["PassSuccessRate"] = (
        passing["PassSuccesses"]
        / passing["PassAttempts"]
        * 100
    )
    # -----------------------------------------------------
    # Convert Rates
    # -----------------------------------------------------

    rate_cols = [
        "PassSuccessRate",
        "ExplosivePassRate",
    ]

    passing[rate_cols] *= 100

    # -----------------------------------------------------
    # Merge Home/Away
    # -----------------------------------------------------

    passing = passing.merge(
        home_lookup,
        on=[
            "gameId",
            "offense",
        ],
        how="left",
    )

    # -----------------------------------------------------
    # Order
    # -----------------------------------------------------

    cols = [
        "season",
        "week",
        "gameId",

        "offense",
        "defense",

        "offenseConference",
        "defenseConference",

        "homeAway",

        "PassPlays",
        "PassSuccesses",
        "PassSuccessRate",

        "PassYards",
        "YardsPerAttempt",

        "PassPPA",
        "PPAPerDropback",

        "ExplosivePasses",
        "ExplosivePassRate",

        "SacksAllowed",
        "InterceptionsThrown",
    ]

    passing = passing[cols]

    passing = passing.sort_values(
        [
            "week",
            "offense",
        ]
    ).reset_index(drop=True)

    return passing