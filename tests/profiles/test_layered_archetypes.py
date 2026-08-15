from cfb_analytics.profiles.layered_archetypes import (
    EVIDENCE_ROOTS,
    LANE_FAMILIES,
    ROOT_MODIFIERS,
    match_lane,
)


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


def test_each_lane_only_returns_evidence_backed_roots_and_root_valid_modifiers():
    profile = _profile()
    for lane in LANE_FAMILIES:
        matches = match_lane(profile, lane, top_n=20)
        assert matches
        assert all(x["rootName"] in EVIDENCE_ROOTS[lane] for x in matches)
        assert all(x["modifier"] in ROOT_MODIFIERS[x["rootName"]] for x in matches)


def test_offense_lane_does_not_return_defensive_funnel_label():
    matches = match_lane(_profile(), "offense", top_n=10)
    assert matches
    assert all(x["rootName"] not in {"Pass Funnel", "Run Funnel", "Open Skies", "Open Highway"} for x in matches)


def test_unmeasured_concepts_are_not_assignable():
    profile = _profile()
    all_matches = [x for lane in LANE_FAMILIES for x in match_lane(profile, lane, top_n=50)]
    forbidden = {"YAC Factory", "Talent Over Scheme", "Scheme Over Talent", "Interior Fortress"}
    assert not ({x["rootName"] for x in all_matches} & forbidden)


def test_known_semantic_contradictions_are_forbidden_by_root():
    assert "Strong" not in ROOT_MODIFIERS["Open Skies"]
    assert "Strong" not in ROOT_MODIFIERS["Open Highway"]
    assert "Strong" not in ROOT_MODIFIERS["Paper Wall"]
    assert "Broken" not in ROOT_MODIFIERS["Complete Team"]
    assert "Defense-Led" not in ROOT_MODIFIERS["Offense First"]
    assert "Offense-Led" not in ROOT_MODIFIERS["Defense First"]
    assert "Stable" not in ROOT_MODIFIERS["Identity Crisis"]
    assert "Well-Fit" not in ROOT_MODIFIERS["Playcalling Prison"]


def test_positive_defensive_roots_allow_positive_strength_modifiers():
    assert "Elite" in ROOT_MODIFIERS["Run Wall"]
    assert "Strong" in ROOT_MODIFIERS["No Fly Zone"]
    assert "Elite" in ROOT_MODIFIERS["Brick Wall"]
