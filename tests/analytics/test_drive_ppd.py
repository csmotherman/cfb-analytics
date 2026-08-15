from cfb_analytics.analytics.drive_ppd import (
    DRIVE_PPD_VERSION,
    attach_postgame_residuals,
    build_matchup_ppd,
    build_pregame_ppd_snapshots,
    build_team_game_drive_rows,
    expected_ppd,
    expected_score,
    fit_ppd_ratings,
    orient_matchup_ppd,
    resolved_drive_points,
)


def drive(game, week, offense, defense, start, end, *, status="PASS", possession=True):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game,
        "driveId": f"{game}-{offense}-{start}-{end}",
        "offense": offense,
        "defense": defense,
        "isPossessionDrive": possession,
        "driveValidationStatus": status,
        "startOffenseScore": start,
        "endOffenseScoreObserved": end,
    }


def test_resolved_drive_points_is_conservative():
    assert resolved_drive_points(drive("g", 1, "A", "B", 0, 7)) == 7.0
    assert resolved_drive_points(drive("g", 1, "A", "B", 7, 10)) == 3.0
    assert resolved_drive_points(drive("g", 1, "A", "B", 7, 6)) is None
    assert resolved_drive_points(drive("g", 1, "A", "B", 0, 9)) is None
    assert resolved_drive_points(drive("g", 1, "A", "B", 0, 7, status="REVIEW")) is None
    assert resolved_drive_points(drive("g", 1, "A", "B", 0, 7, possession=False)) is None


def test_team_game_drive_rows_count_resolved_and_unresolved_separately():
    rows = build_team_game_drive_rows([
        drive("g1", 1, "A", "B", 0, 7),
        drive("g1", 1, "A", "B", 7, 7),
        drive("g1", 1, "A", "B", 7, None),
    ])
    assert len(rows) == 1
    row = rows[0]
    assert row["validatedPossessions"] == 3
    assert row["resolvedPointPossessions"] == 2
    assert row["unresolvedPointPossessions"] == 1
    assert row["offensiveDrivePoints"] == 7.0
    assert row["offensivePPD"] == 3.5
    assert row["drivePpdVersion"] == DRIVE_PPD_VERSION


def test_fit_ppd_ratings_direction_and_expected_ppd():
    rows = [
        {"team": "A", "opponent": "B", "offensivePPD": 4.0, "resolvedPointPossessions": 10},
        {"team": "B", "opponent": "A", "offensivePPD": 1.0, "resolvedPointPossessions": 10},
        {"team": "A", "opponent": "C", "offensivePPD": 3.5, "resolvedPointPossessions": 10},
        {"team": "C", "opponent": "A", "offensivePPD": 1.5, "resolvedPointPossessions": 10},
        {"team": "B", "opponent": "C", "offensivePPD": 2.0, "resolvedPointPossessions": 10},
        {"team": "C", "opponent": "B", "offensivePPD": 2.0, "resolvedPointPossessions": 10},
    ]
    fitted = fit_ppd_ratings(rows, shrinkage_possessions=1.0)
    assert fitted["converged"]
    assert fitted["offense"]["A"] > fitted["offense"]["B"]
    assert fitted["defense"]["A"] > fitted["defense"]["B"]
    assert expected_ppd(fitted, "A", "B") > expected_ppd(fitted, "B", "A")


def test_pregame_snapshots_use_only_prior_partitions():
    team_games = [
        {"season": 2025, "seasonType": "regular", "week": 1, "gameId": "g1", "team": "A", "opponent": "B", "offensiveDrivePoints": 28.0, "resolvedPointPossessions": 7, "offensivePPD": 4.0},
        {"season": 2025, "seasonType": "regular", "week": 1, "gameId": "g1", "team": "B", "opponent": "A", "offensiveDrivePoints": 7.0, "resolvedPointPossessions": 7, "offensivePPD": 1.0},
        {"season": 2025, "seasonType": "regular", "week": 2, "gameId": "g2", "team": "A", "opponent": "B", "offensiveDrivePoints": 0.0, "resolvedPointPossessions": 1, "offensivePPD": 0.0},
        {"season": 2025, "seasonType": "regular", "week": 2, "gameId": "g2", "team": "B", "opponent": "A", "offensiveDrivePoints": 0.0, "resolvedPointPossessions": 1, "offensivePPD": 0.0},
    ]
    snapshots = build_pregame_ppd_snapshots(team_games, 2025, shrinkage_possessions=1.0)
    week1 = [r for r in snapshots if r["week"] == 1]
    week2 = [r for r in snapshots if r["week"] == 2]
    assert all(r["gamesPlayedBefore"] == 0 for r in week1)
    assert all(r["ppdLeagueMeanBefore"] is None for r in week1)
    a2 = next(r for r in week2 if r["team"] == "A")
    b2 = next(r for r in week2 if r["team"] == "B")
    assert a2["gamesPlayedBefore"] == 1
    assert b2["gamesPlayedBefore"] == 1
    assert a2["rawOffensivePPDBefore"] == 4.0
    assert b2["rawOffensivePPDBefore"] == 1.0


def test_matchup_orientation_expected_score_and_postgame_isolation():
    snapshots = [
        {
            "season": 2025, "seasonType": "regular", "week": 3, "gameId": "g3",
            "team": "A", "opponent": "B", "gamesPlayedBefore": 2,
            "ppdLeagueMeanBefore": 2.0,
            "opponentAdjustedOffensePPDAboveAverage": 0.5,
            "opponentAdjustedDefensePPDPreventedAboveAverage": 0.4,
        },
        {
            "season": 2025, "seasonType": "regular", "week": 3, "gameId": "g3",
            "team": "B", "opponent": "A", "gamesPlayedBefore": 2,
            "ppdLeagueMeanBefore": 2.0,
            "opponentAdjustedOffensePPDAboveAverage": -0.2,
            "opponentAdjustedDefensePPDPreventedAboveAverage": -0.1,
        },
    ]
    matchups = build_matchup_ppd(snapshots, 2025)
    assert len(matchups) == 1
    oriented = orient_matchup_ppd(matchups[0], "A", "B")
    assert oriented is not None
    assert oriented["homeExpectedOffensivePPD"] == 2.6
    assert oriented["awayExpectedOffensivePPD"] == 1.4
    assert oriented["expectedPPDEdge"] == 1.2
    assert expected_score(oriented["homeExpectedOffensivePPD"], 10.0) == 26.0

    team_games = [
        {"gameId": "g3", "team": "A", "offensivePPD": 3.0},
        {"gameId": "g3", "team": "B", "offensivePPD": 1.0},
    ]
    post = attach_postgame_residuals(matchups, team_games)
    assert post[0]["postgameTargetDiagnostic"] is True
    assert post[0]["team1OffensivePPDAboveExpectation"] == 0.4
    assert all("Actual" not in key and "AboveExpectation" not in key for key in matchups[0])
