from cfb_analytics.profiles.snapshots import add_context_percentiles, build_identity_snapshots
from cfb_analytics.profiles.discovery import discover_archetypes
from cfb_analytics.profiles.opponent_adjustment import METRIC_SPECS, fit_context


def game(week, team, rush_s, pass_s, *, opponent="B", game_id=None):
    return {
        "season": 2025, "seasonType": "regular", "week": week, "gameId": game_id or f"g{week}-{team}",
        "team": team, "opponent": opponent, "gameValidationStatus": "PASS",
        "rushSuccessEligiblePlays": 20, "rushSuccessfulPlays": rush_s,
        "passSuccessEligiblePlays": 20, "passSuccessfulPlays": pass_s,
        "successEligiblePlays": 40, "successfulPlays": rush_s + pass_s,
        "explosiveEligiblePlays": 40, "explosivePlays": max(1, pass_s // 2),
        "down3SuccessEligiblePlays": 10, "down3SuccessfulPlays": max(1, (rush_s + pass_s) // 4),
        "resolvedPointOpportunities": 4, "opportunityPoints": float(rush_s + pass_s),
        "validatedPossessions": 10, "offensivePlays": 65,
    }


def paired_week(week, a_rush, a_pass, b_rush=8, b_pass=8):
    gid=f"g{week}"
    return [game(week,"A",a_rush,a_pass,opponent="B",game_id=gid), game(week,"B",b_rush,b_pass,opponent="A",game_id=gid)]


def test_snapshots_capture_recent_state_separately_from_full_season():
    rows=[]
    for w in range(1,9): rows += paired_week(w,8 if w<=4 else 16,8 if w<=4 else 16)
    snaps=build_identity_snapshots(rows,min_games=4,recent_games=4)
    last=next(r for r in reversed(snaps) if r["team"]=="A")
    assert last["current_success_off"] > last["baseline_success_off"]
    assert last["gamesPlayed"] == 8
    assert last["recentGames"] == 4
    assert "current_oa_success_off" in last


def test_opponent_adjustment_rewards_same_output_against_stronger_defense():
    rows=[]
    for w in range(1,5):
        rows += [
            game(w,"A",12,12,opponent="X",game_id=f"ax{w}"), game(w,"X",16,16,opponent="A",game_id=f"ax{w}"),
            game(w,"B",12,12,opponent="Y",game_id=f"by{w}"), game(w,"Y",4,4,opponent="B",game_id=f"by{w}"),
        ]
    fit=fit_context(rows)["success"]
    assert fit["defense"]["Y"] > fit["defense"]["X"]


def test_context_percentiles_are_built_for_oa_quality_and_style():
    rows=[]
    for w in range(1,5): rows += paired_week(w,16,14,8,6)
    enriched=add_context_percentiles(build_identity_snapshots(rows,min_games=4,recent_games=4))
    a=next(r for r in enriched if r["team"]=="A")
    b=next(r for r in enriched if r["team"]=="B")
    assert a["current_oa_success_off_percentile"] > b["current_oa_success_off_percentile"]
    assert "identity_run_vs_pass_off" in a
    assert "identity_offense_vs_defense" in a


def test_hierarchical_discovery_produces_more_than_broad_families():
    rows=[]
    for i in range(360):
        r={"season":2025-(i%3),"team":f"T{i}","week":8,"gamesPlayed":8}
        group=i%12
        base=10.0 + group*7.0
        fields=(
            "current_oa_run_efficiency_off_percentile","current_oa_pass_efficiency_off_percentile",
            "current_oa_success_off_percentile","current_oa_explosiveness_off_percentile",
            "current_oa_third_down_off_percentile","current_oa_finishing_off_percentile",
            "current_oa_run_efficiency_def_percentile","current_oa_pass_efficiency_def_percentile",
            "current_oa_success_def_percentile","current_oa_explosiveness_def_percentile",
            "current_oa_third_down_def_percentile","current_oa_finishing_def_percentile",
            "current_rush_rate_percentile","current_pass_rate_percentile","current_plays_per_possession_percentile",
        )
        for j,f in enumerate(fields): r[f]=max(1.0,min(99.0,base + ((j%4)-1.5)*3 + (i%3)))
        r["identity_run_vs_pass_off"]=r["current_oa_run_efficiency_off_percentile"]-r["current_oa_pass_efficiency_off_percentile"]
        r["identity_run_vs_pass_def"]=r["current_oa_run_efficiency_def_percentile"]-r["current_oa_pass_efficiency_def_percentile"]
        r["identity_explosive_vs_methodical"]=r["current_oa_explosiveness_off_percentile"]-r["current_oa_success_off_percentile"]
        r["identity_finishing_vs_foundation"]=r["current_oa_finishing_off_percentile"]-r["current_oa_success_off_percentile"]
        r["identity_offense_vs_defense"]=r["current_oa_success_off_percentile"]-r["current_oa_success_def_percentile"]
        r["identity_rush_vs_pass_tendency"]=r["current_rush_rate_percentile"]-r["current_pass_rate_percentile"]
        rows.append(r)
    report=discover_archetypes(rows,family_k=3,sub_k_min=2,sub_k_max=3,min_coverage=.9,min_cluster=20)
    assert report["familyCount"] == 3
    assert report["archetypeCount"] >= 6
    assert all(a["fanName"] is None for f in report["families"] for a in f["archetypes"])
    assert report["qualityPolicy"].startswith("quality dimensions opponent-adjusted")
