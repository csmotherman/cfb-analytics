import pytest

from cfb_analytics.analytics.iterative_ratings import (
    ENRICHED_DATASET_VERSION,
    ITERATIVE_FEATURES,
    ITERATIVE_RATINGS_VERSION,
    SRS_VERSION,
    build_iterative_model_dataset,
    build_iterative_rating_snapshots,
    build_srs_model_dataset,
    eligible_iterative_row,
    enriched_rows_audit,
    fit_metric_ratings,
    fit_srs,
    fit_srs_direct_reference,
)


def _game(team, opponent, week, game_id, made, attempts):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game_id,
        "team": team,
        "opponent": opponent,
        "successfulPlays": made,
        "successEligiblePlays": attempts,
    }


def _result(home, away, week, game_id, margin):
    return {
        "season": 2025,
        "seasonType": "regular",
        "week": week,
        "gameId": game_id,
        "homeTeam": home,
        "awayTeam": away,
        "target_margin": float(margin),
        "target_homeWin": 1 if margin > 0 else 0 if margin < 0 else None,
    }


def test_iterative_solver_converges_and_centers_ratings():
    rows = [
        _game("A", "B", 1, "g1", 7, 10), _game("B", "A", 1, "g1", 3, 10),
        _game("A", "C", 2, "g2", 6, 10), _game("C", "A", 2, "g2", 4, 10),
        _game("B", "C", 3, "g3", 5, 10), _game("C", "B", 3, "g3", 5, 10),
    ]
    result = fit_metric_ratings(rows, ("Success", "successfulPlays", "successEligiblePlays"), shrinkage=1.0)
    assert result["converged"] is True
    assert result["iterations"] > 1
    assert sum(result["offense"].values()) == pytest.approx(0.0, abs=1e-10)
    assert sum(result["defense"].values()) == pytest.approx(0.0, abs=1e-10)
    assert result["offense"]["A"] > result["offense"]["B"]


def test_centered_ratings_preserve_fitted_game_values():
    rows = [
        _game("A", "B", 1, "g1", 8, 10), _game("B", "A", 1, "g1", 2, 10),
        _game("A", "C", 2, "g2", 7, 10), _game("C", "A", 2, "g2", 3, 10),
        _game("B", "C", 3, "g3", 6, 10), _game("C", "B", 3, "g3", 4, 10),
    ]
    result = fit_metric_ratings(rows, ("Success", "successfulPlays", "successEligiblePlays"), shrinkage=2.0)
    fitted = result["leagueMean"] + result["offense"]["A"] - result["defense"]["B"]
    assert result["converged"] is True
    assert 0.0 < fitted < 1.0
    assert sum(result["offense"].values()) == pytest.approx(0.0, abs=1e-10)
    assert sum(result["defense"].values()) == pytest.approx(0.0, abs=1e-10)


def test_same_partition_is_not_used_in_rating_snapshot():
    rows = [
        _game("A", "B", 1, "g1", 7, 10), _game("B", "A", 1, "g1", 3, 10),
        _game("A", "C", 2, "g2", 9, 10), _game("C", "A", 2, "g2", 1, 10),
        _game("A", "D", 2, "g3", 1, 10), _game("D", "A", 2, "g3", 9, 10),
    ]
    snaps = build_iterative_rating_snapshots(rows, 2025, shrinkage=1.0)
    week2 = [r for r in snaps if r["team"] == "A" and r["week"] == 2]
    assert len(week2) == 2
    assert all(r["gamesPlayedBefore"] == 1 for r in week2)
    assert week2[0]["iterativeSuccessOffense"] == pytest.approx(week2[1]["iterativeSuccessOffense"])
    assert week2[0]["iterativeSuccessDefense"] == pytest.approx(week2[1]["iterativeSuccessDefense"])


