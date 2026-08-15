from cfb_analytics.profiles.layered_archetypes import (
    EVIDENCE_ROOTS,
    LANE_ASSIGNMENT_THRESHOLDS,
    LANE_FAMILIES,
    ROOT_MODIFIERS,
    final_snapshot,
    final_snapshot_profile,
    match_history,
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


def test_complete_team_profile_selects_complete_team_root_before_modifier_refinement():
    profile = _profile(
        identity_offense_quality=82.0,
        identity_defense_quality=82.0,
        identity_offense_vs_defense=0.0,
        identity_rushing_attack=72.0,
        identity_passing_attack=78.0,
        identity_rushing_defense=80.0,
        identity_passing_defense=78.0,
    )
    matches = match_lane(profile, "team", top_n=3)
    assert matches
    assert matches[0]["rootName"] == "Complete Team"


def test_weak_lane_match_is_marked_no_clear_match_instead_of_forced_assignment():
    profile = _profile(
        identity_offense_quality=50.0,
        identity_defense_quality=50.0,
        identity_offense_vs_defense=0.0,
        identity_rushing_attack=50.0,
        identity_passing_attack=50.0,
        identity_rushing_defense=50.0,
        identity_passing_defense=50.0,
        rush_rate=50.0,
        plays_per_possession=50.0,
        identity_explosive_vs_methodical=0.0,
        identity_predictability=50.0,
        identity_scheme_constraint=50.0,
    )
    matches = match_lane(profile, "team", top_n=3)
    assert matches
    assert matches[0]["assignmentThreshold"] == LANE_ASSIGNMENT_THRESHOLDS["team"]
    assert isinstance(matches[0]["isClearMatch"], bool)


def test_root_score_controls_ranking_not_modifier_score():
    profile = _profile(
        identity_offense_quality=82.0,
        identity_defense_quality=82.0,
        identity_offense_vs_defense=0.0,
    )
    matches = match_lane(profile, "team", top_n=5)
    root_scores = [x["rootSimilarity"] for x in matches]
    assert root_scores == sorted(root_scores, reverse=True)


def test_final_snapshot_profile_uses_finished_team_not_average_of_season_states():
    early = {
        "season": 2023,
        "team": "Michigan",
        "seasonType": "regular",
        "week": 4,
        "gamesPlayed": 4,
        "throughGameId": "early",
        "identity_offense_quality": 42.0,
        "identity_defense_quality": 55.0,
    }
    final = {
        "season": 2023,
        "team": "Michigan",
        "seasonType": "postseason",
        "week": 16,
        "gamesPlayed": 15,
        "throughGameId": "title",
        "identity_offense_quality": 82.0,
        "identity_defense_quality": 91.0,
    }
    rows = [final, early]
    assert final_snapshot(rows)["throughGameId"] == "title"
    profile = final_snapshot_profile(rows)
    assert profile["identity_offense_quality"] == 82.0
    assert profile["identity_defense_quality"] == 91.0


def test_historical_output_declares_final_snapshot_basis():
    row = {
        "season": 2023,
        "team": "Michigan",
        "seasonType": "postseason",
        "week": 16,
        "gamesPlayed": 15,
        "throughGameId": "title",
        **_profile(
            identity_offense_quality=82.0,
            identity_defense_quality=82.0,
            identity_offense_vs_defense=0.0,
        ),
    }
    report = match_history([row], seasons=(2023,))
    assert report["profileBasis"] == "FINAL_SNAPSHOT"
    assert report["teamSeasons"][0]["profileBasis"] == "FINAL_SNAPSHOT"
    assert report["teamSeasons"][0]["finalGamesPlayed"] == 15
