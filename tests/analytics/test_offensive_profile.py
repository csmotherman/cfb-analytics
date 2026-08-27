"""Tests for the Michigan Offensive Profile radar data pipeline.

Runs against real repository data (data/raw, data/canonical, data/processed)
rather than synthetic fixtures, matching this repo's existing convention for
analytics pipeline tests -- the whole point is validating what the real
2014-2025 corpus actually produces, not a hand-built toy case.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from cfb_analytics.aggregations.rankings import Metric, add_rankings
from cfb_analytics.analytics.offensive_profile import (
    PROFILE_METRICS,
    SEASONS_2020_ONLY_RAW,
    build_offensive_profile,
    compute_national_offensive_metrics,
)

RAW_ROOT = Path("data/raw")
PROCESSED_ROOT = Path("data/processed")
CANONICAL_ROOT = Path("data/canonical")
PUBLISHED_ROOT = Path("data/published")

# Seasons cheap enough to exercise directly in tests (small field, fast to
# recompute); the full 2014-2025 sweep is exercised once by the publish CLI,
# not per-test, to keep the suite fast.
SMALL_SEASON = 2016


# ---------------------------------------------------------------------------
# 1. Percentile conversion
# ---------------------------------------------------------------------------

def test_percentile_conversion_basic():
    rows = [{"team": "A", "x": 10.0}, {"team": "B", "x": 20.0}, {"team": "C", "x": 30.0}]
    metric = Metric("x", "X", "unit", True, "cat", "offense")
    ranked = add_rankings(rows, metrics=[metric], prefix="")
    by_team = {r["team"]: r for r in ranked}
    # Best (highest) value -> rank 1, percentile 100.
    assert by_team["C"]["x_rank"] == 1
    assert by_team["C"]["x_percentile"] == 1.0
    # Worst (lowest) value -> last rank, percentile 0.
    assert by_team["A"]["x_rank"] == 3
    assert by_team["A"]["x_percentile"] == 0.0
    # Middle value -> exactly 0.5.
    assert by_team["B"]["x_percentile"] == 0.5


def test_percentile_conversion_ties_are_tie_safe():
    rows = [{"team": "A", "x": 10.0}, {"team": "B", "x": 10.0}, {"team": "C", "x": 20.0}]
    metric = Metric("x", "X", "unit", True, "cat", "offense")
    ranked = add_rankings(rows, metrics=[metric], prefix="")
    by_team = {r["team"]: r for r in ranked}
    # Tied teams must receive the same rank, not sequential ranks.
    assert by_team["A"]["x_rank"] == by_team["B"]["x_rank"] == 2
    assert by_team["A"]["x_percentile"] == by_team["B"]["x_percentile"]


# ---------------------------------------------------------------------------
# 2. Inverted lower-is-better metrics
# ---------------------------------------------------------------------------

def test_lower_is_better_percentile_is_inverted():
    """A lower-is-better metric's best (lowest) raw value must still map to
    the highest percentile -- the radar's whole premise is 'outward = better'
    regardless of the metric's own direction."""
    rows = [{"team": "A", "x": 0.05}, {"team": "B", "x": 0.15}, {"team": "C", "x": 0.30}]
    metric = Metric("x", "X", "rate", False, "cat", "offense")  # lower is better
    ranked = add_rankings(rows, metrics=[metric], prefix="")
    by_team = {r["team"]: r for r in ranked}
    assert by_team["A"]["x_percentile"] == 1.0  # lowest raw value, best percentile
    assert by_team["C"]["x_percentile"] == 0.0  # highest raw value, worst percentile


def test_stuff_rate_and_havoc_are_flagged_lower_is_better():
    stuff = next(m for m in PROFILE_METRICS if m.name == "stuff_rate")
    havoc = next(m for m in PROFILE_METRICS if m.name == "havoc_rate_allowed")
    assert stuff.higher_is_better is False
    assert havoc.higher_is_better is False
    # Every other metric in the radar should be higher-is-better.
    others = [m for m in PROFILE_METRICS if m.name not in ("stuff_rate", "havoc_rate_allowed")]
    assert all(m.higher_is_better for m in others)