def test_future_game_does_not_change_historical_snapshot():
    base = [
        _game("A", "B", 1, "g1", 7, 10), _game("B", "A", 1, "g1", 3, 10),
        _game("A", "C", 2, "g2", 6, 10), _game("C", "A", 2, "g2", 4, 10),
    ]
    future = base + [_game("B", "D", 3, "g3", 0, 10), _game("D", "B", 3, "g3", 10, 10)]
    first = build_iterative_rating_snapshots(base, 2025, shrinkage=1.0)
    second = build_iterative_rating_snapshots(future, 2025, shrinkage=1.0)
    a_g2_first = next(r for r in first if r["gameId"] == "g2" and r["team"] == "A")
    a_g2_second = next(r for r in second if r["gameId"] == "g2" and r["team"] == "A")
    assert a_g2_first["iterativeSuccessOffense"] == pytest.approx(a_g2_second["iterativeSuccessOffense"])
    assert a_g2_first["iterativeSuccessDefense"] == pytest.approx(a_g2_second["iterativeSuccessDefense"])


def test_three_and_four_game_eligibility_gates():
    row = {"homeIterativeGamesPlayedBefore": 3, "awayIterativeGamesPlayedBefore": 3, "target_margin": 4.0, "target_homeWin": 1}
    row.update({feature: 0.1 for feature in ITERATIVE_FEATURES})
    assert eligible_iterative_row(row, 3) is True
    assert eligible_iterative_row(row, 4) is False
    row["homeIterativeGamesPlayedBefore"] = 4
    row["awayIterativeGamesPlayedBefore"] = 4
    assert eligible_iterative_row(row, 4) is True


def test_model_edges_use_offense_minus_opposing_defensive_strength():
    base = [{"season": 2025, "gameId": "g1", "homeTeam": "A", "awayTeam": "B", "target_margin": 7.0, "target_homeWin": 1}]
    snaps = [
        {"season": 2025, "gameId": "g1", "team": "A", "gamesPlayedBefore": 3, "iterativeSuccessOffense": 0.08, "iterativeSuccessDefense": 0.03},
        {"season": 2025, "gameId": "g1", "team": "B", "gamesPlayedBefore": 4, "iterativeSuccessOffense": -0.02, "iterativeSuccessDefense": 0.04},
    ]
    rows = build_iterative_model_dataset(base, snaps, 2025)
    assert rows[0]["home_iterativeSuccessEdge"] == pytest.approx(0.04)
    assert rows[0]["away_iterativeSuccessEdge"] == pytest.approx(-0.05)
    assert rows[0]["target_margin"] == 7.0


def test_srs_three_team_least_squares_example():
    rows = [_result("MICH", "OSU", 1, "g1", 10), _result("MICH", "PSU", 2, "g2", 4), _result("OSU", "PSU", 3, "g3", 2)]
    result = fit_srs(rows);ratings = result["ratings"]
    assert result["version"] == SRS_VERSION
    assert result["converged"] is True
    assert result["components"] == 1
    assert result["maxNormalResidual"] < 1e-7
    assert result["maxComponentMeanAbs"] < 1e-10
    assert sum(ratings.values()) == pytest.approx(0.0, abs=1e-8)
    assert ratings["MICH"] == pytest.approx(14 / 3, abs=1e-6)
    assert ratings["OSU"] == pytest.approx(-8 / 3, abs=1e-6)
    assert ratings["PSU"] == pytest.approx(-2.0, abs=1e-6)
    assert ratings["MICH"] > ratings["PSU"] > ratings["OSU"]


def test_fast_srs_matches_explicit_least_squares_matrix():
    rows = [
        _result("A", "B", 1, "g1", 17), _result("A", "C", 1, "g2", -3),
        _result("B", "C", 2, "g3", 7), _result("C", "D", 2, "g4", 10),
        _result("D", "A", 3, "g5", 1), _result("B", "D", 3, "g6", -6),
    ]
    fast = fit_srs(rows);direct = fit_srs_direct_reference(rows)
    assert fast["converged"] is True
    assert fast["maxNormalResidual"] < 1e-7
    assert set(fast["ratings"]) == set(direct["ratings"])
    for team in direct["ratings"]:assert fast["ratings"][team] == pytest.approx(direct["ratings"][team], abs=1e-6)


def test_srs_disconnected_components_are_centered_independently():
    result = fit_srs([_result("A", "B", 1, "g1", 10), _result("C", "D", 1, "g2", 6)])
    assert result["components"] == 2
    assert result["converged"] is True
    assert result["ratings"]["A"] + result["ratings"]["B"] == pytest.approx(0.0, abs=1e-9)
    assert result["ratings"]["C"] + result["ratings"]["D"] == pytest.approx(0.0, abs=1e-9)
    assert result["maxComponentMeanAbs"] < 1e-10


