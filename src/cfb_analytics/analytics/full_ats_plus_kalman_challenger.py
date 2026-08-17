"""Leakage-safe FULL ATS logistic + Kalman two-feature challenger.

This experiment answers one predeclared question only:

    Do Kalman latent strength and uncertainty add useful ATS information beyond
    the existing FULL Prediction-v2 + market-context logistic model?

The frozen 2026 ATS logistic artifact is NOT modified.  Historical evaluation
uses the same minGames=3 eligibility, StandardScaler + LogisticRegression(C=.5),
and confidence threshold 0.575 as the selected baseline.  Both variants train
and score on the exact same chronological outer-fold rows.

This is exploratory challenger evidence because the 2018-2025 outcomes have
already been observed during model discovery.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from cfb_analytics.analytics.ats_logistic_deep_audit import (
    calibration_summary,
    coefficient_rows,
    coefficient_stability,
    fit_logistic,
    make_game_record,
    predict_home_cover,
    summarize_bets,
    threshold_rows,
)
from cfb_analytics.analytics.dynamic_market_edge_zoo import build_dynamic_signals
from cfb_analytics.analytics.market_edge_model_zoo import MODEL_FEATURES, attach_market, finite
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    TEST_SEASONS,
    eligible_site,
    load_data,
)
from cfb_analytics.analytics.prediction_v2_clean_market_benchmark import DEFAULT_LINES, clean_market_rows
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

VERSION = "full-ats-plus-kalman-challenger-v1"
DEFAULT_REPORT = Path("data/processed/market_benchmark/full-ats-plus-kalman-challenger.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/full-ats-plus-kalman-challenger-games.json")
MIN_GAMES = 3
THRESHOLD = 0.575
BASELINE = "FULL_BASELINE"
CHALLENGER = "FULL_PLUS_KALMAN"
KALMAN_FEATURES = ("KALMAN_strength", "KALMAN_uncertainty")
BASELINE_FEATURES = tuple(MODEL_FEATURES)
CHALLENGER_FEATURES = BASELINE_FEATURES + KALMAN_FEATURES

# Historical discovery result selected before this challenger was built.  The
# comparison is invalid if the supposedly identical baseline no longer
# reproduces this exact record.
EXPECTED_BASELINE = {
    "bets": 495,
    "wins": 265,
    "losses": 220,
    "pushes": 10,
}


def _pct(value: Any) -> str:
    return "NA" if value is None else f"{float(value):.3%}"


def _variant(rows: Iterable[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [row for row in rows if row["variant"] == name]


def _summary_at_threshold(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    return summarize_bets(threshold_rows(list(rows), THRESHOLD))


def _check_baseline(summary: dict[str, Any]) -> None:
    observed = {key: int(summary[key]) for key in EXPECTED_BASELINE}
    if observed != EXPECTED_BASELINE:
        raise ValueError(
            "FULL baseline reproduction failed; refusing challenger comparison. "
            f"expected={EXPECTED_BASELINE} observed={observed}"
        )


def selection_overlap(
    baseline_rows: list[dict[str, Any]],
    challenger_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Describe exactly how the two fixed-threshold betting sets differ."""
    bmap = {(int(row["season"]), str(row["gameId"])): row for row in baseline_rows}
    cmap = {(int(row["season"]), str(row["gameId"])): row for row in challenger_rows}
    if set(bmap) != set(cmap):
        raise ValueError("Baseline/challenger per-game key mismatch")

    baseline_only: list[dict[str, Any]] = []
    challenger_only: list[dict[str, Any]] = []
    both_baseline: list[dict[str, Any]] = []
    both_challenger: list[dict[str, Any]] = []
    same_side_baseline: list[dict[str, Any]] = []
    same_side_challenger: list[dict[str, Any]] = []
    opposite_baseline: list[dict[str, Any]] = []
    opposite_challenger: list[dict[str, Any]] = []

    for key in sorted(bmap):
        b = bmap[key]
        c = cmap[key]
        bs = float(b["confidence"]) + 1e-12 >= THRESHOLD
        cs = float(c["confidence"]) + 1e-12 >= THRESHOLD
        if bs and cs:
            both_baseline.append(b)
            both_challenger.append(c)
            if int(b["pickedSideSign"]) == int(c["pickedSideSign"]):
                same_side_baseline.append(b)
                same_side_challenger.append(c)
            else:
                opposite_baseline.append(b)
                opposite_challenger.append(c)
        elif bs:
            baseline_only.append(b)
        elif cs:
            challenger_only.append(c)

    return {
        "allGames": len(bmap),
        "baselineBets": len(baseline_only) + len(both_baseline),
        "challengerBets": len(challenger_only) + len(both_challenger),
        "bothBet": len(both_baseline),
        "bothSameSide": len(same_side_baseline),
        "bothOppositeSide": len(opposite_baseline),
        "baselineOnly": len(baseline_only),
        "challengerOnly": len(challenger_only),
        "baselineOnlyPerformance": summarize_bets(baseline_only),
        "challengerOnlyPerformance": summarize_bets(challenger_only),
        "bothBaselinePerformance": summarize_bets(both_baseline),
        "bothChallengerPerformance": summarize_bets(both_challenger),
        "sameSideBaselinePerformance": summarize_bets(same_side_baseline),
        "sameSideChallengerPerformance": summarize_bets(same_side_challenger),
        "oppositeSideBaselinePerformance": summarize_bets(opposite_baseline),
        "oppositeSideChallengerPerformance": summarize_bets(opposite_challenger),
    }


