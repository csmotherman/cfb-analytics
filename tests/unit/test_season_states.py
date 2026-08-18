from datetime import datetime, timezone

from cfb_analytics.config.seasons import SeasonState, classify_season, michigan_seasons


AS_OF = datetime(2026, 8, 18, tzinfo=timezone.utc)


def test_supported_michigan_window_is_2010_through_2026():
    assert michigan_seasons() == tuple(range(2010, 2027))


def test_2026_without_started_game_evidence_is_preseason():
    status = classify_season(2026, as_of=AS_OF)
    assert status.state is SeasonState.PRESEASON
    assert status.games_started == 0


def test_future_schedule_does_not_become_observed_performance():
    games = [{"startDate": "2026-08-29T16:00:00Z", "completed": False}]
    status = classify_season(2026, games, as_of=AS_OF)
    assert status.state is SeasonState.PRESEASON


def test_started_unfinished_schedule_is_in_season():
    games = [
        {"startDate": "2026-08-15T16:00:00Z", "completed": True},
        {"startDate": "2026-08-29T16:00:00Z", "completed": False},
    ]
    assert classify_season(2026, games, as_of=AS_OF).state is SeasonState.IN_SEASON


def test_all_saved_games_completed_is_complete():
    games = [{"startDate": "2025-08-15T16:00:00Z", "homePoints": 20, "awayPoints": 10}]
    assert classify_season(2025, games, as_of=AS_OF).state is SeasonState.COMPLETE


def test_canonical_team_game_scores_are_completion_evidence():
    games = [{"points_for": 27, "points_against": 24}]
    assert classify_season(2025, games, as_of=AS_OF).state is SeasonState.COMPLETE
