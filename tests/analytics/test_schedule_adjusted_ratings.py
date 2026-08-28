from __future__ import annotations

from math import exp
from pathlib import Path
import json

import pytest

from cfb_analytics.analytics.schedule_adjusted import METRIC_SPECS, MatchupObservation, MetricSpec, build_observations, evaluate_game_metric, fit_schedule_adjusted


def logistic(x: float) -> float: return 1.0 / (1.0 + exp(-x))


def gaussian_obs(game: str, offense: str, defense: str, value: float, weight: float = 100.0) -> MatchupObservation:
    return MatchupObservation(game, offense, defense, offense, defense, value * weight, weight)


def test_gaussian_fit_recovers_connected_schedule_effects() -> None:
    spec = MetricSpec("toy", "num", "den", "gaussian", True, "Toy", "units")
    teams = ("A", "B", "C", "D")
    offense = {"A": 1.2, "B": 0.4, "C": -0.5, "D": -1.1}
    defense = {"A": 0.8, "B": -0.3, "C": 0.6, "D": -1.1}
    mu = 5.0
    observations = []
    game = 0
    for off in teams:
        for deff in teams:
            if off == deff: continue
            game += 1
            observations.append(gaussian_obs(str(game), off, deff, mu + offense[off] - defense[deff]))
    result = fit_schedule_adjusted(observations, spec, ridge=1e-10, fit_home_field=False)
    assert result.league_average_raw() == pytest.approx(mu, abs=1e-7)
    for team in teams:
        assert result.offense_effects[team] == pytest.approx(offense[team], abs=1e-6)
        assert result.defense_effects[team] == pytest.approx(defense[team], abs=1e-6)
    assert sum(result.offense_effects.values()) == pytest.approx(0.0, abs=1e-10)
    assert sum(result.defense_effects.values()) == pytest.approx(0.0, abs=1e-10)


def test_same_raw_game_can_mean_different_quality_after_full_network_adjustment() -> None:
    spec = MetricSpec("toy", "num", "den", "gaussian", True, "Toy", "units")
    teams = ("A", "X", "B", "Y", "C")
    offense = {"A": 1.0, "X": -1.0, "B": 0.3, "Y": -0.3, "C": 0.0}
    defense = {"A": 0.0, "X": 0.0, "B": 1.0, "Y": -1.0, "C": 0.0}
    mu = 5.0
    observations = []
    game = 0
    raw_ab = raw_xy = None
    for off in teams:
        for deff in teams:
            if off == deff: continue
            game += 1
            value = mu + offense[off] - defense[deff]
            observations.append(gaussian_obs(str(game), off, deff, value, 200.0))
            if (off, deff) == ("A", "B"): raw_ab = value
            if (off, deff) == ("X", "Y"): raw_xy = value
    assert raw_ab == pytest.approx(raw_xy)
    result = fit_schedule_adjusted(observations, spec, ridge=1e-10, fit_home_field=False)
    assert result.offense_effects["A"] > result.offense_effects["X"] + 1.5
    assert result.defense_effects["B"] > result.defense_effects["Y"] + 1.5


def test_binomial_fit_recovers_offense_and_defense_order() -> None:
    spec = MetricSpec("rate", "success", "trials", "binomial", True, "Rate", "rate")
    teams = ("A", "B", "C", "D")
    offense = {"A": 0.8, "B": 0.25, "C": -0.25, "D": -0.8}
    defense = {"A": 0.6, "B": 0.2, "C": -0.2, "D": -0.6}
    intercept = -0.15
    observations = []
    game = 0
    trials = 20_000.0
    for off in teams:
        for deff in teams:
            if off == deff: continue
            game += 1
            p = logistic(intercept + offense[off] - defense[deff])
            observations.append(MatchupObservation(str(game), off, deff, off, deff, round(p * trials), trials))
    result = fit_schedule_adjusted(observations, spec, ridge=1e-6, fit_home_field=False, tol=1e-11)
    assert result.converged
    assert [row.team for row in result.offense_rankings()] == ["A", "B", "C", "D"]
    assert [row.team for row in result.defense_rankings()] == ["A", "B", "C", "D"]
    assert result.league_average_raw() == pytest.approx(logistic(intercept), abs=3e-4)


