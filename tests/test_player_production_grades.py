from cfb_analytics.pipelines.publish_player_production_grades import build, classify_roster


def row(player_id, player, position, category, stat_type, stat):
    return {"playerId": player_id, "player": player, "position": position, "team": "Michigan", "season": 2025, "category": category, "statType": stat_type, "stat": str(stat)}


def test_grades_are_position_relative_and_actual():
    rows = [
        row("1", "One", "RB", "rushing", "YDS", 1200), row("1", "One", "RB", "rushing", "TD", 12), row("1", "One", "RB", "rushing", "CAR", 220),
        row("2", "Two", "RB", "rushing", "YDS", 500), row("2", "Two", "RB", "rushing", "TD", 3), row("2", "Two", "RB", "rushing", "CAR", 120),
        row("3", "Three", "RB", "rushing", "YDS", 100), row("3", "Three", "RB", "rushing", "CAR", 30),
    ]
    result = build(rows, {"1", "2"})
    assert [grade["grade"] for grade in result] == ["A", "C"]
    assert all(grade["valueType"] == "ACTUAL" for grade in result)
    assert result[0]["usagePercentile"] > result[1]["usagePercentile"]


def test_unscored_positions_remain_ungraded():
    rows = [row("1", "Lineman", "OL", "receiving", "YDS", 0)]
    assert build(rows, {"1"}) == []


def test_zero_usage_is_not_a_production_grade():
    rows = [row("1", "Receiver", "WR", "receiving", "YDS", 50)]
    assert build(rows, {"1"}) == []


def test_roster_status_uses_2025_team_history():
    history = [
        {"playerId": "1", "timeline": [{"season": 2025, "team": "Michigan"}]},
        {"playerId": "2", "timeline": [{"season": 2025, "team": "Utah"}]},
        {"playerId": "3", "timeline": []},
        {"playerId": "4", "timeline": [{"season": 2024, "team": "Michigan"}]},
    ]
    statuses = {row["playerId"]: row["rosterStatus"] for row in classify_roster(history)}
    assert statuses == {"1": "RETURNING", "2": "TRANSFER", "3": "FRESHMAN", "4": "UNCLASSIFIED"}
