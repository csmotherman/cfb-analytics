from cfb_analytics.analytics.beat_the_model import (
    SLATE_SIZE,
    blend_team_rating,
    matchup_score,
    prior_weight,
    select_official_slate,
)


def test_prior_weight_matches_frozen_four_game_carryover():
    assert [prior_weight(games) for games in range(6)] == [1.0, 0.75, 0.5, 0.25, 0.0, 0.0]


def test_week_one_rating_is_exact_previous_season_rating():
    assert blend_team_rating(prior_rating=24.5, current_rating=None, games_before=0) == 24.5


def test_numeric_power_rating_blends_not_rank_position():
    value = blend_team_rating(prior_rating=20.0, current_rating=12.0, games_before=1)
    assert value == 18.0


def test_matchup_score_rewards_two_good_close_ranked_teams():
    assert matchup_score(2, 5) < matchup_score(1, 40)
    assert matchup_score(15, 16) < matchup_score(1, 40)


def test_official_slate_selection_ignores_model_margin_strength():
    rankings = [
        {"rank": 1, "team": "A", "rating": 25.0},
        {"rank": 2, "team": "B", "rating": 24.0},
        {"rank": 10, "team": "C", "rating": 12.0},
        {"rank": 11, "team": "D", "rating": 11.5},
    ]
    games = [
        {
            "id": "top",
            "seasonType": "regular",
            "homeTeam": "A",
            "awayTeam": "B",
            "modelHomeMargin": 0.1,
            "winnerCorrect": True,
            "modelAbsoluteError": 3.0,
        },
        {
            "id": "lower",
            "seasonType": "regular",
            "homeTeam": "C",
            "awayTeam": "D",
            "modelHomeMargin": 40.0,
            "winnerCorrect": False,
            "modelAbsoluteError": 20.0,
        },
    ]

    annotated, summary = select_official_slate(games, rankings, slate_size=1)
    selected = [row for row in annotated if row["beatTheModelSelected"]]
    assert [row["id"] for row in selected] == ["top"]
    assert summary["selectedGameIds"] == ["top"]


def test_official_slate_requires_regular_game_rankings_and_model_call():
    rankings = [
        {"rank": 1, "team": "A", "rating": 25.0},
        {"rank": 2, "team": "B", "rating": 24.0},
        {"rank": 3, "team": "C", "rating": 23.0},
    ]
    games = [
        {"id": "valid", "seasonType": "regular", "homeTeam": "A", "awayTeam": "B", "modelHomeMargin": 1.0},
        {"id": "no-model", "seasonType": "regular", "homeTeam": "A", "awayTeam": "C", "modelHomeMargin": None},
        {"id": "post", "seasonType": "postseason", "homeTeam": "B", "awayTeam": "C", "modelHomeMargin": 2.0},
    ]
    annotated, summary = select_official_slate(games, rankings, slate_size=SLATE_SIZE)
    selected = [row["id"] for row in annotated if row["beatTheModelSelected"]]
    assert selected == ["valid"]
    assert summary["eligibleGames"] == 1
