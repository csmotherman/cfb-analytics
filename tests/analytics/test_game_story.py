"""Game story pack tests, verified against the real 2025 Michigan/Maryland game.

data/published/** is committed (not gitignored) so opponent_baseline/deltas/
drive_funnel/stories tests run unconditionally. drive_result/half_split need
data/processed/derived/{drives,canonical} (gitignored, cache-restored) --
those are skipped when that data isn't present in the checkout, matching
tests/analytics/test_unit_detail.py's existing skipif convention.
"""
import json
from pathlib import Path

import pytest

from cfb_analytics.analytics.game_story.opponent_baseline import (
    METRIC_SPECS,
    aggregate_rate,
    opponent_baseline_excluding_game,
)
from cfb_analytics.analytics.game_story.deltas import normalized_delta, percentile_within_opponent_season
from cfb_analytics.analytics.game_story.drive_funnel import drive_funnel
from cfb_analytics.analytics.game_story.signal import classify_signal, LIKELY_NOISY, STRONG_SIGNAL
from cfb_analytics.analytics.game_story.stories import build_game_stories
from cfb_analytics.config.constants import DEFAULT_PROCESSED_ROOT, DEFAULT_PUBLISHED_ROOT

SEASON = 2025
GAME_ID = "401752914"  # Michigan 45, Maryland 20, Week 13 2025
PROCESSED_ROOT = DEFAULT_PROCESSED_ROOT
PUBLISHED_ROOT = DEFAULT_PUBLISHED_ROOT
DRIVES_PRESENT = (PROCESSED_ROOT / "derived" / "drives" / f"season={SEASON}").exists()
CANONICAL_PRESENT = (PROCESSED_ROOT / "canonical" / f"season={SEASON}").exists()


def _michigan_game() -> dict:
    games = json.loads((PUBLISHED_ROOT / str(SEASON) / "teams" / "michigan" / "games.json").read_text())
    return next(g for g in games if str(g["gameId"]) == GAME_ID)


def test_metric_specs_reproduce_published_season_rates():
    """Every (numerator, denominator) pair must reproduce the team's own published season.json rate exactly."""
    for slug in ("maryland", "michigan", "ohio-state"):
        season = json.loads((PUBLISHED_ROOT / str(SEASON) / "teams" / slug / "season.json").read_text())[0]
        games = json.loads((PUBLISHED_ROOT / str(SEASON) / "teams" / slug / "games.json").read_text())
        for metric in METRIC_SPECS:
            computed = aggregate_rate(games, metric)
            published = season.get(metric)
            if computed is None or published is None:
                continue
            assert abs(computed - published) < 1e-6, f"{slug}/{metric}: {computed} != {published}"


def test_opponent_baseline_excludes_the_game_itself():
    baseline = opponent_baseline_excluding_game("maryland", SEASON, GAME_ID)
    assert baseline["gamesUsed"] == 10  # Maryland played 11 games in 2025; excl. this one leaves 10
    assert baseline["excludedGameId"] == GAME_ID


def test_normalized_delta_positive_means_good_for_michigan_offense():
    mi_game = _michigan_game()
    baseline = opponent_baseline_excluding_game("maryland", SEASON, GAME_ID)
    delta = normalized_delta("successRate", mi_game["successRate"], baseline["rates"]["successRateAllowed"])
    assert delta > 0  # Michigan (57.1% success) clearly outperformed Maryland's normal allowed rate (~44%)


def test_normalized_delta_field_position_direction():
    """Lower averageStartYardsToGoal is better for offense -- a positive delta here must mean MI started closer than normal."""
    mi_game = _michigan_game()
    baseline = opponent_baseline_excluding_game("maryland", SEASON, GAME_ID)
    delta = normalized_delta("averageStartYardsToGoal", mi_game["averageStartYardsToGoal"], baseline["rates"]["averageStartYardsToGoalAllowed"])
    assert mi_game["averageStartYardsToGoal"] < baseline["rates"]["averageStartYardsToGoalAllowed"]
    assert delta > 0  # MI started closer than Maryland normally allows -> favorable -> positive


