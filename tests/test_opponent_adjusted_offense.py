import pytest

from cfb_analytics.analytics.opponent_adjusted_offense import calculate_opponent_adjusted_offense


def _row(*, game: str, team_id: int, team: str, opp_id: int, opp: str, points: int, possessions: int, successes: int, plays: int, scoring: int, points_allowed: int, possessions_allowed: int, successes_allowed: int, plays_allowed: int, scoring_allowed: int):
    return {
        "season": 2025,
        "classification": "fbs",
        "opponent_classification": "fbs",
        "gameValidationStatus": "PASS",
        "gameId": game,
        "team_id": team_id,
        "team": team,
        "opponent_id": opp_id,
        "opponent": opp,
        "possessionPoints": points,
        "resolvedPointPossessions": possessions,
        "successfulPlays": successes,
        "successEligiblePlays": plays,
        "possessionTouchdowns": scoring,
        "possessionFieldGoals": 0,
        "otherScoringPossessions": 0,
        "validatedPossessions": possessions,
        "possessionPointsAllowed": points_allowed,
        "resolvedPointPossessionsAllowed": possessions_allowed,
        "successfulPlaysAllowed": successes_allowed,
        "successEligiblePlaysAllowed": plays_allowed,
        "possessionTouchdownsAllowed": scoring_allowed,
        "possessionFieldGoalsAllowed": 0,
        "otherScoringPossessionsAllowed": 0,
        "validatedDefensivePossessions": possessions_allowed,
    }


def _sample_rows():
    # Three teams play a double round-robin. Paired rows intentionally mirror
    # each game's offensive/defensive counts so leave-one-out baselines are
    # available for every opponent.
    return [
        _row(game="1", team_id=1, team="Alpha", opp_id=2, opp="Beta", points=35, possessions=10, successes=30, plays=60, scoring=5, points_allowed=14, possessions_allowed=10, successes_allowed=20, plays_allowed=60, scoring_allowed=2),
        _row(game="1", team_id=2, team="Beta", opp_id=1, opp="Alpha", points=14, possessions=10, successes=20, plays=60, scoring=2, points_allowed=35, possessions_allowed=10, successes_allowed=30, plays_allowed=60, scoring_allowed=5),
        _row(game="2", team_id=1, team="Alpha", opp_id=3, opp="Gamma", points=32, possessions=10, successes=29, plays=60, scoring=5, points_allowed=10, possessions_allowed=10, successes_allowed=18, plays_allowed=60, scoring_allowed=1),
        _row(game="2", team_id=3, team="Gamma", opp_id=1, opp="Alpha", points=10, possessions=10, successes=18, plays=60, scoring=1, points_allowed=32, possessions_allowed=10, successes_allowed=29, plays_allowed=60, scoring_allowed=5),
        _row(game="3", team_id=2, team="Beta", opp_id=3, opp="Gamma", points=21, possessions=10, successes=24, plays=60, scoring=3, points_allowed=17, possessions_allowed=10, successes_allowed=21, plays_allowed=60, scoring_allowed=2),
        _row(game="3", team_id=3, team="Gamma", opp_id=2, opp="Beta", points=17, possessions=10, successes=21, plays=60, scoring=2, points_allowed=21, possessions_allowed=10, successes_allowed=24, plays_allowed=60, scoring_allowed=3),
        _row(game="4", team_id=1, team="Alpha", opp_id=2, opp="Beta", points=38, possessions=10, successes=32, plays=60, scoring=6, points_allowed=17, possessions_allowed=10, successes_allowed=21, plays_allowed=60, scoring_allowed=2),
        _row(game="4", team_id=2, team="Beta", opp_id=1, opp="Alpha", points=17, possessions=10, successes=21, plays=60, scoring=2, points_allowed=38, possessions_allowed=10, successes_allowed=32, plays_allowed=60, scoring_allowed=6),
        _row(game="5", team_id=1, team="Alpha", opp_id=3, opp="Gamma", points=35, possessions=10, successes=31, plays=60, scoring=5, points_allowed=13, possessions_allowed=10, successes_allowed=19, plays_allowed=60, scoring_allowed=2),
        _row(game="5", team_id=3, team="Gamma", opp_id=1, opp="Alpha", points=13, possessions=10, successes=19, plays=60, scoring=2, points_allowed=35, possessions_allowed=10, successes_allowed=31, plays_allowed=60, scoring_allowed=5),
        _row(game="6", team_id=2, team="Beta", opp_id=3, opp="Gamma", points=24, possessions=10, successes=25, plays=60, scoring=3, points_allowed=20, possessions_allowed=10, successes_allowed=22, plays_allowed=60, scoring_allowed=3),
        _row(game="6", team_id=3, team="Gamma", opp_id=2, opp="Beta", points=20, possessions=10, successes=22, plays=60, scoring=3, points_allowed=24, possessions_allowed=10, successes_allowed=25, plays_allowed=60, scoring_allowed=3),
    ]


def test_opponent_adjusted_offense_ranks_clear_best_offense_first():
    rankings = calculate_opponent_adjusted_offense(_sample_rows(), 2025)

    assert [row["team"] for row in rankings] == ["Alpha", "Beta", "Gamma"]
    assert rankings[0]["rank"] == 1
    assert rankings[0]["adjusted_points_per_drive"] > rankings[1]["adjusted_points_per_drive"]
    assert rankings[0]["adjusted_success_rate"] > rankings[1]["adjusted_success_rate"]
    assert rankings[0]["adjusted_scoring_drive_rate"] > rankings[1]["adjusted_scoring_drive_rate"]


def test_diagnostics_expose_raw_metrics_and_exact_adjustment_deltas():
    rankings = calculate_opponent_adjusted_offense(_sample_rows(), 2025)
    alpha = next(row for row in rankings if row["team"] == "Alpha")

    # Alpha totals across four 10-possession games: 140 points, 122 successes
    # on 240 eligible plays, and 21 scoring possessions.
    assert alpha["raw_points_per_drive"] == pytest.approx(3.5)
    assert alpha["raw_success_rate"] == pytest.approx(122 / 240)
    assert alpha["raw_scoring_drive_rate"] == pytest.approx(21 / 40)

    assert alpha["points_per_drive_adjustment"] == pytest.approx(
        alpha["adjusted_points_per_drive"] - alpha["raw_points_per_drive"]
    )
    assert alpha["success_rate_adjustment"] == pytest.approx(
        alpha["adjusted_success_rate"] - alpha["raw_success_rate"]
    )
    assert alpha["scoring_drive_rate_adjustment"] == pytest.approx(
        alpha["adjusted_scoring_drive_rate"] - alpha["raw_scoring_drive_rate"]
    )


def test_adjustment_is_not_a_relabeling_of_raw_performance():
    rankings = calculate_opponent_adjusted_offense(_sample_rows(), 2025)

    # At least one team must actually move on each component. This catches a
    # regression where raw metrics accidentally flow straight through as the
    # supposedly opponent-adjusted values.
    assert any(abs(row["points_per_drive_adjustment"]) > 1e-9 for row in rankings)
    assert any(abs(row["success_rate_adjustment"]) > 1e-9 for row in rankings)
    assert any(abs(row["scoring_drive_rate_adjustment"]) > 1e-9 for row in rankings)
