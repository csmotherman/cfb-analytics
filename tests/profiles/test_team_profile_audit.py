from cfb_analytics.profiles.audit_team_profile import summarize_team


def test_profile_audit_exposes_run_and_pass_components():
    rows = [{
        "season": 2014,
        "team": "Example",
        "seasonType": "regular",
        "week": 8,
        "gamesPlayed": 8,
        "current_oa_run_efficiency_off_percentile": 70.0,
        "current_oa_run_explosiveness_off_percentile": 60.0,
        "current_oa_run_success_yards_off_percentile": 50.0,
        "current_oa_pass_efficiency_off_percentile": 40.0,
        "current_oa_pass_explosiveness_off_percentile": 30.0,
        "current_oa_pass_success_yards_off_percentile": 20.0,
        "identity_rushing_attack": 60.0,
        "identity_passing_attack": 30.0,
    }]
    out = summarize_team(rows, season=2014, team="Example")
    assert out["status"] == "OK"
    assert out["oa_run_efficiency_off"] == 70.0
    assert out["oa_run_explosiveness_off"] == 60.0
    assert out["oa_run_success_yards_off"] == 50.0
    assert out["oa_pass_efficiency_off"] == 40.0
    assert out["oa_pass_explosiveness_off"] == 30.0
    assert out["oa_pass_success_yards_off"] == 20.0
    assert out["identity_rushing_attack"] == 60.0
    assert out["identity_passing_attack"] == 30.0
