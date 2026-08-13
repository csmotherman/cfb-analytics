import pytest

from cfb_analytics.analytics.system_metrics import (
    SYSTEM_METRICS_VERSION,
    _aggressiveness,
    _side_components,
    derive_system_team_games,
    system_metrics_audit,
)


def play(pid, offense, defense, subtype, down, distance, yards, period=1, o_score=0, d_score=0, ytg=50):
    return {
        "id": pid,
        "gameId": "g1",
        "offense": offense,
        "defense": defense,
        "eventSubtype": subtype,
        "isScrimmagePlay": True,
        "isOffensivePlay": True,
        "hasNoPlayContext": False,
        "hasStateTransitionModifier": False,
        "down": down,
        "distance": distance,
        "analyticsYardsGained": yards,
        "period": period,
        "offenseScore": o_score,
        "defenseScore": d_score,
        "yardsToGoal": ytg,
    }


def decision(pid, offense, defense, subtype, distance):
    p = play(pid, offense, defense, subtype, 4, distance, 0)
    if "punt" in subtype.lower() or "field" in subtype.lower():
        p["isScrimmagePlay"] = False
    return p


def drive(did, offense, defense, period, start, end):
    return {
        "driveId": did,
        "gameId": "g1",
        "offense": offense,
        "defense": defense,
        "isPossessionDrive": True,
        "driveValidationStatus": "PASS",
        "startPeriod": period,
        "startOffenseScore": start,
        "endOffenseScoreObserved": end,
    }


def test_passing_and_rushing_efficiency_components_are_exact():
    plays = [
        play("p1", "A", "B", "Pass Reception", 1, 10, 8),
        play("p2", "A", "B", "Sack", 2, 7, -5),
        play("p3", "A", "B", "Pass Reception", 3, 5, 25),
        play("p4", "A", "B", "Rush", 1, 10, 6),
        play("p5", "A", "B", "Rush", 2, 4, 0),
        play("p6", "A", "B", "Rush", 3, 2, 12),
    ]
    x = _side_components(plays, [], "A", "offense")
    assert x["passDropbacks"] == 3
    assert x["passAttemptsExcludingSacks"] == 2
    assert x["sacksTaken"] == 1
    assert x["passYards"] == pytest.approx(28.0)
    assert x["yardsPerDropback"] == pytest.approx(28 / 3)
    assert x["sackRate"] == pytest.approx(1 / 3)
    assert x["passSuccessfulPlays"] == 2
    assert x["passSuccessRate"] == pytest.approx(2 / 3)
    assert x["passExplosivePlays"] == 1
    assert x["rushAttempts"] == 3
    assert x["rushYards"] == pytest.approx(18.0)
    assert x["yardsPerRush"] == pytest.approx(6.0)
    assert x["rushSuccessfulPlays"] == 2
    assert x["stuffedRushes"] == 1
    assert x["stuffRate"] == pytest.approx(1 / 3)


def test_play_calling_identity_uses_declared_situations_only():
    plays = [
        play("p1", "A", "B", "Pass Reception", 1, 10, 5, period=1, o_score=0, d_score=0),
        play("p2", "A", "B", "Rush", 1, 10, 5, period=1, o_score=0, d_score=0),
        play("p3", "A", "B", "Pass Reception", 2, 8, 5, period=2, o_score=7, d_score=0),
        play("p4", "A", "B", "Rush", 2, 4, 3, period=3, o_score=28, d_score=0),
        play("p5", "A", "B", "Pass Reception", 3, 6, 6, period=2, o_score=7, d_score=7),
    ]
    x = _side_components(plays, [], "A", "offense")
    assert x["earlyDownPlays"] == 4
    assert x["earlyDownPasses"] == 2
    assert x["earlyDownPassRate"] == pytest.approx(0.5)
    assert x["firstDownPassRate"] == pytest.approx(0.5)
    assert x["secondAndLongPlays"] == 1
    assert x["secondAndLongPassRate"] == pytest.approx(1.0)
    # The 28-0 third-quarter rush is outside the declared +/-14 neutral window.
    assert x["neutralSituationPlays"] == 3
    assert x["neutralSituationPassRate"] == pytest.approx(2 / 3)


def test_fourth_down_aggressiveness_counts_go_punt_and_field_goal_decisions():
    plays = [
        decision("p1", "A", "B", "Rush", 2),
        decision("p2", "A", "B", "Punt", 8),
        decision("p3", "A", "B", "Field Goal Attempt", 3),
        decision("p4", "A", "B", "Pass Reception", 6),
    ]
    x = _aggressiveness(plays, "A")
    assert x["fourthDownDecisionOpportunities"] == 4
    assert x["fourthDownGoDecisions"] == 2
    assert x["fourthDownGoRate"] == pytest.approx(0.5)
    assert x["fourthAndShortDecisionOpportunities"] == 2
    assert x["fourthAndShortGoDecisions"] == 1
    assert x["fourthAndShortGoRate"] == pytest.approx(0.5)


