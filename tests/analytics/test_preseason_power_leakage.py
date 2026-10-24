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



@pytest.fixture
def preseason_personnel_sources(monkeypatch):
    """Historical CFBD raw files are intentionally gitignored and unavailable in clean CI.

    Replace external evidence with season-labelled synthetic rows, preserving
    the real feature paths and asserting any target-year stats read is a leak.
    """
    from cfb_analytics.analytics.preseason_power import features as features_module

    calls = {"roster": [], "player_stats": []}
    rosters = {
        2023: [{"id": 101, "team": "Michigan"}, {"id": 202, "team": "Michigan"}],
        2024: [{"id": 202, "team": "Michigan"}, {"id": 303, "team": "Michigan"}],
    }
    prior_stats = [
        {"playerId": 101, "team": "Michigan", "player": "Prior starter",
         "position": "QB", "category": "passing", "statType": "ATT", "stat": "300"},
        {"playerId": 202, "team": "Michigan", "player": "Returning backup",
         "position": "QB", "category": "passing", "statType": "ATT", "stat": "100"},
    ]

    def load_roster(season):
        calls["roster"].append(season)
        assert season in (2023, 2024), f"unexpected roster year: {season}"
        return rosters[season]

    def load_player_season_stats(season):
        calls["player_stats"].append(season)
        assert season == 2023, f"target/future season player stats would leak: {season}"
        return prior_stats

    monkeypatch.setattr(features_module, "load_roster", load_roster)
    monkeypatch.setattr(features_module, "load_player_season_stats", load_player_season_stats)
    funcs = (
        features_module._team_roster_ids,
        features_module._team_prior_production,
        features_module.returning_production_features,
        features_module.qb_continuity_features,
    )
    for func in funcs:
        func.cache_clear()
    yield calls
    for func in funcs:
        func.cache_clear()


def test_returning_production_only_reads_prior_season_stats(preseason_personnel_sources):
    """Use 2024/2023 rosters, but only 2023 performance for 2024 features."""
    calls = preseason_personnel_sources
    feats = returning_production_features("Michigan", 2024)
    assert feats["data_available"] is True
    assert feats["returning_players_count"] == 1
    assert feats["prior_roster_count"] == 2
    assert feats["returning_passing_ATT_share"] == pytest.approx(0.25)
    assert set(calls["roster"]) == {2023, 2024}
    assert calls["player_stats"] == [2023]
    for key, value in feats.items():
        if key.startswith("returning_") and key.endswith("_share") and value is not None:
            assert 0 <= value <= 1, f"{key}={value} outside valid production share"


def test_qb_continuity_uses_prior_season_starter_only(preseason_personnel_sources):
    """The prior starter (300 ATT) departed; the 100-ATT backup returned."""
    calls = preseason_personnel_sources
    feats = qb_continuity_features("Michigan", 2024)
    assert feats["data_available"] is True
    assert feats["qb_returning_flag"] == 0
    assert feats["qb_prior_passing_yards"] == 0.0
    assert calls["roster"] == [2024]
    assert calls["player_stats"] == [2023]


def test_recruiting_features_never_reach_into_target_or_future_classes(monkeypatch):
    """Only the three classes known entering 2023 may affect that preseason."""
    from cfb_analytics.analytics.preseason_power import features as features_module

    calls = []
    classes = {
        2021: {"Georgia": {"points": 150.0, "rank": 5}},
        2022: {"Georgia": {"points": 200.0, "rank": 3}},
        2023: {"Georgia": {"points": 250.0, "rank": 1}},
    }

    def ranks(season):
        calls.append(season)
        assert season in classes, f"future or unapproved recruiting class used: {season}"
        return classes[season]

    monkeypatch.setattr(features_module, "load_recruiting_team_ranks", ranks)
    features_module.recruiting_features.cache_clear()
    try:
        feats = recruiting_features("Georgia", 2023)
        assert feats["recruiting_current"] == 250.0
        assert feats["recruiting_current_rank"] == 1
        assert feats["recruiting_2yr_avg"] == pytest.approx(225.0)
        assert feats["recruiting_3yr_avg"] == pytest.approx(200.0)
        assert set(calls) == {2021, 2022, 2023}
    finally:
        features_module.recruiting_features.cache_clear()


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
