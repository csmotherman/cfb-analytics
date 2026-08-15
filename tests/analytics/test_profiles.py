from cfb_analytics.profiles.archetypes import classify_archetypes
from cfb_analytics.profiles.grades import grade_percentile, percentile_rank, season_relative_grades
from cfb_analytics.profiles.similarity import historical_comparables


def test_percentile_direction_and_grades():
    population = [1, 2, 3, 4, 5]
    assert percentile_rank(5, population, higher_is_better=True) > percentile_rank(1, population, higher_is_better=True)
    assert percentile_rank(1, population, higher_is_better=False) > percentile_rank(5, population, higher_is_better=False)
    assert grade_percentile(98) == "A+"
    assert grade_percentile(50) == "C"
    assert grade_percentile(10) == "F"


def test_season_relative_grades_do_not_mix_eras():
    rows = [
        {"season": 2014, "team": "A", "x": 2.0},
        {"season": 2014, "team": "B", "x": 1.0},
        {"season": 2025, "team": "C", "x": 5.0},
        {"season": 2025, "team": "D", "x": 4.0},
    ]
    out = season_relative_grades(rows, {"x": True})
    a = next(r for r in out if r["team"] == "A")
    c = next(r for r in out if r["team"] == "C")
    assert a["x_percentile"] == c["x_percentile"]


def test_historical_comparables_return_top_three_and_explanations():
    target = {"season": 2026, "team": "NOW", "pass_rate_percentile": 95.0, "explosiveness_off_percentile": 90.0}
    history = [
        {"season": 2021, "team": "A", "pass_rate_percentile": 94.0, "explosiveness_off_percentile": 89.0},
        {"season": 2019, "team": "B", "pass_rate_percentile": 90.0, "explosiveness_off_percentile": 85.0},
        {"season": 2018, "team": "C", "pass_rate_percentile": 80.0, "explosiveness_off_percentile": 80.0},
        {"season": 2017, "team": "D", "pass_rate_percentile": 20.0, "explosiveness_off_percentile": 30.0},
    ]
    result = historical_comparables(target, history, ("pass_rate", "explosiveness_off"))
    assert [x["team"] for x in result] == ["A", "B", "C"]
    assert result[0]["similarity"] > result[1]["similarity"]
    assert result[0]["closestTraits"]


def test_air_it_out_archetype_is_explainable():
    profile = {
        "pass_rate": 95,
        "explosiveness_off": 85,
        "turnover_avoidance": 30,
        "drive_suppression_def": 25,
    }
    result = classify_archetypes(profile)
    assert result[0]["name"] == "Air It Out"
    assert result[0]["description"]
