from __future__ import annotations

import pytest

from cfb_analytics.analytics.schedule_adjusted.darren_data_pack import (
    build_tendencies,
    resolve_team,
)


def _row(**overrides):
    row = {
        "team_id": 2711,
        "team": "Western Michigan",
        "team_slug": "western-michigan",
        "conference": "Mid-American",
        "classification": "fbs",
        "gameValidationStatus": "PASS",
        "gameId": "1",
        "week": 1,
        "seasonType": "regular",
        "win": 1,
        "loss": 0,
        "points_for": 30,
        "points_against": 20,
        "offensivePlays": 30,
        "defensivePlays": 30,
        "possessions": 10,
        "possessionsAllowed": 10,
        "rushAttempts": 10,
        "dropbacks": 20,
        "rushAttemptsFaced": 15,
        "dropbacksFaced": 15,
        "standardDownPlays": 20,
        "passingDownPlays": 10,
        "successfulPlays": 1,
        "successEligiblePlays": 2,
        "rushSuccessfulPlays": 4,
        "rushSuccessEligiblePlays": 10,
        "passSuccessfulPlays": 8,
        "passSuccessEligiblePlays": 20,
        "explosivePlays": 3,
        "explosiveEligiblePlays": 30,
        "rushExplosivePlays": 1,
        "rushExplosiveEligiblePlays": 10,
        "passExplosivePlays": 2,
        "passExplosiveEligiblePlays": 20,
        "basicYardageYards": 180,
        "basicYardagePlays": 30,
        "rushYards": 50,
        "netPassYards": 130,
        "standardDownSuccesses": 9,
        "passingDownSuccesses": 3,
        "thirdDownConversions": 4,
        "thirdDownAttempts": 10,
        "sacksAllowed": 2,
        "havocPlaysAllowed": 4,
        "havocEligiblePlays": 30,
        "successfulPlaysAllowed": 12,
        "successEligiblePlaysAllowed": 30,
        "rushSuccessfulPlaysAllowed": 5,
        "rushSuccessEligiblePlaysAllowed": 15,
        "passSuccessfulPlaysAllowed": 7,
        "passSuccessEligiblePlaysAllowed": 15,
        "explosivePlaysAllowed": 3,
        "explosiveEligiblePlaysAllowed": 30,
        "rushExplosivePlaysAllowed": 1,
        "rushExplosiveEligiblePlaysAllowed": 15,
        "passExplosivePlaysAllowed": 2,
        "passExplosiveEligiblePlaysAllowed": 15,
        "basicYardageYardsAllowed": 150,
        "basicYardagePlaysFaced": 30,
        "rushYardsAllowed": 60,
        "netPassYardsAllowed": 90,
        "thirdDownConversionsAllowed": 3,
        "thirdDownAttemptsAllowed": 10,
        "sacks": 3,
        "havocPlays": 5,
        "havocEligiblePlaysFaced": 30,
    }
    row.update(overrides)
    return row


def test_resolve_team_accepts_name_slug_and_id():
    rows = [
        _row(),
        _row(team_id=130, team="Michigan", team_slug="michigan", conference="Big Ten", gameId="2"),
    ]

    assert resolve_team(rows, "Western Michigan").id == "2711"
    assert resolve_team(rows, "western-michigan").id == "2711"
    assert resolve_team(rows, "2711").name == "Western Michigan"


def test_tendencies_use_weighted_counts_not_mean_of_game_rates():
    rows = [
        _row(),
        _row(
            gameId="2",
            week=2,
            rushAttempts=30,
            dropbacks=10,
            successfulPlays=9,
            successEligiblePlays=10,
            points_for=20,
            win=0,
            loss=1,
        ),
        _row(
            gameId="3",
            week=3,
            gameValidationStatus="FAIL",
            rushAttempts=100,
            dropbacks=0,
            successfulPlays=100,
            successEligiblePlays=100,
        ),
    ]

    tendencies = build_tendencies(rows, "2711")

    assert tendencies["games"] == 2
    assert tendencies["wins"] == 1
    assert tendencies["losses"] == 1
    assert tendencies["offense"]["rushDecisionRate"] == pytest.approx(40 / 70)
    assert tendencies["offense"]["dropbackRate"] == pytest.approx(30 / 70)
    assert tendencies["offense"]["successRate"] == pytest.approx(10 / 12)
    assert tendencies["offense"]["pointsPerGame"] == pytest.approx(25.0)
