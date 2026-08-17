"""Freeze and score the primary ATS logistic challenger for 2026.

The research rule is fixed before 2026 outcomes:
- feature family: FULL = Prediction v2 football features + market context
- eligibility: minGames=3
- confidence threshold: 0.575
- model: StandardScaler + LogisticRegression(C=0.5, max_iter=2000)
- target: home cover vs away cover; pushes excluded from fitting

This module intentionally separates artifact creation from prospective scoring.
The artifact must be built once from the complete pre-2026 corpus, checksummed,
and then treated as immutable for the 2026 prospective test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from cfb_analytics.analytics.market_edge_model_zoo import (
    MARKET_CONTEXT_FEATURES,
    MODEL_FEATURES,
    _sign,
    attach_market,
    finite,
)
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import eligible_site, load_data
from cfb_analytics.analytics.prediction_v2_clean_market_benchmark import DEFAULT_LINES, clean_market_rows
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

FREEZE_VERSION = "ats-logistic-full-min3-0575-prospective-v1"
MIN_GAMES = 3
CONFIDENCE_THRESHOLD = 0.575
LOGISTIC_C = 0.5
FIT_MAX_ITER = 2000
FIT_RANDOM_STATE = 42
TRAINING_CUTOFF_SEASON = 2025
DEFAULT_ARTIFACT = Path("data/processed/market_benchmark/ats-logistic-full-min3-0575-prospective-v1.json")
DEFAULT_SHA = Path("data/processed/market_benchmark/ats-logistic-full-min3-0575-prospective-v1.sha256")

TARGET_KEYS = {
    "target_margin", "target", "homePoints", "awayPoints", "homeScore", "awayScore",
    "home_points", "away_points", "home_score", "away_score",
}


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def artifact_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _training_rows(lines: Path, raw_root: Path, processed_root: Path) -> tuple[list[dict[str, Any]], int]:
    market = clean_market_rows(lines)
    market_by_id = {str(row["gameId"]): row for row in market}
    data = load_data(raw_root, processed_root)
    rows: list[dict[str, Any]] = []
    pushes = 0

    for season in DEFAULT_SEASONS:
        if season > TRAINING_CUTOFF_SEASON:
            continue
        for base in data[season]:
            if not eligible_site(base, MIN_GAMES):
                continue
            market_row = market_by_id.get(str(base.get("gameId")))
            if market_row is None:
                continue
            row = attach_market(base, market_row)
            if not all(finite(row.get(name)) for name in MODEL_FEATURES):
                continue
            cover = _sign(float(row["target_margin"]) - float(row["marketHomeMargin"]))
            if cover == 0:
                pushes += 1
                continue
            rows.append(row)

    if not rows:
        raise ValueError("No pre-2026 ATS logistic training rows were available")
    return rows, pushes


def fit_artifact(lines: Path, raw_root: Path, processed_root: Path) -> dict[str, Any]:
    rows, pushes = _training_rows(lines, raw_root, processed_root)
    x = np.asarray([[float(row[name]) for name in MODEL_FEATURES] for row in rows], dtype=float)
    y = np.asarray([
        1 if float(row["target_margin"]) > float(row["marketHomeMargin"]) else 0
        for row in rows
    ], dtype=int)

    pipe = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=LOGISTIC_C, max_iter=FIT_MAX_ITER, random_state=FIT_RANDOM_STATE),
    )
    pipe.fit(x, y)
    scaler: StandardScaler = pipe.named_steps["standardscaler"]
    logistic: LogisticRegression = pipe.named_steps["logisticregression"]
    if list(logistic.classes_) != [0, 1]:
        raise ValueError(f"Unexpected logistic classes: {list(logistic.classes_)}")

    seasons = sorted({int(row["season"]) for row in rows})
    artifact = {
        "schemaVersion": 1,
        "freezeVersion": FREEZE_VERSION,
        "status": "FROZEN_FOR_2026_PROSPECTIVE_TEST_AFTER_ARTIFACT_COMMIT",
        "researchBoundary": "Do not alter features, C, minGames, threshold, scaler, coefficients, or intercept using 2026 outcomes.",
        "marketSelection": "first parseable formattedSpread in CFBD provider order",
        "spreadConvention": "positive=home favored; negative=away favored",
        "target": "home-cover-vs-away-cover; historical pushes excluded from fitting",
        "features": list(MODEL_FEATURES),
        "marketContextFeatures": list(MARKET_CONTEXT_FEATURES),
        "minGames": MIN_GAMES,
        "confidenceThreshold": CONFIDENCE_THRESHOLD,
        "model": {
            "family": "StandardScaler+LogisticRegression",
            "C": LOGISTIC_C,
            "maxIter": FIT_MAX_ITER,
            "randomState": FIT_RANDOM_STATE,
            "classes": [0, 1],
            "scalerMean": [float(v) for v in scaler.mean_],
            "scalerScale": [float(v) for v in scaler.scale_],
            "coefficients": [float(v) for v in logistic.coef_[0]],
            "intercept": float(logistic.intercept_[0]),
        },
        "training": {
            "cutoffSeason": TRAINING_CUTOFF_SEASON,
            "seasons": seasons,
            "rows": len(rows),
            "pushesExcluded": pushes,
        },
        "discoveryEvidence": {
            "min3Threshold0575": {"wins": 265, "losses": 220, "pushes": 10, "atsAccuracy": 265 / 485, "roiMinus110": 0.04311},
            "note": "Historical discovery evidence only; not confirmatory evidence.",
        },
    }
    return artifact


def validate_artifact(artifact: dict[str, Any]) -> None:
    if artifact.get("freezeVersion") != FREEZE_VERSION:
        raise ValueError("Unexpected ATS freeze version")
    if tuple(artifact.get("features", [])) != tuple(MODEL_FEATURES):
        raise ValueError("Frozen ATS feature list mismatch")
    if int(artifact.get("minGames")) != MIN_GAMES:
        raise ValueError("Frozen minGames mismatch")
    if abs(float(artifact.get("confidenceThreshold")) - CONFIDENCE_THRESHOLD) > 1e-12:
        raise ValueError("Frozen confidence threshold mismatch")
    model = artifact.get("model") or {}
    if abs(float(model.get("C")) - LOGISTIC_C) > 1e-12:
        raise ValueError("Frozen logistic C mismatch")
    n = len(MODEL_FEATURES)
    for key in ("scalerMean", "scalerScale", "coefficients"):
        values = model.get(key)
        if not isinstance(values, list) or len(values) != n or not all(finite(v) for v in values):
            raise ValueError(f"Invalid frozen vector: {key}")
    if not finite(model.get("intercept")):
        raise ValueError("Invalid frozen intercept")
    if any(float(v) <= 0.0 for v in model["scalerScale"]):
        raise ValueError("Frozen scaler contains non-positive scale")


def reject_target_leakage(row: dict[str, Any]) -> None:
    for key in TARGET_KEYS:
        if key not in row:
            continue
        value = row.get(key)
        if finite(value):
            raise ValueError(f"Prospective ATS row contains target/outcome field {key}")


def add_market_context(row: dict[str, Any], market_home_margin: float) -> dict[str, Any]:
    if not finite(market_home_margin):
        raise ValueError("market_home_margin must be finite")
    out = dict(row)
    spread = float(market_home_margin)
    out.update({
        "marketHomeMargin": spread,
        "marketAbsSpread": abs(spread),
        "marketSpreadSquared": spread * spread,
        "marketHomeFavorite": 1.0 if spread > 0.0 else 0.0,
        "marketPickem": 1.0 if abs(spread) <= 1e-12 else 0.0,
        "weekNumber": float(row.get("week") or 0),
        "neutralSite": 1.0 if row.get("isNeutralSite") is True else 0.0,
    })
    return out


def score_prospective(row: dict[str, Any], market_home_margin: float, artifact: dict[str, Any]) -> dict[str, Any]:
    validate_artifact(artifact)
    reject_target_leakage(row)
    prepared = add_market_context(row, market_home_margin)
    missing = [name for name in MODEL_FEATURES if not finite(prepared.get(name))]
    if missing:
        raise ValueError(f"Prospective ATS row missing/non-finite frozen features: {missing}")

    model = artifact["model"]
    x = np.asarray([float(prepared[name]) for name in MODEL_FEATURES], dtype=float)
    mean = np.asarray(model["scalerMean"], dtype=float)
    scale = np.asarray(model["scalerScale"], dtype=float)
    coef = np.asarray(model["coefficients"], dtype=float)
    z = (x - mean) / scale
    logit = float(np.dot(z, coef) + float(model["intercept"]))
    p_home = 1.0 / (1.0 + math.exp(-max(-700.0, min(700.0, logit))))
    confidence = max(p_home, 1.0 - p_home)
    if confidence + 1e-12 < CONFIDENCE_THRESHOLD:
        pick = "NO_BET"
    else:
        pick = "HOME" if p_home >= 0.5 else "AWAY"
    return {
        "freezeVersion": FREEZE_VERSION,
        "gameId": str(row.get("gameId")) if row.get("gameId") is not None else None,
        "homeTeam": row.get("homeTeam"),
        "awayTeam": row.get("awayTeam"),
        "marketHomeMargin": float(market_home_margin),
        "homeCoverProbability": p_home,
        "awayCoverProbability": 1.0 - p_home,
        "confidence": confidence,
        "threshold": CONFIDENCE_THRESHOLD,
        "pick": pick,
    }


def write_artifact(artifact: dict[str, Any], output: Path, sha_output: Path, overwrite: bool) -> str:
    validate_artifact(artifact)
    if (output.exists() or sha_output.exists()) and not overwrite:
        raise FileExistsError("Frozen artifact/sha exists; use --overwrite only before the artifact is committed")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    sha = artifact_sha256(artifact)
    sha_output.write_text(sha + "\n")
    return sha


def main() -> None:
    parser = argparse.ArgumentParser(description="Build or verify the frozen 2026 ATS logistic challenger")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--sha-output", type=Path, default=DEFAULT_SHA)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        artifact = json.loads(args.output.read_text())
        validate_artifact(artifact)
        actual = artifact_sha256(artifact)
        expected = args.sha_output.read_text().strip()
        if actual != expected:
            raise ValueError(f"ATS artifact checksum mismatch: expected={expected} actual={actual}")
        print("ATS LOGISTIC PROSPECTIVE FREEZE: VERIFIED")
        print(f"Version: {FREEZE_VERSION}")
        print(f"SHA256: {actual}")
        return

    artifact = fit_artifact(args.lines, args.raw_root, args.processed_root)
    sha = write_artifact(artifact, args.output, args.sha_output, args.overwrite)
    print("ATS LOGISTIC PROSPECTIVE FREEZE: BUILT")
    print(f"Version: {FREEZE_VERSION}")
    print(f"Training rows: {artifact['training']['rows']}")
    print(f"Training seasons: {artifact['training']['seasons']}")
    print(f"Threshold: {CONFIDENCE_THRESHOLD:.3f}")
    print(f"Artifact: {args.output}")
    print(f"SHA256: {sha}")
    print("COMMIT THE ARTIFACT AND SHA BEFORE USING ANY 2026 OUTCOMES.")


if __name__ == "__main__":
    main()
