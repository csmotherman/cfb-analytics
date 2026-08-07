import numpy as np
import pandas as pd

from src.utils.io import (
    load_raw,
    load_clean,
    save_feature,
)


# ============================================================
# BUILD TEAM GAME STATS
# ============================================================

def build_team_game_stats(season: int) -> pd.DataFrame:

    print(f"\nBuilding team game stats for {season}...")

    # ========================================================
    # LOAD DATA
    # ========================================================

    games = load_raw(season, "games").copy()
    drives = load_raw(season, "drives").copy()
    plays = load_clean(season, "plays_clean").copy()

    # Regular season only
    if "seasonType" in games.columns:
        games = games[
            games["seasonType"].astype(str).str.lower() == "regular"
        ].copy()

    valid_game_ids = set(games["id"])

    drives = drives[
        drives["gameId"].isin(valid_game_ids)
    ].copy()

    plays = plays[
        plays["gameId"].isin(valid_game_ids)
    ].copy()

    # ========================================================
    # BASE TEAM-GAME TABLE
    # ========================================================

    home = pd.DataFrame({
        "season": games["season"],
        "week": games["week"],
        "gameId": games["id"],

        "team": games["homeTeam"],
        "opponent": games["awayTeam"],

        "conference": games["homeConference"],
        "opponentConference": games["awayConference"],

        "homeAway": "Home",

        "pointsFor": games["homePoints"],
        "pointsAgainst": games["awayPoints"],
    })

    away = pd.DataFrame({
        "season": games["season"],
        "week": games["week"],
        "gameId": games["id"],

        "team": games["awayTeam"],
        "opponent": games["homeTeam"],

        "conference": games["awayConference"],
        "opponentConference": games["homeConference"],

        "homeAway": "Away",

        "pointsFor": games["awayPoints"],
        "pointsAgainst": games["homePoints"],
    })

    team_games = pd.concat(
        [home, away],
        ignore_index=True
    )

    team_games["win"] = (
        team_games["pointsFor"]
        > team_games["pointsAgainst"]
    )

    # ========================================================
    # OFFENSIVE PLAYS ONLY
    # ========================================================

    offense_plays = plays[
        plays["isOffensivePlay"]
    ].copy()

    # ========================================================
    # EXTRA PLAY FLAGS
    # ========================================================

    offense_plays["isThirdDown"] = (
        offense_plays["down"] == 3
    )

    offense_plays["isThirdDownConversion"] = (
        offense_plays["isThirdDown"]
        & offense_plays["isSuccess"]
    )

    offense_plays["isFourthDown"] = (
        offense_plays["down"] == 4
    )

    offense_plays["isFourthDownConversion"] = (
        offense_plays["isFourthDown"]
        & offense_plays["isSuccess"]
    )

    offense_plays["isRushSuccess"] = (
        offense_plays["isRun"]
        & offense_plays["isSuccess"]
    )

    offense_plays["isPassSuccess"] = (
        offense_plays["isPass"]
        & offense_plays["isSuccess"]
    )

    offense_plays["isSack"] = (
        offense_plays["playType"] == "Sack"
    )

    offense_plays["isInterception"] = (
        offense_plays["playType"].isin([
            "Interception",
            "Pass Interception Return",
            "Interception Return Touchdown",
        ])
    )

    # ========================================================
    # OFFENSIVE GAME STATS
    # ========================================================

    offense = (
        offense_plays
        .groupby(
            ["gameId", "offense"],
            as_index=False
        )
        .agg(
            OffensivePlays=("playUID", "count"),

            TotalYards=("yardsGained", "sum"),
            YardsPerPlay=("yardsGained", "mean"),

            SuccessfulPlays=("isSuccess", "sum"),
            OffensiveSuccessRate=("isSuccess", "mean"),

            ExplosivePlays=("isExplosive", "sum"),
            ExplosiveRate=("isExplosive", "mean"),

            NegativePlays=("isNegativePlay", "sum"),
            NegativePlayRate=("isNegativePlay", "mean"),

            RushAttempts=("isRun", "sum"),
            RushSuccessfulPlays=("isRushSuccess", "sum"),

            PassPlays=("isPass", "sum"),
            PassSuccessfulPlays=("isPassSuccess", "sum"),

            SacksAllowed=("isSack", "sum"),
            InterceptionsThrown=("isInterception", "sum"),

            TotalPPA=("ppa", lambda x: x.sum(min_count=1)),
            PPAPerPlay=("ppa", "mean"),

            ThirdDownAttempts=("isThirdDown", "sum"),
            ThirdDownConversions=("isThirdDownConversion", "sum"),

            FourthDownAttempts=("isFourthDown", "sum"),
            FourthDownConversions=("isFourthDownConversion", "sum"),

            RedZonePlays=("isRedZone", "sum"),
            GoalToGoPlays=("isGoalToGo", "sum"),
        )
        .rename(
            columns={
                "offense": "team"
            }
        )
    )

    # ========================================================
    # OFFENSIVE RATES
    # ========================================================

    offense["OffensiveSuccessRate"] *= 100
    offense["ExplosiveRate"] *= 100
    offense["NegativePlayRate"] *= 100

    offense["RushSuccessRate"] = np.where(
        offense["RushAttempts"] > 0,
        offense["RushSuccessfulPlays"]
        / offense["RushAttempts"] * 100,
        np.nan,
    )

    offense["PassSuccessRate"] = np.where(
        offense["PassPlays"] > 0,
        offense["PassSuccessfulPlays"]
        / offense["PassPlays"] * 100,
        np.nan,
    )

    offense["ThirdDownRate"] = np.where(
        offense["ThirdDownAttempts"] > 0,
        offense["ThirdDownConversions"]
        / offense["ThirdDownAttempts"] * 100,
        np.nan,
    )

    offense["FourthDownRate"] = np.where(
        offense["FourthDownAttempts"] > 0,
        offense["FourthDownConversions"]
        / offense["FourthDownAttempts"] * 100,
        np.nan,
    )

    # ========================================================
    # DEFENSIVE GAME STATS
    # ========================================================

    defense = (
        offense_plays
        .groupby(
            ["gameId", "defense"],
            as_index=False
        )
        .agg(
            DefensivePlays=("playUID", "count"),

            YardsAllowed=("yardsGained", "sum"),
            YardsPerPlayAllowed=("yardsGained", "mean"),

            SuccessfulPlaysAllowed=("isSuccess", "sum"),
            DefensiveSuccessRateAllowed=("isSuccess", "mean"),

            ExplosivePlaysAllowed=("isExplosive", "sum"),
            ExplosiveRateAllowed=("isExplosive", "mean"),

            NegativePlaysForced=("isNegativePlay", "sum"),

            RushAttemptsFaced=("isRun", "sum"),
            RushSuccessesAllowed=("isRushSuccess", "sum"),

            PassPlaysFaced=("isPass", "sum"),
            PassSuccessesAllowed=("isPassSuccess", "sum"),

            SacksMade=("isSack", "sum"),
            InterceptionsMade=("isInterception", "sum"),

            PPAAllowed=("ppa", lambda x: x.sum(min_count=1)),
            PPAPerPlayAllowed=("ppa", "mean"),

            ThirdDownAttemptsFaced=("isThirdDown", "sum"),
            ThirdDownConversionsAllowed=(
                "isThirdDownConversion",
                "sum"
            ),

            FourthDownAttemptsFaced=("isFourthDown", "sum"),
            FourthDownConversionsAllowed=(
                "isFourthDownConversion",
                "sum"
            ),
        )
        .rename(
            columns={
                "defense": "team"
            }
        )
    )

    # ========================================================
    # DEFENSIVE RATES
    # ========================================================

    defense["DefensiveSuccessRateAllowed"] *= 100
    defense["ExplosiveRateAllowed"] *= 100

    defense["RushSuccessRateAllowed"] = np.where(
        defense["RushAttemptsFaced"] > 0,
        defense["RushSuccessesAllowed"]
        / defense["RushAttemptsFaced"] * 100,
        np.nan,
    )

    defense["PassSuccessRateAllowed"] = np.where(
        defense["PassPlaysFaced"] > 0,
        defense["PassSuccessesAllowed"]
        / defense["PassPlaysFaced"] * 100,
        np.nan,
    )

    defense["ThirdDownAllowed"] = np.where(
        defense["ThirdDownAttemptsFaced"] > 0,
        defense["ThirdDownConversionsAllowed"]
        / defense["ThirdDownAttemptsFaced"] * 100,
        np.nan,
    )

    defense["FourthDownAllowed"] = np.where(
        defense["FourthDownAttemptsFaced"] > 0,
        defense["FourthDownConversionsAllowed"]
        / defense["FourthDownAttemptsFaced"] * 100,
        np.nan,
    )

    # ========================================================
    # DRIVE FLAGS
    # ========================================================

    drives["drivePoints"] = (
        drives["endOffenseScore"]
        - drives["startOffenseScore"]
    )

    drives["StartFieldPosition"] = (
        100 - drives["startYardsToGoal"]
    )

    result = (
        drives["driveResult"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    drives["ScoringDrive"] = (
        drives["drivePoints"] > 0
    )

    drives["TouchdownDrive"] = (
        drives["drivePoints"] >= 6
    )

    drives["PuntDrive"] = (
        result.str.contains("punt")
    )

    drives["TurnoverDrive"] = (
        result.str.contains(
            "interception|fumble",
            regex=True
        )
    )

    drives["TurnoverOnDowns"] = (
        result.str.contains("downs")
    )

    drives["ThreeAndOut"] = (
        (drives["plays"] <= 3)
        & drives["PuntDrive"]
    )

    # ========================================================
    # RED ZONE DRIVE FLAGS FROM PLAY DATA
    # ========================================================

    red_zone_drives = (
        offense_plays
        .groupby(
            ["gameId", "driveId"],
            as_index=False
        )
        .agg(
            RedZoneTrip=("isRedZone", "any")
        )
    )

    drives["id"] = drives["id"].astype(str)
    red_zone_drives["driveId"] = (
        red_zone_drives["driveId"].astype(str)
    )

    drives = drives.merge(
        red_zone_drives,
        left_on=["gameId", "id"],
        right_on=["gameId", "driveId"],
        how="left"
    )

    drives["RedZoneTrip"] = (
        drives["RedZoneTrip"]
        .fillna(False)
        .astype(bool)
    )

    drives["RedZoneTouchdown"] = (
        drives["RedZoneTrip"]
        & drives["TouchdownDrive"]
    )

    # ========================================================
    # OFFENSIVE DRIVE STATS
    # ========================================================

    drive_offense = (
        drives
        .groupby(
            ["gameId", "offense"],
            as_index=False
        )
        .agg(
            Drives=("id", "count"),

            DriveYards=("yards", "sum"),
            AvgYardsPerDrive=("yards", "mean"),

            OffensiveDrivePoints=("drivePoints", "sum"),

            AvgStartingFieldPosition=(
                "StartFieldPosition",
                "mean"
            ),

            ScoringDrives=("ScoringDrive", "sum"),
            TouchdownDrives=("TouchdownDrive", "sum"),

            PuntDrives=("PuntDrive", "sum"),
            ThreeAndOuts=("ThreeAndOut", "sum"),

            TurnoverDrives=("TurnoverDrive", "sum"),
            TurnoverOnDowns=("TurnoverOnDowns", "sum"),

            RedZoneTrips=("RedZoneTrip", "sum"),
            RedZoneTouchdowns=("RedZoneTouchdown", "sum"),
        )
        .rename(
            columns={
                "offense": "team"
            }
        )
    )

    drive_offense["PointsPerDrive"] = np.where(
        drive_offense["Drives"] > 0,
        drive_offense["OffensiveDrivePoints"]
        / drive_offense["Drives"],
        np.nan,
    )

    drive_offense["ScoringDriveRate"] = np.where(
        drive_offense["Drives"] > 0,
        drive_offense["ScoringDrives"]
        / drive_offense["Drives"] * 100,
        np.nan,
    )

    drive_offense["ThreeAndOutRate"] = np.where(
        drive_offense["Drives"] > 0,
        drive_offense["ThreeAndOuts"]
        / drive_offense["Drives"] * 100,
        np.nan,
    )

    drive_offense["TurnoverDriveRate"] = np.where(
        drive_offense["Drives"] > 0,
        drive_offense["TurnoverDrives"]
        / drive_offense["Drives"] * 100,
        np.nan,
    )

    drive_offense["RedZoneTDRate"] = np.where(
        drive_offense["RedZoneTrips"] > 0,
        drive_offense["RedZoneTouchdowns"]
        / drive_offense["RedZoneTrips"] * 100,
        np.nan,
    )

    # ========================================================
    # DEFENSIVE DRIVE STATS
    # ========================================================

    drive_defense = (
        drives
        .groupby(
            ["gameId", "defense"],
            as_index=False
        )
        .agg(
            OpponentDrives=("id", "count"),

            OpponentDriveYards=("yards", "sum"),
            AvgYardsAllowedPerDrive=("yards", "mean"),

            OpponentDrivePoints=("drivePoints", "sum"),

            AvgOpponentStartingFieldPosition=(
                "StartFieldPosition",
                "mean"
            ),

            OpponentScoringDrives=("ScoringDrive", "sum"),
            OpponentTouchdownDrives=("TouchdownDrive", "sum"),

            OpponentThreeAndOuts=("ThreeAndOut", "sum"),

            TakeawayDrives=("TurnoverDrive", "sum"),

            OpponentRedZoneTrips=("RedZoneTrip", "sum"),
            OpponentRedZoneTouchdowns=(
                "RedZoneTouchdown",
                "sum"
            ),
        )
        .rename(
            columns={
                "defense": "team"
            }
        )
    )

    drive_defense["PointsAllowedPerDrive"] = np.where(
        drive_defense["OpponentDrives"] > 0,
        drive_defense["OpponentDrivePoints"]
        / drive_defense["OpponentDrives"],
        np.nan,
    )

    drive_defense["OpponentScoringDriveRate"] = np.where(
        drive_defense["OpponentDrives"] > 0,
        drive_defense["OpponentScoringDrives"]
        / drive_defense["OpponentDrives"] * 100,
        np.nan,
    )

    drive_defense["OpponentThreeAndOutRate"] = np.where(
        drive_defense["OpponentDrives"] > 0,
        drive_defense["OpponentThreeAndOuts"]
        / drive_defense["OpponentDrives"] * 100,
        np.nan,
    )

    drive_defense["TakeawayDriveRate"] = np.where(
        drive_defense["OpponentDrives"] > 0,
        drive_defense["TakeawayDrives"]
        / drive_defense["OpponentDrives"] * 100,
        np.nan,
    )

    drive_defense["OpponentRedZoneTDRate"] = np.where(
        drive_defense["OpponentRedZoneTrips"] > 0,
        drive_defense["OpponentRedZoneTouchdowns"]
        / drive_defense["OpponentRedZoneTrips"] * 100,
        np.nan,
    )

    # ========================================================
    # PENALTIES
    # ========================================================

    penalties = plays[
        plays["isPenalty"]
    ].copy()

    penalty_offense = (
        penalties
        .groupby(
            ["gameId", "offense"],
            as_index=False
        )
        .agg(
            PenaltyPlays=("playUID", "count")
        )
        .rename(
            columns={
                "offense": "team"
            }
        )
    )

    # NOTE:
    # Current cleaned play data does not contain an official
    # penalty-yards field, so PenaltyYards is intentionally
    # not fabricated here.

    # ========================================================
    # MERGE EVERYTHING
    # ========================================================

    team_game_stats = team_games.merge(
        offense,
        on=["gameId", "team"],
        how="left"
    )

    team_game_stats = team_game_stats.merge(
        defense,
        on=["gameId", "team"],
        how="left"
    )

    team_game_stats = team_game_stats.merge(
        drive_offense,
        on=["gameId", "team"],
        how="left"
    )

    team_game_stats = team_game_stats.merge(
        drive_defense,
        on=["gameId", "team"],
        how="left"
    )

    team_game_stats = team_game_stats.merge(
        penalty_offense,
        on=["gameId", "team"],
        how="left"
    )

    # ========================================================
    # TURNOVER MARGIN
    # ========================================================

    team_game_stats["Giveaways"] = (
        team_game_stats["InterceptionsThrown"]
        .fillna(0)
        + team_game_stats["TurnoverDrives"]
        .fillna(0)
    )

    # Avoid counting interceptions twice:
    # TurnoverDrives already contains interception drives.
    # Use drive-level giveaways as canonical turnover count.

    team_game_stats["Giveaways"] = (
        team_game_stats["TurnoverDrives"]
        .fillna(0)
    )

    team_game_stats["Takeaways"] = (
        team_game_stats["TakeawayDrives"]
        .fillna(0)
    )

    team_game_stats["TurnoverMargin"] = (
        team_game_stats["Takeaways"]
        - team_game_stats["Giveaways"]
    )

    # ========================================================
    # FIELD POSITION DIFFERENTIAL
    # ========================================================

    team_game_stats["FieldPositionMargin"] = (
        team_game_stats["AvgStartingFieldPosition"]
        - team_game_stats["AvgOpponentStartingFieldPosition"]
    )

    # ========================================================
    # ROUND
    # ========================================================

    numeric_cols = (
        team_game_stats
        .select_dtypes(include="number")
        .columns
    )

    team_game_stats[numeric_cols] = (
        team_game_stats[numeric_cols]
        .round(3)
    )

    # ========================================================
    # SORT
    # ========================================================

    team_game_stats = (
        team_game_stats
        .sort_values(
            [
                "season",
                "week",
                "gameId",
                "team",
            ]
        )
        .reset_index(drop=True)
    )

    # ========================================================
    # SAVE
    # ========================================================

    save_feature(
        team_game_stats,
        season,
        "team_game_stats"
    )

    print(
        f"Saved {len(team_game_stats):,} team-game rows."
    )

    return team_game_stats