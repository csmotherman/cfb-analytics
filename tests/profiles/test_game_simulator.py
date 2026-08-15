from cfb_analytics.profiles.game_simulator import reconcile_score, simulate_matchup


def test_reconcile_score_matches_total_and_margin():
    home, away = reconcile_score(60.0, 10.0)
    assert abs((home + away) - 60.0) < 1e-12
    assert abs((home - away) - 10.0) < 1e-12


def test_simulation_is_reproducible(monkeypatch):
    home = {"season": 2023, "team": "A"}
    away = {"season": 2019, "team": "B"}

    monkeypatch.setattr("cfb_analytics.profiles.game_simulator.eligible_state", lambda s: True)
    monkeypatch.setattr(
        "cfb_analytics.profiles.game_simulator.matchup_features",
        lambda h, a: {"expectedPossessionsPerTeam": 12.0},
    )
    monkeypatch.setattr("cfb_analytics.profiles.game_simulator.predict_margin", lambda m, h, a: 7.0)
    monkeypatch.setattr("cfb_analytics.profiles.game_simulator.expected_total_points", lambda h, a, f: 55.0)

    model = {"residualSd": 14.0}
    x = simulate_matchup(model, home, away, simulations=1000, seed=7)
    y = simulate_matchup(model, home, away, simulations=1000, seed=7)
    assert x["homeWinProbability"] == y["homeWinProbability"]
    assert x["medianMarginHome"] == y["medianMarginHome"]
    assert abs((x["expectedHomeScore"] - x["expectedAwayScore"]) - 7.0) < 1e-12


def test_positive_expected_margin_favors_home(monkeypatch):
    home = {"season": 2023, "team": "A"}
    away = {"season": 2019, "team": "B"}
    monkeypatch.setattr("cfb_analytics.profiles.game_simulator.eligible_state", lambda s: True)
    monkeypatch.setattr(
        "cfb_analytics.profiles.game_simulator.matchup_features",
        lambda h, a: {"expectedPossessionsPerTeam": 12.0},
    )
    monkeypatch.setattr("cfb_analytics.profiles.game_simulator.predict_margin", lambda m, h, a: 10.0)
    monkeypatch.setattr("cfb_analytics.profiles.game_simulator.expected_total_points", lambda h, a, f: 60.0)

    result = simulate_matchup({"residualSd": 10.0}, home, away, simulations=5000, seed=1)
    assert result["homeWinProbability"] > 0.5
    assert result["expectedHomeScore"] > result["expectedAwayScore"]