def test_lower_is_better_rate_has_consistent_effect_semantics() -> None:
    spec = METRIC_SPECS["sackRate"]
    rows = [
        {"gameId":"1","team_id":1,"opponent_id":3,"team":"Good O","opponent":"D1","sacksAllowed":1,"dropbacks":50,"neutral_site":True},
        {"gameId":"2","team_id":1,"opponent_id":4,"team":"Good O","opponent":"D2","sacksAllowed":2,"dropbacks":50,"neutral_site":True},
        {"gameId":"3","team_id":2,"opponent_id":3,"team":"Bad O","opponent":"D1","sacksAllowed":8,"dropbacks":50,"neutral_site":True},
        {"gameId":"4","team_id":2,"opponent_id":4,"team":"Bad O","opponent":"D2","sacksAllowed":9,"dropbacks":50,"neutral_site":True},
        {"gameId":"5","team_id":3,"opponent_id":1,"team":"D1","opponent":"Good O","sacksAllowed":4,"dropbacks":50,"neutral_site":True},
        {"gameId":"6","team_id":4,"opponent_id":2,"team":"D2","opponent":"Bad O","sacksAllowed":4,"dropbacks":50,"neutral_site":True},
    ]
    result = fit_schedule_adjusted(build_observations(rows, spec), spec, ridge=2.0, fit_home_field=False)
    assert result.offense_effects["1"] > result.offense_effects["2"]
    assert result.adjusted_offense_value("1") < result.adjusted_offense_value("2")


def test_builder_uses_counts_not_stored_display_rate_and_deduplicates() -> None:
    spec = METRIC_SPECS["successRate"]
    row = {"gameId":"g1","season":2025,"team_id":1,"opponent_id":2,"team":"A","opponent":"B","successfulPlays":30,"successEligiblePlays":60,"successRate":0.999,"home_away":"home","neutral_site":False,"gameValidationStatus":"PASS"}
    observations = build_observations([row, dict(row)], spec, season=2025)
    assert len(observations) == 1
    assert observations[0].raw_value == pytest.approx(0.5)
    assert observations[0].venue == 1.0


def _network_rows(target_successes: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    games = [("1",1,"A",3,"C",28,60),("2",1,"A",4,"D",30,60),("3",2,"B",3,"C",23,60),("4",2,"B",4,"D",25,60),("5",3,"C",1,"A",24,60),("6",4,"D",2,"B",26,60)]
    for game_id, team_id, team, opp_id, opp, successes, trials in games:
        rows.append({"gameId":game_id,"team_id":team_id,"opponent_id":opp_id,"team":team,"opponent":opp,"successfulPlays":successes,"successEligiblePlays":trials,"neutral_site":True})
    rows.extend([
        {"gameId":"target","team_id":1,"opponent_id":2,"team":"A","opponent":"B","successfulPlays":target_successes,"successEligiblePlays":60,"neutral_site":True},
        {"gameId":"target","team_id":2,"opponent_id":1,"team":"B","opponent":"A","successfulPlays":27,"successEligiblePlays":60,"neutral_site":True},
    ])
    return rows


def test_game_evaluation_is_strict_leave_one_game_out() -> None:
    low = evaluate_game_metric(_network_rows(10), game_id="target", team=1, metric="successRate", ridge=3.0, fit_home_field=False)
    high = evaluate_game_metric(_network_rows(55), game_id="target", team=1, metric="successRate", ridge=3.0, fit_home_field=False)
    assert low.expected == pytest.approx(high.expected, abs=1e-12)
    assert low.adjusted_subject_value == pytest.approx(high.adjusted_subject_value, abs=1e-12)
    assert low.performance_over_expected < high.performance_over_expected


def test_defense_perspective_reverses_performance_sign() -> None:
    rows = _network_rows(40)
    offense_eval = evaluate_game_metric(rows, game_id="target", team=1, metric="successRate", perspective="offense", ridge=3.0, fit_home_field=False)
    defense_eval = evaluate_game_metric(rows, game_id="target", team=2, metric="successRate", perspective="defense", ridge=3.0, fit_home_field=False)
    assert defense_eval.actual == pytest.approx(offense_eval.actual)
    assert defense_eval.expected == pytest.approx(offense_eval.expected)
    assert defense_eval.performance_over_expected == pytest.approx(-offense_eval.performance_over_expected)


def test_registry_pairs_reproduce_real_2025_michigan_published_values() -> None:
    path = Path("data/published/2025/teams/michigan/games.json")
    if not path.exists(): pytest.skip("published Michigan fixture not available")
    games = json.loads(path.read_text())
    for name, spec in METRIC_SPECS.items():
        checked = 0
        for row in games:
            numerator, denominator, stored = row.get(spec.numerator_field), row.get(spec.denominator_field), row.get(name)
            if isinstance(numerator,(int,float)) and not isinstance(numerator,bool) and isinstance(denominator,(int,float)) and not isinstance(denominator,bool) and denominator > 0 and isinstance(stored,(int,float)) and not isinstance(stored,bool):
                assert numerator / denominator == pytest.approx(stored, abs=1e-12), name
                checked += 1
        assert checked > 0, f"no published verification rows for {name}"
