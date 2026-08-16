from cfb_analytics.analytics.prediction_v2_early_prior_audit import (
    adjacent_prior_map,
    covered_game,
    current_games_before,
    is_early_regular_game,
)


def test_adjacent_prior_map_never_bridges_missing_2020():
    mapping = adjacent_prior_map()
    assert mapping[2015] == 2014
    assert mapping[2019] == 2018
    assert 2021 not in mapping
    assert mapping[2022] == 2021
    assert mapping[2025] == 2024
    assert 2014 not in mapping


def test_early_regular_game_uses_regular_week_four_or_earlier_only():
    assert is_early_regular_game({"seasonType": "regular", "week": 0}) is True
    assert is_early_regular_game({"seasonType": "regular", "week": 4}) is True
    assert is_early_regular_game({"seasonType": "regular", "week": 5}) is False
    assert is_early_regular_game({"seasonType": "postseason", "week": 1}) is False


def test_current_games_before_reads_iterative_counts():
    row = {"homeIterativeGamesPlayedBefore": 2, "awayIterativeGamesPlayedBefore": 3}
    assert current_games_before(row) == (2, 3)


def test_covered_game_requires_both_teams_in_complete_prior_state():
    row = {"homeTeam": "A", "awayTeam": "B"}
    assert covered_game(row, {"A", "B"}) is True
    assert covered_game(row, {"A"}) is False
