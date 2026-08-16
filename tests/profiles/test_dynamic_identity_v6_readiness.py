from cfb_analytics.profiles.dynamic_identity import build_dynamic_identity


def test_commitment_tag_uses_same_classifier_as_style():
    profile = {
        "identity_offense_quality": 70.0,
        "identity_defense_quality": 45.0,
        "identity_rushing_attack": 52.0,
        "identity_passing_attack": 68.0,
        "rush_rate": 82.0,
        "identity_explosive_vs_methodical": 0.0,
        "identity_success_quality": 72.0,
        "identity_explosiveness_quality": 72.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["style"]["commitment"] == "aligned"
    assert "Run-Committed" not in identity["tags"]


def test_true_run_commitment_is_shared_across_style_tags_and_name():
    profile = {
        "identity_offense_quality": 74.0,
        "identity_defense_quality": 48.0,
        "identity_rushing_attack": 48.0,
        "identity_passing_attack": 72.0,
        "rush_rate": 88.0,
        "identity_explosive_vs_methodical": 0.0,
        "identity_success_quality": 80.0,
        "identity_explosiveness_quality": 78.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["style"]["commitment"] == "run-committed"
    assert "Run-Committed" in identity["tags"]
    assert identity["name"] == "Run-Committed Complete Offense"


def test_volatile_offense_is_exposed_as_structured_signal_and_tag():
    profile = {
        "identity_offense_quality": 72.0,
        "identity_defense_quality": 55.0,
        "identity_rushing_attack": 70.0,
        "identity_passing_attack": 70.0,
        "rush_rate": 50.0,
        "identity_explosive_vs_methodical": 0.0,
        "identity_success_quality": 70.0,
        "identity_explosiveness_quality": 70.0,
    }
    history = [
        {**profile, "identity_offense_quality": 50.0},
        {**profile, "identity_offense_quality": 95.0},
        {**profile, "identity_offense_quality": 45.0},
        {**profile, "identity_offense_quality": 90.0},
        profile,
    ]
    identity = build_dynamic_identity(profile, season_profiles=history)
    assert identity["style"]["offenseConsistency"] == "volatile"
    assert "Volatile Offense" in identity["tags"]
    assert "varied sharply" in identity["summary"]


def test_offense_carried_complete_team_uses_engine_wording():
    profile = {
        "identity_offense_quality": 95.0,
        "identity_defense_quality": 38.0,
        "identity_rushing_attack": 86.0,
        "identity_passing_attack": 92.0,
        "rush_rate": 50.0,
        "identity_explosive_vs_methodical": 0.0,
        "identity_success_quality": 90.0,
        "identity_explosiveness_quality": 90.0,
    }
    identity = build_dynamic_identity(profile)
    assert identity["style"]["teamStructure"] == "offense-carried"
    assert identity["name"] == "Complete Offensive Engine"
    assert "Carry" not in identity["name"]


def test_michigan_identity_stays_run_committed_defensive_control():
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
    identity = build_dynamic_identity(profile)
    assert identity["name"] == "Run-Committed Defensive Control"
