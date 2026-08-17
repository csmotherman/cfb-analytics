"""Retrospective Prediction-v2 versus CFBD market-spread benchmark.

This module never changes the frozen Prediction-v2 model. It:
1. snapshots historical CFBD betting lines,
2. normalizes market spreads into signed expected home margin,
3. rebuilds the locked Prediction-v2 outer-season OOS predictions, and
4. compares model error and disagreement picks with the market on matched game IDs.

The official Prediction-v2 benchmark test seasons remain unchanged. Historical
market coverage outside those test folds is reported but is not relabeled as
official model OOS evidence.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import httpx

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
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

BENCHMARK_VERSION = "prediction-v2-vs-cfbd-market-v1"
DEFAULT_BASE_URL = "https://api.collegefootballdata.com/lines"
MARKET_SEASONS = tuple(range(2014, 2026))
SEASON_TYPES = ("regular", "postseason")
DEFAULT_RAW_LINES = Path("data/raw/market_lines/cfbd-lines-2014-2025.json")
DEFAULT_REPORT = Path("data/processed/market_benchmark/prediction-v2-vs-market.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/prediction-v2-vs-market-games.json")

_PICK_RE = re.compile(r"^(pick(?:'em)?|pk|even)$", re.IGNORECASE)


def finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _norm_name(value: Any) -> str:
    text = str(value or "").casefold()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def parse_formatted_spread(
    spread_text: Any,
    home: Any,
    away: Any,
) -> float | None:
    """Convert a formatted CFBD spread into signed expected home margin.

    Positive means the market favors the home team by that many points.
    Negative means the market favors the away team.
    """
    if not isinstance(spread_text, str):
        return None
    text = " ".join(spread_text.strip().split())
    if not text:
        return None
    if _PICK_RE.match(text):
        return 0.0

    parts = text.rsplit(" ", 1)
    if len(parts) != 2:
        return None
    team_text, number_text = parts
    try:
        number = float(number_text.replace("+", ""))
    except ValueError:
        return None

    team = _norm_name(team_text)
    home_name = _norm_name(home)
    away_name = _norm_name(away)
    if not team or not home_name or not away_name:
        return None

    magnitude = abs(number)
    if team == home_name:
        return magnitude
    if team == away_name:
        return -magnitude
    return None


def _provider_name(line: dict[str, Any]) -> str:
    provider = line.get("provider")
    if isinstance(provider, dict):
        provider = provider.get("name")
    return str(provider or "").strip()


def _line_home_margin(
    line: dict[str, Any],
    home: Any,
    away: Any,
) -> tuple[float | None, str | None]:
    """Normalize one provider line to expected home margin.

    CFBD's numeric ``spread`` is the home-team betting spread, so expected home
    scoring margin is its negative. ``formattedSpread`` is used as a semantic
    cross-check when it can be parsed.
    """
    formatted = parse_formatted_spread(line.get("formattedSpread"), home, away)
    numeric = -float(line["spread"]) if finite(line.get("spread")) else None

    if formatted is not None and numeric is not None:
        if abs(formatted - numeric) > 1e-9:
            return None, "formatted/numeric spread sign conflict"
        return formatted, None
    if formatted is not None:
        return formatted, None
    if numeric is not None:
        return numeric, None
    return None, "missing parseable spread"


def _line_open_home_margin(line: dict[str, Any]) -> float | None:
    return -float(line["spreadOpen"]) if finite(line.get("spreadOpen")) else None


def select_market_line(
    game: dict[str, Any],
    *,
    fallback_median: bool = True,
) -> dict[str, Any] | None:
    """Select a reproducible market line for one game.

    Prefer the CFBD ``consensus`` provider. If unavailable and fallback_median
    is enabled, use the median normalized line across all parseable providers.
    """
    home = game.get("homeTeam")
    away = game.get("awayTeam")
    lines = game.get("lines")
    if not home or not away or not isinstance(lines, list):
        return None

    usable: list[dict[str, Any]] = []
    conflicts = 0
    for line in lines:
        if not isinstance(line, dict):
            continue
        margin, reason = _line_home_margin(line, home, away)
        if margin is None:
            conflicts += int(reason == "formatted/numeric spread sign conflict")
            continue
        usable.append(
            {
                "provider": _provider_name(line),
                "marketHomeMargin": float(margin),
                "marketOpenHomeMargin": _line_open_home_margin(line),
                "formattedSpread": line.get("formattedSpread"),
            }
        )
    if not usable:
        return None

    consensus = [
        row for row in usable
        if row["provider"].casefold() == "consensus"
    ]
    if consensus:
        chosen = consensus[0]
        return {
            **chosen,
            "selection": "consensus",
            "providerCount": len(usable),
            "lineConflicts": conflicts,
        }

    if not fallback_median:
        return None

    closing = statistics.median(row["marketHomeMargin"] for row in usable)
    openings = [
        float(row["marketOpenHomeMargin"])
        for row in usable
        if finite(row.get("marketOpenHomeMargin"))
    ]
    return {
        "provider": "median",
        "marketHomeMargin": float(closing),
        "marketOpenHomeMargin": statistics.median(openings) if openings else None,
        "formattedSpread": None,
        "selection": "median-fallback",
        "providerCount": len(usable),
        "lineConflicts": conflicts,
    }


def normalize_market_games(
    payload: Iterable[dict[str, Any]],
    *,
    fallback_median: bool = True,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for game in payload:
        gid_value = game.get("id", game.get("gameId"))
        if gid_value is None:
            continue
        gid = str(gid_value)
        if gid in seen:
            raise ValueError(f"Duplicate market gameId {gid}")
        seen.add(gid)

        selected = select_market_line(game, fallback_median=fallback_median)
        if selected is None:
            continue
        rows.append(
            {
                "season": int(game["season"]) if game.get("season") is not None else None,
                "seasonType": game.get("seasonType"),
                "week": int(game["week"]) if game.get("week") is not None else None,
                "gameId": gid,
                "homeTeam": game.get("homeTeam"),
                "awayTeam": game.get("awayTeam"),
                **selected,
            }
        )
    return rows


def _request_lines(
    client: httpx.Client,
    api_key: str,
    year: int,
    season_type: str,
) -> list[dict[str, Any]]:
    response = client.get(
        DEFAULT_BASE_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        params={"year": int(year), "seasonType": season_type},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(
            f"Expected list from CFBD lines endpoint for {year} {season_type}"
        )
    return [row for row in payload if isinstance(row, dict)]


def download_lines_snapshot(
    output: Path,
    *,
    api_key: str,
    seasons: tuple[int, ...] = MARKET_SEASONS,
    overwrite: bool = False,
) -> dict[str, Any]:
    if not api_key:
        raise ValueError("CFBD_API_KEY is required")
    if output.exists() and not overwrite:
        raise FileExistsError(
            f"Market snapshot already exists: {output}. "
            "Use --overwrite only if you intentionally want a new raw snapshot."
        )

    requests_meta: list[dict[str, Any]] = []
    games: list[dict[str, Any]] = []
    with httpx.Client(timeout=60.0) as client:
        for year in seasons:
            for season_type in SEASON_TYPES:
                rows = _request_lines(client, api_key, year, season_type)
                requests_meta.append(
                    {
                        "season": year,
                        "seasonType": season_type,
                        "gamesReturned": len(rows),
                    }
                )
                games.extend(rows)
                print(
                    f"CFBD LINES {year} {season_type}: "
                    f"{len(rows)} games"
                )

    snapshot = {
        "schemaVersion": 1,
        "benchmarkVersion": BENCHMARK_VERSION,
        "source": DEFAULT_BASE_URL,
        "retrievedAtUtc": datetime.now(timezone.utc).isoformat(),
        "seasons": list(seasons),
        "seasonTypes": list(SEASON_TYPES),
        "requests": requests_meta,
        "games": games,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    return snapshot


def load_lines_snapshot(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
        raise ValueError(f"Invalid CFBD market snapshot: {path}")
    return payload


def build_official_oos_predictions(
    raw_root: Path,
    processed_root: Path,
) -> list[dict[str, Any]]:
    """Recreate the locked Prediction-v2 outer-season OOS per-game predictions."""
    data = load_data(raw_root, processed_root)
    out: list[dict[str, Any]] = []

    for min_games in MIN_GAMES_VALUES:
        eligible = {
            season: [row for row in data[season] if eligible_site(row, min_games)]
            for season in DEFAULT_SEASONS
        }
        for test_season in TEST_SEASONS:
            train = [
                row
                for season in DEFAULT_SEASONS
                if season < test_season
                for row in eligible[season]
            ]
            test = eligible[test_season]
            model = fit_generic(
                prepare_generic(train, PREDICTION_V2_FEATURES)
            )
            for row in test:
                gid = row.get("gameId")
                if gid is None:
                    raise ValueError(
                        f"Prediction-v2 OOS row without gameId in {test_season}"
                    )
                prediction = predict_generic(model, row)
                out.append(
                    {
                        "benchmark": "official-oos",
                        "minGames": int(min_games),
                        "season": int(test_season),
                        "seasonType": row.get("seasonType"),
                        "week": int(row.get("week") or 0),
                        "gameId": str(gid),
                        "homeTeam": row.get("homeTeam"),
                        "awayTeam": row.get("awayTeam"),
                        "modelHomeMargin": float(prediction),
                        "actualHomeMargin": float(row["target_margin"]),
                    }
                )
    return out


def _sign(value: float, *, tol: float = 1e-12) -> int:
    if value > tol:
        return 1
    if value < -tol:
        return -1
    return 0


def summarize_matched(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "n": 0,
            "modelMae": None,
            "marketMae": None,
            "deltaMae": None,
            "modelRmse": None,
            "marketRmse": None,
            "deltaRmse": None,
            "modelWinnerAccuracy": None,
            "marketWinnerAccuracy": None,
            "atsDecisions": 0,
            "atsWins": 0,
            "atsLosses": 0,
            "atsPushes": 0,
            "atsAccuracy": None,
            "meanAbsModelMarketDisagreement": None,
        }

    model_abs: list[float] = []
    market_abs: list[float] = []
    model_sq: list[float] = []
    market_sq: list[float] = []
    model_winner = 0
    market_winner = 0
    ats_wins = 0
    ats_losses = 0
    ats_pushes = 0
    disagreements: list[float] = []

    for row in rows:
        actual = float(row["actualHomeMargin"])
        model = float(row["modelHomeMargin"])
        market = float(row["marketHomeMargin"])
        model_error = model - actual
        market_error = market - actual
        model_abs.append(abs(model_error))
        market_abs.append(abs(market_error))
        model_sq.append(model_error * model_error)
        market_sq.append(market_error * market_error)
        model_winner += int(_sign(model) == _sign(actual))
        market_winner += int(_sign(market) == _sign(actual))
        disagreements.append(abs(model - market))

        pick = _sign(model - market)
        cover = _sign(actual - market)
        if cover == 0:
            ats_pushes += 1
        elif pick == 0:
            ats_pushes += 1
        elif pick == cover:
            ats_wins += 1
        else:
            ats_losses += 1

    n = len(rows)
    decisions = ats_wins + ats_losses
    model_mae = sum(model_abs) / n
    market_mae = sum(market_abs) / n
    model_rmse = math.sqrt(sum(model_sq) / n)
    market_rmse = math.sqrt(sum(market_sq) / n)
    return {
        "n": n,
        "modelMae": model_mae,
        "marketMae": market_mae,
        "deltaMae": model_mae - market_mae,
        "modelRmse": model_rmse,
        "marketRmse": market_rmse,
        "deltaRmse": model_rmse - market_rmse,
        "modelWinnerAccuracy": model_winner / n,
        "marketWinnerAccuracy": market_winner / n,
        "atsDecisions": decisions,
        "atsWins": ats_wins,
        "atsLosses": ats_losses,
        "atsPushes": ats_pushes,
        "atsAccuracy": ats_wins / decisions if decisions else None,
        "meanAbsModelMarketDisagreement": sum(disagreements) / n,
    }


def summarize_edge_buckets(
    rows: list[dict[str, Any]],
    thresholds: tuple[float, ...] = (0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0),
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for threshold in thresholds:
        subset = [
            row for row in rows
            if abs(float(row["modelHomeMargin"]) - float(row["marketHomeMargin"]))
            >= threshold
        ]
        summary = summarize_matched(subset)
        out.append({"minEdge": threshold, **summary})
    return out


def join_predictions_to_market(
    predictions: list[dict[str, Any]],
    market_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    market_by_id = {str(row["gameId"]): row for row in market_rows}
    matched: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []

    for pred in predictions:
        market = market_by_id.get(str(pred["gameId"]))
        if market is None:
            missing.append(pred)
            continue

        if (
            pred.get("homeTeam")
            and market.get("homeTeam")
            and str(pred["homeTeam"]) != str(market["homeTeam"])
        ) or (
            pred.get("awayTeam")
            and market.get("awayTeam")
            and str(pred["awayTeam"]) != str(market["awayTeam"])
        ):
            raise ValueError(
                "Market/model home-away identity mismatch for gameId "
                f"{pred['gameId']}: model={pred.get('awayTeam')}@{pred.get('homeTeam')} "
                f"market={market.get('awayTeam')}@{market.get('homeTeam')}"
            )

        actual = float(pred["actualHomeMargin"])
        model = float(pred["modelHomeMargin"])
        market_margin = float(market["marketHomeMargin"])
        matched.append(
            {
                **pred,
                "marketProvider": market.get("provider"),
                "marketSelection": market.get("selection"),
                "marketProviderCount": market.get("providerCount"),
                "marketHomeMargin": market_margin,
                "marketOpenHomeMargin": market.get("marketOpenHomeMargin"),
                "modelError": model - actual,
                "marketError": market_margin - actual,
                "modelAbsoluteError": abs(model - actual),
                "marketAbsoluteError": abs(market_margin - actual),
                "modelMarketEdge": model - market_margin,
                "actualCoverMargin": actual - market_margin,
            }
        )
    return matched, missing


def _coverage_by_season(
    market_rows: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    matched: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    market_count = {season: 0 for season in MARKET_SEASONS}
    for row in market_rows:
        season = row.get("season")
        if season in market_count:
            market_count[season] += 1

    pred_count: dict[tuple[int, int], int] = {}
    match_count: dict[tuple[int, int], int] = {}
    for row in predictions:
        key = (int(row["season"]), int(row["minGames"]))
        pred_count[key] = pred_count.get(key, 0) + 1
    for row in matched:
        key = (int(row["season"]), int(row["minGames"]))
        match_count[key] = match_count.get(key, 0) + 1

    out: list[dict[str, Any]] = []
    for season in MARKET_SEASONS:
        for min_games in MIN_GAMES_VALUES:
            model_rows = pred_count.get((season, min_games), 0)
            matched_rows = match_count.get((season, min_games), 0)
            out.append(
                {
                    "season": season,
                    "minGames": int(min_games),
                    "marketGamesWithSpread": market_count.get(season, 0),
                    "officialOosModelRows": model_rows,
                    "matchedRows": matched_rows,
                    "marketMatchRate": (
                        matched_rows / model_rows if model_rows else None
                    ),
                    "officialOosSeason": season in TEST_SEASONS,
                }
            )
    return out


def build_benchmark_report(
    snapshot: dict[str, Any],
    *,
    raw_root: Path,
    processed_root: Path,
    fallback_median: bool = True,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    market_rows = normalize_market_games(
        snapshot["games"],
        fallback_median=fallback_median,
    )
    predictions = build_official_oos_predictions(raw_root, processed_root)
    matched, missing = join_predictions_to_market(predictions, market_rows)

    summaries: list[dict[str, Any]] = []
    edge_buckets: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        subset = [row for row in matched if row["minGames"] == min_games]
        summaries.append(
            {
                "scope": "pooled-official-oos",
                "minGames": int(min_games),
                **summarize_matched(subset),
            }
        )
        for season in TEST_SEASONS:
            season_rows = [
                row for row in subset if row["season"] == season
            ]
            summaries.append(
                {
                    "scope": "season",
                    "minGames": int(min_games),
                    "season": int(season),
                    **summarize_matched(season_rows),
                }
            )
        edge_buckets.extend(
            {
                "minGames": int(min_games),
                **row,
            }
            for row in summarize_edge_buckets(subset)
        )

    market_by_selection: dict[str, int] = {}
    for row in market_rows:
        selection = str(row.get("selection"))
        market_by_selection[selection] = market_by_selection.get(selection, 0) + 1

    report = {
        "schemaVersion": 1,
        "benchmarkVersion": BENCHMARK_VERSION,
        "predictionVersion": "prediction-v2-site-aware-srs-hfa-v1",
        "marketSource": snapshot.get("source"),
        "marketSnapshotRetrievedAtUtc": snapshot.get("retrievedAtUtc"),
        "marketSeasonsRequested": list(MARKET_SEASONS),
        "officialModelTestSeasons": list(TEST_SEASONS),
        "excludedModelSeason": 2020,
        "notes": [
            "Market coverage is collected for 2014-2025.",
            "Official Prediction-v2 OOS comparison uses only the locked benchmark test seasons.",
            "2014-2017 market rows are coverage context, not relabeled as official Prediction-v2 holdouts.",
            "2020 is omitted from the historical model corpus by contract.",
            "Positive modelHomeMargin/marketHomeMargin means expected home-team win margin.",
            "ATS accuracy grades the side implied by modelHomeMargin - marketHomeMargin against final actual margin; pushes and zero-edge picks are excluded from ATS decisions.",
        ],
        "marketGamesReturned": len(snapshot["games"]),
        "marketGamesWithUsableSpread": len(market_rows),
        "marketSelectionCounts": dict(sorted(market_by_selection.items())),
        "officialOosPredictionRows": len(predictions),
        "matchedPredictionRows": len(matched),
        "missingMarketRows": len(missing),
        "coverageBySeason": _coverage_by_season(
            market_rows, predictions, matched
        ),
        "summaries": summaries,
        "edgeBuckets": edge_buckets,
        "missingMarketGameIds": sorted(
            {
                str(row["gameId"])
                for row in missing
            }
        ),
    }
    return report, matched


def _write_json(path: Path, payload: Any, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"Output already exists: {path}. Use --overwrite intentionally."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _print_report(report: dict[str, Any]) -> None:
    print("PREDICTION V2 VS CFBD MARKET")
    print(
        f"Market usable spreads: {report['marketGamesWithUsableSpread']} "
        f"/ {report['marketGamesReturned']}"
    )
    print(
        f"Official OOS prediction rows: {report['officialOosPredictionRows']} "
        f"matched={report['matchedPredictionRows']} "
        f"missing_market={report['missingMarketRows']}"
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
            f"ATS={row['atsWins']}-{row['atsLosses']} "
            f"({row['atsAccuracy']:.3%})"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark locked Prediction v2 against historical CFBD market spreads"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    download = sub.add_parser(
        "download",
        help="Snapshot CFBD lines for 2014-2025 using CFBD_API_KEY",
    )
    download.add_argument("--output", type=Path, default=DEFAULT_RAW_LINES)
    download.add_argument("--overwrite", action="store_true")

    evaluate = sub.add_parser(
        "evaluate",
        help="Join locked OOS Prediction-v2 predictions to a saved market snapshot",
    )
    evaluate.add_argument("--lines", type=Path, default=DEFAULT_RAW_LINES)
    evaluate.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    evaluate.add_argument(
        "--processed-root",
        type=Path,
        default=Path("data/processed"),
    )
    evaluate.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    evaluate.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    evaluate.add_argument(
        "--consensus-only",
        action="store_true",
        help="Do not use median provider fallback when CFBD consensus is absent",
    )
    evaluate.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()
    if args.command == "download":
        api_key = os.environ.get("CFBD_API_KEY", "")
        snapshot = download_lines_snapshot(
            args.output,
            api_key=api_key,
            overwrite=args.overwrite,
        )
        print(
            f"Saved {len(snapshot['games'])} raw market games to {args.output}"
        )
        return

    snapshot = load_lines_snapshot(args.lines)
    report, games = build_benchmark_report(
        snapshot,
        raw_root=args.raw_root,
        processed_root=args.processed_root,
        fallback_median=not args.consensus_only,
    )
    _print_report(report)
    _write_json(args.output, report, overwrite=args.overwrite)
    _write_json(args.games_output, games, overwrite=args.overwrite)
    print(f"Report: {args.output}")
    print(f"Matched games: {args.games_output}")


if __name__ == "__main__":
    main()
