"""Deep audit of the exploratory Kalman ATS signal.

This audit does not tune Kalman parameters or select a new threshold. It focuses
on the already-screened Kalman ATS candidate at minGames=4 and confidence 0.55,
while retaining minGames=3 as a robustness comparator.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from cfb_analytics.analytics.ats_logistic_deep_audit import (
    bankroll_path,
    binomial_upper_tail,
    calibration_summary,
    coefficient_stability,
    confidence_bucket,
    picked_side_role,
    probability_bucket,
    spread_bucket,
    summarize_bets,
    threshold_rows,
    week_bucket,
    wilson_interval,
)
from cfb_analytics.analytics.dynamic_market_edge_zoo import (
    KALMAN_HFA,
    KALMAN_INITIAL_VARIANCE,
    KALMAN_OBSERVATION_VARIANCE,
    KALMAN_PROCESS_VARIANCE,
    OFFSEASON_CARRY,
    _ats_probability,
    _fit_ats,
    build_dynamic_signals,
)
from cfb_analytics.analytics.market_edge_model_zoo import (
    BREAK_EVEN_MINUS_110,
    _sign,
    attach_market,
)
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    TEST_SEASONS,
    eligible_site,
    load_data,
)
from cfb_analytics.analytics.prediction_v2_clean_market_benchmark import (
    DEFAULT_LINES,
    clean_market_rows,
)
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

VERSION = "kalman-ats-deep-audit-v1"
PRIMARY_MIN_GAMES = 4
PRIMARY_THRESHOLD = 0.55
COMPARATOR_MIN_GAMES = 3
DEFAULT_REPORT = Path("data/processed/market_benchmark/kalman-ats-deep-audit.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/kalman-ats-deep-audit-games.json")

KALMAN_ATS_FEATURES = (
    "dynamicStrength",
    "dynamicUncertainty",
    "marketHomeMargin",
    "marketAbsSpread",
    "marketHomeFavorite",
    "weekNumber",
    "neutralSite",
)


def _game_record(row: dict[str, Any], probability: float, min_games: int, season: int) -> dict[str, Any]:
    p = float(probability)
    confidence = max(p, 1.0 - p)
    picked_sign = 1 if p >= 0.5 else -1
    market_margin = float(row["marketHomeMargin"])
    cover_sign = _sign(float(row["target_margin"]) - market_margin)
    result = "PUSH" if cover_sign == 0 else ("WIN" if picked_sign == cover_sign else "LOSS")
    week = int(row.get("week") or 0)
    home_games = int(row.get("homeIterativeGamesPlayedBefore", 0))
    away_games = int(row.get("awayIterativeGamesPlayedBefore", 0))
    depth = min(home_games, away_games)
    if depth == 3:
        depth_bucket = "EXACTLY_3"
    elif depth == 4:
        depth_bucket = "EXACTLY_4"
    elif depth == 5:
        depth_bucket = "EXACTLY_5"
    else:
        depth_bucket = "6+"
    return {
        "minGames": int(min_games),
        "season": int(season),
        "seasonType": row.get("seasonType"),
        "week": week,
        "gameId": str(row["gameId"]),
        "homeTeam": row.get("homeTeam"),
        "awayTeam": row.get("awayTeam"),
        "homeGamesBefore": home_games,
        "awayGamesBefore": away_games,
        "eligibilityDepth": depth,
        "eligibilityDepthBucket": depth_bucket,
        "dynamicStrength": float(row["KALMAN_strength"]),
        "dynamicUncertainty": float(row["KALMAN_uncertainty"]),
        "marketHomeMargin": market_margin,
        "marketAbsSpread": abs(market_margin),
        "marketHomeFavorite": float(row["marketHomeFavorite"]),
        "weekNumber": float(row["weekNumber"]),
        "neutralSite": float(row["neutralSite"]),
        "probabilityHomeCover": p,
        "probabilityBucket": probability_bucket(p),
        "confidence": confidence,
        "confidenceBucket": confidence_bucket(confidence),
        "pickedSide": "HOME" if picked_sign > 0 else "AWAY",
        "pickedSideSign": picked_sign,
        "pickedSideRole": picked_side_role(picked_sign, market_margin),
        "spreadBucket": spread_bucket(market_margin),
        "weekBucket": week_bucket(week),
        "siteBucket": "NEUTRAL" if row.get("isNeutralSite") is True else "NON_NEUTRAL",
        "actualHomeMargin": float(row["target_margin"]),
        "actualCoverSign": cover_sign,
        "result": result,
    }


def _coefficient_rows(model: Any, min_games: int, season: int) -> list[dict[str, Any]]:
    estimator = model.steps[-1][1]
    coefs = np.asarray(estimator.coef_[0], dtype=float)
    return [
        {
            "minGames": int(min_games),
            "season": int(season),
            "variant": "KALMAN_ATS",
            "feature": feature,
            "standardizedCoefficient": float(value),
        }
        for feature, value in zip(KALMAN_ATS_FEATURES, coefs)
    ]


def _group(rows: list[dict[str, Any]], threshold: float, field: str) -> list[dict[str, Any]]:
    selected = threshold_rows(rows, threshold)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        groups[str(row.get(field))].append(row)
    return [{"group": key, **summarize_bets(value)} for key, value in sorted(groups.items())]


def build_audit(lines: Path, raw_root: Path, processed_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = load_data(raw_root, processed_root)
    signals = build_dynamic_signals(data)["KALMAN"]
    market_by_id = {str(row["gameId"]): row for row in clean_market_rows(lines)}

    attached: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        rows: list[dict[str, Any]] = []
        for base in data[season]:
            gid = str(base.get("gameId"))
            market = market_by_id.get(gid)
            signal = signals.get(gid)
            if market is None or signal is None:
                continue
            row = attach_market(base, market)
            row["KALMAN_strength"] = float(signal[0])
            row["KALMAN_uncertainty"] = float(signal[1])
            rows.append(row)
        attached[season] = rows

    games: list[dict[str, Any]] = []
    coefficients: list[dict[str, Any]] = []
    for min_games in (COMPARATOR_MIN_GAMES, PRIMARY_MIN_GAMES):
        eligible = {
            season: [row for row in attached[season] if eligible_site(row, min_games)]
            for season in DEFAULT_SEASONS
        }
        for test_season in TEST_SEASONS:
            train = [row for season in DEFAULT_SEASONS if season < test_season for row in eligible[season]]
            test = eligible[test_season]
            if not train or not test:
                raise ValueError(f"Empty Kalman audit fold min{min_games} {test_season}")
            fitted = _fit_ats(train, "KALMAN")
            coefficients.extend(_coefficient_rows(fitted, min_games, test_season))
            probs = _ats_probability(fitted, test, "KALMAN")
            for row, probability in zip(test, probs):
                games.append(_game_record(row, float(probability), min_games, test_season))

    pooled: list[dict[str, Any]] = []
    season_rows: list[dict[str, Any]] = []
    subgroup_rows: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    bankroll_rows: list[dict[str, Any]] = []
    subgroup_fields = (
        "pickedSide",
        "pickedSideRole",
        "spreadBucket",
        "weekBucket",
        "siteBucket",
        "confidenceBucket",
        "eligibilityDepthBucket",
    )

    for min_games in (COMPARATOR_MIN_GAMES, PRIMARY_MIN_GAMES):
        pool = [row for row in games if row["minGames"] == min_games]
        selected = threshold_rows(pool, PRIMARY_THRESHOLD)
        pooled.append({"minGames": min_games, "threshold": PRIMARY_THRESHOLD, **summarize_bets(selected)})
        bankroll_rows.append({"minGames": min_games, "threshold": PRIMARY_THRESHOLD, **bankroll_path(pool, PRIMARY_THRESHOLD)})
        calibration_rows.append({"minGames": min_games, **calibration_summary(pool)})
        for season in TEST_SEASONS:
            season_pool = [row for row in pool if row["season"] == season]
            season_rows.append({
                "minGames": min_games,
                "season": season,
                "threshold": PRIMARY_THRESHOLD,
                **summarize_bets(threshold_rows(season_pool, PRIMARY_THRESHOLD)),
            })
        for field in subgroup_fields:
            for summary in _group(pool, PRIMARY_THRESHOLD, field):
                subgroup_rows.append({"minGames": min_games, "field": field, **summary})

    # Critical same-model decomposition: use min3 probabilities, then partition
    # their decisions by whether the matchup would also satisfy min4.
    min3_pool = [row for row in games if row["minGames"] == COMPARATOR_MIN_GAMES]
    min3_selected = threshold_rows(min3_pool, PRIMARY_THRESHOLD)
    min3_only = [row for row in min3_selected if int(row["eligibilityDepth"]) == 3]
    min3_also_min4 = [row for row in min3_selected if int(row["eligibilityDepth"]) >= 4]
    depth_comparison = [
        {"group": "MIN3_ONLY_EXACTLY_3", **summarize_bets(min3_only)},
        {"group": "MIN3_MODEL_ON_4PLUS", **summarize_bets(min3_also_min4)},
    ]

    report = {
        "schemaVersion": 1,
        "version": VERSION,
        "status": "EXPLORATORY_DEEP_AUDIT_NOT_PROMOTION_EVIDENCE",
        "primaryCandidate": {"model": "KALMAN", "minGames": PRIMARY_MIN_GAMES, "confidenceThreshold": PRIMARY_THRESHOLD},
        "comparator": {"minGames": COMPARATOR_MIN_GAMES, "confidenceThreshold": PRIMARY_THRESHOLD},
        "breakEvenMinus110": BREAK_EVEN_MINUS_110,
        "parametersFrozenForAudit": {
            "offseasonCarry": OFFSEASON_CARRY,
            "kalmanInitialVariance": KALMAN_INITIAL_VARIANCE,
            "kalmanProcessVariance": KALMAN_PROCESS_VARIANCE,
            "kalmanObservationVariance": KALMAN_OBSERVATION_VARIANCE,
            "kalmanHfa": KALMAN_HFA,
            "atsLogisticC": 0.5,
        },
        "pooled": pooled,
        "seasonStability": season_rows,
        "subgroups": subgroup_rows,
        "calibration": calibration_rows,
        "bankroll": bankroll_rows,
        "min3DepthComparison": depth_comparison,
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
    parser = argparse.ArgumentParser(description="Deep audit the exploratory Kalman ATS signal")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = build_audit(args.lines, args.raw_root, args.processed_root)
    print("KALMAN ATS DEEP AUDIT — EXPLORATORY")
    print(f"Version: {VERSION}")
    print("No Kalman parameter or confidence threshold is tuned in this audit.")
    print(f"Primary candidate: min{PRIMARY_MIN_GAMES}, confidence>={PRIMARY_THRESHOLD:.3f}\n")

    print("=== POOLED ===")
    for row in report["pooled"]:
        print(
            f"min{row['minGames']}: bets={row['bets']} ATS={row['wins']}-{row['losses']}-{row['pushes']} "
            f"({_pct(row['accuracy'])}) ROI={_pct(row['roiMinus110'])} "
            f"CI=[{_pct(row['wilson95Low'])},{_pct(row['wilson95High'])}] "
            f"p_vs_BE={row['pValueOneSidedVsBreakEven']:.4f}" if row['pValueOneSidedVsBreakEven'] is not None else ""
        )

    print("\n=== PRIMARY min4 SEASON STABILITY ===")
    for row in report["seasonStability"]:
        if row["minGames"] != PRIMARY_MIN_GAMES:
            continue
        print(f"{row['season']}: {row['wins']}-{row['losses']}-{row['pushes']} ATS={_pct(row['accuracy'])} ROI={_pct(row['roiMinus110'])} bets={row['bets']}")

    print("\n=== WHY min3 FAILS? SAME min3 MODEL SPLIT BY ELIGIBILITY DEPTH ===")
    for row in report["min3DepthComparison"]:
        print(f"{row['group']:<24} {row['wins']}-{row['losses']}-{row['pushes']} ATS={_pct(row['accuracy'])} ROI={_pct(row['roiMinus110'])} bets={row['bets']}")

    print("\n=== PRIMARY min4 SUBGROUPS ===")
    for field in ("pickedSide", "pickedSideRole", "spreadBucket", "weekBucket", "eligibilityDepthBucket"):
        print(f"  {field}")
        for row in report["subgroups"]:
            if row["minGames"] == PRIMARY_MIN_GAMES and row["field"] == field:
                print(f"    {row['group']:<18} {row['wins']}-{row['losses']}-{row['pushes']} ATS={_pct(row['accuracy'])} ROI={_pct(row['roiMinus110'])} bets={row['bets']}")

    print("\n=== PRIMARY min4 BANKROLL ===")
    for row in report["bankroll"]:
        if row["minGames"] == PRIMARY_MIN_GAMES:
            print(f"netUnits={row['netUnits']:+.3f} maxDrawdown={row['maxDrawdownUnits']:.3f} longestLosingStreak={row['longestLosingStreak']}")

    print("\n=== KALMAN ATS COEFFICIENT STABILITY min4 ===")
    rows = [r for r in report["coefficientStability"] if r["minGames"] == PRIMARY_MIN_GAMES]
    rows.sort(key=lambda r: -abs(float(r["mean"])))
    for row in rows:
        print(f"{row['feature']:<24} mean={row['mean']:+.4f} std={row['std']:.4f} sign=+{row['positiveFolds']}/-{row['negativeFolds']}")

    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"\nReport: {args.output}")
    print(f"Per-game probabilities: {args.games_output}")
    print("WARNING: This audit diagnoses an already-discovered row; it is not independent confirmation evidence.")


if __name__ == "__main__":
    main()
