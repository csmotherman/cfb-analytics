"""Historical Prediction-v2 rows used by the public website archive.

This module does not introduce or tune a new model. It reconstructs the already
frozen early-season adjacent-prior Prediction-v2 rule in chronological outer
folds and uses those rows only to supplement games that do not already have a
stored mature minGames=3 OOS Prediction-v2 benchmark call.

Important evidence boundary:
- each early-prior test season is scored by a model trained only on earlier seasons;
- 2021 is not reconstructed with an early prior because 2020 is intentionally absent;
- no early-prior result is used to choose a different weight, feature, threshold,
  or model family;
- mature stored OOS predictions remain authoritative when both sources exist.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    fit_generic,
    predict_generic,
    prepare_generic,
)
from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.prediction_v2_early_prior_challenger import (
    CHALLENGER_VERSION,
    TEST_SEASONS,
    build_datasets,
)

EARLY_ARCHIVE_SOURCE = "prediction-v2-early-prior-walk-forward-oos"
MATURE_ARCHIVE_SOURCE = "prediction-v2-min3-stored-oos"


def _game_id(row: dict[str, Any]) -> str:
    value = row.get("gameId")
    if value is None:
        raise ValueError("Historical early-prior row is missing gameId")
    return str(value)


def _fit_early_model(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Cannot fit historical early-prior model on an empty training set")
    return fit_generic(prepare_generic(rows, PREDICTION_V2_FEATURES))


def build_early_prior_oos_predictions(
    raw_root: Path,
    processed_root: Path,
) -> dict[str, dict[str, Any]]:
    """Reconstruct frozen early-prior predictions in strict chronological folds."""
    datasets = build_datasets(raw_root, processed_root)
    blend: dict[int, list[dict[str, Any]]] = datasets["blend"]
    available = sorted(int(season) for season in datasets["priorMap"])

    missing_test_seasons = [season for season in TEST_SEASONS if season not in available]
    if missing_test_seasons:
        raise ValueError(
            "Historical early-prior corpus is incomplete for required test seasons: "
            + ", ".join(map(str, missing_test_seasons))
        )

    out: dict[str, dict[str, Any]] = {}
    for test_season in TEST_SEASONS:
        train_seasons = [season for season in available if season < test_season]
        train = [
            row
            for season in train_seasons
            for row in blend.get(season, [])
        ]
        test = list(blend.get(test_season, []))
        if not train:
            raise ValueError(f"No earlier early-prior training rows for {test_season}")
        if not test:
            raise ValueError(f"No early-prior test rows for {test_season}")

        model = _fit_early_model(train)
        for row in test:
            gid = _game_id(row)
            if gid in out:
                raise ValueError(f"Duplicate historical early-prior gameId: {gid}")
            margin = float(predict_generic(model, row))
            out[gid] = {
                "gameId": gid,
                "season": int(test_season),
                "seasonType": row.get("seasonType"),
                "week": int(row.get("week") or 0),
                "homeTeam": row.get("homeTeam"),
                "awayTeam": row.get("awayTeam"),
                "modelHomeMargin": margin,
                "predictionSource": EARLY_ARCHIVE_SOURCE,
                "earlyPriorVersion": CHALLENGER_VERSION,
                "priorWeightHome": row.get("priorWeightHome"),
                "priorWeightAway": row.get("priorWeightAway"),
                "trainingSeasons": train_seasons,
            }
    return out


def mark_mature_predictions(
    rows: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Attach explicit provenance to the stored mature OOS benchmark rows."""
    return {
        gid: {
            **row,
            "predictionSource": row.get("predictionSource") or MATURE_ARCHIVE_SOURCE,
        }
        for gid, row in rows.items()
    }


def combine_historical_oos_predictions(
    mature: dict[str, dict[str, Any]],
    early: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    """Supplement missing mature calls with early-prior OOS calls.

    Stored mature Prediction-v2 evidence wins on overlap. This preserves the exact
    historical benchmark and its ATS recommendation alignment while using the
    frozen early-prior reconstruction to fill previously blank early-season games.
    """
    mature_marked = mark_mature_predictions(mature)
    combined = dict(mature_marked)
    overlap = 0
    supplement = 0
    for gid, row in early.items():
        if gid in combined:
            overlap += 1
            continue
        combined[gid] = row
        supplement += 1

    return combined, {
        "mature": len(mature_marked),
        "earlyGenerated": len(early),
        "earlyOverlap": overlap,
        "earlySupplement": supplement,
        "combined": len(combined),
    }
