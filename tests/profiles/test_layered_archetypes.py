from cfb_analytics.profiles.layered_archetypes import LANE_FAMILIES, match_lane


def _profile(**overrides):
    row = {
        "identity_rushing_attack": 55.0,
        "identity_passing_attack": 75.0,
        "identity_rushing_defense": 70.0,
        "identity_passing_defense": 35.0,
        "identity_offense_quality": 72.0,
        "identity_defense_quality": 50.0,
        "rush_rate": 58.0,
        "plays_per_possession": 78.0,
        "identity_explosive_vs_methodical": -10.0,
        "identity_offense_vs_defense": 22.0,
        "identity_run_vs_pass_off": -20.0,
        "identity_run_vs_pass_def": 35.0,
        "identity_predictability": 30.0,
        "identity_one_dimensionality": 20.0,
        "identity_playcalling_fit": 5.0,
        "identity_scheme_constraint": 15.0,
    }
    row.update(overrides)
    return row


def test_each_lane_only_returns_its_allowed_families():
    profile = _profile()
    for lane, families in LANE_FAMILIES.items():
        matches = match_lane(profile, lane, top_n=5)
        assert matches
        assert all(x["family"] in families for x in matches)


def test_offense_lane_does_not_return_defensive_funnel_label():
    matches = match_lane(_profile(), "offense", top_n=10)
    assert matches
    assert all(x["rootName"] not in {"Pass Funnel", "Run Funnel", "Open Skies", "Open Highway"} for x in matches)
