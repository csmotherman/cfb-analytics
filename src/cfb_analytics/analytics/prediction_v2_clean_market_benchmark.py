"""Evaluate locked Prediction v2 against the audited clean CFBD spread snapshot."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.cfbd_market_spread_audit import load_rows
from cfb_analytics.analytics.prediction_v1_integrity_audit import MIN_GAMES_VALUES
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import TEST_SEASONS
from cfb_analytics.analytics.prediction_v2_market_benchmark import (
    build_official_oos_predictions,
    join_predictions_to_market,
    summarize_edge_buckets,
    summarize_matched,
)

DEFAULT_LINES = Path("data/raw/market_lines/cfbd-market-spreads-2014-2025.json")
DEFAULT_REPORT = Path("data/processed/market_benchmark/prediction-v2-vs-clean-market.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/prediction-v2-vs-clean-market-games.json")


def clean_market_rows(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in load_rows(path):
        spread = float(row["marketSpread"])
        if not math.isfinite(spread):
            raise ValueError(f"Non-finite clean market spread for {row.get('gameId')}")
        out.append(
            {
                "season": int(row["season"]),
                "seasonType": row.get("seasonType"),
                "week": row.get("week"),
                "gameId": str(row["gameId"]),
                "homeTeam": row.get("homeTeam"),
                "awayTeam": row.get("awayTeam"),
                "provider": row.get("provider"),
                "selection": "first-formatted",
                "providerCount": None,
                "marketHomeMargin": spread,
                "marketOpenHomeMargin": None,
            }
        )
    return out


def build_report(lines: Path, raw_root: Path, processed_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    market = clean_market_rows(lines)
    predictions = build_official_oos_predictions(raw_root, processed_root)
    matched, missing = join_predictions_to_market(predictions, market)

    summaries: list[dict[str, Any]] = []
    edge_buckets: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        pooled = [row for row in matched if row["minGames"] == min_games]
        summaries.append(
            {
                "scope": "pooled-official-oos",
                "minGames": int(min_games),
                **summarize_matched(pooled),
            }
        )
        for season in TEST_SEASONS:
            season_rows = [row for row in pooled if row["season"] == season]
            summaries.append(
                {
                    "scope": "season",
                    "minGames": int(min_games),
                    "season": int(season),
                    **summarize_matched(season_rows),
                }
            )
        for bucket in summarize_edge_buckets(pooled):
            edge_buckets.append({"minGames": int(min_games), **bucket})

    return (
        {
            "schemaVersion": 1,
            "benchmarkVersion": "prediction-v2-vs-clean-cfbd-market-v1",
            "spreadConvention": "positive=home favored; negative=away favored",
            "selectionRule": "first parseable formattedSpread in CFBD provider order",
            "marketRows": len(market),
            "officialOosPredictionRows": len(predictions),
            "matchedPredictionRows": len(matched),
            "missingMarketRows": len(missing),
            "missingMarketGameIds": sorted({str(row["gameId"]) for row in missing}),
            "summaries": summaries,
            "edgeBuckets": edge_buckets,
        },
        matched,
    )


def _write(path: Path, payload: Any, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prediction v2 versus clean historical CFBD market spreads")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = build_report(args.lines, args.raw_root, args.processed_root)
    print("PREDICTION V2 VS CLEAN CFBD MARKET")
    print(
        f"market_rows={report['marketRows']} official_oos={report['officialOosPredictionRows']} "
        f"matched={report['matchedPredictionRows']} missing_market={report['missingMarketRows']}"
    )
    for row in report["summaries"]:
        if row["scope"] != "pooled-official-oos":
            continue
        print(
            f"min{row['minGames']}: n={row['n']} "
            f"model_MAE={row['modelMae']:.4f} market_MAE={row['marketMae']:.4f} "
            f"dMAE={row['deltaMae']:+.4f} "
            f"model_RMSE={row['modelRmse']:.4f} market_RMSE={row['marketRmse']:.4f} "
            f"dRMSE={row['deltaRmse']:+.4f} "
            f"model_win={row['modelWinnerAccuracy']:.3%} market_win={row['marketWinnerAccuracy']:.3%} "
            f"ATS={row['atsWins']}-{row['atsLosses']}-{row['atsPushes']} "
            f"({row['atsAccuracy']:.3%})"
        )
    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"Report: {args.output}")
    print(f"Matched games: {args.games_output}")


if __name__ == "__main__":
    main()
