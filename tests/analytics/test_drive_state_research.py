from cfb_analytics.analytics.drive_state_research import (
    DEFENSE_QUALITY_FIELDS,
    OFFENSE_QUALITY_FIELDS,
    build_drive_row,
    drive_outcome_family,
    matchup_team_states,
)


def _matchup():
    row = {
        "gameId": "g1",
        "team1": "A",
        "team2": "B",
        "team1GamesPlayedBefore": 3,
        "team2GamesPlayedBefore": 4,
    }
    for field in OFFENSE_QUALITY_FIELDS + DEFENSE_QUALITY_FIELDS:
        row[f"team1_{field}"] = 0.5
        row[f"team2_{field}"] = 0.4
    return row


def _raw_drive():
    return {
        "gameId": "g1",
        "id": "d1",
        "driveNumber": 7,
        "offense": "A",
        "defense": "B",
        "driveResult": "TD",
        "scoring": True,
        "startPeriod": 2,
        "endPeriod": 2,
        "startTime": {"minutes": 12, "seconds": 37},
        "startYardsToGoal": 75,
        "startOffenseScore": 7,
        "startDefenseScore": 10,
        "isHomeOffense": True,
        # Deliberately absurd score fields: v2 must never turn these into a
        # drive-points target.
        "endOffenseScore": 21,
        "endDefenseScore": 10,
    }


def _derived_drive():
    return {
        "season": 2023,
        "seasonType": "regular",
        "week": 5,
        "gameId": "g1",
        "driveId": "d1",
        "offense": "A",
        "defense": "B",
        "isPossessionDrive": True,
        "driveValidationStatus": "PASS",
    }


def test_matchup_team_states_preserve_team_specific_pregame_values():
    states = matchup_team_states(_matchup())
    assert states["A"]["gamesPlayedBefore"] == 3
    assert states["B"]["gamesPlayedBefore"] == 4
    assert states["A"][OFFENSE_QUALITY_FIELDS[0]] == 0.5
    assert states["B"][DEFENSE_QUALITY_FIELDS[0]] == 0.4


def test_drive_row_uses_raw_start_state_and_categorical_target():
    row = build_drive_row(_raw_drive(), _derived_drive(), _matchup())
    assert row is not None
    assert row["startYardsToGoal"] == 75.0
    assert row["startClockSeconds"] == 12 * 60 + 37
    assert row["startScoreMargin"] == -3.0
    assert row["startScoreState"] == "trailing"
    assert row["targetDriveResult"] == "TD"
    assert row["targetOutcomeFamily"] == "TOUCHDOWN"
    assert row["targetOffensiveScore"] == 1
    assert row["targetOpponentScore"] == 0
    assert row["offenseGamesPlayedBefore"] == 3
    assert row["defenseGamesPlayedBefore"] == 4
    assert row[f"offense_{OFFENSE_QUALITY_FIELDS[0]}"] == 0.5
    assert row[f"defense_{DEFENSE_QUALITY_FIELDS[0]}"] == 0.4
    assert "targetPoints" not in row
    assert "startDown" not in row
    assert "startDistance" not in row
    assert not any(key.startswith("end") for key in row)


def test_invalid_or_unresolved_derived_drive_is_not_research_eligible():
    derived = _derived_drive()
    derived["driveValidationStatus"] = "REVIEW"
    assert build_drive_row(_raw_drive(), derived, _matchup()) is None


def test_raw_and_derived_ownership_must_agree():
    raw = _raw_drive()
    raw["offense"] = "B"
    raw["defense"] = "A"
    assert build_drive_row(raw, _derived_drive(), _matchup()) is None


def test_overtime_is_excluded_by_default_but_can_be_requested():
    raw = _raw_drive()
    raw["startPeriod"] = 5
    raw["endPeriod"] = 5
    assert build_drive_row(raw, _derived_drive(), _matchup()) is None

    row = build_drive_row(raw, _derived_drive(), _matchup(), include_overtime=True)
    assert row is not None
    assert row["overtime"] is True


def test_drive_outcome_family_collapses_only_semantically_related_results():
    assert drive_outcome_family("TD") == "TOUCHDOWN"
    assert drive_outcome_family("FG") == "FIELD_GOAL"
    assert drive_outcome_family("INT") == "TURNOVER"
    assert drive_outcome_family("FUMBLE") == "TURNOVER"
    assert drive_outcome_family("MISSED FG") == "MISSED_FIELD_GOAL"
    assert drive_outcome_family("BLOCKED FG") == "MISSED_FIELD_GOAL"
    assert drive_outcome_family("INT TD") == "RETURN_TOUCHDOWN"
    assert drive_outcome_family("PUNT RETURN TD") == "RETURN_TOUCHDOWN"
    assert drive_outcome_family("SF") == "SAFETY"
    assert drive_outcome_family("END OF HALF") == "PERIOD_END"
    assert drive_outcome_family("Uncategorized") == "OTHER"
