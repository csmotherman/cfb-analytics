from cfb_analytics.analytics.situational_splits import build_situational_rows


def _play(
    *, pid, play_number, down, distance, yards, subtype, period=1,
    yards_to_goal=50, offense_score=0, defense_score=0,
):
    return {
        "id": str(pid),
        "gameId": "g1",
        "driveId": "d1",
        "driveNumber": 1,
        "playNumber": play_number,
        "offense": "Michigan",
        "defense": "Ohio State",
        "period": period,
        "down": down,
        "distance": distance,
        "yardsToGoal": yards_to_goal,
        "offenseScore": offense_score,
        "defenseScore": defense_score,
        "analyticsYardsGained": yards,
        "isScrimmagePlay": True,
        "isOffensivePlay": True,
        "hasStateTransitionModifier": False,
        "hasNoPlayContext": False,
        "eventSubtype": subtype,
        "sourcePlayType": subtype,
        "playText": "",
    }


def _drive():
    return {
        "gameId": "g1",
        "driveId": "d1",
        "offense": "Michigan",
        "defense": "Ohio State",
        "isPossessionDrive": True,
        "driveValidationStatus": "PASS",
    }


def test_builds_exact_down_distance_rows_for_both_sides():
    plays = [
        _play(pid=1, play_number=1, down=3, distance=2, yards=3, subtype="Rush", period=1),
        _play(pid=2, play_number=2, down=1, distance=10, yards=6, subtype="Pass Reception", period=1),
    ]
    rows = build_situational_rows(plays, [_drive()], 2023)

    offense = next(
        r for r in rows
        if r["team"] == "Michigan" and r["side"] == "offense" and r["down"] == 3 and r["distance"] == 2
    )
    defense = next(
        r for r in rows
        if r["team"] == "Ohio State" and r["side"] == "defense" and r["down"] == 3 and r["distance"] == 2
    )

    assert offense["plays"] == 1
    assert offense["successRate"] == 1.0
    assert offense["rushRate"] == 1.0
    assert offense["firstDownRate"] == 1.0
    assert offense["conversionRate"] == 1.0
    assert defense["plays"] == offense["plays"]
    assert defense["successes"] == offense["successes"]


def test_first_down_generation_uses_next_down_reset_evidence():
    plays = [
        _play(pid=1, play_number=1, down=2, distance=10, yards=6, subtype="Rush", period=3),
        _play(pid=2, play_number=2, down=1, distance=10, yards=2, subtype="Rush", period=3),
    ]
    rows = build_situational_rows(plays, [_drive()], 2023)

    row = next(
        r for r in rows
        if r["team"] == "Michigan" and r["side"] == "offense" and r["down"] == 2 and r["distance"] == 10
    )

    assert row["quarter"] == 3
    assert row["half"] == 2
    assert row["successRate"] == 0.0
    assert row["firstDowns"] == 1
    assert row["firstDownRate"] == 1.0


def test_run_pass_playcalling_and_success_are_separate():
    plays = [
        _play(pid=1, play_number=1, down=3, distance=5, yards=5, subtype="Rush"),
        _play(pid=2, play_number=2, down=3, distance=5, yards=2, subtype="Pass Reception"),
        _play(pid=3, play_number=3, down=3, distance=5, yards=8, subtype="Pass Reception"),
    ]
    rows = build_situational_rows(plays, [_drive()], 2023)
    row = next(
        r for r in rows
        if r["team"] == "Michigan" and r["side"] == "offense" and r["down"] == 3 and r["distance"] == 5
    )

    assert row["plays"] == 3
    assert row["rushPlays"] == 1
    assert row["passPlays"] == 2
    assert row["rushRate"] == 1 / 3
    assert row["passRate"] == 2 / 3
    assert row["rushSuccessRate"] == 1.0
    assert row["passSuccessRate"] == 0.5
    assert row["conversionRate"] == 2 / 3


def test_v2_context_dimensions_are_explicit():
    plays = [
        _play(
            pid=1, play_number=1, down=3, distance=4, yards=4,
            subtype="Rush", period=4, yards_to_goal=4,
            offense_score=21, defense_score=24,
        )
    ]
    rows = build_situational_rows(plays, [_drive()], 2023)
    row = next(r for r in rows if r["team"] == "Michigan" and r["side"] == "offense")

    assert row["quarter"] == 4
    assert row["half"] == 2
    assert row["fieldPositionBucket"] == "red_zone"
    assert row["redZone"] is True
    assert row["goalToGo"] is True
    assert row["scoreState"] == "trailing"


def test_unknown_context_is_preserved_not_dropped():
    play = _play(pid=1, play_number=1, down=1, distance=10, yards=5, subtype="Rush")
    play.pop("yardsToGoal")
    play.pop("offenseScore")
    play.pop("defenseScore")

    rows = build_situational_rows([play], [_drive()], 2023)
    row = next(r for r in rows if r["team"] == "Michigan" and r["side"] == "offense")

    assert row["fieldPositionBucket"] == "unknown"
    assert row["redZone"] is False
    assert row["goalToGo"] is False
    assert row["scoreState"] == "unknown"
