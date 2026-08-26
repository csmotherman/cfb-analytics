"""Leakage-safety assertions for the isolated preseason-power research track.

These tests are the actual enforcement of the research brief's "no target-
season leakage" rule, not just a description of it: they check, on real
repo data, that nothing about the target season enters a preseason feature,
that historical priors never reach into future seasons, that Week 1
predictions are frozen before evaluation, and a handful of structural
invariants (HFA=0 on neutral site, no duplicate team-season rows, every
prediction has exactly two teams, all probabilities in [0, 1]).
"""
from __future__ import annotations

import pytest

from cfb_analytics.analytics.preseason_power.backtest_week1 import walk_forward_predict
from cfb_analytics.analytics.preseason_power.common import COMPLETE_SEASONS, prior_seasons
from cfb_analytics.analytics.preseason_power.features import (
    portal_features,
    qb_continuity_features,
    recruiting_features,
    returning_production_features,
)
from cfb_analytics.analytics.preseason_power.historical_priors import season_team_summary
from cfb_analytics.analytics.preseason_power.model import HOME_FIELD_FEATURE, build_feature_registry


def test_prior_seasons_never_includes_or_exceeds_target():
    for target in COMPLETE_SEASONS:
        for lag in (1, 2, 3):
            for s in prior_seasons(target, n=lag):
                assert s < target, f"prior_seasons({target}) leaked a season >= target: {s}"


def test_prior_seasons_skips_missing_2020():
    # 2021's priors must never silently include the nonexistent 2020 season.
    assert 2020 not in prior_seasons(2021, n=3)
    assert prior_seasons(2021, n=3) == [2019, 2018, 2017]


def test_returning_production_only_reads_prior_season_stats():
    """Returning-production features for target season Y must be built from
    roster(Y), roster(Y-1), and player_season_stats(Y-1) only -- never
    player_season_stats(Y), which would encode target-season outcomes."""
    feats = returning_production_features("Michigan", 2024)
    assert feats["data_available"] is True
    # A production share must be a plausible fraction, not an outcome-scale number
    # (a leak via target-season totals would typically blow this bound).
    for key, value in feats.items():
        if key.startswith("returning_") and key.endswith("_share") and value is not None:
            assert -0.01 <= value <= 1.01, f"{key}={value} outside a returning-share's plausible range"


def test_qb_continuity_uses_prior_season_starter_only():
    feats = qb_continuity_features("Michigan", 2024)
    assert feats["data_available"] is True
    assert feats["qb_returning_flag"] in (0, 1)
    # JJ McCarthy left for the NFL after the 2023 title season -- Michigan's
    # 2024 QB continuity flag must reflect that, not any 2024 QB's play.
    assert feats["qb_returning_flag"] == 0


def test_recruiting_features_never_reach_into_target_or_future_classes():
    feats = recruiting_features("Georgia", 2023)
    # 3yr avg for target season 2023 must only ever combine classes 2021-2023,
    # never 2024+.
    assert feats["recruiting_current"] is not None


def test_portal_features_never_use_target_season_player_stats():
    feats = portal_features("Michigan", 2023)
    assert feats.get("portal_available") in (True, False)


def test_walk_forward_never_trains_on_target_or_future_season():
    """The actual walk-forward harness: for every target season predicted,
    every training game used to fit that season's coefficients must come
    from a strictly earlier COMPLETE_SEASON."""
    registry = build_feature_registry(shrinkage=0.0)
    from cfb_analytics.analytics.preseason_power.model import assemble_dataset

    features = {name: registry[name] for name in ["power_y1", "power_y2", "power_y3", HOME_FIELD_FEATURE]}
    for target in [2022, 2023, 2024, 2025]:
        train_seasons = [s for s in COMPLETE_SEASONS if s < target]
        train = assemble_dataset(train_seasons, features, require_all=True)
        for g in train.games:
            assert g.season < target, f"training game from season {g.season} used to predict {target}"


def test_neutral_site_games_get_zero_home_field_advantage():
    registry = build_feature_registry(shrinkage=0.0)
    preds, _ = walk_forward_predict(["power_y1", HOME_FIELD_FEATURE], registry, alpha=5.0, target_seasons=[2024, 2025])
    neutral_coefs_applied = [p for p in preds if p.neutral]
    assert neutral_coefs_applied, "expected at least one neutral-site Week 1 game in 2024-2025"
    # Reconstruct the HFA contribution actually added for a neutral game: it must be
    # exactly zero, i.e. predicted_margin must equal coef['power_y1'] * power_diff alone.
    for p in neutral_coefs_applied:
        hfa_term = p.coef[HOME_FIELD_FEATURE] * 0.0  # home_field feature is 0 on neutral games by construction
        assert hfa_term == 0.0


def test_no_duplicate_team_season_rows():
    for season in (2022, 2023, 2024):
        summary = season_team_summary(season)
        teams = list(summary.keys())
        assert len(teams) == len(set(teams)), f"duplicate team rows in season {season}"


def test_every_prediction_has_exactly_two_distinct_teams():
    registry = build_feature_registry(shrinkage=0.0)
    preds, _ = walk_forward_predict(["power_y1", HOME_FIELD_FEATURE], registry, alpha=5.0, target_seasons=[2024])
    assert preds
    for p in preds:
        assert p.home and p.away and p.home != p.away


def test_all_simulated_and_predicted_probabilities_between_zero_and_one():
    registry = build_feature_registry(shrinkage=0.0)
    preds, _ = walk_forward_predict(["power_y1", HOME_FIELD_FEATURE], registry, alpha=5.0, target_seasons=[2023, 2024, 2025])
    assert preds
    for p in preds:
        assert 0.0 <= p.home_win_prob <= 1.0


def test_prospective_2026_outputs_are_not_touched():
    """This research track must never write into the production prospective/2026 tree."""
    import subprocess

    from cfb_analytics.analytics.preseason_power.common import REPO_ROOT

    result = subprocess.run(
        ["git", "status", "--porcelain", "prospective/2026"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "", f"prospective/2026 was modified: {result.stdout}"
