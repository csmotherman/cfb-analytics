import pytest

from cfb_analytics.analytics.drive_ppd import (
    DRIVE_PPD_POINTS_FOUNDATION,
    DRIVE_PPD_VERSION,
    adjudicated_drive_points,
    attach_postgame_residuals,
    build_matchup_ppd,
    build_pregame_ppd_snapshots,
    build_team_game_drive_rows,
    expected_ppd,
    expected_score,
    fit_ppd_ratings,
    orient_matchup_ppd,
)


def drive(game, week, offense, defense, drive_id, *, status="PASS", possession=True):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game,
        "driveId": drive_id,
        "offense": offense,
        "defense": defense,
        "isPossessionDrive": possession,
        "driveValidationStatus": status,
    }


def play(game, drive_id, offense, subtype, pid):
    return {
        "gameId": game,
        "driveId": drive_id,
        "offense": offense,
        "eventSubtype": subtype,
        "id": pid,
        "period": 1,
        "clock": {"minutes": 10, "seconds": 0},
    }


def test_adjudicated_drive_points_uses_locked_possession_outcome():
    d = drive("g", 1, "A", "B", "d1")
    fg = [play("g", "d1", "A", "FIELD_GOAL_GOOD", "p1")]
    assert adjudicated_drive_points(d, fg, fg) == 3.0

    empty = [play("g", "d1", "A", "RUSH", "p2")]
    assert adjudicated_drive_points(d, empty, empty) == 0.0

    safety = [play("g", "d1", "A", "SAFETY", "p3")]
    assert adjudicated_drive_points(d, safety, safety) is None
    assert adjudicated_drive_points(drive("g", 1, "A", "B", "d1", status="REVIEW"), fg, fg) is None


def test_team_game_drive_rows_count_resolved_and_unresolved_separately():
    drives = [
        drive("g1", 1, "A", "B", "fg"),
        drive("g1", 1, "A", "B", "empty"),
        drive("g1", 1, "A", "B", "safety"),
    ]
    plays = [
        play("g1", "fg", "A", "FIELD_GOAL_GOOD", "p1"),
        play("g1", "empty", "A", "RUSH", "p2"),
        play("g1", "safety", "A", "SAFETY", "p3"),
    ]
    rows = build_team_game_drive_rows(drives, plays)
    assert len(rows) == 1
    row = rows[0]
    assert row["validatedPossessions"] == 3
    assert row["resolvedPointPossessions"] == 2
    assert row["unresolvedPointPossessions"] == 1
    assert row["offensiveDrivePoints"] == 3.0
    assert row["offensivePPD"] == 1.5
    assert row["drivePpdPointsFoundation"] == DRIVE_PPD_POINTS_FOUNDATION
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
    rows = [
        {"season": 2025, "seasonType": "regular", "week": 1, "gameId": "g1", "team": "A", "opponent": "B", "offensiveDrivePoints": 28.0, "resolvedPointPossessions": 7, "offensivePPD": 4.0},
        {"season": 2025, "seasonType": "regular", "week": 1, "gameId": "g1", "team": "B", "opponent": "A", "offensiveDrivePoints": 7.0, "resolvedPointPossessions": 7, "offensivePPD": 1.0},
        {"season": 2025, "seasonType": "regular", "week": 2, "gameId": "g2", "team": "A", "opponent": "B", "offensiveDrivePoints": 0.0, "resolvedPointPossessions": 1, "offensivePPD": 0.0},
        {"season": 2025, "seasonType": "regular", "week": 2, "gameId": "g2", "team": "B", "opponent": "A", "offensiveDrivePoints": 0.0, "resolvedPointPossessions": 1, "offensivePPD": 0.0},
    ]
    snapshots = build_pregame_ppd_snapshots(rows, 2025, shrinkage_possessions=1.0)
    week1 = [r for r in snapshots if r["week"] == 1]
    week2 = [r for r in snapshots if r["week"] == 2]
    assert all(r["gamesPlayedBefore"] == 0 for r in week1)
    assert all(r["ppdLeagueMeanBefore"] is None for r in week1)
    assert next(r for r in week2 if r["team"] == "A")["rawOffensivePPDBefore"] == 4.0
    assert next(r for r in week2 if r["team"] == "B")["rawOffensivePPDBefore"] == 1.0


def test_matchup_orientation_expected_score_and_postgame_isolation():
    snapshots = [
        {"season": 2025, "seasonType": "regular", "week": 3, "gameId": "g3", "team": "A", "opponent": "B",
         "gamesPlayedBefore": 2, "ppdLeagueMeanBefore": 2.0,
         "opponentAdjustedOffensePPDAboveAverage": 0.5, "opponentAdjustedDefensePPDPreventedAboveAverage": 0.4},
        {"season": 2025, "seasonType": "regular", "week": 3, "gameId": "g3", "team": "B", "opponent": "A",
         "gamesPlayedBefore": 2, "ppdLeagueMeanBefore": 2.0,
         "opponentAdjustedOffensePPDAboveAverage": -0.2, "opponentAdjustedDefensePPDPreventedAboveAverage": -0.1},
    ]
    matchups = build_matchup_ppd(snapshots, 2025)
    oriented = orient_matchup_ppd(matchups[0], "A", "B")
    assert oriented["homeExpectedOffensivePPD"] == pytest.approx(2.6)
    assert oriented["awayExpectedOffensivePPD"] == pytest.approx(1.4)
    assert oriented["expectedPPDEdge"] == pytest.approx(1.2)
    assert expected_score(oriented["homeExpectedOffensivePPD"], 10.0) == pytest.approx(26.0)

    post = attach_postgame_residuals(matchups, [
        {"gameId": "g3", "team": "A", "offensivePPD": 3.0},
        {"gameId": "g3", "team": "B", "offensivePPD": 1.0},
    ])
    assert post[0]["postgameTargetDiagnostic"] is True
    assert post[0]["team1OffensivePPDAboveExpectation"] == pytest.approx(0.4)
    assert all("Actual" not in key and "AboveExpectation" not in key for key in matchups[0])
