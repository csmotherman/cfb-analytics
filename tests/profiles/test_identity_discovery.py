from cfb_analytics.profiles.snapshots import add_context_percentiles, build_identity_snapshots
from cfb_analytics.profiles.discovery import discover_archetypes


def game(week, team, rush_s, pass_s, *, opponent="B"):
    return {
        "season": 2025, "seasonType": "regular", "week": week, "gameId": f"g{week}-{team}",
        "team": team, "opponent": opponent, "gameValidationStatus": "PASS",
        "rushSuccessEligiblePlays": 20, "rushSuccessfulPlays": rush_s,
        "passSuccessEligiblePlays": 20, "passSuccessfulPlays": pass_s,
        "successEligiblePlays": 40, "successfulPlays": rush_s + pass_s,
        "explosiveEligiblePlays": 40, "explosivePlays": 4,
        "rushSuccessEligiblePlaysAllowed": 20, "rushSuccessfulPlaysAllowed": 8,
        "passSuccessEligiblePlaysAllowed": 20, "passSuccessfulPlaysAllowed": 8,
        "explosiveEligiblePlaysAllowed": 40, "explosivePlaysAllowed": 4,
        "down3SuccessEligiblePlays": 10, "down3SuccessfulPlays": 4,
        "down3SuccessEligiblePlaysAllowed": 10, "down3SuccessfulPlaysAllowed": 4,
        "resolvedPointOpportunities": 4, "opportunityPoints": 14,
        "resolvedPointOpportunitiesAllowed": 4, "opportunityPointsAllowed": 14,
        "validatedPossessions": 10, "offensivePlays": 65,
    }


def test_snapshots_capture_recent_state_separately_from_full_season():
    rows = [game(w, "A", 8 if w <= 4 else 16, 8 if w <= 4 else 16) for w in range(1, 9)]
    snaps = build_identity_snapshots(rows, min_games=4, recent_games=4)
    assert len(snaps) == 5
    last = snaps[-1]
    assert last["current_success_off"] > last["baseline_success_off"]
    assert last["gamesPlayed"] == 8
    assert last["recentGames"] == 4


def test_context_percentiles_compare_same_week_states():
    rows = []
    for team, successes in (("A", 16), ("B", 8), ("C", 12)):
        rows.extend(game(w, team, successes, successes, opponent="X") for w in range(1, 5))
    enriched = add_context_percentiles(build_identity_snapshots(rows, min_games=4, recent_games=4))
    a = next(r for r in enriched if r["team"] == "A")
    b = next(r for r in enriched if r["team"] == "B")
    assert a["current_success_off_percentile"] > b["current_success_off_percentile"]


def test_unsupervised_discovery_finds_recurring_shapes():
    rows = []
    for i in range(60):
        high = i < 30
        row = {"season": 2025, "team": f"T{i}", "week": 8, "gamesPlayed": 8}
        for key in ("success_off", "explosiveness_off", "run_efficiency_off", "pass_efficiency_off", "run_efficiency_def", "pass_efficiency_def"):
            row[f"current_{key}_percentile"] = (85.0 + (i % 3)) if high else (15.0 + (i % 3))
            row[f"trend_{key}"] = 0.0
        rows.append(row)
    report = discover_archetypes(rows, k_min=2, k_max=3, min_coverage=0.9, include_trend=False)
    assert report["selectedK"] in (2, 3)
    assert report["snapshotCount"] == 60
    assert len(report["clusters"]) == report["selectedK"]
    assert all(cluster["fanName"] is None for cluster in report["clusters"])
