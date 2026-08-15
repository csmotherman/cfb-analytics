from cfb_analytics.profiles.dynamic_identity import build_dynamic_identity, season_consistency


def test_michigan_like_profile_builds_dynamic_identity_name_and_tags():
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
    assert identity["name"] == "Elite Defensive Control"
    assert "Elite Defense" in identity["tags"]
    assert "Good Offense" in identity["tags"]
    assert "Run-Heavy" in identity["tags"]
    assert "Methodical" in identity["tags"]
    assert "Run-Committed" in identity["tags"]
    assert "Offense Faded Late" in identity["tags"]
    assert "fixed archetype" not in identity["summary"].lower()
    assert identity["summary"].startswith("An elite defense")


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


def test_explosive_bad_offense_is_not_called_attack():
    profile = {
        "identity_offense_quality": 38.0,
        "identity_defense_quality": 50.0,
        "rush_rate": 55.0,
        "identity_explosive_vs_methodical": 30.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Explosive but Inefficient"
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