def test_situational_mastery_components_use_locked_success_definition():
    plays = [
        play("p1", "A", "B", "Rush", 3, 2, 2, ytg=18),
        play("p2", "A", "B", "Pass Reception", 3, 5, 4, ytg=15),
        play("p3", "A", "B", "Rush", 4, 1, 1, ytg=9),
        play("p4", "A", "B", "Pass Reception", 1, 10, 6, ytg=12),
    ]
    x = _side_components(plays, [], "A", "offense")
    assert x["thirdDownAttempts"] == 2
    assert x["thirdDownConversions"] == 1
    assert x["thirdDownConversionRate"] == pytest.approx(0.5)
    assert x["fourthDownGoAttempts"] == 1
    assert x["fourthDownConversionRate"] == pytest.approx(1.0)
    assert x["shortYardageAttempts"] == 2
    assert x["shortYardageConversionRate"] == pytest.approx(1.0)
    assert x["redZonePlayAttempts"] == 4
    assert x["redZoneSuccessfulPlays"] == 3
    assert x["redZoneSuccessRate"] == pytest.approx(0.75)


def test_second_half_adjustment_is_h2_minus_h1_and_excludes_overtime():
    plays = [
        play("p1", "A", "B", "Rush", 1, 10, 5, period=1),
        play("p2", "A", "B", "Rush", 2, 10, 2, period=2),
        play("p3", "A", "B", "Rush", 1, 10, 10, period=3),
        play("p4", "A", "B", "Pass Reception", 2, 10, 10, period=4),
        play("p5", "A", "B", "Pass Reception", 1, 10, 50, period=5),
    ]
    drives = [
        drive("d1", "A", "B", 1, 0, 0),
        drive("d2", "A", "B", 2, 0, 3),
        drive("d3", "A", "B", 3, 3, 10),
        drive("d4", "A", "B", 4, 10, 13),
        drive("d5", "A", "B", 5, 13, 21),
    ]
    x = _side_components(plays, drives, "A", "offense")
    assert x["H1Plays"] == 2
    assert x["H2Plays"] == 2
    assert x["H1SuccessRate"] == pytest.approx(0.5)
    assert x["H2SuccessRate"] == pytest.approx(1.0)
    assert x["secondHalfSuccessRateDelta"] == pytest.approx(0.5)
    assert x["H1YardsPerPlay"] == pytest.approx(3.5)
    assert x["H2YardsPerPlay"] == pytest.approx(10.0)
    assert x["secondHalfYardsPerPlayDelta"] == pytest.approx(6.5)
    assert x["H1PointsPerPossession"] == pytest.approx(1.5)
    assert x["H2PointsPerPossession"] == pytest.approx(5.0)
    assert x["secondHalfPointsPerPossessionDelta"] == pytest.approx(3.5)


def test_team_game_derivation_reconciles_offense_to_opponent_allowed():
    plays = [
        play("a1", "A", "B", "Pass Reception", 1, 10, 20),
        play("a2", "A", "B", "Rush", 2, 5, 4),
        play("b1", "B", "A", "Pass Reception", 1, 10, 8),
        play("b2", "B", "A", "Rush", 3, 2, 0),
    ]
    drives = [drive("a", "A", "B", 1, 0, 7), drive("b", "B", "A", 1, 0, 0)]
    rows = derive_system_team_games(plays, drives, 2025, "regular", 1)
    assert len(rows) == 2
    a = next(r for r in rows if r["team"] == "A")
    b = next(r for r in rows if r["team"] == "B")
    assert a["systemMetricsVersion"] == SYSTEM_METRICS_VERSION
    assert a["passDropbacks"] == b["passDropbacksAllowed"]
    assert a["rushAttempts"] == b["rushAttemptsAllowed"]
    assert a["passYards"] == pytest.approx(b["passYardsAllowed"])
    assert a["rushYards"] == pytest.approx(b["rushYardsAllowed"])
    assert a["thirdDownAttempts"] == b["thirdDownAttemptsAllowed"]
    audit = system_metrics_audit(rows)
    assert audit["status"] == "PASS"
    assert all(audit["checks"].values())


def test_no_play_and_modified_contexts_do_not_enter_system_metrics():
    clean = play("p1", "A", "B", "Rush", 1, 10, 5)
    no_play = play("p2", "A", "B", "Pass Reception", 1, 10, 99)
    no_play["hasNoPlayContext"] = True
    modified = play("p3", "A", "B", "Pass Reception", 1, 10, 99)
    modified["hasStateTransitionModifier"] = True
    x = _side_components([clean, no_play, modified], [], "A", "offense")
    assert x["scrimmageRunPassPlays"] == 2
    # Modified plays are retained for identity volume but remain ineligible for
    # locked success/explosive classification; no-play context is fully excluded.
    assert x["rushAttempts"] == 1
    assert x["passDropbacks"] == 1
    assert x["passSuccessEligiblePlays"] == 0
