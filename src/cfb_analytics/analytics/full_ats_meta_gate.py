"""Cross-fitted bet-quality gate for the existing FULL ATS logistic signal.

The first-stage FULL ATS logistic model chooses the side.  This module trains a
second-stage classifier whose only action is BET or PASS for an already-selected
FULL candidate.  The gate is never allowed to reverse the side.

This is exploratory/post-discovery work.  It does not modify the frozen 2026 ATS
artifact.  Every gate-training example uses a first-stage FULL probability from
a season that was itself predicted out-of-sample from strictly earlier seasons.
The gate is then evaluated chronologically on the official 2018-2025 OOS seasons.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from cfb_analytics.analytics.ats_logistic_deep_audit import (
    bankroll_path,
    fit_logistic,
    make_game_record,
    predict_home_cover,
    summarize_bets,
)
from cfb_analytics.analytics.dynamic_bayesian_offense_defense import (
    FAMILY_FEATURES,
    STATE_SPECS,
    _attach_state_features,
    build_od_signals,
)
from cfb_analytics.analytics.dynamic_market_edge_zoo import build_dynamic_signals
from cfb_analytics.analytics.market_edge_model_zoo import (
    BREAK_EVEN_MINUS_110,
    MODEL_FEATURES,
    _sign,
    attach_market,
    finite,
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

VERSION = "full-ats-meta-gate-v1"
DEFAULT_REPORT = Path("data/processed/market_benchmark/full-ats-meta-gate.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/full-ats-meta-gate-games.json")

MIN_GAMES = 3
BASELINE_THRESHOLD = 0.575
GATE_THRESHOLD = BREAK_EVEN_MINUS_110
BASELINE_FEATURES = tuple(MODEL_FEATURES)

OD_FEATURES = tuple(
    feature
    for family in ("POINTS_OD", "YPP_OD", "SUCCESS_OD")
    for feature in FAMILY_FEATURES[family]
)
KALMAN_FEATURES = ("KALMAN_strength", "KALMAN_uncertainty")
META_OUTPUT_FEATURES = (
    "baselineProbabilityHomeCover",
    "baselineConfidence",
    "baselinePickedSideSign",
    "homeGamesPlayedBefore",
    "awayGamesPlayedBefore",
)
GATE_FEATURES = BASELINE_FEATURES + OD_FEATURES + KALMAN_FEATURES + META_OUTPUT_FEATURES

GATE_VARIANTS = ("META_LOGISTIC", "META_HIST_GB")
EXPECTED_BASELINE = {"bets": 495, "wins": 265, "losses": 220, "pushes": 10}

# First-stage OOS predictions from 2015-2017 are used only as gate-training
# examples.  Official gate evaluation remains the frozen 2018-2025 OOS contract.
OOF_SOURCE_SEASONS = tuple(season for season in DEFAULT_SEASONS if season > min(DEFAULT_SEASONS))


def _matrix(rows: list[dict[str, Any]], features: tuple[str, ...]) -> np.ndarray:
    x = np.asarray([[float(row[name]) for name in features] for row in rows], dtype=float)
    if x.ndim != 2 or not np.isfinite(x).all():
        raise ValueError("Non-finite meta-gate feature matrix")
    return x


def _candidate(row: dict[str, Any]) -> bool:
    return float(row["baselineConfidence"]) + 1e-12 >= BASELINE_THRESHOLD


def _gate_target(row: dict[str, Any]) -> int | None:
    cover = int(row["actualCoverSign"])
    if cover == 0:
        return None
    return 1 if int(row["baselinePickedSideSign"]) == cover else 0


def _fit_gate(rows: list[dict[str, Any]], variant: str) -> Any:
    train = [row for row in rows if row.get("gateTarget") in (0, 1)]
    if not train:
        raise ValueError("Cannot fit meta gate with zero non-push rows")
    y = np.asarray([int(row["gateTarget"]) for row in train], dtype=int)
    if len(set(y.tolist())) < 2:
        raise ValueError("Meta-gate training fold has only one class")
    x = _matrix(train, GATE_FEATURES)
    if variant == "META_LOGISTIC":
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=0.5, max_iter=2000, random_state=42),
        )
    elif variant == "META_HIST_GB":
        model = HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=150,
            max_leaf_nodes=15,
            min_samples_leaf=30,
            l2_regularization=1.0,
            random_state=42,
        )
    else:
        raise ValueError(f"Unknown gate variant: {variant}")
    model.fit(x, y)
    return model


def _predict_gate(model: Any, rows: list[dict[str, Any]]) -> np.ndarray:
    probs = np.asarray(model.predict_proba(_matrix(rows, GATE_FEATURES)), dtype=float)
    classes = list(model.classes_)
    return probs[:, classes.index(1)]


def _gate_brier(rows: Iterable[dict[str, Any]]) -> float | None:
    usable = [row for row in rows if row.get("gateTarget") in (0, 1)]
    if not usable:
        return None
    return sum(
        (float(row["gateProbabilityCorrect"]) - float(row["gateTarget"])) ** 2
        for row in usable
    ) / len(usable)


def _baseline_record_from_meta(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "minGames": MIN_GAMES,
        "season": int(row["season"]),
        "seasonType": row.get("seasonType"),
        "week": int(row.get("week") or 0),
        "gameId": str(row["gameId"]),
        "homeTeam": row.get("homeTeam"),
        "awayTeam": row.get("awayTeam"),
        "variant": "FULL_BASELINE",
        "probabilityHomeCover": float(row["baselineProbabilityHomeCover"]),
        "confidence": float(row["baselineConfidence"]),
        "pickedSide": "HOME" if int(row["baselinePickedSideSign"]) > 0 else "AWAY",
        "pickedSideSign": int(row["baselinePickedSideSign"]),
        "marketHomeMargin": float(row["marketHomeMargin"]),
        "actualHomeMargin": float(row["target_margin"]),
        "actualCoverSign": int(row["actualCoverSign"]),
        "result": str(row["baselineResult"]),
    }


def _gate_bet_record(row: dict[str, Any], variant: str, probability: float) -> dict[str, Any]:
    # Intentionally inherit the first-stage side/result.  The gate cannot reverse it.
    record = _baseline_record_from_meta(row)
    record["variant"] = variant
    record["gateProbabilityCorrect"] = float(probability)
    record["gateAccepted"] = float(probability) + 1e-12 >= GATE_THRESHOLD
    record["gateTarget"] = row.get("gateTarget")
    return record


def _check_baseline(rows: list[dict[str, Any]]) -> None:
    summary = summarize_bets(rows)
    observed = {key: int(summary[key]) for key in EXPECTED_BASELINE}
    if observed != EXPECTED_BASELINE:
        raise ValueError(
            "FULL baseline reproduction failed; refusing meta-gate evaluation. "
            f"expected={EXPECTED_BASELINE} observed={observed}"
        )


def _selected(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("gateAccepted") is True]


def _passed(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("gateAccepted") is False]


def _perf(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_bets(rows)
    return {**summary, "bankroll": bankroll_path(rows, 0.0) if rows else None}


def _quality_bucket(prob: float) -> str:
    if prob < 0.45:
        return "<0.450"
    if prob < 0.50:
        return "0.450-<0.500"
    if prob < GATE_THRESHOLD:
        return "0.500-<0.52381"
    if prob < 0.55:
        return "0.52381-<0.550"
    if prob < 0.575:
        return "0.550-<0.575"
    if prob < 0.60:
        return "0.575-<0.600"
    return "0.600+"


def quality_curve(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[_quality_bucket(float(row["gateProbabilityCorrect"]))].append(row)
    order = (
        "<0.450",
        "0.450-<0.500",
        "0.500-<0.52381",
        "0.52381-<0.550",
        "0.550-<0.575",
        "0.575-<0.600",
        "0.600+",
    )
    return [{"bucket": key, **summarize_bets(groups[key])} for key in order if key in groups]


def cumulative_rank_curve(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda r: float(r["gateProbabilityCorrect"]), reverse=True)
    out: list[dict[str, Any]] = []
    for fraction in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.75, 1.00):
        n = max(1, int(math.ceil(len(ordered) * fraction))) if ordered else 0
        chosen = ordered[:n]
        out.append({"topFraction": fraction, "n": n, **summarize_bets(chosen)})
    return out


def logistic_coefficient_rows(model: Any, season: int) -> list[dict[str, Any]]:
    if not hasattr(model, "steps"):
        return []
    estimator = model.steps[-1][1]
    coef = np.asarray(estimator.coef_[0], dtype=float)
    return [
        {"season": int(season), "feature": feature, "coefficient": float(value)}
        for feature, value in zip(GATE_FEATURES, coef)
    ]


def coefficient_stability(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: defaultdict[str, list[float]] = defaultdict(list)
    for row in rows:
        groups[str(row["feature"])].append(float(row["coefficient"]))
    out = []
    for feature, values in groups.items():
        arr = np.asarray(values, dtype=float)
        out.append({
            "feature": feature,
            "folds": len(values),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "positive": int(np.sum(arr > 0.0)),
            "negative": int(np.sum(arr < 0.0)),
        })
    return out


def _prepare_rows(
    lines: Path,
    raw_root: Path,
    processed_root: Path,
) -> tuple[dict[int, list[dict[str, Any]]], dict[str, int]]:
    data = load_data(raw_root, processed_root)
    market = clean_market_rows(lines)
    market_by_id = {str(row["gameId"]): row for row in market}
    od_signals, missing_observations = build_od_signals(data, raw_root, processed_root)
    kalman = build_dynamic_signals(data)["KALMAN"]

    attached: dict[int, list[dict[str, Any]]] = {}
    required = BASELINE_FEATURES + OD_FEATURES + KALMAN_FEATURES + (
        "homeGamesPlayedBefore",
        "awayGamesPlayedBefore",
    )
    for season in DEFAULT_SEASONS:
        rows: list[dict[str, Any]] = []
        for base in data[season]:
            gid = str(base.get("gameId"))
            market_row = market_by_id.get(gid)
            pair = kalman.get(gid)
            if market_row is None or pair is None:
                continue
            row = attach_market(base, market_row)
            row = _attach_state_features(row, od_signals)
            row["KALMAN_strength"] = float(pair[0])
            row["KALMAN_uncertainty"] = float(pair[1])
            if all(finite(row.get(name)) for name in required):
                rows.append(row)
        attached[season] = [row for row in rows if eligible_site(row, MIN_GAMES)]
    return attached, missing_observations


def _build_cross_fitted_candidates(
    eligible: dict[int, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Generate first-stage OOS candidate bets for every possible source season."""
    out: list[dict[str, Any]] = []
    for source_season in OOF_SOURCE_SEASONS:
        train = [
            row
            for season in DEFAULT_SEASONS
            if season < source_season
            for row in eligible[season]
        ]
        test = eligible[source_season]
        if not train or not test:
            continue
        model = fit_logistic(train, BASELINE_FEATURES)
        probs = predict_home_cover(model, test, BASELINE_FEATURES)
        for row, prob in zip(test, probs):
            p = float(prob)
            side = 1 if p >= 0.5 else -1
            confidence = max(p, 1.0 - p)
            cover = _sign(float(row["target_margin"]) - float(row["marketHomeMargin"]))
            result = "PUSH" if cover == 0 else ("WIN" if side == cover else "LOSS")
            meta = dict(row)
            meta["baselineProbabilityHomeCover"] = p
            meta["baselineConfidence"] = confidence
            meta["baselinePickedSideSign"] = side
            meta["actualCoverSign"] = int(cover)
            meta["baselineResult"] = result
            meta["gateTarget"] = None if cover == 0 else int(side == cover)
            if _candidate(meta):
                out.append(meta)
    return out


