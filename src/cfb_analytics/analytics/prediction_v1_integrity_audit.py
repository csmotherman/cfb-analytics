"""Integrity and stability audit for the locked Prediction v1 benchmark.

This audit is intentionally cheap: it reads already-materialized feature stores,
football-mechanism matchups, and authoritative raw CFBD games. It does not replay
play-by-play, rebuild profiles, or refit expensive drive-outcome models.

The audit has three gates:

1. TARGET: compare model targets to final scores in raw CFBD games.json.
2. MWDR: quantify the incremental value of the MWDR family on the exact current
   Prediction-v1 common sample.
3. STABILITY: inspect standardized coefficient signs, leave-one-feature-out OOS
   deltas, and pooled feature correlations across expanding-season holdouts.

If TARGET finds any margin mismatch, the default all-in-one run stops before
model-selection diagnostics. Fix the target contract before optimizing features.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.football_mechanisms import orient_matchup
from cfb_analytics.analytics.iterative_ratings import (
    ITERATIVE_FEATURES,
    SRS_FEATURES,
    eligible_iterative_row,
)
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS, _solve
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.raw.storage import partition_dir

AUDIT_VERSION = "prediction-v1-integrity-audit-v1"
RECENT_TEST_SEASONS = (2023, 2024, 2025)
STABILITY_TEST_SEASONS = tuple(s for s in DEFAULT_SEASONS if s >= 2018)
MIN_GAMES_VALUES = (3, 4)

BASE = tuple(ITERATIVE_FEATURES) + tuple(SRS_FEATURES)
MWDR = ("home_MWDR_OffenseEdge", "home_MWDR_DefenseEdge")
MWDR_INTERACTION = ("mwdrXExpectedPossessions",)
VOLUME = ("successVolumeEdge", "explosiveVolumeEdge", "turnoverVolumeEdge")
FULL = BASE + MWDR + MWDR_INTERACTION + VOLUME
NO_MWDR = BASE + VOLUME
MWDR_WITHOUT_INTERACTION = BASE + MWDR + VOLUME
INDEX = {feature: i for i, feature in enumerate(FULL)}

ID_FIELDS = ("id", "gameId", "game_id")
HOME_TEAM_FIELDS = ("homeTeam", "home_team", "home")
AWAY_TEAM_FIELDS = ("awayTeam", "away_team", "away")
SCORE_FIELD_PAIRS = (
    ("homePoints", "awayPoints"),
    ("home_points", "away_points"),
    ("homeScore", "awayScore"),
    ("home_score", "away_score"),
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _first_value(row: dict[str, Any], fields: tuple[str, ...]) -> Any:
    for field in fields:
        value = row.get(field)
        if value is not None:
            return value
    return None


def extract_authoritative_game(row: dict[str, Any]) -> dict[str, Any] | None:
    """Extract ID, home/away teams, and final score without assuming one schema."""
    game_id = _first_value(row, ID_FIELDS)
    if game_id is None:
        return None
    home_team = _first_value(row, HOME_TEAM_FIELDS)
    away_team = _first_value(row, AWAY_TEAM_FIELDS)
    for home_field, away_field in SCORE_FIELD_PAIRS:
        home_score = row.get(home_field)
        away_score = row.get(away_field)
        if finite(home_score) and finite(away_score):
            return {
                "gameId": str(game_id),
                "homeTeam": home_team,
                "awayTeam": away_team,
                "homeScore": float(home_score),
                "awayScore": float(away_score),
                "scoreFields": f"{home_field}/{away_field}",
            }
    return {
        "gameId": str(game_id),
        "homeTeam": home_team,
        "awayTeam": away_team,
        "homeScore": None,
        "awayScore": None,
        "scoreFields": None,
    }


def load_raw_games(raw_root: Path, season: int) -> tuple[dict[str, dict[str, Any]], list[str]]:
    games: dict[str, dict[str, Any]] = {}
    conflicts: list[str] = []
    for season_type, week in discover_partitions(raw_root, season):
        path = partition_dir(raw_root, season, season_type, week) / "games.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing raw games file: {path}")
        payload = json.loads(path.read_text())
        if not isinstance(payload, list):
            raise ValueError(f"Raw games payload is not a list: {path}")
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            game = extract_authoritative_game(raw)
            if game is None:
                continue
            gid = game["gameId"]
            existing = games.get(gid)
            if existing is not None and existing != game:
                conflicts.append(gid)
            games[gid] = game
    return games, sorted(set(conflicts))


def target_integrity_audit(raw_root: Path, processed_root: Path) -> dict[str, Any]:
    season_reports: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    total_matched = total_exact_score = total_exact_margin = 0
    total_model = total_raw = total_raw_score_missing = 0
    schema_counts: dict[str, int] = {}
    duplicate_conflicts: list[str] = []

    for season in DEFAULT_SEASONS:
        raw_games, conflicts = load_raw_games(raw_root, season)
        duplicate_conflicts.extend(f"{season}:{gid}" for gid in conflicts)
        model_rows = load_saved_feature_store(processed_root, season)
        model_by_id = {str(row.get("gameId")): row for row in model_rows}

        matched = exact_score = exact_margin = raw_score_missing = 0
        for game in raw_games.values():
            fields = game.get("scoreFields")
            if fields:
                schema_counts[fields] = schema_counts.get(fields, 0) + 1
            if not finite(game.get("homeScore")) or not finite(game.get("awayScore")):
                raw_score_missing += 1
                continue
            model = model_by_id.get(game["gameId"])
            if model is None:
                continue
            matched += 1
            raw_home = float(game["homeScore"])
            raw_away = float(game["awayScore"])
            raw_margin = raw_home - raw_away
            model_home = model.get("target_homeScore")
            model_away = model.get("target_awayScore")
            model_margin = model.get("target_margin")

            score_ok = (
                finite(model_home)
                and finite(model_away)
                and abs(float(model_home) - raw_home) <= 1e-9
                and abs(float(model_away) - raw_away) <= 1e-9
            )
            margin_ok = finite(model_margin) and abs(float(model_margin) - raw_margin) <= 1e-9
            exact_score += int(score_ok)
            exact_margin += int(margin_ok)
            if not score_ok or not margin_ok:
                mismatches.append(
                    {
                        "season": season,
                        "gameId": game["gameId"],
                        "raw": f"{game.get('homeTeam')} {raw_home:g}-{raw_away:g} {game.get('awayTeam')}",
                        "model": f"{model.get('homeTeam')} {model_home}-{model_away} {model.get('awayTeam')}",
                        "rawMargin": raw_margin,
                        "modelMargin": model_margin,
                    }
                )

        report = {
            "season": season,
            "rawGames": len(raw_games),
            "modelRows": len(model_rows),
            "matchedScoredGames": matched,
            "exactScore": exact_score,
            "exactMargin": exact_margin,
            "rawScoreMissing": raw_score_missing,
        }
        season_reports.append(report)
        total_raw += len(raw_games)
        total_model += len(model_rows)
        total_matched += matched
        total_exact_score += exact_score
        total_exact_margin += exact_margin
        total_raw_score_missing += raw_score_missing

    status = (
        "PASS"
        if total_matched > 0
        and total_exact_margin == total_matched
        and not duplicate_conflicts
        else "FAIL"
    )
    return {
        "version": AUDIT_VERSION,
        "status": status,
        "rawGames": total_raw,
        "modelRows": total_model,
        "matchedScoredGames": total_matched,
        "exactScore": total_exact_score,
        "exactMargin": total_exact_margin,
        "rawScoreMissing": total_raw_score_missing,
        "scoreSchemas": dict(sorted(schema_counts.items())),
        "duplicateConflicts": duplicate_conflicts,
        "seasons": season_reports,
        "mismatches": mismatches,
    }


def add_prediction_features(row: dict[str, Any], matchup: dict[str, Any]) -> dict[str, Any]:
    out = {**row, **matchup}
    poss = out.get("expectedPossessionsPerTeam")
    mwdr = (
        float(out[MWDR[0]]) + float(out[MWDR[1]])
        if finite(out.get(MWDR[0])) and finite(out.get(MWDR[1]))
        else None
    )
    out["mwdrXExpectedPossessions"] = (
        mwdr * float(poss) if finite(mwdr) and finite(poss) else None
    )
    out["successVolumeEdge"] = (
        float(out["netSuccessRateEdge"]) * float(poss)
        if finite(out.get("netSuccessRateEdge")) and finite(poss)
        else None
    )
    out["explosiveVolumeEdge"] = (
        float(out["netExplosiveRateEdge"]) * float(poss)
        if finite(out.get("netExplosiveRateEdge")) and finite(poss)
        else None
    )
    out["turnoverVolumeEdge"] = (
        float(out["netTurnoverPressureEdge"]) * float(poss)
        if finite(out.get("netTurnoverPressureEdge")) and finite(poss)
        else None
    )
    return out


def load_prediction_rows(processed_root: Path, season: int) -> list[dict[str, Any]]:
    base_rows = load_saved_feature_store(processed_root, season)
    matchup_path = (
        processed_root
        / "derived"
        / "football_mechanisms"
        / f"season={season}"
        / "matchups.json"
    )
    if not matchup_path.exists():
        raise FileNotFoundError(
            f"Missing football mechanisms for {season}: {matchup_path}. "
            "Run python -m cfb_analytics.analytics.football_mechanisms --all once."
        )
    matchups = {
        str(row.get("gameId")): row
        for row in json.loads(matchup_path.read_text())
        if row.get("gameId") is not None
    }
    out: list[dict[str, Any]] = []
    for row in base_rows:
        matchup = matchups.get(str(row.get("gameId")))
        if matchup is None:
            continue
        oriented = orient_matchup(matchup, row.get("homeTeam"), row.get("awayTeam"))
        if oriented is not None:
            out.append(add_prediction_features(row, oriented))
    return out


def eligible_full(row: dict[str, Any], min_games: int) -> bool:
    return eligible_iterative_row(row, min_games) and all(
        finite(row.get(feature)) for feature in FULL
    )


def prepare(rows: list[dict[str, Any]]) -> dict[str, Any]:
    means: list[float] = []
    scales: list[float] = []
    for feature in FULL:
        values = [float(row[feature]) for row in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        means.append(mean)
        scales.append(math.sqrt(variance) or 1.0)

    p = len(FULL) + 1
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    for row in rows:
        x = [1.0] + [
            (float(row[feature]) - means[i]) / scales[i]
            for i, feature in enumerate(FULL)
        ]
        y = float(row["target_margin"])
        for i, xi in enumerate(x):
            xty[i] += xi * y
            for j in range(i, p):
                xtx[i][j] += xi * x[j]
    for i in range(p):
        for j in range(i):
            xtx[i][j] = xtx[j][i]
    return {"means": means, "scales": scales, "xtx": xtx, "xty": xty}


def fit(stats: dict[str, Any], features: tuple[str, ...], ridge: float = 1e-6) -> dict[str, Any]:
    indices = [0] + [INDEX[feature] + 1 for feature in features]
    matrix = [[stats["xtx"][i][j] for j in indices] for i in indices]
    target = [stats["xty"][i] for i in indices]
    for i in range(1, len(matrix)):
        matrix[i][i] += ridge
    weights = _solve(matrix, target)
    if weights is None:
        raise ValueError("singular model")
    return {
        "features": features,
        "weights": weights,
        "means": stats["means"],
        "scales": stats["scales"],
    }


def predict(model: dict[str, Any], row: dict[str, Any]) -> float:
    value = float(model["weights"][0])
    for j, feature in enumerate(model["features"], 1):
        i = INDEX[feature]
        value += float(model["weights"][j]) * (
            (float(row[feature]) - float(model["means"][i]))
            / float(model["scales"][i])
        )
    return value


def score(model: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, float]:
    absolute: list[float] = []
    squared: list[float] = []
    correct = 0
    for row in rows:
        prediction = predict(model, row)
        actual = float(row["target_margin"])
        absolute.append(abs(prediction - actual))
        squared.append((prediction - actual) ** 2)
        correct += int((prediction > 0.0) == bool(row["target_homeWin"]))
    n = len(rows)
    return {
        "n": n,
        "mae": sum(absolute) / n,
        "rmse": math.sqrt(sum(squared) / n),
        "winner": correct / n,
    }


def coefficient_map(model: dict[str, Any]) -> dict[str, float]:
    return {
        feature: float(model["weights"][i + 1])
        for i, feature in enumerate(model["features"])
    }


def load_all_prediction_rows(processed_root: Path) -> dict[int, list[dict[str, Any]]]:
    print("Loading saved Prediction-v1 feature stores only; no PBP replay.", flush=True)
    data: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        rows = load_prediction_rows(processed_root, season)
        data[season] = rows
        print(f" LOAD {season}: {len(rows):,} merged game rows", flush=True)
    return data


def mwdr_dependency_audit(data: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    variants = {
        "NO_MWDR": NO_MWDR,
        "MWDR_NO_INTERACTION": MWDR_WITHOUT_INTERACTION,
    }
    rows_out: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        eligible = {
            season: [row for row in data[season] if eligible_full(row, min_games)]
            for season in DEFAULT_SEASONS
        }
        for test_season in RECENT_TEST_SEASONS:
            train = [
                row
                for season in DEFAULT_SEASONS
                if season < test_season
                for row in eligible[season]
            ]
            test = eligible[test_season]
            stats = prepare(train)
            full = score(fit(stats, FULL), test)
            for name, features in variants.items():
                challenger = score(fit(stats, features), test)
                rows_out.append(
                    {
                        "variant": name,
                        "minGames": min_games,
                        "season": test_season,
                        "n": len(test),
                        "deltaMaeVsFull": challenger["mae"] - full["mae"],
                        "deltaRmseVsFull": challenger["rmse"] - full["rmse"],
                        "deltaWinnerVsFullPP": (challenger["winner"] - full["winner"]) * 100.0,
                        "fullMae": full["mae"],
                        "variantMae": challenger["mae"],
                    }
                )

    summary: dict[str, Any] = {}
    for name in variants:
        subset = [row for row in rows_out if row["variant"] == name]
        summary[name] = {
            "folds": len(subset),
            "meanDeltaMae": sum(row["deltaMaeVsFull"] for row in subset) / len(subset),
            "meanDeltaRmse": sum(row["deltaRmseVsFull"] for row in subset) / len(subset),
            "meanDeltaWinnerPP": sum(row["deltaWinnerVsFullPP"] for row in subset) / len(subset),
            "maeBetterThanFull": sum(row["deltaMaeVsFull"] < 0 for row in subset),
            "rmseBetterThanFull": sum(row["deltaRmseVsFull"] < 0 for row in subset),
        }
    return {"rows": rows_out, "summary": summary}


def pearson(rows: list[dict[str, Any]], left: str, right: str) -> float:
    xs = [float(row[left]) for row in rows]
    ys = [float(row[right]) for row in rows]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    xx = sum((x - mx) ** 2 for x in xs)
    yy = sum((y - my) ** 2 for y in ys)
    if xx <= 0.0 or yy <= 0.0:
        return 0.0
    xy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return xy / math.sqrt(xx * yy)


def stability_audit(data: dict[int, list[dict[str, Any]]]) -> dict[str, Any]:
    per_feature: dict[str, list[dict[str, Any]]] = {feature: [] for feature in FULL}
    folds: list[dict[str, Any]] = []

    for min_games in MIN_GAMES_VALUES:
        eligible = {
            season: [row for row in data[season] if eligible_full(row, min_games)]
            for season in DEFAULT_SEASONS
        }
        for test_season in STABILITY_TEST_SEASONS:
            prior_seasons = [season for season in DEFAULT_SEASONS if season < test_season]
            if len(prior_seasons) < 4:
                continue
            train = [row for season in prior_seasons for row in eligible[season]]
            test = eligible[test_season]
            if not train or not test:
                continue
            stats = prepare(train)
            full_model = fit(stats, FULL)
            full_score = score(full_model, test)
            coefs = coefficient_map(full_model)
            folds.append(
                {
                    "minGames": min_games,
                    "season": test_season,
                    "train": len(train),
                    "test": len(test),
                    "fullMae": full_score["mae"],
                    "fullRmse": full_score["rmse"],
                }
            )
            for feature in FULL:
                reduced_features = tuple(item for item in FULL if item != feature)
                reduced = score(fit(stats, reduced_features), test)
                per_feature[feature].append(
                    {
                        "minGames": min_games,
                        "season": test_season,
                        "coefficient": coefs[feature],
                        "dropDeltaMae": reduced["mae"] - full_score["mae"],
                        "dropDeltaRmse": reduced["rmse"] - full_score["rmse"],
                        "dropDeltaWinnerPP": (reduced["winner"] - full_score["winner"]) * 100.0,
                    }
                )

    feature_summary: list[dict[str, Any]] = []
    for feature, rows in per_feature.items():
        coefficients = [row["coefficient"] for row in rows]
        mae = [row["dropDeltaMae"] for row in rows]
        rmse = [row["dropDeltaRmse"] for row in rows]
        positive = sum(value > 0 for value in coefficients)
        negative = sum(value < 0 for value in coefficients)
        near_zero = sum(abs(value) < 0.05 for value in coefficients)
        feature_summary.append(
            {
                "feature": feature,
                "folds": len(rows),
                "meanCoefficient": sum(coefficients) / len(coefficients),
                "positiveCoefficientFolds": positive,
                "negativeCoefficientFolds": negative,
                "nearZeroCoefficientFolds": near_zero,
                "meanDropDeltaMae": sum(mae) / len(mae),
                "meanDropDeltaRmse": sum(rmse) / len(rmse),
                "dropWorsensMaeFolds": sum(value > 0 for value in mae),
                "dropWorsensRmseFolds": sum(value > 0 for value in rmse),
            }
        )
    feature_summary.sort(
        key=lambda row: (row["meanDropDeltaMae"], row["meanDropDeltaRmse"]),
        reverse=True,
    )

    pooled = [
        row
        for season in DEFAULT_SEASONS
        for row in data[season]
        if eligible_full(row, 3)
    ]
    correlations: list[dict[str, Any]] = []
    for i, left in enumerate(FULL):
        for right in FULL[i + 1 :]:
            correlation = pearson(pooled, left, right)
            correlations.append(
                {"left": left, "right": right, "correlation": correlation}
            )
    correlations.sort(key=lambda row: abs(row["correlation"]), reverse=True)

    prune_candidates = [
        row["feature"]
        for row in feature_summary
        if row["meanDropDeltaMae"] < 0.0 and row["meanDropDeltaRmse"] < 0.0
    ]
    return {
        "folds": folds,
        "features": feature_summary,
        "topCorrelations": correlations[:12],
        "pruneScreenCandidates": prune_candidates,
    }


def print_target_report(result: dict[str, Any]) -> None:
    print("PREDICTION V1 TARGET INTEGRITY")
    print(f"Status: {result['status']}")
    print(f"Raw games: {result['rawGames']:,}")
    print(f"Model rows: {result['modelRows']:,}")
    print(f"Matched scored games: {result['matchedScoredGames']:,}")
    print(f"Exact final scores: {result['exactScore']:,}/{result['matchedScoredGames']:,}")
    print(f"Exact margins: {result['exactMargin']:,}/{result['matchedScoredGames']:,}")
    print(f"Raw games without numeric final score: {result['rawScoreMissing']:,}")
    print("Score fields observed: " + ", ".join(
        f"{key}={value:,}" for key, value in result["scoreSchemas"].items()
    ))
    if result["duplicateConflicts"]:
        print(f"Conflicting duplicate raw game IDs: {len(result['duplicateConflicts']):,}")
    for row in result["seasons"]:
        print(
            f" {row['season']}: matched={row['matchedScoredGames']:,} | "
            f"score={row['exactScore']:,}/{row['matchedScoredGames']:,} | "
            f"margin={row['exactMargin']:,}/{row['matchedScoredGames']:,} | "
            f"raw missing score={row['rawScoreMissing']:,}"
        )
    if result["mismatches"]:
        print("Mismatch examples:")
        for row in result["mismatches"][:10]:
            print(
                f" {row['season']} {row['gameId']}: raw {row['raw']} | "
                f"model {row['model']} | margin {row['rawMargin']} vs {row['modelMargin']}"
            )


def print_mwdr_report(result: dict[str, Any]) -> None:
    print("\nMWDR FAMILY DEPENDENCY — RECENT SIX HOLDOUTS")
    print("Deltas are challenger minus CURRENT FULL; negative means removing/simplifying MWDR is better.")
    for row in result["rows"]:
        print(
            f" {row['variant']} min{row['minGames']} {row['season']}: "
            f"MAE {row['deltaMaeVsFull']:+.4f} | RMSE {row['deltaRmseVsFull']:+.4f} | "
            f"Winner {row['deltaWinnerVsFullPP']:+.2f} pp | n={row['n']:,}"
        )
    print("SUMMARY:")
    for name, summary in result["summary"].items():
        print(
            f" {name}: mean MAE {summary['meanDeltaMae']:+.4f} | "
            f"RMSE {summary['meanDeltaRmse']:+.4f} | Winner {summary['meanDeltaWinnerPP']:+.2f} pp | "
            f"MAE better {summary['maeBetterThanFull']}/{summary['folds']} | "
            f"RMSE better {summary['rmseBetterThanFull']}/{summary['folds']}"
        )


def print_stability_report(result: dict[str, Any]) -> None:
    print("\nPREDICTION V1 FEATURE STABILITY — 14-FOLD EXPANDING-SEASON SCREEN")
    print("drop Δ = model WITHOUT feature minus FULL; positive means the feature helped FULL.")
    print("Features ranked by mean OOS MAE damage when dropped:")
    for row in result["features"]:
        folds = row["folds"]
        print(
            f" {row['feature']}: coef {row['meanCoefficient']:+.3f} "
            f"(+{row['positiveCoefficientFolds']}/-{row['negativeCoefficientFolds']}, near0 {row['nearZeroCoefficientFolds']}/{folds}) | "
            f"drop MAE {row['meanDropDeltaMae']:+.4f} ({row['dropWorsensMaeFolds']}/{folds} worse) | "
            f"drop RMSE {row['meanDropDeltaRmse']:+.4f} ({row['dropWorsensRmseFolds']}/{folds} worse)"
        )
    print("\nTOP ABSOLUTE FEATURE CORRELATIONS (pooled min3 common sample):")
    for row in result["topCorrelations"]:
        print(
            f" {row['left']} <> {row['right']}: r={row['correlation']:+.3f}"
        )
    candidates = result["pruneScreenCandidates"]
    print("\nPRUNE SCREEN CANDIDATES:")
    if candidates:
        print(" " + ", ".join(candidates))
        print("These are only candidates for a dedicated same-sample lean-model challenger; nothing is removed by this audit.")
    else:
        print(" None. No feature improved both mean MAE and RMSE when removed across the stability folds.")


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path, default=root / "data" / "raw")
    parser.add_argument("--processed-root", type=Path, default=root / "data" / "processed")
    parser.add_argument(
        "--section",
        choices=("all", "targets", "model"),
        default="all",
        help="targets = score contract only; model = MWDR/stability only; all = target gate then model diagnostics",
    )
    args = parser.parse_args()

    if args.section in {"all", "targets"}:
        targets = target_integrity_audit(args.raw_root, args.processed_root)
        print_target_report(targets)
        if args.section == "targets":
            return
        if targets["status"] != "PASS":
            print("\nSTOP: target integrity failed. Model diagnostics were intentionally skipped.")
            raise SystemExit(2)

    data = load_all_prediction_rows(args.processed_root)
    mwdr = mwdr_dependency_audit(data)
    stability = stability_audit(data)
    print_mwdr_report(mwdr)
    print_stability_report(stability)


if __name__ == "__main__":
    main()
