import math

from cfb_analytics.analytics.prediction_v1_integrity_audit import (
    MWDR,
    add_prediction_features,
    extract_authoritative_game,
    pearson,
)


def test_extract_authoritative_game_uses_cfbd_points_schema():
    row = {
        "id": 123,
        "homeTeam": "Home",
        "awayTeam": "Away",
        "homePoints": 31,
        "awayPoints": 24,
    }
    game = extract_authoritative_game(row)
    assert game == {
        "gameId": "123",
        "homeTeam": "Home",
        "awayTeam": "Away",
        "homeScore": 31.0,
        "awayScore": 24.0,
        "scoreFields": "homePoints/awayPoints",
    }


def test_extract_authoritative_game_falls_back_across_supported_score_schemas():
    row = {
        "game_id": "g1",
        "home": "A",
        "away": "B",
        "home_score": 17,
        "away_score": 14,
    }
    game = extract_authoritative_game(row)
    assert game is not None
    assert game["gameId"] == "g1"
    assert game["homeScore"] == 17.0
    assert game["awayScore"] == 14.0
    assert game["scoreFields"] == "home_score/away_score"


def test_extract_authoritative_game_preserves_missing_final_score_for_coverage_report():
    game = extract_authoritative_game({"id": 5, "homeTeam": "A", "awayTeam": "B"})
    assert game is not None
    assert game["homeScore"] is None
    assert game["awayScore"] is None
    assert game["scoreFields"] is None


def test_add_prediction_features_reconstructs_locked_interactions():
    row = {
        MWDR[0]: 0.4,
        MWDR[1]: 0.1,
    }
    matchup = {
        "expectedPossessionsPerTeam": 12.0,
        "netSuccessRateEdge": 0.05,
        "netExplosiveRateEdge": 0.02,
        "netTurnoverPressureEdge": -0.03,
    }
    out = add_prediction_features(row, matchup)
    assert math.isclose(out["mwdrXExpectedPossessions"], 6.0)
    assert math.isclose(out["successVolumeEdge"], 0.6)
    assert math.isclose(out["explosiveVolumeEdge"], 0.24)
    assert math.isclose(out["turnoverVolumeEdge"], -0.36)


def test_pearson_detects_perfect_positive_and_negative_relationships():
    rows = [
        {"x": 1.0, "y": 2.0, "z": -2.0},
        {"x": 2.0, "y": 4.0, "z": -4.0},
        {"x": 3.0, "y": 6.0, "z": -6.0},
    ]
    assert math.isclose(pearson(rows, "x", "y"), 1.0)
    assert math.isclose(pearson(rows, "x", "z"), -1.0)
