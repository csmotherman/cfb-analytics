import pandas as pd

# -----------------------------------------------------------------------------
# Columns included in the canonical game lookup.
# Add additional game-level metadata here as needed.
# -----------------------------------------------------------------------------

GAME_LOOKUP_COLUMNS = [
    "id",
    "season",
    "week",
    "homeTeam",
    "awayTeam",
    "homeConference",
    "awayConference",
]


# -----------------------------------------------------------------------------
# Lookup Builders
# -----------------------------------------------------------------------------

def build_game_lookup(games_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the canonical game lookup used by every feature builder.

    Returns
    -------
    pd.DataFrame
        One row per game containing game metadata.
    """

    lookup = (
        games_df[GAME_LOOKUP_COLUMNS]
        .rename(columns={"id": "gameId"})
        .sort_values(["season", "week", "gameId"])
        .reset_index(drop=True)
    )

    return lookup


# -----------------------------------------------------------------------------
# Merge Helpers
# -----------------------------------------------------------------------------

def attach_game_info(
    df: pd.DataFrame,
    games_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge game metadata onto any dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing:
            - gameId
            - season
            - week

    games_df : pd.DataFrame
        Raw games dataframe.

    Returns
    -------
    pd.DataFrame
        Original dataframe with game metadata attached.
    """

    lookup = build_game_lookup(games_df)

    return df.merge(
        lookup,
        on="gameId",
        how="left",
        validate="many_to_one",
    )


# -----------------------------------------------------------------------------
# Team Helpers
# -----------------------------------------------------------------------------

def get_home_team(game_id, games_df):
    """
    Return the home team for a game.
    """
    return games_df.loc[
        games_df["id"] == game_id,
        "homeTeam",
    ].iat[0]


def get_away_team(game_id, games_df):
    """
    Return the away team for a game.
    """
    return games_df.loc[
        games_df["id"] == game_id,
        "awayTeam",
    ].iat[0]


def get_opponent(team: str, game_row: pd.Series) -> str:
    """
    Return the opponent for a team in a game.
    """

    if team == game_row["homeTeam"]:
        return game_row["awayTeam"]

    if team == game_row["awayTeam"]:
        return game_row["homeTeam"]

    raise ValueError(f"{team} is not a participant in this game.")


def is_home(team: str, game_row: pd.Series) -> bool:
    """
    Return True if the team is the home team.
    """
    return team == game_row["homeTeam"]


def team_in_game(team: str, game_row: pd.Series) -> bool:
    """
    Return True if the team participated in the game.
    """
    return team in (game_row["homeTeam"], game_row["awayTeam"])


def add_home_indicator(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add an 'isHome' boolean column.

    Expects:
        - team
        - homeTeam
    """

    df = df.copy()
    df["isHome"] = df["team"] == df["homeTeam"]

    return df