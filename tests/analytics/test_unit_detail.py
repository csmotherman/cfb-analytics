"""Tests for the full offense/defense analytics-page data pipeline
(unit_detail.py) -- the ~31-metric breakdown behind the 12-metric radar.

Runs against real repository data, matching this repo's and
test_offensive_profile.py's convention.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from cfb_analytics.analytics.unit_detail import (
    SPECS,
    _season_2020_ts_fallback,
    build_unit_detail_profile,
    build_unit_detail_rows,
)

RAW_ROOT = Path("data/raw")
PROCESSED_ROOT = Path("data/processed")
CANONICAL_ROOT = Path("data/canonical")
PUBLISHED_ROOT = Path("data/published")
SMALL_SEASON = 2016

# Fields that legitimately cannot be computed for 2020 without drive-level
# validation this repo has never built for that season's drives.
EXPECTED_2020_GAPS = {"red_zone_scoring_rate", "red_zone_td_rate", "points_per_drive", "interceptions_per_game", "turnovers_per_game"}


def test_spec_count_and_group_coverage():
    assert len(SPECS) == 31
    groups = {s.group for s in SPECS}
    assert groups == {"Efficiency", "Explosiveness", "Line Play", "Passing", "Situational", "Havoc & Turnovers"}


@pytest.mark.skipif(not (RAW_ROOT / "cfbd" / f"season={SMALL_SEASON}").exists(), reason="raw play-by-play not present in this checkout")
def test_real_season_both_sides_full_bounds():
    for side in ("offense", "defense"):
        profile = build_unit_detail_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, SMALL_SEASON, "Michigan", side)
        assert len(profile["metrics"]) == 31
        assert profile["side"] == side
        for m in profile["metrics"]:
            assert 0.0 <= m["percentile"] <= 100.0
            assert 1 <= m["rank"] <= m["fieldSize"]
            assert m["group"] in profile["groups"]


@pytest.mark.skipif(not (RAW_ROOT / "cfbd" / f"season={SMALL_SEASON}").exists(), reason="raw play-by-play not present in this checkout")
def test_offense_and_defense_are_genuinely_different_teams_perspective():
    """A team's own offense and defense metrics for the same season must not
    be identical -- this would indicate the offense/defense split silently
    collapsed to one side."""
    off = build_unit_detail_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, SMALL_SEASON, "Michigan", "offense")
    dfn = build_unit_detail_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, SMALL_SEASON, "Michigan", "defense")
    off_values = [m["value"] for m in off["metrics"] if m["value"] is not None]
    def_values = [m["value"] for m in dfn["metrics"] if m["value"] is not None]
    assert off_values != def_values


def test_invalid_side_raises():
    with pytest.raises(ValueError):
        build_unit_detail_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, SMALL_SEASON, "Michigan", "special_teams")


# ---------------------------------------------------------------------------
# 2020
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not (RAW_ROOT / "cfbd_facts" / "season=2020").exists(), reason="2020 raw play-by-play not present in this checkout")
def test_2020_only_the_documented_five_metrics_are_unavailable():
    for side in ("offense", "defense"):
        profile = build_unit_detail_profile(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, 2020, "Michigan", side)
        assert profile["sampleSizeCaveat"] is not None
        missing = {m["key"] for m in profile["metrics"] if m["percentile"] is None}
        assert missing == EXPECTED_2020_GAPS, f"{side}: unexpected gap set {missing}"
        # every present metric must still be in-bounds
        for m in profile["metrics"]:
            if m["percentile"] is not None:
                assert 0.0 <= m["percentile"] <= 100.0
                assert 1 <= m["rank"] <= m["fieldSize"]


@pytest.mark.skipif(not (RAW_ROOT / "cfbd_facts" / "season=2020").exists(), reason="2020 raw play-by-play not present in this checkout")
def test_2020_turnover_fields_are_none_not_a_fabricated_near_zero():
    """Regression test for a real bug found during development: turnover
    counting was nested inside success.py's strict eligibility gate, which
    excludes any play whose text merely mentions fumble/intercept -- i.e.
    every real turnover play -- so it always silently produced ~0 for every
    team. The fix is to report None (honestly unavailable) rather than a
    confidently wrong near-zero count."""
    fallback = _season_2020_ts_fallback(RAW_ROOT, CANONICAL_ROOT)
    assert fallback["Michigan"]["giveaways"] is None
    assert fallback["Michigan"]["takeaways"] is None
    assert fallback["Michigan"]["interceptionsThrown"] is None
    assert fallback["Michigan"]["interceptionsMade"] is None


@pytest.mark.skipif(not (RAW_ROOT / "cfbd_facts" / "season=2020").exists(), reason="2020 raw play-by-play not present in this checkout")
def test_2020_havoc_and_tfl_are_real_nonzero_values_not_swept_up_by_the_same_bug():
    """The turnover bug (above) must not have also zeroed out TFL/havoc,
    which use a real per-play classifier (classify_tfl) rather than the
    broken isTurnover-under-`eligible` path."""
    fallback = _season_2020_ts_fallback(RAW_ROOT, CANONICAL_ROOT)
    mich = fallback["Michigan"]
    assert mich["tacklesForLoss"] > 0
    assert mich["tacklesForLossAllowed"] > 0
    assert mich["havocRate"] is not None and mich["havocRate"] > 0
    assert mich["havocRateAllowed"] is not None and mich["havocRateAllowed"] > 0
    # sanity range: this repo's real (non-2020) havoc rates run ~5-15%; a
    # value wildly outside that would indicate a different denominator bug.
    assert 0.02 <= mich["havocRate"] <= 0.25
    assert 0.02 <= mich["havocRateAllowed"] <= 0.25


@pytest.mark.skipif(not (RAW_ROOT / "cfbd_facts" / "season=2020").exists(), reason="2020 raw play-by-play not present in this checkout")
def test_2020_rows_cover_a_real_national_field():
    rows = build_unit_detail_rows(RAW_ROOT, PROCESSED_ROOT, CANONICAL_ROOT, 2020)
    assert len(rows) > 100
    assert any(r["team"] == "Michigan" for r in rows)