def test_percentile_within_opponent_season_ranks_a_dominant_game_first():
    mi_game = _michigan_game()
    pct = percentile_within_opponent_season("maryland", SEASON, "successRateAllowed", mi_game["successRate"], GAME_ID)
    assert pct["rank"] == 1  # best success rate Maryland allowed all season, verified by hand this session
    assert pct["percentile"] == 1.0


def test_percentile_suppressed_below_minimum_sample(tmp_path):
    fixture_root = tmp_path / str(SEASON) / "teams" / "thin-team"
    fixture_root.mkdir(parents=True)
    # Only 3 other games -- below MIN_OPPONENT_GAMES_FOR_PERCENTILE (6) -- must suppress the ranking claim.
    (fixture_root / "games.json").write_text(json.dumps([
        {"gameId": "1", "successRateAllowed": 0.40},
        {"gameId": "2", "successRateAllowed": 0.45},
        {"gameId": "3", "successRateAllowed": 0.35},
        {"gameId": "999", "successRateAllowed": 0.99},  # the game being excluded/analyzed
    ]))
    pct = percentile_within_opponent_season("thin-team", SEASON, "successRateAllowed", 0.5, "999", published_root=tmp_path)
    assert pct["percentile"] is None
    assert pct["rank"] is None
    assert pct["sampleSize"] == 3
    assert pct["sampleSizeCaveat"] is not None


def test_drive_funnel_matches_known_box_score():
    mi_game = _michigan_game()
    funnel = drive_funnel(mi_game, "")
    assert funnel["possessions"] == 10
    assert funnel["redZonePossessions"] == 8
    assert funnel["touchdowns"] == 6


def test_signal_classification_turnovers_always_noisy():
    assert classify_signal("turnoverMargin", "possessions", 10) == LIKELY_NOISY


def test_signal_classification_large_sample_is_strong():
    assert classify_signal("successRate", "successEligiblePlays", 70) == STRONG_SIGNAL


def test_build_game_stories_produces_honest_concern_for_a_bad_loss():
    """Michigan lost 9-27 to Ohio State in 2025 -- the top story must not be artificially positive."""
    games = json.loads((PUBLISHED_ROOT / str(SEASON) / "teams" / "michigan" / "games.json").read_text())
    game = next(g for g in games if g["opponent"] == "Ohio State")
    result = build_game_stories(game, "ohio-state", SEASON, str(game["gameId"]))
    assert len(result["stories"]) >= 3
    assert any(s["polarity"] == "concern" for s in result["stories"])


def test_build_game_stories_field_position_evidence_is_not_a_percentage():
    """Regression test: averageStartYardsToGoal is a yardage number, not a 0-1 rate -- must never render as e.g. '5990.0%'."""
    mi_game = _michigan_game()
    result = build_game_stories(mi_game, "maryland", SEASON, GAME_ID)
    fp_stories = [s for s in result["stories"] if s["metric"] == "averageStartYardsToGoal"]
    for s in fp_stories:
        for line in s["evidence"]:
            assert "%" not in line


@pytest.mark.skipif(not DRIVES_PRESENT or not CANONICAL_PRESENT, reason="derived drives/canonical plays not present in this checkout")
def test_drive_results_reproduce_the_final_score():
    from cfb_analytics.analytics.game_story.drive_result import drive_results_for_game

    drives = drive_results_for_game(SEASON, "regular", 13, GAME_ID)
    assert len(drives) == 19
    points = {"Michigan": 0, "Maryland": 0}
    for d in drives:
        if d["result"] == "TOUCHDOWN":
            points[d["scoredBy"]] += 7  # every TD this game had a made PAT, verified by hand
        elif d["result"] == "FIELD_GOAL":
            points[d["scoredBy"]] += 3
    assert points["Michigan"] == 45
    assert points["Maryland"] == 20
    assert sum(1 for d in drives if d["result"] == "UNKNOWN") == 0


@pytest.mark.skipif(not CANONICAL_PRESENT, reason="canonical plays not present in this checkout")
def test_half_split_totals_match_season_eligible_plays():
    from cfb_analytics.analytics.game_story.half_split import half_split_success_rate

    mi_game = _michigan_game()
    split = half_split_success_rate(SEASON, "regular", 13, GAME_ID, "Michigan")
    total_eligible = split["firstHalf"]["eligiblePlays"] + split["secondHalf"]["eligiblePlays"]
    assert total_eligible == mi_game["successEligiblePlays"]
