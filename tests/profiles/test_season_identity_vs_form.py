from cfb_analytics.profiles.layered_archetypes import (
    closing_form_profile,
    final_snapshot_profile,
    match_team_season,
)


def _final_row():
    row = {
        "season": 2023,
        "team": "Michigan",
        "seasonType": "postseason",
        "week": 1,
        "startDate": "2024-01-09T00:30:00.000Z",
        "gamesPlayed": 15,
        "throughGameId": "title",
        "identity_rushing_attack": 53.0,
        "identity_passing_attack": 59.0,
        "identity_rushing_defense": 77.0,
        "identity_passing_defense": 97.0,
        "identity_offense_quality": 53.0,
        "identity_defense_quality": 90.0,
        "identity_explosive_vs_methodical": 14.0,
        "identity_offense_vs_defense": -37.0,
        "identity_run_vs_pass_off": -6.0,
        "identity_run_vs_pass_def": -20.0,
        "identity_predictability": 39.0,
        "identity_one_dimensionality": 6.0,
        "identity_playcalling_fit": -2.0,
        "identity_scheme_constraint": 18.0,
        "current_rush_rate_percentile": 70.0,
        "current_plays_per_possession_percentile": 8.0,
    }

    baseline = {
        "oa_run_efficiency_off": 66.0,
        "oa_run_explosiveness_off": 61.0,
        "oa_run_success_yards_off": 63.0,
        "oa_pass_efficiency_off": 82.0,
        "oa_pass_explosiveness_off": 70.0,
        "oa_pass_success_yards_off": 78.0,
        "oa_success_off": 88.0,
        "oa_explosiveness_off": 58.0,
        "oa_third_down_off": 66.0,
        "oa_finishing_off": 92.0,
        "oa_run_efficiency_def": 84.0,
        "oa_run_explosiveness_def": 88.0,
        "oa_run_success_yards_def": 82.0,
        "oa_pass_efficiency_def": 96.0,
        "oa_pass_explosiveness_def": 98.0,
        "oa_pass_success_yards_def": 94.0,
        "oa_success_def": 93.0,
        "oa_explosiveness_def": 98.0,
        "oa_third_down_def": 86.0,
        "oa_finishing_def": 97.0,
        "rush_rate": 79.0,
        "pass_rate": 21.0,
        "plays_per_possession": 72.0,
    }
    for key, value in baseline.items():
        row[f"baseline_{key}_percentile"] = value
    return row


def test_final_snapshot_profile_uses_season_to_date_baseline_not_recent_form():
    row = _final_row()
    season = final_snapshot_profile([row])
    form = closing_form_profile([row])

    assert season["identity_offense_quality"] != form["identity_offense_quality"]
    assert season["identity_offense_quality"] > form["identity_offense_quality"]
    assert season["rush_rate"] == 79.0
    assert form["rush_rate"] == 70.0


def test_match_team_season_exposes_both_temporal_profiles():
    result = match_team_season([_final_row()], season=2023, team="Michigan")

    assert result["profileBasis"] == "FINAL_SNAPSHOT"
    assert result["identityBasis"] == "SEASON_TO_DATE_BASELINE"
    assert result["closingFormBasis"] == "RECENT_FOUR_GAMES"
    assert result["profile"] != result["closingFormProfile"]
    assert "lanes" in result
    assert "closingFormLanes" in result
