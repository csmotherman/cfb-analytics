"""Standalone leakage-safe opponent-adjusted scoring model.

This model predicts home and away points directly from prior completed games:

    score = basePoints + offense(team) - defense(opponent) + site * HFA

The predicted game margin is expectedHomePoints - expectedAwayPoints. It is kept
separate from Prediction v2 so the two models can be compared head-to-head on the
same historical OOS game sample.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.prediction_v1_integrity_audit import MIN_GAMES_VALUES, load_raw_games
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import TEST_SEASONS, eligible_site, load_data
from cfb_analytics.analytics.prediction_v2_adjusted_scoring_challenger import add_scoring_features
from cfb_analytics.analytics.prediction_v2_market_benchmark import build_official_oos_predictions
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

MODEL_VERSION = "standalone-adjusted-scoring-v1"


def load_rows(raw_root: Path, processed_root: Path) -> dict[int, list[dict[str, Any]]]:
    base = load_data(raw_root, processed_root)
    out: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        raw_games, conflicts = load_raw_games(raw_root, season)
        if conflicts:
            raise ValueError(f"Conflicting raw game scores in {season}: {conflicts[:5]}")
        out[season] = add_scoring_features(base[season], raw_games)
    return out


def build_standalone_predictions(
    raw_root: Path,
    processed_root: Path,
) -> list[dict[str, Any]]:
    data = load_rows(raw_root, processed_root)
    out: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        for season in TEST_SEASONS:
            for row in data[season]:
                if not eligible_site(row, min_games):
                    continue
                home_points = row.get("adjustedScoringExpectedHomePoints")
                away_points = row.get("adjustedScoringExpectedAwayPoints")
                if not isinstance(home_points, (int, float)) or not math.isfinite(float(home_points)):
                    raise ValueError(f"Missing standalone home-points prediction for game {row.get('gameId')}")
                if not isinstance(away_points, (int, float)) or not math.isfinite(float(away_points)):
                    raise ValueError(f"Missing standalone away-points prediction for game {row.get('gameId')}")
                margin = float(home_points) - float(away_points)
                out.append(
                    {
                        "modelVersion": MODEL_VERSION,
                        "minGames": int(min_games),
                        "season": int(season),
                        "seasonType": row.get("seasonType"),
                        "week": int(row.get("week") or 0),
                        "gameId": str(row["gameId"]),
                        "homeTeam": row.get("homeTeam"),
                        "awayTeam": row.get("awayTeam"),
                        "actualHomeMargin": float(row["target_margin"]),
                        "predictedHomePoints": float(home_points),
                        "predictedAwayPoints": float(away_points),
                        "predictedHomeMargin": margin,
                    }
                )
    return out


def _metrics(rows: list[dict[str, Any]], prediction_field: str) -> dict[str, float]:
    absolute: list[float] = []
    squared: list[float] = []
    correct = 0
    for row in rows:
        actual = float(row["actualHomeMargin"])
        pred = float(row[prediction_field])
        absolute.append(abs(pred - actual))
        squared.append((pred - actual) ** 2)
        if actual != 0.0:
            correct += int((pred > 0.0) == (actual > 0.0))
    n = len(rows)
    return {
        "n": n,
        "mae": sum(absolute) / n,
        "rmse": math.sqrt(sum(squared) / n),
        "winnerAccuracy": correct / n,
    }


def compare_models(
    raw_root: Path,
    processed_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    standalone = build_standalone_predictions(raw_root, processed_root)
    v2 = build_official_oos_predictions(raw_root, processed_root)

    v2_by_key = {
        (int(row["minGames"]), int(row["season"]), str(row["gameId"])): row
        for row in v2
    }
    standalone_by_key = {
        (int(row["minGames"]), int(row["season"]), str(row["gameId"])): row
        for row in standalone
    }
    if set(v2_by_key) != set(standalone_by_key):
        missing_standalone = sorted(set(v2_by_key) - set(standalone_by_key))[:10]
        missing_v2 = sorted(set(standalone_by_key) - set(v2_by_key))[:10]
        raise ValueError(
            "Standalone/v2 common-sample mismatch: "
            f"missing_standalone={missing_standalone} missing_v2={missing_v2}"
        )

    joined: list[dict[str, Any]] = []
    for key in sorted(v2_by_key):
        s = standalone_by_key[key]
        p = v2_by_key[key]
        joined.append(
            {
                **s,
                "predictionV2HomeMargin": float(p["modelHomeMargin"]),
                "standaloneAbsError": abs(float(s["predictedHomeMargin"]) - float(s["actualHomeMargin"])),
                "predictionV2AbsError": abs(float(p["modelHomeMargin"]) - float(s["actualHomeMargin"])),
            }
        )

    summaries: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        pooled = [row for row in joined if row["minGames"] == min_games]
        standalone_metrics = _metrics(pooled, "predictedHomeMargin")
        v2_metrics = _metrics(pooled, "predictionV2HomeMargin")
        summaries.append(
            {
                "scope": "pooled",
                "minGames": int(min_games),
                "n": len(pooled),
                "standalone": standalone_metrics,
                "predictionV2": v2_metrics,
                "deltaMae": standalone_metrics["mae"] - v2_metrics["mae"],
                "deltaRmse": standalone_metrics["rmse"] - v2_metrics["rmse"],
                "deltaWinnerPP": (
                    standalone_metrics["winnerAccuracy"] - v2_metrics["winnerAccuracy"]
                ) * 100.0,
            }
        )
        for season in TEST_SEASONS:
            season_rows = [row for row in pooled if row["season"] == season]
            sm = _metrics(season_rows, "predictedHomeMargin")
            vm = _metrics(season_rows, "predictionV2HomeMargin")
            summaries.append(
                {
                    "scope": "season",
                    "minGames": int(min_games),
                    "season": int(season),
                    "n": len(season_rows),
                    "standalone": sm,
                    "predictionV2": vm,
                    "deltaMae": sm["mae"] - vm["mae"],
                    "deltaRmse": sm["rmse"] - vm["rmse"],
                    "deltaWinnerPP": (sm["winnerAccuracy"] - vm["winnerAccuracy"]) * 100.0,
                }
            )

    return (
        {
            "schemaVersion": 1,
            "modelVersion": MODEL_VERSION,
            "comparison": "standalone-adjusted-scoring-vs-prediction-v2",
            "testSeasons": list(TEST_SEASONS),
            "summaries": summaries,
        },
        joined,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare standalone adjusted scoring model with Prediction v2")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/standalone_adjusted_scoring_vs_prediction_v2.json"),
    )
    parser.add_argument(
        "--games-output",
        type=Path,
        default=Path("data/processed/standalone_adjusted_scoring_vs_prediction_v2_games.json"),
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = compare_models(args.raw_root, args.processed_root)
    print("STANDALONE ADJUSTED SCORING VS PREDICTION V2")
    for row in report["summaries"]:
        if row["scope"] != "pooled":
            continue
        s = row["standalone"]
        v = row["predictionV2"]
        print(
            f"min{row['minGames']}: n={row['n']} "
            f"scoring_MAE={s['mae']:.4f} v2_MAE={v['mae']:.4f} dMAE={row['deltaMae']:+.4f} "
            f"scoring_RMSE={s['rmse']:.4f} v2_RMSE={v['rmse']:.4f} dRMSE={row['deltaRmse']:+.4f} "
            f"scoring_win={s['winnerAccuracy']:.3%} v2_win={v['winnerAccuracy']:.3%} "
            f"dWin={row['deltaWinnerPP']:+.3f}pp"
        )

    for path, payload in ((args.output, report), (args.games_output, games)):
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"Report: {args.output}")
    print(f"Matched games: {args.games_output}")


if __name__ == "__main__":
    main()
