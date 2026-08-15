from cfb_analytics.profiles.dynamic_identity import build_dynamic_identity, season_consistency


def test_michigan_like_profile_is_methodical_defensive_control():
    profile = {
        "identity_rushing_attack": 41.1,
        "identity_passing_attack": 66.5,
        "identity_rushing_defense": 81.9,
        "identity_passing_defense": 93.5,
        "identity_offense_quality": 68.5,
        "identity_defense_quality": 91.7,
        "rush_rate": 86.3,
        "plays_per_possession": 47.0,
        "identity_explosive_vs_methodical": -29.8,
        "identity_predictability": 72.6,
        "identity_scheme_constraint": 42.8,
        "identity_success_quality": 87.5,
        "identity_explosiveness_quality": 57.7,
        "identity_finishing_quality": 92.3,
        "identity_third_down_quality": 66.1,
    }
    closing = {
        **profile,
        "identity_offense_quality": 52.7,
        "identity_defense_quality": 90.1,
    }
    history = [
        {**profile, "identity_offense_quality": 77.0, "identity_defense_quality": 84.0},
        {**profile, "identity_offense_quality": 74.0, "identity_defense_quality": 87.0},
        {**profile, "identity_offense_quality": 71.0, "identity_defense_quality": 90.0},
        profile,
    ]
    identity = build_dynamic_identity(profile, closing_form=closing, season_profiles=history)
    assert identity["name"] == "Methodical Defensive Control"
    assert identity["style"]["usage"] == "run-heavy"
    assert identity["style"]["method"] == "methodical"
    assert identity["style"]["teamStructure"] == "defense-led"
    assert "Run-Heavy" in identity["tags"]
    assert "Methodical" in identity["tags"]
    assert "Elite Finishing" in identity["tags"]
    assert "Run-Committed" in identity["tags"]
    assert "Elite Defense" in identity["tags"]
    assert "Offense Faded Late" in identity["tags"]
    assert identity["summary"].startswith("Heavy run commitment")


def test_balanced_efficient_team_gets_balanced_efficiency_identity():
    profile = {
        "identity_offense_quality": 88.0,
        "identity_defense_quality": 86.0,
        "identity_rushing_attack": 82.0,
        "identity_passing_attack": 84.0,
        "rush_rate": 50.0,
        "plays_per_possession": 65.0,
        "identity_explosive_vs_methodical": 2.0,
        "identity_success_quality": 84.0,
        "identity_explosiveness_quality": 68.0,
        "identity_finishing_quality": 80.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Two-Way Balanced Efficiency"
    assert identity["style"]["efficiencyShape"] == "balanced-efficient"
    assert identity["style"]["attackBalance"] == "balanced"


def test_big_play_dependent_team_is_boom_or_bust_not_generic_attack():
    profile = {
        "identity_offense_quality": 76.0,
        "identity_defense_quality": 54.0,
        "identity_rushing_attack": 55.0,
        "identity_passing_attack": 82.0,
        "rush_rate": 30.0,
        "identity_explosive_vs_methodical": 28.0,
        "identity_success_quality": 42.0,
        "identity_explosiveness_quality": 91.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Offense-Led Boom-or-Bust"
    assert identity["style"]["efficiencyShape"] == "boom-bust"
    assert "Big-Play Threat" in identity["tags"]


def test_weak_units_do_not_create_strength_sounding_led_identity():
    profile = {
        "identity_offense_quality": 24.0,
        "identity_defense_quality": 40.0,
        "rush_rate": 18.0,
        "identity_explosive_vs_methodical": 4.0,
    }
    identity = build_dynamic_identity(profile)
    assert "Defense-Led" not in identity["name"]
    assert "Offense-Led" not in identity["name"]
    assert "Power" not in identity["name"]
    assert "Attack" not in identity["name"]


def test_smooth_trend_is_not_treated_as_volatility():
    profiles = [{"identity_offense_quality": v} for v in (60.0, 65.0, 70.0, 75.0, 80.0)]
    stats = season_consistency(profiles)["identity_offense_quality"]
    assert stats["slopePerSnapshot"] == 5.0
    assert stats["residualSd"] < 1e-9
    assert stats["stabilityScore"] > 99.0


def test_choppy_series_has_lower_stability():
    profiles = [{"identity_defense_quality": v} for v in (60.0, 90.0, 45.0, 85.0, 50.0)]
    stats = season_consistency(profiles)["identity_defense_quality"]
    assert stats["residualSd"] > 10.0
    assert stats["stabilityScore"] < 50.0
