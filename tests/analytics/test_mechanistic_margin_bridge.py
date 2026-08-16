import math

from cfb_analytics.analytics.drive_outcome_model import OUTCOME_CLASSES
from cfb_analytics.analytics.drive_state_research import (
    DEFENSE_QUALITY_FIELDS,
    OFFENSE_QUALITY_FIELDS,
)
from cfb_analytics.analytics.mechanistic_margin_bridge import (
    NEUTRAL_START_CLOCK_SECONDS,
    NEUTRAL_START_YARDS_TO_GOAL,
    expected_points_from_probabilities,
    mechanistic_game_values,
    neutral_drive_row,
)


def _matchup():
    row = {
        "gameId": "g1",
        "team1": "A",
        "team2": "B",
        "team1GamesPlayedBefore": 4,
        "team2GamesPlayedBefore": 5,
    }
    for field in OFFENSE_QUALITY_FIELDS:
        row[f"team1_{field}"] = 0.60
        row[f"team2_{field}"] = 0.40
    for field in DEFENSE_QUALITY_FIELDS:
        row[f"team1_{field}"] = 0.30
        row[f"team2_{field}"] = 0.50
    return row


def test_neutral_drive_row_orients_offense_and_defense_quality():
    row = neutral_drive_row(_matchup(), "A", "B", is_home_offense=True)
    assert row is not None
    assert row["startYardsToGoal"] == NEUTRAL_START_YARDS_TO_GOAL
    assert row["startClockSeconds"] == NEUTRAL_START_CLOCK_SECONDS
    assert row["startScoreMargin"] == 0.0
    assert row["startScoreState"] == "tied"
    assert row["isHomeOffense"] is True
    assert row["offenseGamesPlayedBefore"] == 4
    assert row["defenseGamesPlayedBefore"] == 5
    assert row[f"offense_{OFFENSE_QUALITY_FIELDS[0]}"] == 0.60
    assert row[f"defense_{DEFENSE_QUALITY_FIELDS[0]}"] == 0.50


def test_expected_points_use_football_values_not_raw_score_deltas():
    p = {label: 0.0 for label in OUTCOME_CLASSES}
    p["TOUCHDOWN"] = 0.40
    p["FIELD_GOAL"] = 0.20
    p["PUNT"] = 0.25
    p["RETURN_TOUCHDOWN"] = 0.10
    p["SAFETY"] = 0.05
    probs = [p[label] for label in OUTCOME_CLASSES]

    result = expected_points_from_probabilities(probs)
    assert math.isclose(result["pointsFor"], 0.40 * 7 + 0.20 * 3)
    assert math.isclose(result["pointsAgainst"], 0.10 * 7 + 0.05 * 2)
    assert math.isclose(
        result["netPoints"],
        result["pointsFor"] - result["pointsAgainst"],
    )


def test_game_values_credit_defensive_scores_to_opponent_possessions():
    home_drive = {
        "pointsFor": 2.0,
        "pointsAgainst": 0.2,
        "netPoints": 1.8,
        "totalPoints": 2.2,
    }
    away_drive = {
        "pointsFor": 1.5,
        "pointsAgainst": 0.1,
        "netPoints": 1.4,
        "totalPoints": 1.6,
    }
    result = mechanistic_game_values(home_drive, away_drive, 10.0)
    assert math.isclose(result["mechanisticExpectedHomeScore"], 21.0)
    assert math.isclose(result["mechanisticExpectedAwayScore"], 17.0)
    assert math.isclose(result["mechanisticExpectedMarginHome"], 4.0)
    assert math.isclose(result["mechanisticExpectedTotal"], 38.0)
