from cfb_analytics.analytics.schedule_adjusted.analytics_lab_export import build_analytics_lab


def _game(game_id, week, home, away, home_success, away_success):
    common = {
        "season": 2025,
        "seasonType": "regular",
        "season_type": "regular",
        "week": week,
        "gameId": game_id,
        "game_id": game_id,
        "classification": "fbs",
        "conference": "Test",
        "gameValidationStatus": "PASS",
        "successEligiblePlays": 10,
        "successEligiblePlaysAllowed": 10,
        "neutral_site": False,
    }
    home_row = {
        **common,
        "team": home,
        "team_id": home,
        "team_slug": home.lower(),
        "opponent": away,
        "opponent_id": away,
        "home_away": "home",
        "successfulPlays": home_success,
        "successRate": home_success / 10,
        "successRateAllowed": away_success / 10,
        "points_for": 24,
        "points_against": 17,
    }
    away_row = {
        **common,
        "team": away,
        "team_id": away,
        "team_slug": away.lower(),
        "opponent": home,
        "opponent_id": home,
        "home_away": "away",
        "successfulPlays": away_success,
        "successRate": away_success / 10,
        "successRateAllowed": home_success / 10,
        "points_for": 17,
        "points_against": 24,
    }
    return [home_row, away_row]


def _rows():
    rows = []
    rows += _game("ab", 1, "A", "B", 6, 4)
    rows += _game("ac", 2, "A", "C", 5, 5)
    rows += _game("bd", 2, "B", "D", 5, 5)
    rows += _game("cd", 3, "C", "D", 4, 6)
    return rows


def _target(payload):
    return next(row for row in payload["games"] if row["id"] == "ab" and row["t"] == "A")


def test_target_game_changes_actual_but_not_leave_one_out_expectation():
    original_rows = _rows()
    original = build_analytics_lab(original_rows, season=2025, metric_names=("successRate",))

    changed_rows = [dict(row) for row in original_rows]
    for row in changed_rows:
        if row["gameId"] == "ab" and row["team"] == "A":
            row["successfulPlays"] = 9
            row["successRate"] = 0.9
        if row["gameId"] == "ab" and row["team"] == "B":
            row["successRateAllowed"] = 0.9

    changed = build_analytics_lab(changed_rows, season=2025, metric_names=("successRate",))
    original_target = _target(original)["m"][0]
    changed_target = _target(changed)["m"][0]

    assert original_target[0] == 0.6
    assert changed_target[0] == 0.9
    assert changed_target[1] == original_target[1]
    assert changed_target[2] != original_target[2]
    assert original["ridge"] == 40.0
    assert original["homeRidge"] == 20.0
