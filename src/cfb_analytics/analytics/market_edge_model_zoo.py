"""Broad, leakage-safe market-edge discovery screen for college football.

This module asks a different question from Prediction v2:

    Can pregame football features predict *the market's error*?

The clean CFBD spread is treated as the benchmark forecast.  For every official
outer test season, candidate models are fit only on earlier seasons.  Prediction
v2 remains untouched and is included only as a reference / fixed-blend input.

This is a DISCOVERY screen, not a promotion test.  Many model families are
reported together, so an attractive isolated result must be confirmed by a
predeclared follow-up test and, ultimately, the untouched 2026 prospective set.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
from sklearn.base import clone
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import (
    BayesianRidge,
    ElasticNet,
    HuberRegressor,
    LogisticRegression,
    QuantileRegressor,
    Ridge,
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from cfb_analytics.analytics.prediction_v1_integrity_audit import MIN_GAMES_VALUES
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    TEST_SEASONS,
    eligible_site,
    fit_generic,
    load_data,
    predict_generic,
    prepare_generic,
)
from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v2_clean_market_benchmark import (
    DEFAULT_LINES,
    clean_market_rows,
)
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

DISCOVERY_VERSION = "market-edge-model-zoo-v1"
DEFAULT_REPORT = Path("data/processed/market_benchmark/market-edge-model-zoo.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/market-edge-model-zoo-games.json")
BREAK_EVEN_MINUS_110 = 110.0 / 210.0
CONFIDENCE_THRESHOLDS = (0.50, 0.55, 0.575, 0.60)

# All fields below are known before kickoff.  The market transformations make
# simple linear models capable of expressing favourite/longshot and week effects
# without forcing tree models to discover them from scratch.
MARKET_CONTEXT_FEATURES = (
    "marketHomeMargin",
    "marketAbsSpread",
    "marketSpreadSquared",
    "marketHomeFavorite",
    "marketPickem",
    "weekNumber",
    "neutralSite",
)
MODEL_FEATURES = tuple(PREDICTION_V2_FEATURES) + MARKET_CONTEXT_FEATURES


@dataclass(frozen=True)
class RegressionSpec:
    name: str
    target: str  # "residual" or "direct"
    factory: Callable[[], Any]


@dataclass(frozen=True)
class ClassifierSpec:
    name: str
    factory: Callable[[], Any]


def _scaled(model: Any) -> Any:
    return make_pipeline(StandardScaler(), model)


REGRESSION_SPECS = (
    RegressionSpec("RESIDUAL_RIDGE", "residual", lambda: _scaled(Ridge(alpha=10.0))),
    RegressionSpec(
        "RESIDUAL_ELASTICNET",
        "residual",
        lambda: _scaled(ElasticNet(alpha=0.05, l1_ratio=0.2, max_iter=5000, random_state=42)),
    ),
    RegressionSpec(
        "RESIDUAL_HUBER",
        "residual",
        lambda: _scaled(HuberRegressor(epsilon=1.35, alpha=0.0001, max_iter=500)),
    ),
    RegressionSpec(
        "RESIDUAL_MEDIAN_QUANTILE",
        "residual",
        lambda: _scaled(QuantileRegressor(quantile=0.5, alpha=0.05, solver="highs")),
    ),
    RegressionSpec("RESIDUAL_BAYESIAN_RIDGE", "residual", lambda: _scaled(BayesianRidge())),
    RegressionSpec(
        "RESIDUAL_GRADIENT_BOOSTING",
        "residual",
        lambda: GradientBoostingRegressor(
            loss="huber", n_estimators=300, learning_rate=0.03, max_depth=2,
            min_samples_leaf=12, random_state=42,
        ),
    ),
    RegressionSpec(
        "RESIDUAL_HIST_GB",
        "residual",
        lambda: HistGradientBoostingRegressor(
            loss="squared_error", learning_rate=0.05, max_iter=300,
            max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=1.0,
            random_state=42,
        ),
    ),
    RegressionSpec(
        "RESIDUAL_RANDOM_FOREST",
        "residual",
        lambda: RandomForestRegressor(
            n_estimators=300, min_samples_leaf=8, max_features=0.75,
            n_jobs=-1, random_state=42,
        ),
    ),
    RegressionSpec(
        "RESIDUAL_EXTRA_TREES",
        "residual",
        lambda: ExtraTreesRegressor(
            n_estimators=300, min_samples_leaf=8, max_features=0.75,
            n_jobs=-1, random_state=42,
        ),
    ),
    RegressionSpec(
        "RESIDUAL_KNN",
        "residual",
        lambda: _scaled(KNeighborsRegressor(n_neighbors=50, weights="distance", p=2)),
    ),
    RegressionSpec(
        "RESIDUAL_RBF_SVR",
        "residual",
        lambda: _scaled(SVR(C=3.0, epsilon=0.2, gamma="scale", kernel="rbf")),
    ),
    RegressionSpec(
        "RESIDUAL_MLP",
        "residual",
        lambda: _scaled(
            MLPRegressor(
                hidden_layer_sizes=(64, 32), activation="relu", alpha=0.01,
                early_stopping=True, validation_fraction=0.15,
                max_iter=500, random_state=42,
            )
        ),
    ),
    RegressionSpec("DIRECT_RIDGE", "direct", lambda: _scaled(Ridge(alpha=10.0))),
    RegressionSpec(
        "DIRECT_HIST_GB",
        "direct",
        lambda: HistGradientBoostingRegressor(
            loss="squared_error", learning_rate=0.05, max_iter=300,
            max_leaf_nodes=15, min_samples_leaf=20, l2_regularization=1.0,
            random_state=42,
        ),
    ),
    RegressionSpec(
        "DIRECT_EXTRA_TREES",
        "direct",
        lambda: ExtraTreesRegressor(
            n_estimators=300, min_samples_leaf=8, max_features=0.75,
            n_jobs=-1, random_state=42,
        ),
    ),
)

CLASSIFIER_SPECS = (
    ClassifierSpec(
        "ATS_LOGISTIC",
        lambda: _scaled(LogisticRegression(C=0.5, max_iter=2000, random_state=42)),
    ),
    ClassifierSpec(
        "ATS_GRADIENT_BOOSTING",
        lambda: GradientBoostingClassifier(
            n_estimators=250, learning_rate=0.03, max_depth=2,
            min_samples_leaf=15, random_state=42,
        ),
    ),
    ClassifierSpec(
        "ATS_HIST_GB",
        lambda: HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=250, max_leaf_nodes=15,
            min_samples_leaf=20, l2_regularization=1.0, random_state=42,
        ),
    ),
    ClassifierSpec(
        "ATS_RANDOM_FOREST",
        lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=10, max_features=0.75,
            class_weight="balanced_subsample", n_jobs=-1, random_state=42,
        ),
    ),
    ClassifierSpec(
        "ATS_EXTRA_TREES",
        lambda: ExtraTreesClassifier(
            n_estimators=300, min_samples_leaf=10, max_features=0.75,
            class_weight="balanced", n_jobs=-1, random_state=42,
        ),
    ),
    ClassifierSpec(
        "ATS_MLP",
        lambda: _scaled(
            MLPClassifier(
                hidden_layer_sizes=(48, 24), alpha=0.01, early_stopping=True,
                validation_fraction=0.15, max_iter=500, random_state=42,
            )
        ),
    ),
)

FIXED_BLEND_WEIGHTS = (0.10, 0.25, 0.50, 0.75)


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _sign(value: float, tol: float = 1e-12) -> int:
    return 1 if value > tol else (-1 if value < -tol else 0)


def attach_market(row: dict[str, Any], market: dict[str, Any]) -> dict[str, Any]:
    if str(row.get("homeTeam")) != str(market.get("homeTeam")) or str(row.get("awayTeam")) != str(market.get("awayTeam")):
        raise ValueError(f"Market identity mismatch for game {row.get('gameId')}")
    spread = float(market["marketHomeMargin"])
    week = float(row.get("week") or 0)
    neutral = 1.0 if row.get("isNeutralSite") is True else 0.0
    return {
        **row,
        "marketHomeMargin": spread,
        "marketAbsSpread": abs(spread),
        "marketSpreadSquared": spread * spread,
        "marketHomeFavorite": 1.0 if spread > 0.0 else 0.0,
        "marketPickem": 1.0 if abs(spread) <= 1e-12 else 0.0,
        "weekNumber": week,
        "neutralSite": neutral,
    }


def feature_matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    matrix = np.asarray([[float(row[name]) for name in MODEL_FEATURES] for row in rows], dtype=float)
    if not np.isfinite(matrix).all():
        raise ValueError("Non-finite model-zoo feature matrix")
    return matrix


def regression_prediction(model: Any, rows: list[dict[str, Any]], target: str) -> np.ndarray:
    raw = np.asarray(model.predict(feature_matrix(rows)), dtype=float)
    if target == "residual":
        market = np.asarray([float(row["marketHomeMargin"]) for row in rows], dtype=float)
        raw = market + raw
    if not np.isfinite(raw).all():
        raise ValueError("Non-finite regression prediction")
    return raw


def _roi_minus_110(wins: int, losses: int) -> float | None:
    decisions = wins + losses
    if not decisions:
        return None
    # Risk 1 unit on every -110 bet: win returns 100/110 units of profit.
    return (wins * (100.0 / 110.0) - losses) / decisions


def grade_margin_predictions(
    rows: list[dict[str, Any]], predictions: np.ndarray,
) -> dict[str, Any]:
    if len(rows) != len(predictions):
        raise ValueError("Prediction length mismatch")
    model_abs: list[float] = []
    market_abs: list[float] = []
    model_sq: list[float] = []
    market_sq: list[float] = []
    winner_correct = 0
    market_winner_correct = 0
    ats_wins = ats_losses = ats_pushes = 0
    for row, pred_raw in zip(rows, predictions):
        pred = float(pred_raw)
        actual = float(row["target_margin"])
        market = float(row["marketHomeMargin"])
        model_abs.append(abs(pred - actual))
        market_abs.append(abs(market - actual))
        model_sq.append((pred - actual) ** 2)
        market_sq.append((market - actual) ** 2)
        winner_correct += int(_sign(pred) == _sign(actual))
        market_winner_correct += int(_sign(market) == _sign(actual))
        pick = _sign(pred - market)
        cover = _sign(actual - market)
        if pick == 0 or cover == 0:
            ats_pushes += 1
        elif pick == cover:
            ats_wins += 1
        else:
            ats_losses += 1
    n = len(rows)
    decisions = ats_wins + ats_losses
    mae = sum(model_abs) / n
    market_mae = sum(market_abs) / n
    rmse = math.sqrt(sum(model_sq) / n)
    market_rmse = math.sqrt(sum(market_sq) / n)
    return {
        "n": n,
        "mae": mae,
        "marketMae": market_mae,
        "deltaMaeVsMarket": mae - market_mae,
        "rmse": rmse,
        "marketRmse": market_rmse,
        "deltaRmseVsMarket": rmse - market_rmse,
        "winnerAccuracy": winner_correct / n,
        "marketWinnerAccuracy": market_winner_correct / n,
        "atsWins": ats_wins,
        "atsLosses": ats_losses,
        "atsPushes": ats_pushes,
        "atsDecisions": decisions,
        "atsAccuracy": ats_wins / decisions if decisions else None,
        "roiMinus110": _roi_minus_110(ats_wins, ats_losses),
    }


def grade_classifier(
    rows: list[dict[str, Any]], probabilities_home_cover: np.ndarray, threshold: float,
) -> dict[str, Any]:
    wins = losses = pushes = no_bet = 0
    confidence_sum = 0.0
    for row, p_raw in zip(rows, probabilities_home_cover):
        p = float(p_raw)
        confidence = max(p, 1.0 - p)
        if confidence + 1e-12 < threshold:
            no_bet += 1
            continue
        side = 1 if p >= 0.5 else -1
        cover = _sign(float(row["target_margin"]) - float(row["marketHomeMargin"]))
        confidence_sum += confidence
        if cover == 0:
            pushes += 1
        elif side == cover:
            wins += 1
        else:
            losses += 1
    decisions = wins + losses
    bets = decisions + pushes
    return {
        "confidenceThreshold": threshold,
        "bets": bets,
        "noBet": no_bet,
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "decisions": decisions,
        "accuracy": wins / decisions if decisions else None,
        "roiMinus110": _roi_minus_110(wins, losses),
        "meanConfidenceOnBets": confidence_sum / bets if bets else None,
    }


def _fit_regression(spec: RegressionSpec, train: list[dict[str, Any]]) -> Any:
    x = feature_matrix(train)
    if spec.target == "residual":
        y = np.asarray([
            float(row["target_margin"]) - float(row["marketHomeMargin"])
            for row in train
        ])
    else:
        y = np.asarray([float(row["target_margin"]) for row in train])
    model = spec.factory()
    model.fit(x, y)
    return model


def _fit_classifier(spec: ClassifierSpec, train: list[dict[str, Any]]) -> Any:
    no_push = [row for row in train if _sign(float(row["target_margin"]) - float(row["marketHomeMargin"])) != 0]
    x = feature_matrix(no_push)
    y = np.asarray([
        1 if float(row["target_margin"]) > float(row["marketHomeMargin"]) else 0
        for row in no_push
    ], dtype=int)
    model = spec.factory()
    model.fit(x, y)
    return model


def _predict_home_cover_probability(model: Any, rows: list[dict[str, Any]]) -> np.ndarray:
    probs = np.asarray(model.predict_proba(feature_matrix(rows)), dtype=float)
    classes = list(model.classes_)
    if 1 not in classes:
        raise ValueError("ATS classifier has no positive/home-cover class")
    return probs[:, classes.index(1)]


def _pooled_margin(rows: list[dict[str, Any]], model_name: str) -> dict[str, Any]:
    subset = [row for row in rows if row.get("model") == model_name and row.get("prediction") is not None]
    return grade_margin_predictions(subset, np.asarray([float(row["prediction"]) for row in subset]))


def run_discovery(lines: Path, raw_root: Path, processed_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    clean_market = clean_market_rows(lines)
    market_by_id = {str(row["gameId"]): row for row in clean_market}
    data = load_data(raw_root, processed_root)

    attached: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        rows: list[dict[str, Any]] = []
        for row in data[season]:
            market = market_by_id.get(str(row.get("gameId")))
            if market is None:
                continue
            merged = attach_market(row, market)
            if all(finite(merged.get(name)) for name in MODEL_FEATURES):
                rows.append(merged)
        attached[season] = rows

    fold_summaries: list[dict[str, Any]] = []
    per_game: list[dict[str, Any]] = []
    classifier_folds: list[dict[str, Any]] = []

    for min_games in MIN_GAMES_VALUES:
        eligible_full = {
            season: [row for row in data[season] if eligible_site(row, min_games)]
            for season in DEFAULT_SEASONS
        }
        eligible_market = {
            season: [row for row in attached[season] if eligible_site(row, min_games)]
            for season in DEFAULT_SEASONS
        }

        for test_season in TEST_SEASONS:
            train_market = [
                row for season in DEFAULT_SEASONS if season < test_season
                for row in eligible_market[season]
            ]
            test = eligible_market[test_season]
            train_v2 = [
                row for season in DEFAULT_SEASONS if season < test_season
                for row in eligible_full[season]
            ]
            if not train_market or not test or not train_v2:
                raise ValueError(f"Empty market-edge fold min{min_games} {test_season}")

            v2_model = fit_generic(prepare_generic(train_v2, PREDICTION_V2_FEATURES))
            v2_preds = np.asarray([predict_generic(v2_model, row) for row in test], dtype=float)
            market_preds = np.asarray([float(row["marketHomeMargin"]) for row in test], dtype=float)

            # Reference forecasts.
            for model_name, predictions in (("MARKET", market_preds), ("PREDICTION_V2", v2_preds)):
                summary = grade_margin_predictions(test, predictions)
                fold_summaries.append({
                    "minGames": min_games, "season": test_season, "model": model_name,
                    "trainN": len(train_market), **summary,
                })
                for row, pred in zip(test, predictions):
                    per_game.append({
                        "minGames": min_games,
                        "season": test_season,
                        "gameId": str(row["gameId"]),
                        "homeTeam": row.get("homeTeam"),
                        "awayTeam": row.get("awayTeam"),
                        "actualHomeMargin": float(row["target_margin"]),
                        "marketHomeMargin": float(row["marketHomeMargin"]),
                        "model": model_name,
                        "prediction": float(pred),
                    })

            # Fixed shrinkage/blend family: market + lambda * (v2 - market).
            for weight in FIXED_BLEND_WEIGHTS:
                predictions = market_preds + weight * (v2_preds - market_preds)
                model_name = f"BLEND_V2_{int(round(weight * 100)):02d}PCT"
                summary = grade_margin_predictions(test, predictions)
                fold_summaries.append({
                    "minGames": min_games, "season": test_season, "model": model_name,
                    "trainN": len(train_market), **summary,
                })
                for row, pred in zip(test, predictions):
                    per_game.append({
                        "minGames": min_games, "season": test_season,
                        "gameId": str(row["gameId"]), "homeTeam": row.get("homeTeam"),
                        "awayTeam": row.get("awayTeam"),
                        "actualHomeMargin": float(row["target_margin"]),
                        "marketHomeMargin": float(row["marketHomeMargin"]),
                        "model": model_name, "prediction": float(pred),
                    })

            for spec in REGRESSION_SPECS:
                fitted = _fit_regression(spec, train_market)
                predictions = regression_prediction(fitted, test, spec.target)
                summary = grade_margin_predictions(test, predictions)
                fold_summaries.append({
                    "minGames": min_games, "season": test_season, "model": spec.name,
                    "targetMode": spec.target, "trainN": len(train_market), **summary,
                })
                for row, pred in zip(test, predictions):
                    per_game.append({
                        "minGames": min_games, "season": test_season,
                        "gameId": str(row["gameId"]), "homeTeam": row.get("homeTeam"),
                        "awayTeam": row.get("awayTeam"),
                        "actualHomeMargin": float(row["target_margin"]),
                        "marketHomeMargin": float(row["marketHomeMargin"]),
                        "model": spec.name, "prediction": float(pred),
                    })

            for spec in CLASSIFIER_SPECS:
                fitted = _fit_classifier(spec, train_market)
                probabilities = _predict_home_cover_probability(fitted, test)
                for threshold in CONFIDENCE_THRESHOLDS:
                    classifier_folds.append({
                        "minGames": min_games,
                        "season": test_season,
                        "model": spec.name,
                        "trainN": len(train_market),
                        **grade_classifier(test, probabilities, threshold),
                    })

    margin_models = sorted({row["model"] for row in per_game})
    pooled_margin: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        for model_name in margin_models:
            rows = [row for row in per_game if row["minGames"] == min_games and row["model"] == model_name]
            if not rows:
                continue
            converted = [
                {
                    "target_margin": row["actualHomeMargin"],
                    "marketHomeMargin": row["marketHomeMargin"],
                }
                for row in rows
            ]
            summary = grade_margin_predictions(converted, np.asarray([float(row["prediction"]) for row in rows]))
            pooled_margin.append({"minGames": min_games, "model": model_name, **summary})

    pooled_classifiers: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        for spec in CLASSIFIER_SPECS:
            for threshold in CONFIDENCE_THRESHOLDS:
                folds = [
                    row for row in classifier_folds
                    if row["minGames"] == min_games and row["model"] == spec.name
                    and abs(float(row["confidenceThreshold"]) - threshold) <= 1e-12
                ]
                wins = sum(int(row["wins"]) for row in folds)
                losses = sum(int(row["losses"]) for row in folds)
                pushes = sum(int(row["pushes"]) for row in folds)
                no_bet = sum(int(row["noBet"]) for row in folds)
                decisions = wins + losses
                pooled_classifiers.append({
                    "minGames": min_games,
                    "model": spec.name,
                    "confidenceThreshold": threshold,
                    "wins": wins, "losses": losses, "pushes": pushes,
                    "decisions": decisions, "noBet": no_bet,
                    "accuracy": wins / decisions if decisions else None,
                    "roiMinus110": _roi_minus_110(wins, losses),
                })

    return {
        "schemaVersion": 1,
        "discoveryVersion": DISCOVERY_VERSION,
        "status": "EXPLORATORY_MODEL_ZOO_NOT_PROMOTION_EVIDENCE",
        "marketSelection": "first parseable formattedSpread in CFBD provider order",
        "testSeasons": list(TEST_SEASONS),
        "minGamesValues": list(MIN_GAMES_VALUES),
        "features": list(MODEL_FEATURES),
        "breakEvenMinus110": BREAK_EVEN_MINUS_110,
        "fixedBlendWeights": list(FIXED_BLEND_WEIGHTS),
        "classifierConfidenceThresholds": list(CONFIDENCE_THRESHOLDS),
        "regressionModels": [spec.name for spec in REGRESSION_SPECS],
        "classifierModels": [spec.name for spec in CLASSIFIER_SPECS],
        "folds": fold_summaries,
        "pooledMargin": pooled_margin,
        "classifierFolds": classifier_folds,
        "pooledClassifiers": pooled_classifiers,
    }, per_game


def _write(path: Path, payload: Any, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _fmt(value: Any, percent: bool = False) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.3%}" if percent else f"{float(value):+.4f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Leakage-safe market-edge model zoo")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = run_discovery(args.lines, args.raw_root, args.processed_root)
    print("MARKET EDGE MODEL ZOO — EXPLORATORY")
    print(f"Version: {DISCOVERY_VERSION}")
    print("Every outer test season is predicted from earlier seasons only.")
    print(f"-110 break-even ATS rate: {BREAK_EVEN_MINUS_110:.3%}\n")

    for min_games in MIN_GAMES_VALUES:
        print(f"=== MARGIN / RESIDUAL MODELS min{min_games} ===")
        rows = [row for row in report["pooledMargin"] if row["minGames"] == min_games]
        rows.sort(key=lambda row: (float(row["deltaMaeVsMarket"]), float(row["deltaRmseVsMarket"])))
        for row in rows:
            print(
                f"{row['model']:<28} n={row['n']:4d} "
                f"MAE={row['mae']:.4f} dMAE={row['deltaMaeVsMarket']:+.4f} "
                f"RMSE={row['rmse']:.4f} dRMSE={row['deltaRmseVsMarket']:+.4f} "
                f"ATS={row['atsWins']}-{row['atsLosses']}-{row['atsPushes']} "
                f"({_fmt(row['atsAccuracy'], True)}) ROI={_fmt(row['roiMinus110'], True)}"
            )
        print()

        print(f"=== DIRECT ATS CLASSIFIERS min{min_games} ===")
        rows = [row for row in report["pooledClassifiers"] if row["minGames"] == min_games]
        rows.sort(key=lambda row: (-(float(row["roiMinus110"]) if row["roiMinus110"] is not None else -999.0), -row["decisions"]))
        for row in rows:
            print(
                f"{row['model']:<24} conf>={row['confidenceThreshold']:.3f} "
                f"bets={row['decisions']:4d} ATS={row['wins']}-{row['losses']}-{row['pushes']} "
                f"({_fmt(row['accuracy'], True)}) ROI={_fmt(row['roiMinus110'], True)}"
            )
        print()

    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"Report: {args.output}")
    print(f"Per-game margin predictions: {args.games_output}")
    print("WARNING: This is a many-model discovery screen. Do not promote the best-looking row without a separately frozen confirmation test.")


if __name__ == "__main__":
    main()
