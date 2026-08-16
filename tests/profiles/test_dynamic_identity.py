from cfb_analytics.profiles.dynamic_identity import build_dynamic_identity, season_consistency


def test_michigan_like_profile_is_run_committed_defensive_control():
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
    closing = {**profile, "identity_offense_quality": 52.7, "identity_defense_quality": 90.1}
    history = [
        {**profile, "identity_offense_quality": 77.0, "identity_defense_quality": 84.0},
        {**profile, "identity_offense_quality": 74.0, "identity_defense_quality": 87.0},
        {**profile, "identity_offense_quality": 71.0, "identity_defense_quality": 90.0},
        profile,
    ]
    identity = build_dynamic_identity(profile, closing_form=closing, season_profiles=history)
    assert identity["name"] == "Run-Committed Defensive Control"
    assert identity["style"]["usage"] == "run-heavy"
    assert identity["style"]["method"] == "methodical"
    assert identity["style"]["attackDriver"] == "pass-driven"
    assert identity["style"]["commitment"] == "run-committed"
    assert identity["style"]["teamStructure"] == "defense-supported"
    assert identity["style"]["effectiveness"] == "control"
    assert "Run-Committed" in identity["tags"]
    assert "Elite Defense" in identity["tags"]


def test_balanced_efficient_two_way_team_gets_power_only_when_quality_earns_it():
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
    assert identity["name"] == "Efficient Two-Way Power"
    assert identity["style"]["effectiveness"] == "power"


def test_big_play_dependent_good_offense_can_earn_attack_language():
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
    assert identity["name"] == "Quick-Strike Attack"
    assert identity["style"]["efficiencyShape"] == "boom-bust"
    assert identity["style"]["effectiveness"] == "dangerous-attack"


def test_explosive_limited_offense_keeps_neutral_style_not_attack_language():
    profile = {
        "identity_offense_quality": 38.0,
        "identity_defense_quality": 52.0,
        "identity_rushing_attack": 52.0,
        "identity_passing_attack": 44.0,
        "rush_rate": 84.0,
        "identity_explosive_vs_methodical": 28.0,
        "identity_success_quality": 42.0,
        "identity_explosiveness_quality": 82.0,
    }
    identity = build_dynamic_identity(profile)
    assert "Attack" not in identity["name"]
    assert "Power" not in identity["name"]


def test_poor_offense_with_strong_defense_is_carried_not_supported():
    profile = {
        "identity_offense_quality": 28.0,
        "identity_defense_quality": 76.0,
        "identity_rushing_attack": 40.0,
        "identity_passing_attack": 44.0,
        "rush_rate": 84.0,
        "identity_explosive_vs_methodical": 2.0,
        "identity_success_quality": 34.0,
        "identity_explosiveness_quality": 32.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["style"]["teamStructure"] == "defense-carried"
    assert identity["name"] == "Defense-Carried Run-First Football"


def test_stalled_balanced_offense_surfaces_low_output_in_headline():
    profile = {
        "identity_offense_quality": 35.0,
        "identity_defense_quality": 56.0,
        "identity_rushing_attack": 38.0,
        "identity_passing_attack": 42.0,
        "rush_rate": 50.0,
        "identity_explosive_vs_methodical": 0.0,
        "identity_success_quality": 30.0,
        "identity_explosiveness_quality": 33.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Low-Output Balanced Football"
    assert "Low-Output" in identity["tags"]


def test_complete_offense_preserves_extreme_run_usage():
    profile = {
        "identity_offense_quality": 91.0,
        "identity_defense_quality": 62.0,
        "identity_rushing_attack": 86.0,
        "identity_passing_attack": 84.0,
        "rush_rate": 86.0,
        "identity_explosive_vs_methodical": 4.0,
        "identity_success_quality": 88.0,
        "identity_explosiveness_quality": 84.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Run-First Complete Attack"


def test_complete_offense_preserves_extreme_pass_usage():
    profile = {
        "identity_offense_quality": 91.0,
        "identity_defense_quality": 62.0,
        "identity_rushing_attack": 84.0,
        "identity_passing_attack": 88.0,
        "rush_rate": 14.0,
        "identity_explosive_vs_methodical": 4.0,
        "identity_success_quality": 88.0,
        "identity_explosiveness_quality": 84.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Pass-First Complete Attack"


def test_generic_balanced_identity_uses_secondary_mechanism_when_available():
    profile = {
        "identity_offense_quality": 58.0,
        "identity_defense_quality": 55.0,
        "identity_rushing_attack": 42.0,
        "identity_passing_attack": 67.0,
        "rush_rate": 50.0,
        "plays_per_possession": 50.0,
        "identity_explosive_vs_methodical": 0.0,
        "identity_success_quality": 55.0,
        "identity_explosiveness_quality": 52.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Pass-Driven Balanced Football"
    assert identity["style"]["secondaryMechanism"] == "Pass-Driven"


def test_weak_units_do_not_create_strength_sounding_identity():
    profile = {
        "identity_offense_quality": 24.0,
        "identity_defense_quality": 40.0,
        "rush_rate": 18.0,
        "identity_explosive_vs_methodical": 4.0,
    }
    identity = build_dynamic_identity(profile)
    assert "Power" not in identity["name"]
    assert "Attack" not in identity["name"]
    assert "Control" not in identity["name"]


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