# ---------------------------------------------------------------------------
# 3. Metric bounds, on real computed data
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not (RAW_ROOT / "cfbd" / f"season={SMALL_SEASON}").exists(), reason="raw play-by-play not present in this checkout")
def test_real_season_percentiles_and_ranks_are_in_bounds():
    profile = build_offensive_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, PUBLISHED_ROOT, SMALL_SEASON, "Michigan")
    assert profile["team"] == "Michigan"
    assert profile["season"] == SMALL_SEASON
    assert len(profile["metrics"]) == len(PROFILE_METRICS) == 12
    for m in profile["metrics"]:
        assert 0.0 <= m["percentile"] <= 100.0
        assert 1 <= m["rank"] <= m["fieldSize"]
        assert m["fieldSize"] == profile["fieldSize"]
        assert m["fieldSize"] > 100  # a real FBS-sized field, not a stub


@pytest.mark.skipif(not (RAW_ROOT / "cfbd" / f"season={SMALL_SEASON}").exists(), reason="raw play-by-play not present in this checkout")
def test_reused_metrics_match_locked_team_seasons_exactly():
    """explosive_play_rate/pass_success_rate/havoc_rate_allowed/yards_per_dropback
    must be read verbatim from team_seasons.json, never recomputed, for any
    season where that locked artifact exists."""
    import json

    profile = build_offensive_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, PUBLISHED_ROOT, SMALL_SEASON, "Michigan")
    team_seasons_path = PROCESSED_ROOT / "derived" / "seasons" / f"season={SMALL_SEASON}" / "team_seasons.json"
    mich = next(r for r in json.loads(team_seasons_path.read_text()) if r["team"] == "Michigan")
    by_key = {m["key"]: m for m in profile["metrics"]}
    assert by_key["explosive_play_rate"]["value"] == round(mich["explosivePlayRate"], 4)
    assert by_key["pass_success_rate"]["value"] == round(mich["passSuccessRate"], 4)
    assert by_key["havoc_rate_allowed"]["value"] == round(mich["havocRateAllowed"], 4)
    assert by_key["yards_per_dropback"]["value"] == round(mich["netPassYardsPerDropback"], 4)


# ---------------------------------------------------------------------------
# 4. Missing-data / unknown-team handling
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not (RAW_ROOT / "cfbd" / f"season={SMALL_SEASON}").exists(), reason="raw play-by-play not present in this checkout")
def test_unknown_team_raises_rather_than_fabricating():
    with pytest.raises(ValueError):
        build_offensive_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, PUBLISHED_ROOT, SMALL_SEASON, "Not A Real Team")


# ---------------------------------------------------------------------------
# 5. 2020 handling
# ---------------------------------------------------------------------------

def test_2020_is_the_only_season_using_the_raw_fallback_path():
    assert SEASONS_2020_ONLY_RAW == {2020}


@pytest.mark.skipif(not (RAW_ROOT / "cfbd_facts" / "season=2020").exists(), reason="2020 raw play-by-play not present in this checkout")
def test_2020_produces_a_complete_profile_with_a_sample_size_caveat():
    profile = build_offensive_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, PUBLISHED_ROOT, 2020, "Michigan")
    assert profile["season"] == 2020
    assert len(profile["metrics"]) == 12
    assert all(m["percentile"] is not None for m in profile["metrics"]), "2020 must not silently omit any metric"
    assert profile["sampleSizeCaveat"] is not None
    assert "2020" in profile["sampleSizeCaveat"] or "COVID" in profile["sampleSizeCaveat"]
    # A real, plausible FBS field size for the COVID season (not every team played).
    assert 100 <= profile["fieldSize"] <= 136


@pytest.mark.skipif(not (RAW_ROOT / "cfbd_facts" / "season=2020").exists(), reason="2020 raw play-by-play not present in this checkout")
def test_2020_national_metrics_cover_multiple_teams_not_just_michigan():
    metrics = compute_national_offensive_metrics(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, 2020)
    assert "Michigan" in metrics
    assert len(metrics) > 100  # a real national FBS cohort, not a single team