def test_srs_duplicate_game_id_is_not_double_counted():
    game = _result("A", "B", 1, "g1", 10);result = fit_srs([game, dict(game)])
    assert result["games"] == 1
    assert result["ratings"]["A"] == pytest.approx(5.0, abs=1e-6)
    assert result["ratings"]["B"] == pytest.approx(-5.0, abs=1e-6)


def test_srs_same_week_isolation_and_edge_contract():
    rows = [_result("A", "B", 1, "g1", 10), _result("A", "C", 2, "g2", 4), _result("B", "C", 2, "g3", 2), _result("A", "B", 3, "g4", 1)]
    out = build_srs_model_dataset(rows, 2025)
    week2 = [r for r in out if r["week"] == 2]
    assert len(week2) == 2
    assert all(r["srsGamesBefore"] == 1 for r in week2)
    assert all(r["srsConverged"] is True for r in week2)
    week3 = next(r for r in out if r["gameId"] == "g4")
    assert week3["srsVersion"] == SRS_VERSION
    assert week3["srsEdge"] == pytest.approx(week3["homeSrs"] - week3["awaySrs"])
    assert week3["srsMaxNormalResidual"] < 1e-7


def test_future_result_does_not_change_prior_srs_snapshot():
    base = [_result("A", "B", 1, "g1", 7), _result("A", "C", 2, "g2", 3), _result("B", "C", 2, "g3", 1), _result("A", "B", 3, "g4", 0)]
    future = base + [_result("C", "A", 4, "g5", 40)]
    first = build_srs_model_dataset(base, 2025);second = build_srs_model_dataset(future, 2025)
    g4_first = next(r for r in first if r["gameId"] == "g4");g4_second = next(r for r in second if r["gameId"] == "g4")
    assert g4_first["homeSrs"] == pytest.approx(g4_second["homeSrs"])
    assert g4_first["awaySrs"] == pytest.approx(g4_second["awaySrs"])
    assert g4_first["srsEdge"] == pytest.approx(g4_second["srsEdge"])


def _audit_fixture():
    games=[]
    for gid,week,home,away in (("g1",1,"A","B"),("g2",2,"A","B")):
        games += [
            {"season":2025,"seasonType":"regular","week":week,"gameId":gid,"team":home,"opponent":away},
            {"season":2025,"seasonType":"regular","week":week,"gameId":gid,"team":away,"opponent":home},
        ]
    common={
        "season":2025,"seasonType":"regular","enrichedDatasetVersion":ENRICHED_DATASET_VERSION,
        "iterativeRatingsVersion":ITERATIVE_RATINGS_VERSION,"srsVersion":SRS_VERSION,
        "iterativeAllSolversConverged":True,"iterativeWorstMaxDelta":0.0,
        "srsConverged":True,"srsMaxNormalResidual":0.0,"srsMaxComponentMeanAbs":0.0,
    }
    rows=[
        {**common,"week":1,"gameId":"g1","homeTeam":"A","awayTeam":"B","target_margin":7.0,"target_homeWin":1,"srsGamesBefore":0,"homeSrs":None,"awaySrs":None,"srsEdge":None,"homeIterativeGamesPlayedBefore":0,"awayIterativeGamesPlayedBefore":0},
        {**common,"week":2,"gameId":"g2","homeTeam":"A","awayTeam":"B","target_margin":3.0,"target_homeWin":1,"srsGamesBefore":1,"homeSrs":3.5,"awaySrs":-3.5,"srsEdge":7.0,"homeIterativeGamesPlayedBefore":1,"awayIterativeGamesPlayedBefore":1},
    ]
    return games,rows


def test_enriched_rows_audit_accepts_consistent_cached_rows():
    games,rows=_audit_fixture();result=enriched_rows_audit(games,rows,2025)
    assert result["status"] == "PASS"
    assert all(result["checks"].values())


def test_enriched_rows_audit_rejects_corrupt_srs_edge_and_leakage_count():
    games,rows=_audit_fixture();rows[1]["srsEdge"]=99.0;rows[1]["srsGamesBefore"]=2
    result=enriched_rows_audit(games,rows,2025)
    assert result["status"] == "REVIEW"
    assert result["checks"]["srs_edge_reconciles"] is False
    assert result["checks"]["srs_prior_game_count"] is False
