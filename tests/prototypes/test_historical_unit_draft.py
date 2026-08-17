from __future__ import annotations

import math

from cfb_analytics.prototypes.historical_unit_draft import (
    CATEGORY_ORDER,
    _oracle_assignment,
    _season_category_scores,
    evaluate_selections,
    fit_strength_model,
    greedy_draft,
    neutral_win_probability,
)


def _raw_team(team: str, shift: float, srs: float) -> dict:
    # Every path used by CATEGORY_SPECS is populated. Higher shift means a stronger
    # offense/positive havoc profile and a stingier defense (defensive rates are
    # explicitly inverted below where lower is better).
    return {
        "season": 2019,
        "team": team,
        "srs": srs,
        "sp": {
            "offense": {
                "standardDowns": 1.0 + shift,
                "passingDowns": 1.2 + shift,
                "success": 2.0 + shift,
                "rushing": 2.5 + shift,
                "passing": 3.0 + shift,
            },
            "defense": {
                "passing": 3.0 - shift,
                "rushing": 2.5 - shift,
                "success": 2.0 - shift,
            },
        },
        "advanced": {
            "offense": {
                "standardDowns": {"successRate": 0.40 + shift * 0.01},
                "passingDowns": {"successRate": 0.30 + shift * 0.01},
                "pointsPerOpportunity": 3.0 + shift * 0.10,
                "rushingPlays": {
                    "successRate": 0.40 + shift * 0.01,
                    "ppa": 0.10 + shift * 0.01,
                    "explosiveness": 1.0 + shift * 0.05,
                },
                "passingPlays": {
                    "successRate": 0.40 + shift * 0.01,
                    "ppa": 0.10 + shift * 0.01,
                    "explosiveness": 1.0 + shift * 0.05,
                },
                "secondLevelYards": 1.0 + shift * 0.10,
                "openFieldYards": 0.5 + shift * 0.10,
                "lineYards": 2.5 + shift * 0.10,
                "stuffRate": 0.20 - shift * 0.005,
                "powerSuccess": 0.60 + shift * 0.01,
                "successRate": 0.40 + shift * 0.01,
            },
            "defense": {
                "passingPlays": {
                    "successRate": 0.45 - shift * 0.01,
                    "ppa": 0.15 - shift * 0.01,
                    "explosiveness": 1.2 - shift * 0.05,
                },
                "rushingPlays": {
                    "successRate": 0.45 - shift * 0.01,
                    "ppa": 0.15 - shift * 0.01,
                },
                "stuffRate": 0.18 + shift * 0.005,
                "successRate": 0.45 - shift * 0.01,
                "pointsPerOpportunity": 4.0 - shift * 0.10,
                "havoc": {
                    "db": 0.05 + shift * 0.005,
                    "frontSeven": 0.10 + shift * 0.005,
                },
            },
        },
    }


def test_category_grades_reward_stronger_profile() -> None:
    rows = [_raw_team(f"Team {i}", float(i), float(i) * 3.0) for i in range(10)]
    _season_category_scores(rows)
    weak = rows[0]["categories"]
    strong = rows[-1]["categories"]
    for category in CATEGORY_ORDER:
        assert strong[category]["z"] > weak[category]["z"]
        assert strong[category]["grade"] > weak[category]["grade"]
        assert strong[category]["letter"] in {"A+", "A", "A-"}


def test_strength_model_is_monotone_in_every_unit() -> None:
    rows = [_raw_team(f"Team {i}", float(i) / 5.0, float(i) * 0.75) for i in range(80)]
    _season_category_scores(rows)
    model = fit_strength_model(rows)
    assert model["trainingTeamSeasons"] == 80
    assert math.isclose(sum(model["categoryWeights"].values()), 1.0, rel_tol=1e-9)
    assert all(weight > 0 for weight in model["categoryWeights"].values())
    assert model["scale"] > 0


def _unit_row(name: str, season: int, z_by_category: dict[str, float]) -> dict:
    return {
        "team": name,
        "season": season,
        "categories": {
            category: {
                "z": z_by_category[category],
                "grade": 50.0 + 10.0 * z_by_category[category],
                "letter": "B",
            }
            for category in CATEGORY_ORDER
        },
    }


def _game_dataset(spins: list[dict]) -> dict:
    return {
        "rules": {"winThreshold": 0.50},
        "target": {"srs": 20.0},
        "strengthModel": {
            "categoryWeights": {category: 1.0 / len(CATEGORY_ORDER) for category in CATEGORY_ORDER},
            "intercept": 10.0,
            "scale": 10.0,
        },
        "marginCalibration": {"srsToMarginScale": 1.0, "residualSd": 14.0},
        "wheelPool": spins,
    }


def test_equal_strength_is_exactly_fifty_percent() -> None:
    calibration = {"srsToMarginScale": 1.25, "residualSd": 13.5}
    assert neutral_win_probability(25.0, 25.0, calibration) == 0.5
    assert neutral_win_probability(30.0, 25.0, calibration) > 0.5
    assert neutral_win_probability(20.0, 25.0, calibration) < 0.5


def test_oracle_assignment_is_never_worse_than_greedy() -> None:
    spins = []
    for i in range(7):
        scores = {category: -0.5 for category in CATEGORY_ORDER}
        scores[CATEGORY_ORDER[i]] = 1.5
        # Make the first spin tempt the greedy strategy with a second strong unit;
        # the oracle can preserve the better one-to-one assignment.
        if i == 0:
            scores[CATEGORY_ORDER[1]] = 1.4
        spins.append(_unit_row(f"Spin {i}", 2010 + i, scores))
    dataset = _game_dataset(spins)
    _, greedy = greedy_draft(dataset, spins)
    _, oracle = _oracle_assignment(dataset, spins)
    assert oracle["estimatedHybridSrs"] >= greedy["estimatedHybridSrs"]
    assert oracle["winProbability"] >= greedy["winProbability"]


def test_evaluate_selections_requires_all_units_and_can_win() -> None:
    spins = [
        _unit_row(
            f"Elite {i}",
            2010 + i,
            {category: 2.0 for category in CATEGORY_ORDER},
        )
        for i in range(7)
    ]
    dataset = _game_dataset(spins)
    selections = {
        category: {
            "z": 2.0,
            "team": spins[i]["team"],
            "season": spins[i]["season"],
        }
        for i, category in enumerate(CATEGORY_ORDER)
    }
    result = evaluate_selections(dataset, selections)
    assert math.isclose(result["estimatedHybridSrs"], 30.0, rel_tol=1e-12, abs_tol=1e-12)
    assert result["winProbability"] > 0.5
    assert result["win"] is True
