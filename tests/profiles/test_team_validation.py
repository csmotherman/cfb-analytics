from cfb_analytics.profiles.validate_team import provisional_name, validate_team


def snap(**overrides):
    row = {
        "season": 2025,
        "team": "Michigan",
        "week": 8,
        "throughGameId": "g8",
        "gamesPlayed": 8,
        "current_oa_run_efficiency_off_percentile": 50.0,
        "current_oa_pass_efficiency_off_percentile": 50.0,
        "current_oa_success_off_percentile": 50.0,
        "current_oa_explosiveness_off_percentile": 50.0,
        "current_oa_finishing_off_percentile": 50.0,
        "current_oa_run_efficiency_def_percentile": 50.0,
        "current_oa_pass_efficiency_def_percentile": 50.0,
        "current_oa_success_def_percentile": 50.0,
        "current_oa_explosiveness_def_percentile": 50.0,
        "current_rush_rate_percentile": 50.0,
        "current_pass_rate_percentile": 50.0,
        "current_plays_per_possession_percentile": 50.0,
        "identity_run_vs_pass_off": 0.0,
        "identity_run_vs_pass_def": 0.0,
        "identity_explosive_vs_methodical": 0.0,
        "identity_finishing_vs_foundation": 0.0,
        "identity_offense_vs_defense": 0.0,
        "identity_rush_vs_pass_tendency": 0.0,
    }
    row.update(overrides)
    return row


def test_provisional_name_can_identify_run_or_die():
    row = snap(
        current_oa_run_efficiency_off_percentile=88.0,
        current_oa_pass_efficiency_off_percentile=30.0,
        current_rush_rate_percentile=90.0,
    )
    assert provisional_name(row)[0] == "Run or Die"


def test_provisional_name_can_identify_defense_or_bust():
    row = snap(
        current_oa_run_efficiency_off_percentile=25.0,
        current_oa_pass_efficiency_off_percentile=25.0,
        current_oa_success_off_percentile=25.0,
        current_oa_explosiveness_off_percentile=25.0,
        current_oa_finishing_off_percentile=25.0,
        current_oa_run_efficiency_def_percentile=90.0,
        current_oa_pass_efficiency_def_percentile=90.0,
        current_oa_success_def_percentile=90.0,
        current_oa_explosiveness_def_percentile=90.0,
    )
    assert provisional_name(row)[0] == "Defense or Bust"


def test_validation_joins_snapshot_to_cluster_assignment():
    snapshots = [snap()]
    discovery = {
        "assignments": [
            {"season": 2025, "team": "Michigan", "throughGameId": "g8", "archetype": "F00-A00"}
        ],
        "families": [
            {"archetypes": [{"id": "F00-A00", "exemplars": [{"season": 2021, "team": "Example", "week": 8}]}]}
        ],
    }
    report = validate_team(snapshots, discovery, team="Michigan", seasons=(2025,))
    season = report["seasons"][0]
    assert season["status"] == "OK"
    assert season["dominantCluster"] == "F00-A00"
    assert season["clusterExemplars"][0]["team"] == "Example"
