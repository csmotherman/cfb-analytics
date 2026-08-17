from __future__ import annotations

from cfb_analytics.analytics.kalman_ats_deep_audit import (
    COMPARATOR_MIN_GAMES,
    KALMAN_ATS_FEATURES,
    PRIMARY_MIN_GAMES,
    PRIMARY_THRESHOLD,
    _game_record,
)
from cfb_analytics.analytics.ats_logistic_deep_audit import summarize_bets


def _row(**overrides):
    base = {
        "gameId": "g1",
        "seasonType": "regular",
        "week": 5,
        "homeTeam": "Home",
        "awayTeam": "Away",
        "homeIterativeGamesPlayedBefore": 4,
        "awayIterativeGamesPlayedBefore": 5,
        "KALMAN_strength": 3.0,
        "KALMAN_uncertainty": 15.0,
        "marketHomeMargin": 2.5,
        "marketAbsSpread": 2.5,
        "marketHomeFavorite": 1.0,
        "weekNumber": 5.0,
        "neutralSite": 0.0,
        "isNeutralSite": False,
        "target_margin": 7.0,
    }
    base.update(overrides)
    return base


def test_candidate_contract_is_predeclared() -> None:
    assert PRIMARY_MIN_GAMES == 4
    assert COMPARATOR_MIN_GAMES == 3
    assert PRIMARY_THRESHOLD == 0.55
    assert KALMAN_ATS_FEATURES == (
        "dynamicStrength",
        "dynamicUncertainty",
        "marketHomeMargin",
        "marketAbsSpread",
        "marketHomeFavorite",
        "weekNumber",
        "neutralSite",
    )


def test_game_record_grades_home_cover_win() -> None:
    record = _game_record(_row(), probability=0.61, min_games=4, season=2025)
    assert record["pickedSide"] == "HOME"
    assert record["pickedSideRole"] == "FAVORITE"
    assert record["result"] == "WIN"
    assert record["eligibilityDepth"] == 4
    assert record["eligibilityDepthBucket"] == "EXACTLY_4"


def test_game_record_grades_away_cover_and_role() -> None:
    record = _game_record(
        _row(marketHomeMargin=-6.0, marketAbsSpread=6.0, target_margin=-2.0),
        probability=0.40,
        min_games=3,
        season=2024,
    )
    assert record["pickedSide"] == "AWAY"
    assert record["pickedSideRole"] == "FAVORITE"
    # Actual home margin -2 beats an away-favored market line of -6: home covers.
    assert record["result"] == "LOSS"


def test_exact_three_depth_is_identified() -> None:
    record = _game_record(
        _row(homeIterativeGamesPlayedBefore=3, awayIterativeGamesPlayedBefore=7),
        probability=0.56,
        min_games=3,
        season=2023,
    )
    assert record["eligibilityDepth"] == 3
    assert record["eligibilityDepthBucket"] == "EXACTLY_3"


def test_summarize_bets_uses_minus_110_roi() -> None:
    rows = [
        {"result": "WIN"},
        {"result": "WIN"},
        {"result": "LOSS"},
        {"result": "PUSH"},
    ]
    summary = summarize_bets(rows)
    assert summary["wins"] == 2
    assert summary["losses"] == 1
    assert summary["pushes"] == 1
    assert summary["decisions"] == 3
    assert summary["roiMinus110"] is not None
    assert summary["roiMinus110"] > 0