def run(
    lines: Path,
    raw_root: Path,
    processed_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    eligible, missing_observations = _prepare_rows(lines, raw_root, processed_root)
    candidates = _build_cross_fitted_candidates(eligible)

    official_candidates = [row for row in candidates if int(row["season"]) in TEST_SEASONS]
    baseline_games = [_baseline_record_from_meta(row) for row in official_candidates]
    _check_baseline(baseline_games)

    gate_games: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []
    logistic_coefficients: list[dict[str, Any]] = []

    for test_season in TEST_SEASONS:
        gate_train = [
            row for row in candidates
            if int(row["season"]) < test_season and row.get("gateTarget") in (0, 1)
        ]
        gate_test = [row for row in candidates if int(row["season"]) == test_season]
        if not gate_train or not gate_test:
            raise ValueError(f"Empty meta-gate fold for {test_season}")

        fold: dict[str, Any] = {
            "season": int(test_season),
            "gateTrainN": len(gate_train),
            "candidateN": len(gate_test),
            "baseline": summarize_bets([_baseline_record_from_meta(row) for row in gate_test]),
            "variants": [],
        }

        for variant in GATE_VARIANTS:
            model = _fit_gate(gate_train, variant)
            probs = _predict_gate(model, gate_test)
            records = [
                _gate_bet_record(row, variant, float(prob))
                for row, prob in zip(gate_test, probs)
            ]
            gate_games.extend(records)
            accepted = _selected(records)
            passed = _passed(records)
            fold["variants"].append({
                "variant": variant,
                "accepted": summarize_bets(accepted),
                "passed": summarize_bets(passed),
                "retention": len(accepted) / len(records),
                "gateBrier": _gate_brier(records),
            })
            if variant == "META_LOGISTIC":
                logistic_coefficients.extend(logistic_coefficient_rows(model, test_season))
        folds.append(fold)

    baseline_summary = summarize_bets(baseline_games)
    pooled: list[dict[str, Any]] = []
    recent: list[dict[str, Any]] = []
    quality: dict[str, Any] = {}
    bankroll: dict[str, Any] = {}

    for variant in GATE_VARIANTS:
        rows = [row for row in gate_games if row["variant"] == variant]
        accepted = _selected(rows)
        passed = _passed(rows)
        recent_rows = [row for row in rows if int(row["season"]) >= 2023]
        recent_accepted = _selected(recent_rows)
        recent_passed = _passed(recent_rows)
        pooled.append({
            "variant": variant,
            "accepted": summarize_bets(accepted),
            "passed": summarize_bets(passed),
            "retention": len(accepted) / len(rows),
            "gateBrier": _gate_brier(rows),
            "deltaAccuracyPPVsBaseline": (
                (float(summarize_bets(accepted)["accuracy"]) - float(baseline_summary["accuracy"])) * 100.0
                if summarize_bets(accepted)["accuracy"] is not None else None
            ),
            "deltaRoiPPVsBaseline": (
                (float(summarize_bets(accepted)["roiMinus110"]) - float(baseline_summary["roiMinus110"])) * 100.0
                if summarize_bets(accepted)["roiMinus110"] is not None else None
            ),
        })
        recent.append({
            "variant": variant,
            "accepted": summarize_bets(recent_accepted),
            "passed": summarize_bets(recent_passed),
            "retention": len(recent_accepted) / len(recent_rows) if recent_rows else None,
            "gateBrier": _gate_brier(recent_rows),
        })
        quality[variant] = {
            "scoreBuckets": quality_curve(rows),
            "cumulativeRank": cumulative_rank_curve(rows),
        }
        bankroll[variant] = {
            "accepted": bankroll_path(accepted, 0.0) if accepted else None,
            "baselineReference": bankroll_path(baseline_games, 0.0),
        }

    report = {
        "schemaVersion": 1,
        "version": VERSION,
        "status": "EXPLORATORY_POST_DISCOVERY_META_GATE",
        "researchQuestion": "Can all validated pregame feature families identify which existing FULL ATS candidate bets deserve action?",
        "firstStage": {
            "model": "FULL ATS logistic",
            "minGames": MIN_GAMES,
            "candidateThreshold": BASELINE_THRESHOLD,
            "sideIsImmutable": True,
            "expectedHistoricalRecord": EXPECTED_BASELINE,
            "reproduction": "PASS",
        },
        "gate": {
            "decisionThreshold": GATE_THRESHOLD,
            "thresholdMeaning": "-110 break-even probability; fixed before evaluation",
            "variants": list(GATE_VARIANTS),
            "featureCount": len(GATE_FEATURES),
            "features": list(GATE_FEATURES),
            "featureBlocks": {
                "fullAts": list(BASELINE_FEATURES),
                "dynamicOffenseDefense": list(OD_FEATURES),
                "kalman": list(KALMAN_FEATURES),
                "crossFittedFirstStageAndDepth": list(META_OUTPUT_FEATURES),
            },
            "crossFitContract": "every gate-training example uses a FULL prediction trained only on seasons earlier than that example season",
        },
        "testSeasons": list(TEST_SEASONS),
        "oofSourceSeasons": list(OOF_SOURCE_SEASONS),
        "missingObservationGames": missing_observations,
        "baselinePooled": baseline_summary,
        "pooled": pooled,
        "recent2023To2025": recent,
        "folds": folds,
        "qualityCurves": quality,
        "bankroll": bankroll,
        "logisticCoefficientRows": logistic_coefficients,
        "logisticCoefficientStability": coefficient_stability(logistic_coefficients),
    }
    return report, baseline_games + gate_games


def _pct(value: Any) -> str:
    return "NA" if value is None else f"{float(value):.3%}"


def _write(path: Path, payload: Any, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-fitted FULL ATS bet-quality meta gate")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = run(args.lines, args.raw_root, args.processed_root)
    print("FULL ATS BET-QUALITY META GATE — EXPLORATORY")
    print(f"Version: {VERSION}")
    print(f"Candidate contract: minGames={MIN_GAMES} FULL confidence>={BASELINE_THRESHOLD:.3f}")
    print(f"Gate decision: predicted pick-win probability >= {GATE_THRESHOLD:.6f} (-110 break-even)")
    print(f"Gate features: {len(GATE_FEATURES)} validated pregame inputs")
    print("BASELINE REPRODUCTION: PASS (265-220-10, 495 bets)")
    print("Gate never reverses the FULL side.\n")

    b = report["baselinePooled"]
    print("=== POOLED ===")
    print(
        f"BASELINE       bets={b['bets']:3d} ATS={b['wins']}-{b['losses']}-{b['pushes']} "
        f"({_pct(b['accuracy'])}) ROI={_pct(b['roiMinus110'])}"
    )
    for row in report["pooled"]:
        a, p = row["accepted"], row["passed"]
        print(
            f"{row['variant']:<14} BET={a['bets']:3d} {a['wins']}-{a['losses']}-{a['pushes']} "
            f"({_pct(a['accuracy'])}) ROI={_pct(a['roiMinus110'])} retention={_pct(row['retention'])} "
            f"dATS={row['deltaAccuracyPPVsBaseline']:+.3f}pp dROI={row['deltaRoiPPVsBaseline']:+.3f}pp gateBrier={row['gateBrier']:.6f}"
        )
        print(
            f"{'':14} PASS={p['bets']:3d} {p['wins']}-{p['losses']}-{p['pushes']} "
            f"({_pct(p['accuracy'])}) ROI={_pct(p['roiMinus110'])}"
        )

    print("\n=== SEASON STABILITY ===")
    for fold in report["folds"]:
        print(f"{fold['season']} baseline {fold['baseline']['wins']}-{fold['baseline']['losses']}-{fold['baseline']['pushes']} {_pct(fold['baseline']['accuracy'])}")
        for row in fold["variants"]:
            a, p = row["accepted"], row["passed"]
            print(
                f"  {row['variant']:<14} BET {a['wins']}-{a['losses']}-{a['pushes']} {_pct(a['accuracy'])} ROI={_pct(a['roiMinus110'])} "
                f"| PASS {p['wins']}-{p['losses']}-{p['pushes']} {_pct(p['accuracy'])} retention={_pct(row['retention'])}"
            )

    print("\n=== RECENT 2023-2025 ===")
    for row in report["recent2023To2025"]:
        a, p = row["accepted"], row["passed"]
        print(
            f"{row['variant']:<14} BET {a['wins']}-{a['losses']}-{a['pushes']} {_pct(a['accuracy'])} ROI={_pct(a['roiMinus110'])} "
            f"| PASS {p['wins']}-{p['losses']}-{p['pushes']} {_pct(p['accuracy'])} retention={_pct(row['retention'])}"
        )

    print("\n=== GATE QUALITY CURVE ===")
    for variant in GATE_VARIANTS:
        print(f"{variant}:")
        for row in report["qualityCurves"][variant]["scoreBuckets"]:
            print(
                f"  {row['bucket']:<16} n={row['bets']:3d} ATS={row['wins']}-{row['losses']}-{row['pushes']} "
                f"{_pct(row['accuracy'])} ROI={_pct(row['roiMinus110'])}"
            )

    print("\n=== CUMULATIVE TOP-RANKED BETS — DIAGNOSTIC ONLY ===")
    for variant in GATE_VARIANTS:
        print(f"{variant}:")
        for row in report["qualityCurves"][variant]["cumulativeRank"]:
            print(
                f"  top {row['topFraction']:.0%}: n={row['bets']:3d} ATS={row['wins']}-{row['losses']}-{row['pushes']} "
                f"{_pct(row['accuracy'])} ROI={_pct(row['roiMinus110'])}"
            )

    print("\n=== META_LOGISTIC COEFFICIENT STABILITY — TOP ABS MEAN ===")
    for row in sorted(report["logisticCoefficientStability"], key=lambda r: abs(float(r["mean"])), reverse=True)[:20]:
        print(
            f"{row['feature']:<42} mean={row['mean']:+.4f} std={row['std']:.4f} "
            f"sign=+{row['positive']}/-{row['negative']}"
        )

    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"\nReport: {args.output}")
    print(f"Per-game decisions: {args.games_output}")
    print("WARNING: gate architecture is post-discovery historical research, not untouched confirmation evidence.")


if __name__ == "__main__":
    main()
