import json

import pytest

from cfb_analytics.analytics.iterative_ratings import SPECS
from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v2_2026_features import (
    _target_schedule,
    build_early_prior_feature_row,
)
from cfb_analytics.analytics.prediction_v2_early_prior_audit import REQUIRED_MECHANISM_FIELDS
from cfb_analytics.analytics.prediction_v2_early_prior_challenger import _build_variant_row
from cfb_analytics.raw.storage import partition_dir


def _mechanism_values(offset=0.0):
    values = {
        "OffSuccessRate": 0.50,
        "DefSuccessRateAllowed": 0.42,
        "OffExplosiveRate": 0.15,
        "DefExplosiveRateAllowed": 0.11,
        "OffGiveawayRate": 0.08,
        "DefTakeawayRate": 0.10,
        "OffPossessionsPerGame": 12.0,
        "DefPossessionsPerGame": 12.5,
    }
    return {field: values[field] + offset for field in REQUIRED_MECHANISM_FIELDS}


def _fixture():
    home = "Home"
    away = "Away"
    current = {
        "season": 2025,
        "seasonType": "regular",
        "week": 3,
        "gameId": "synthetic",
        "homeTeam": home,
        "awayTeam": away,
        "isNeutralSite": False,
        "homeIterativeGamesPlayedBefore": 2,
        "awayIterativeGamesPlayedBefore": 1,
        "currentSiteAwareHomeRating": 7.0,
        "currentSiteAwareAwayRating": -3.0,
        "siteAwareSrsHfaBefore": 2.4,
    }
    prior = {
        "iterative": {home: {}, away: {}},
        "siteRatings": {home: 5.0, away: -2.0},
        "hfa": 2.0,
        "mwdr": {
            home: {"Off": 0.9, "Def": 0.4},
            away: {"Off": -0.2, "Def": -0.5},
        },
        "mechanisms": {
            home: _mechanism_values(0.00),
            away: _mechanism_values(0.02),
        },
    }

    for index, (name, *_) in enumerate(SPECS):
        base = float(index + 1)
        prior["iterative"][home][f"{name}Offense"] = base + 0.6
        prior["iterative"][home][f"{name}Defense"] = base - 0.3
        prior["iterative"][away][f"{name}Offense"] = base - 0.4
        prior["iterative"][away][f"{name}Defense"] = base + 0.2
        current[f"home_iterative{name}Offense"] = base + 0.8
        current[f"home_iterative{name}Defense"] = base - 0.1
        current[f"away_iterative{name}Offense"] = base - 0.2
        current[f"away_iterative{name}Defense"] = base + 0.4

    current_mechanisms = {
        home: _mechanism_values(0.01),
        away: _mechanism_values(0.03),
    }
    mechanism_matchup = {"team1": home, "team2": away}
    for field in REQUIRED_MECHANISM_FIELDS:
        mechanism_matchup[f"team1_{field}"] = current_mechanisms[home][field]
        mechanism_matchup[f"team2_{field}"] = current_mechanisms[away][field]

    current_mwdr = {
        home: {"Off": 1.1, "Def": 0.5},
        away: {"Off": -0.1, "Def": -0.4},
    }
    sandbox_matchup = {
        "team1": home,
        "team2": away,
        "team1_Off_MWDR": current_mwdr[home]["Off"],
        "team1_Def_MWDR": current_mwdr[home]["Def"],
        "team2_Off_MWDR": current_mwdr[away]["Off"],
        "team2_Def_MWDR": current_mwdr[away]["Def"],
    }
    return current, prior, current_mechanisms, current_mwdr, mechanism_matchup, sandbox_matchup


def test_outcome_free_builder_matches_frozen_historical_feature_math():
    current, prior, mechanisms, mwdr, mechanism_matchup, sandbox_matchup = _fixture()
    historical_input = {
        **current,
        "target_margin": 7.0,
        "target_homeWin": 1,
    }
    historical = _build_variant_row(
        historical_input,
        prior,
        mechanism_matchup,
        sandbox_matchup,
        "blend",
    )
    prospective = build_early_prior_feature_row(current, prior, mechanisms, mwdr)

    assert historical is not None
    assert prospective is not None
    for feature in PREDICTION_V2_FEATURES:
        assert prospective[feature] == pytest.approx(historical[feature], abs=1e-12)
    assert prospective["priorWeightHome"] == historical["priorWeightHome"]
    assert prospective["priorWeightAway"] == historical["priorWeightAway"]
    assert not any(key.startswith("target_") for key in prospective)


def test_outcome_free_builder_rejects_target_fields():
    current, prior, mechanisms, mwdr, _, _ = _fixture()
    current["target_margin"] = 1.0
    with pytest.raises(ValueError, match="outcome-bearing target fields"):
        build_early_prior_feature_row(current, prior, mechanisms, mwdr)


def test_target_schedule_rejects_partition_after_scores_exist(tmp_path):
    raw_root = tmp_path / "raw"
    path = partition_dir(raw_root, 2026, "regular", 1)
    path.mkdir(parents=True)
    games_path = path / "games.json"
    base = {
        "id": 123,
        "homeTeam": "Home",
        "awayTeam": "Away",
        "neutralSite": False,
    }

    games_path.write_text(json.dumps([base]))
    rows = _target_schedule(raw_root, 2026, "regular", 1)
    assert len(rows) == 1
    assert rows[0]["gameId"] == "123"

    games_path.write_text(json.dumps([{**base, "homePoints": 21, "awayPoints": 17}]))
    with pytest.raises(ValueError, match="already contains scores"):
        _target_schedule(raw_root, 2026, "regular", 1)
