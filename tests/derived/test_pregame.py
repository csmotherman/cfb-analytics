from cfb_analytics.derived.pregame import build_pregame_snapshots, pregame_snapshot_audit


def game(team, opp, week, game_id, yards, plays, success_eligible=10, successful=5):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game_id,
        "team": team,
        "opponent": opp,
        "validatedPossessions": 2,
        "validatedDefensivePossessions": 2,
        "offensivePlays": plays,
        "defensivePlays": plays,
        "offensiveYards": yards,
        "defensiveYardsAllowed": yards,
        "reviewPossessionGroups": 0,
        "gameValidationStatus": "PASS",
        "successEligiblePlays": success_eligible,
        "successfulPlays": successful,
        "successEligiblePlaysAllowed": success_eligible,
        "successfulPlaysAllowed": successful,
    }


def test_first_partition_has_zero_history():
    rows = [game("A", "B", 1, "g1", 100, 10), game("B", "A", 1, "g1", 80, 10)]
    snaps = build_pregame_snapshots(rows, 2025)
    assert len(snaps) == 2
    assert all(s["gamesPlayedBefore"] == 0 for s in snaps)
    assert all(s["historyAvailable"] is False for s in snaps)


def test_same_week_games_do_not_leak_into_each_other():
    rows = [
        game("A", "B", 1, "g1", 100, 10),
        game("B", "A", 1, "g1", 80, 10),
        game("A", "C", 2, "g2", 200, 20),
        game("C", "A", 2, "g2", 120, 20),
        game("A", "D", 2, "g3", 300, 30),
        game("D", "A", 2, "g3", 90, 30),
    ]
    snaps = build_pregame_snapshots(rows, 2025)
    a_week2 = [s for s in snaps if s["team"] == "A" and s["week"] == 2]
    assert len(a_week2) == 2
    assert all(s["gamesPlayedBefore"] == 1 for s in a_week2)
    assert all(s["offensiveYards"] == 100 for s in a_week2)


def test_rates_recompute_from_prior_totals():
    rows = [
        game("A", "B", 1, "g1", 100, 10, success_eligible=10, successful=2),
        game("B", "A", 1, "g1", 80, 10),
        game("A", "C", 2, "g2", 200, 20, success_eligible=30, successful=18),
        game("C", "A", 2, "g2", 120, 20),
        game("A", "D", 3, "g3", 150, 15),
        game("D", "A", 3, "g3", 90, 15),
    ]
    snaps = build_pregame_snapshots(rows, 2025)
    a_week3 = next(s for s in snaps if s["team"] == "A" and s["week"] == 3)
    assert a_week3["gamesPlayedBefore"] == 2
    assert a_week3["offensiveYards"] == 300
    assert a_week3["yardsPerPlay"] == 10
    assert a_week3["successEligiblePlays"] == 40
    assert a_week3["successfulPlays"] == 20
    assert a_week3["successRate"] == 0.5


def test_snapshot_audit_matches_team_game_keys_and_prior_counts():
    rows = [
        game("A", "B", 1, "g1", 100, 10),
        game("B", "A", 1, "g1", 80, 10),
        game("A", "B", 2, "g2", 120, 10),
        game("B", "A", 2, "g2", 90, 10),
    ]
    snaps = build_pregame_snapshots(rows, 2025)
    audit = pregame_snapshot_audit(rows, snaps, 2025)
    assert audit["status"] == "PASS"
    assert all(audit["checks"].values())
