from cfb_analytics.analytics.football_mechanisms import TEAM_FIELDS
from cfb_analytics.analytics.iterative_ratings import SPECS
from cfb_analytics.profiles.historical_tournament import (
    INDEX,
    LEADING,
    neutral_prediction,
    simulate_field,
)


def _state(season, team, srs):
    row = {
        "season": season,
        "team": team,
        "key": f"{season}::{team}",
        "games": 12,
        "srs": float(srs),
        "MWDR_Off": 0.0,
        "MWDR_Def": 0.0,
    }
    for field in TEAM_FIELDS:
        row[field] = 0.5
    row["OffPossessionsPerGame"] = 10.0
    row["DefPossessionsPerGame"] = 10.0
    for name, *_ in SPECS:
        row[f"iterative{name}Offense"] = 0.0
        row[f"iterative{name}Defense"] = 0.0
    return row


def _srs_only_model(intercept=3.0, residual_sd=14.0):
    weights = [0.0] * (len(LEADING) + 1)
    weights[0] = float(intercept)
    weights[INDEX["srsEdge"] + 1] = 1.0
    return {
        "features": LEADING,
        "weights": weights,
        "means": [0.0] * len(LEADING),
        "scales": [1.0] * len(LEADING),
        "trainingRows": 100,
        "residualSd": float(residual_sd),
    }


def test_neutral_prediction_cancels_home_intercept():
    model = _srs_only_model(intercept=4.25)
    a = _state(2019, "A", 12.0)
    b = _state(2023, "B", 5.0)
    assert abs(neutral_prediction(model, a, b) - 7.0) < 1e-12
    assert abs(neutral_prediction(model, b, a) + 7.0) < 1e-12


def test_all_vs_all_ranking_orders_stronger_synthetic_teams():
    model = _srs_only_model()
    states = [
        _state(2019, "Elite", 20.0),
        _state(2021, "Good", 10.0),
        _state(2023, "Average", 0.0),
        _state(2025, "Weak", -10.0),
    ]
    report = simulate_field(states, model, min_games=6)
    assert report["pairCount"] == 6
    assert [r["team"] for r in report["rankings"]] == ["Elite", "Good", "Average", "Weak"]
    assert report["rankings"][0]["expectedWinPct"] > report["rankings"][-1]["expectedWinPct"]


def test_every_pair_is_simulated_once():
    model = _srs_only_model()
    states = [_state(2014 + i, f"T{i}", i) for i in range(5)]
    report = simulate_field(states, model)
    assert report["teamSeasonCount"] == 5
    assert report["pairCount"] == 10
    assert all(r["simulatedOpponents"] == 4 for r in report["rankings"])
