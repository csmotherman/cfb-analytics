from cfb_analytics.analytics.drive_state_research import (
    QUALITY_FIELDS,
    build_drive_row,
    matchup_team_states,
    point_outcome_bucket,
)


def _matchup():
    row = {
        "gameId": "g1",
        "team1": "A",
        "team2": "B",
        "team1GamesPlayedBefore": 3,
        "team2GamesPlayedBefore": 4,
    }
    for field in QUALITY_FIELDS:
        row[f"team1_{field}"] = 0.5
        row[f"team2_{field}"] = 0.4
    return row


def _drive():
    return {
        "season": 2023,
        "seasonType": "regular",
        "week": 5,
        "gameId": "g1",
        "driveId": "d1",
        "driveNumber": 7,
        "offense": "A",
        "defense": "B",
        "isPossessionDrive": True,
        "driveValidationStatus": "PASS",
        "startPeriod": 2,
        "startYardsToGoal": 75,
        "startDown": 1,
        "startDistance": 10,
        "startOffenseScore": 7,
        "startDefenseScore": 10,
        "endOffenseScoreObserved": 10,
    }


def test_matchup_team_states_preserve_team_specific_pregame_values():
    states = matchup_team_states(_matchup())
    assert states["A"]["gamesPlayedBefore"] == 3
    assert states["B"]["gamesPlayedBefore"] == 4
    assert states["A"][QUALITY_FIELDS[0]] == 0.5
    assert states["B"][QUALITY_FIELDS[0]] == 0.4


def test_drive_row_uses_start_state_and_pregame_quality_with_points_as_target():
    row = build_drive_row(_drive(), _matchup())
    assert row is not None
    assert row["startYardsToGoal"] == 75.0
    assert row["startScoreMargin"] == -3.0
    assert row["startScoreState"] == "trailing"
    assert row["targetPoints"] == 3.0
    assert row["targetScored"] == 1
    assert row["targetPointBucket"] == "3"
    assert row["offenseGamesPlayedBefore"] == 3
    assert row["defenseGamesPlayedBefore"] == 4
    assert row[f"offense_{QUALITY_FIELDS[0]}"] == 0.5
    assert row[f"defense_{QUALITY_FIELDS[0]}"] == 0.4
    assert not any(key.startswith("end") for key in row)


def test_invalid_or_unresolved_drive_is_not_research_eligible():
    drive = _drive()
    drive["driveValidationStatus"] = "REVIEW"
    assert build_drive_row(drive, _matchup()) is None


def test_point_outcome_bucket_is_descriptive_not_assumptive():
    assert point_outcome_bucket(0.0) == "0"
    assert point_outcome_bucket(3.0) == "3"
    assert point_outcome_bucket(7.0) == "7"
    assert point_outcome_bucket(2.5) == "other"
    assert point_outcome_bucket(None) == "missing"