def _season_summary(rows: list[dict[str, Any]], season: int, variant: str) -> dict[str, Any]:
    selected = [
        row for row in rows
        if int(row["season"]) == season and row["variant"] == variant
    ]
    return {
        "season": season,
        "variant": variant,
        **_summary_at_threshold(selected),
        "calibration": calibration_summary(selected),
    }


def _pooled_summary(rows: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    pool = _variant(rows, variant)
    bets = _summary_at_threshold(pool)
    calibration = calibration_summary(pool)
    return {"variant": variant, **bets, "brier": calibration["brier"], "calibration": calibration}


def _recent_summary(rows: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    recent = [row for row in rows if row["variant"] == variant and int(row["season"]) >= 2023]
    calibration = calibration_summary(recent)
    return {"variant": variant, **_summary_at_threshold(recent), "brier": calibration["brier"]}


def run(
    lines: Path,
    raw_root: Path,
    processed_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = load_data(raw_root, processed_root)
    signals = build_dynamic_signals(data)
    kalman = signals["KALMAN"]
    market = clean_market_rows(lines)
    market_by_id = {str(row["gameId"]): row for row in market}

    attached: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        rows: list[dict[str, Any]] = []
        for base in data[season]:
            gid = str(base.get("gameId"))
            market_row = market_by_id.get(gid)
            pair = kalman.get(gid)
            if market_row is None or pair is None:
                continue
            row = attach_market(base, market_row)
            row["KALMAN_strength"] = float(pair[0])
            row["KALMAN_uncertainty"] = float(pair[1])
            if all(finite(row.get(name)) for name in CHALLENGER_FEATURES):
                rows.append(row)
        attached[season] = rows

    eligible = {
        season: [row for row in attached[season] if eligible_site(row, MIN_GAMES)]
        for season in DEFAULT_SEASONS
    }

    games: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []
    coefficients: list[dict[str, Any]] = []

    for test_season in TEST_SEASONS:
        train = [
            row
            for season in DEFAULT_SEASONS
            if season < test_season
            for row in eligible[season]
        ]
        test = eligible[test_season]
        if not train or not test:
            raise ValueError(f"Empty FULL+Kalman fold for {test_season}")

        baseline_model = fit_logistic(train, BASELINE_FEATURES)
        challenger_model = fit_logistic(train, CHALLENGER_FEATURES)
        baseline_prob = predict_home_cover(baseline_model, test, BASELINE_FEATURES)
        challenger_prob = predict_home_cover(challenger_model, test, CHALLENGER_FEATURES)

        coefficients.extend(
            row for row in coefficient_rows(
                challenger_model,
                CHALLENGER_FEATURES,
                MIN_GAMES,
                test_season,
                CHALLENGER,
            )
            if row["feature"] in KALMAN_FEATURES
        )

        season_records: dict[str, list[dict[str, Any]]] = {BASELINE: [], CHALLENGER: []}
        for row, bp, cp in zip(test, baseline_prob, challenger_prob):
            b = make_game_record(
                row,
                min_games=MIN_GAMES,
                season=test_season,
                variant=BASELINE,
                probability_home_cover=float(bp),
            )
            c = make_game_record(
                row,
                min_games=MIN_GAMES,
                season=test_season,
                variant=CHALLENGER,
                probability_home_cover=float(cp),
            )
            b["KALMAN_strength"] = float(row["KALMAN_strength"])
            b["KALMAN_uncertainty"] = float(row["KALMAN_uncertainty"])
            c["KALMAN_strength"] = float(row["KALMAN_strength"])
            c["KALMAN_uncertainty"] = float(row["KALMAN_uncertainty"])
            season_records[BASELINE].append(b)
            season_records[CHALLENGER].append(c)
            games.extend((b, c))

        bsum = _summary_at_threshold(season_records[BASELINE])
        csum = _summary_at_threshold(season_records[CHALLENGER])
        bcal = calibration_summary(season_records[BASELINE])
        ccal = calibration_summary(season_records[CHALLENGER])
        folds.append({
            "season": int(test_season),
            "trainN": len(train),
            "testN": len(test),
            "baseline": {**bsum, "brier": bcal["brier"]},
            "challenger": {**csum, "brier": ccal["brier"]},
            "deltaAccuracyPP": (
                (float(csum["accuracy"]) - float(bsum["accuracy"])) * 100.0
                if csum["accuracy"] is not None and bsum["accuracy"] is not None else None
            ),
            "deltaRoiPP": (
                (float(csum["roiMinus110"]) - float(bsum["roiMinus110"])) * 100.0
                if csum["roiMinus110"] is not None and bsum["roiMinus110"] is not None else None
            ),
            "deltaBrier": (
                float(ccal["brier"]) - float(bcal["brier"])
                if ccal["brier"] is not None and bcal["brier"] is not None else None
            ),
        })

    baseline = _pooled_summary(games, BASELINE)
    challenger = _pooled_summary(games, CHALLENGER)
    _check_baseline(baseline)

    baseline_rows = _variant(games, BASELINE)
    challenger_rows = _variant(games, CHALLENGER)
    overlap = selection_overlap(baseline_rows, challenger_rows)
    recent_baseline = _recent_summary(games, BASELINE)
    recent_challenger = _recent_summary(games, CHALLENGER)
    stability = coefficient_stability(coefficients)

    report = {
        "schemaVersion": 1,
        "version": VERSION,
        "status": "EXPLORATORY_POST_DISCOVERY_CHALLENGER",
        "researchQuestion": "Do fixed Kalman strength and uncertainty features improve the existing FULL ATS logistic model?",
        "minGames": MIN_GAMES,
        "confidenceThreshold": THRESHOLD,
        "testSeasons": list(TEST_SEASONS),
        "baselineFeatures": list(BASELINE_FEATURES),
        "challengerFeatures": list(CHALLENGER_FEATURES),
        "kalmanFeaturesAdded": list(KALMAN_FEATURES),
        "baselineExpectedDiscoveryRecord": EXPECTED_BASELINE,
        "baselineReproduction": "PASS",
        "pooled": {
            "baseline": baseline,
            "challenger": challenger,
            "deltaAccuracyPP": (float(challenger["accuracy"]) - float(baseline["accuracy"])) * 100.0,
            "deltaRoiPP": (float(challenger["roiMinus110"]) - float(baseline["roiMinus110"])) * 100.0,
            "deltaBrier": float(challenger["brier"]) - float(baseline["brier"]),
        },
        "recent2023To2025": {
            "baseline": recent_baseline,
            "challenger": recent_challenger,
            "deltaAccuracyPP": (
                (float(recent_challenger["accuracy"]) - float(recent_baseline["accuracy"])) * 100.0
                if recent_challenger["accuracy"] is not None and recent_baseline["accuracy"] is not None else None
            ),
            "deltaRoiPP": (
                (float(recent_challenger["roiMinus110"]) - float(recent_baseline["roiMinus110"])) * 100.0
                if recent_challenger["roiMinus110"] is not None and recent_baseline["roiMinus110"] is not None else None
            ),
            "deltaBrier": float(recent_challenger["brier"]) - float(recent_baseline["brier"]),
        },
        "folds": folds,
        "selectionOverlap": overlap,
        "kalmanCoefficientRows": coefficients,
        "kalmanCoefficientStability": stability,
    }
    return report, games


def _write(path: Path, payload: Any, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _print_perf(label: str, row: dict[str, Any]) -> None:
    print(
        f"{label:<16} bets={row['bets']:3d} ATS={row['wins']}-{row['losses']}-{row['pushes']} "
        f"({_pct(row['accuracy'])}) ROI={_pct(row['roiMinus110'])} Brier={row.get('brier', float('nan')):.6f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="FULL ATS logistic plus Kalman challenger")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = run(args.lines, args.raw_root, args.processed_root)
    pooled = report["pooled"]
    recent = report["recent2023To2025"]

    print("FULL ATS LOGISTIC + KALMAN CHALLENGER — EXPLORATORY")
    print(f"Version: {VERSION}")
    print(f"minGames={MIN_GAMES} threshold={THRESHOLD:.3f} C=0.5")
    print("Only added features: KALMAN_strength, KALMAN_uncertainty")
    print("BASELINE REPRODUCTION: PASS (265-220-10, 495 bets)\n")

    print("=== POOLED 2018-2025 OFFICIAL OOS ===")
    _print_perf("BASELINE", pooled["baseline"])
    _print_perf("PLUS_KALMAN", pooled["challenger"])
    print(
        f"delta ATS={pooled['deltaAccuracyPP']:+.3f}pp "
        f"delta ROI={pooled['deltaRoiPP']:+.3f}pp "
        f"delta Brier={pooled['deltaBrier']:+.6f} (negative Brier is better)\n"
    )

    print("=== SEASON STABILITY ===")
    for fold in report["folds"]:
        b, c = fold["baseline"], fold["challenger"]
        print(
            f"{fold['season']}: BASE {b['wins']}-{b['losses']}-{b['pushes']} "
            f"ATS={_pct(b['accuracy'])} ROI={_pct(b['roiMinus110'])} | "
            f"KAL {c['wins']}-{c['losses']}-{c['pushes']} "
            f"ATS={_pct(c['accuracy'])} ROI={_pct(c['roiMinus110'])} | "
            f"dATS={fold['deltaAccuracyPP']:+.3f}pp dBrier={fold['deltaBrier']:+.6f}"
        )

    print("\n=== RECENT 2023-2025 ===")
    _print_perf("BASELINE", recent["baseline"])
    _print_perf("PLUS_KALMAN", recent["challenger"])
    print(
        f"delta ATS={recent['deltaAccuracyPP']:+.3f}pp "
        f"delta ROI={recent['deltaRoiPP']:+.3f}pp "
        f"delta Brier={recent['deltaBrier']:+.6f}\n"
    )

    o = report["selectionOverlap"]
    print("=== BET SELECTION OVERLAP ===")
    print(
        f"baseline={o['baselineBets']} challenger={o['challengerBets']} both={o['bothBet']} "
        f"same_side={o['bothSameSide']} opposite_side={o['bothOppositeSide']} "
        f"baseline_only={o['baselineOnly']} challenger_only={o['challengerOnly']}"
    )
    bo = o["baselineOnlyPerformance"]
    co = o["challengerOnlyPerformance"]
    print(f"baseline-only:   {bo['wins']}-{bo['losses']}-{bo['pushes']} ATS={_pct(bo['accuracy'])} ROI={_pct(bo['roiMinus110'])}")
    print(f"challenger-only: {co['wins']}-{co['losses']}-{co['pushes']} ATS={_pct(co['accuracy'])} ROI={_pct(co['roiMinus110'])}\n")

    print("=== ADDED KALMAN COEFFICIENT STABILITY ===")
    for row in report["kalmanCoefficientStability"]:
        print(
            f"{row['feature']:<20} mean={row['mean']:+.4f} std={row['std']:.4f} "
            f"sign=+{row['positiveFolds']}/-{row['negativeFolds']}"
        )

    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"\nReport: {args.output}")
    print(f"Per-game predictions: {args.games_output}")
    print("WARNING: This is post-discovery historical challenger evidence, not untouched confirmation evidence.")


if __name__ == "__main__":
    main()
