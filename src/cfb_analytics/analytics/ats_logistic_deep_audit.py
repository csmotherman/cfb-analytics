"""Deep diagnostic audit for the exploratory ATS logistic market-edge signal.

This module does NOT promote a betting strategy.  It reproduces the chronological
outer-season ATS logistic experiment and diagnoses whether the discovery-screen
signal is stable across seasons, sides, spread regimes, weeks, sites, feature
families, and coefficients.

No new confidence threshold is selected here.  The primary diagnostic thresholds
are the already-screened 0.55, 0.575, and 0.60 values.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from cfb_analytics.analytics.market_edge_model_zoo import (
    BREAK_EVEN_MINUS_110,
    MARKET_CONTEXT_FEATURES,
    MODEL_FEATURES,
    _sign,
    attach_market,
    finite,
)
from cfb_analytics.analytics.prediction_v1_integrity_audit import MIN_GAMES_VALUES
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    TEST_SEASONS,
    eligible_site,
    load_data,
)
from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v2_clean_market_benchmark import (
    DEFAULT_LINES,
    clean_market_rows,
)
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

AUDIT_VERSION = "ats-logistic-deep-audit-v1"
DEFAULT_REPORT = Path("data/processed/market_benchmark/ats-logistic-deep-audit.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/ats-logistic-deep-audit-games.json")
PRIMARY_THRESHOLDS = (0.55, 0.575, 0.60)

FEATURE_VARIANTS: dict[str, tuple[str, ...]] = {
    "FULL": tuple(MODEL_FEATURES),
    "FOOTBALL_ONLY": tuple(PREDICTION_V2_FEATURES),
    "MARKET_ONLY": tuple(MARKET_CONTEXT_FEATURES),
}


def _roi_minus_110(wins: int, losses: int) -> float | None:
    decisions = wins + losses
    if not decisions:
        return None
    return (wins * (100.0 / 110.0) - losses) / decisions


def wilson_interval(wins: int, losses: int, z: float = 1.959963984540054) -> tuple[float | None, float | None]:
    n = wins + losses
    if n <= 0:
        return None, None
    p = wins / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n) / denom
    return max(0.0, center - half), min(1.0, center + half)


def binomial_upper_tail(k: int, n: int, p: float) -> float | None:
    """P[X >= k] for X~Binomial(n,p), using log-space probabilities."""
    if n <= 0 or not (0.0 < p < 1.0):
        return None
    terms: list[float] = []
    for x in range(k, n + 1):
        log_prob = (
            math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
            + x * math.log(p) + (n - x) * math.log1p(-p)
        )
        terms.append(log_prob)
    if not terms:
        return 0.0
    m = max(terms)
    return min(1.0, math.exp(m) * sum(math.exp(v - m) for v in terms))


def _matrix(rows: list[dict[str, Any]], features: tuple[str, ...]) -> np.ndarray:
    x = np.asarray([[float(row[name]) for name in features] for row in rows], dtype=float)
    if x.ndim != 2 or not np.isfinite(x).all():
        raise ValueError("Non-finite ATS logistic feature matrix")
    return x


def fit_logistic(rows: list[dict[str, Any]], features: tuple[str, ...]) -> Any:
    no_push = [
        row for row in rows
        if _sign(float(row["target_margin"]) - float(row["marketHomeMargin"])) != 0
    ]
    if not no_push:
        raise ValueError("Cannot fit ATS logistic with zero non-push training rows")
    y = np.asarray([
        1 if float(row["target_margin"]) > float(row["marketHomeMargin"]) else 0
        for row in no_push
    ], dtype=int)
    if len(set(y.tolist())) < 2:
        raise ValueError("ATS logistic training fold has only one cover class")
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.5, max_iter=2000, random_state=42),
    )
    model.fit(_matrix(no_push, features), y)
    return model


def predict_home_cover(model: Any, rows: list[dict[str, Any]], features: tuple[str, ...]) -> np.ndarray:
    probs = np.asarray(model.predict_proba(_matrix(rows, features)), dtype=float)
    classes = list(model.classes_)
    return probs[:, classes.index(1)]


def picked_side_role(side: int, market_margin: float) -> str:
    if abs(market_margin) <= 1e-12:
        return "PICKEM"
    market_favorite_side = 1 if market_margin > 0 else -1
    return "FAVORITE" if side == market_favorite_side else "UNDERDOG"


def spread_bucket(market_margin: float) -> str:
    value = abs(market_margin)
    if value < 3.0:
        return "0-<3"
    if value < 7.0:
        return "3-<7"
    if value < 14.0:
        return "7-<14"
    return "14+"


def week_bucket(week: int) -> str:
    if week <= 4:
        return "1-4"
    if week <= 8:
        return "5-8"
    if week <= 12:
        return "9-12"
    return "13+"


def confidence_bucket(confidence: float) -> str:
    if confidence < 0.525:
        return "0.500-<0.525"
    if confidence < 0.55:
        return "0.525-<0.550"
    if confidence < 0.575:
        return "0.550-<0.575"
    if confidence < 0.60:
        return "0.575-<0.600"
    if confidence < 0.65:
        return "0.600-<0.650"
    return "0.650+"


def probability_bucket(probability: float) -> str:
    if probability < 0.40:
        return "<0.40"
    if probability < 0.45:
        return "0.40-<0.45"
    if probability < 0.50:
        return "0.45-<0.50"
    if probability < 0.55:
        return "0.50-<0.55"
    if probability < 0.60:
        return "0.55-<0.60"
    return "0.60+"


def make_game_record(
    row: dict[str, Any],
    *,
    min_games: int,
    season: int,
    variant: str,
    probability_home_cover: float,
) -> dict[str, Any]:
    p = float(probability_home_cover)
    side = 1 if p >= 0.5 else -1
    market_margin = float(row["marketHomeMargin"])
    cover = _sign(float(row["target_margin"]) - market_margin)
    confidence = max(p, 1.0 - p)
    result = "PUSH" if cover == 0 else ("WIN" if side == cover else "LOSS")
    week = int(row.get("week") or 0)
    return {
        "minGames": int(min_games),
        "season": int(season),
        "seasonType": row.get("seasonType"),
        "week": week,
        "gameId": str(row["gameId"]),
        "homeTeam": row.get("homeTeam"),
        "awayTeam": row.get("awayTeam"),
        "variant": variant,
        "probabilityHomeCover": p,
        "confidence": confidence,
        "pickedSide": "HOME" if side > 0 else "AWAY",
        "pickedSideSign": side,
        "pickedSideRole": picked_side_role(side, market_margin),
        "marketHomeMargin": market_margin,
        "marketAbsSpread": abs(market_margin),
        "spreadBucket": spread_bucket(market_margin),
        "weekBucket": week_bucket(week),
        "siteBucket": "NEUTRAL" if row.get("isNeutralSite") is True else "NON_NEUTRAL",
        "confidenceBucket": confidence_bucket(confidence),
        "probabilityBucket": probability_bucket(p),
        "actualHomeMargin": float(row["target_margin"]),
        "actualCoverSign": cover,
        "result": result,
    }


def summarize_bets(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = list(rows)
    wins = sum(row["result"] == "WIN" for row in materialized)
    losses = sum(row["result"] == "LOSS" for row in materialized)
    pushes = sum(row["result"] == "PUSH" for row in materialized)
    decisions = wins + losses
    low, high = wilson_interval(wins, losses)
    return {
        "bets": len(materialized),
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "decisions": decisions,
        "accuracy": wins / decisions if decisions else None,
        "roiMinus110": _roi_minus_110(wins, losses),
        "wilson95Low": low,
        "wilson95High": high,
        "pValueOneSidedVsBreakEven": binomial_upper_tail(wins, decisions, BREAK_EVEN_MINUS_110) if decisions else None,
    }


def threshold_rows(rows: Iterable[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    return [row for row in rows if float(row["confidence"]) + 1e-12 >= threshold]


def subgroup_summaries(rows: list[dict[str, Any]], threshold: float, field: str) -> list[dict[str, Any]]:
    selected = threshold_rows(rows, threshold)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        groups[str(row.get(field))].append(row)
    return [
        {"group": key, **summarize_bets(group_rows)}
        for key, group_rows in sorted(groups.items())
    ]


def bankroll_path(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    selected = threshold_rows(rows, threshold)
    ordered = sorted(selected, key=lambda r: (int(r["season"]), int(r["week"]), str(r["gameId"])))
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    longest_losing_streak = 0
    current_losing_streak = 0
    for row in ordered:
        if row["result"] == "WIN":
            equity += 100.0 / 110.0
            current_losing_streak = 0
        elif row["result"] == "LOSS":
            equity -= 1.0
            current_losing_streak += 1
            longest_losing_streak = max(longest_losing_streak, current_losing_streak)
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return {
        "ordering": "season-week-gameId deterministic partition order",
        "netUnits": equity,
        "maxDrawdownUnits": max_drawdown,
        "longestLosingStreak": longest_losing_streak,
    }


def calibration_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    non_push = [row for row in rows if int(row["actualCoverSign"]) != 0]
    if not non_push:
        return {"n": 0, "brier": None, "bins": []}
    brier = sum(
        (float(row["probabilityHomeCover"]) - (1.0 if int(row["actualCoverSign"]) > 0 else 0.0)) ** 2
        for row in non_push
    ) / len(non_push)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in non_push:
        groups[str(row["probabilityBucket"])].append(row)
    bins: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        mean_p = sum(float(row["probabilityHomeCover"]) for row in group) / len(group)
        observed = sum(int(row["actualCoverSign"]) > 0 for row in group) / len(group)
        bins.append({
            "probabilityBucket": key,
            "n": len(group),
            "meanPredictedHomeCover": mean_p,
            "observedHomeCover": observed,
            "calibrationError": observed - mean_p,
        })
    return {"n": len(non_push), "brier": brier, "bins": bins}


def coefficient_rows(model: Any, features: tuple[str, ...], min_games: int, season: int, variant: str) -> list[dict[str, Any]]:
    estimator = model.steps[-1][1]
    coefs = np.asarray(estimator.coef_[0], dtype=float)
    return [
        {
            "minGames": int(min_games),
            "season": int(season),
            "variant": variant,
            "feature": feature,
            "standardizedCoefficient": float(value),
        }
        for feature, value in zip(features, coefs)
    ]


def coefficient_stability(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[int, str, str], list[float]] = defaultdict(list)
    for row in rows:
        groups[(int(row["minGames"]), str(row["variant"]), str(row["feature"]))].append(float(row["standardizedCoefficient"]))
    out: list[dict[str, Any]] = []
    for (min_games, variant, feature), values in sorted(groups.items()):
        out.append({
            "minGames": min_games,
            "variant": variant,
            "feature": feature,
            "folds": len(values),
            "mean": sum(values) / len(values),
            "std": float(np.std(np.asarray(values), ddof=0)),
            "min": min(values),
            "max": max(values),
            "positiveFolds": sum(value > 0 for value in values),
            "negativeFolds": sum(value < 0 for value in values),
        })
    return out


def build_audit(lines: Path, raw_root: Path, processed_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    market = clean_market_rows(lines)
    market_by_id = {str(row["gameId"]): row for row in market}
    data = load_data(raw_root, processed_root)

    attached: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        season_rows: list[dict[str, Any]] = []
        for row in data[season]:
            market_row = market_by_id.get(str(row.get("gameId")))
            if market_row is None:
                continue
            merged = attach_market(row, market_row)
            if all(finite(merged.get(name)) for name in MODEL_FEATURES):
                season_rows.append(merged)
        attached[season] = season_rows

    games: list[dict[str, Any]] = []
    coefficients: list[dict[str, Any]] = []

    for min_games in MIN_GAMES_VALUES:
        eligible = {
            season: [row for row in attached[season] if eligible_site(row, min_games)]
            for season in DEFAULT_SEASONS
        }
        for test_season in TEST_SEASONS:
            train = [
                row for season in DEFAULT_SEASONS if season < test_season
                for row in eligible[season]
            ]
            test = eligible[test_season]
            if not train or not test:
                raise ValueError(f"Empty ATS logistic audit fold min{min_games} {test_season}")
            for variant, features in FEATURE_VARIANTS.items():
                fitted = fit_logistic(train, features)
                probabilities = predict_home_cover(fitted, test, features)
                coefficients.extend(coefficient_rows(fitted, features, min_games, test_season, variant))
                for row, probability in zip(test, probabilities):
                    games.append(make_game_record(
                        row,
                        min_games=min_games,
                        season=test_season,
                        variant=variant,
                        probability_home_cover=float(probability),
                    ))

    summaries: list[dict[str, Any]] = []
    season_summaries: list[dict[str, Any]] = []
    subgroups: list[dict[str, Any]] = []
    bankroll: list[dict[str, Any]] = []
    calibration: list[dict[str, Any]] = []
    subgroup_fields = (
        "pickedSide", "pickedSideRole", "spreadBucket", "weekBucket",
        "siteBucket", "confidenceBucket",
    )

    for min_games in MIN_GAMES_VALUES:
        for variant in FEATURE_VARIANTS:
            pool = [row for row in games if row["minGames"] == min_games and row["variant"] == variant]
            calibration.append({
                "minGames": int(min_games),
                "variant": variant,
                **calibration_summary(pool),
            })
            for threshold in PRIMARY_THRESHOLDS:
                selected = threshold_rows(pool, threshold)
                summaries.append({
                    "minGames": int(min_games),
                    "variant": variant,
                    "threshold": threshold,
                    **summarize_bets(selected),
                })
                bankroll.append({
                    "minGames": int(min_games),
                    "variant": variant,
                    "threshold": threshold,
                    **bankroll_path(pool, threshold),
                })
                for season in TEST_SEASONS:
                    season_rows = [row for row in selected if int(row["season"]) == int(season)]
                    season_summaries.append({
                        "minGames": int(min_games),
                        "variant": variant,
                        "threshold": threshold,
                        "season": int(season),
                        **summarize_bets(season_rows),
                    })
                if variant == "FULL":
                    for field in subgroup_fields:
                        for result in subgroup_summaries(pool, threshold, field):
                            subgroups.append({
                                "minGames": int(min_games),
                                "variant": variant,
                                "threshold": threshold,
                                "dimension": field,
                                **result,
                            })

    report = {
        "schemaVersion": 1,
        "auditVersion": AUDIT_VERSION,
        "status": "EXPLORATORY_DIAGNOSTIC_NOT_PROMOTION_EVIDENCE",
        "marketSelection": "first parseable formattedSpread in CFBD provider order",
        "testSeasons": list(TEST_SEASONS),
        "minGamesValues": list(MIN_GAMES_VALUES),
        "primaryThresholds": list(PRIMARY_THRESHOLDS),
        "breakEvenMinus110": BREAK_EVEN_MINUS_110,
        "featureVariants": {name: list(features) for name, features in FEATURE_VARIANTS.items()},
        "pooled": summaries,
        "bySeason": season_summaries,
        "subgroupsFull": subgroups,
        "bankroll": bankroll,
        "calibration": calibration,
        "coefficientsByFold": coefficients,
        "coefficientStability": coefficient_stability(coefficients),
    }
    return report, games


def _write(path: Path, payload: Any, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _pct(value: Any) -> str:
    return "NA" if value is None else f"{float(value):.3%}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep audit of exploratory ATS logistic market-edge signal")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = build_audit(args.lines, args.raw_root, args.processed_root)
    print("ATS LOGISTIC DEEP AUDIT — EXPLORATORY")
    print(f"Version: {AUDIT_VERSION}")
    print(f"-110 break-even: {BREAK_EVEN_MINUS_110:.3%}")
    print("No new confidence threshold is selected in this audit.\n")

    for min_games in MIN_GAMES_VALUES:
        print(f"=== min{min_games} POOLED FEATURE ABLATION ===")
        for threshold in PRIMARY_THRESHOLDS:
            print(f"  confidence >= {threshold:.3f}")
            for variant in FEATURE_VARIANTS:
                row = next(
                    item for item in report["pooled"]
                    if item["minGames"] == min_games and item["variant"] == variant
                    and abs(float(item["threshold"]) - threshold) <= 1e-12
                )
                print(
                    f"    {variant:<13} bets={row['bets']:4d} "
                    f"ATS={row['wins']}-{row['losses']}-{row['pushes']} "
                    f"({_pct(row['accuracy'])}) ROI={_pct(row['roiMinus110'])} "
                    f"CI=[{_pct(row['wilson95Low'])},{_pct(row['wilson95High'])}] "
                    f"p_vs_BE={row['pValueOneSidedVsBreakEven']:.4f}"
                    if row["pValueOneSidedVsBreakEven"] is not None else ""
                )
        print()

    print("=== FULL MODEL SEASON STABILITY ===")
    for min_games in MIN_GAMES_VALUES:
        for threshold in PRIMARY_THRESHOLDS:
            rows = [
                row for row in report["bySeason"]
                if row["minGames"] == min_games and row["variant"] == "FULL"
                and abs(float(row["threshold"]) - threshold) <= 1e-12
            ]
            profitable = sum(
                row["accuracy"] is not None and float(row["accuracy"]) > BREAK_EVEN_MINUS_110
                for row in rows
            )
            print(f"min{min_games} conf>={threshold:.3f}: profitable seasons {profitable}/{len(rows)}")
            for row in rows:
                print(
                    f"  {row['season']}: {row['wins']}-{row['losses']}-{row['pushes']} "
                    f"ATS={_pct(row['accuracy'])} ROI={_pct(row['roiMinus110'])} bets={row['bets']}"
                )
    print()

    for min_games in MIN_GAMES_VALUES:
        print(f"=== min{min_games} FULL MODEL COEFFICIENT STABILITY ===")
        rows = [
            row for row in report["coefficientStability"]
            if row["minGames"] == min_games and row["variant"] == "FULL"
        ]
        rows.sort(key=lambda row: abs(float(row["mean"])), reverse=True)
        for row in rows[:15]:
            print(
                f"  {row['feature']:<34} mean={row['mean']:+.4f} std={row['std']:.4f} "
                f"sign=+{row['positiveFolds']}/-{row['negativeFolds']}"
            )
        print()

    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"Report: {args.output}")
    print(f"Per-game probabilities: {args.games_output}")
    print("WARNING: Deep audit is exploratory diagnosis, not promotion evidence.")


if __name__ == "__main__":
    main()
