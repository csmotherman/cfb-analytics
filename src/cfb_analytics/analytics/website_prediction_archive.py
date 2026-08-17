"""Export the supported 2014-2025 historical slate for the focused prediction website.

The website archive is deliberately truthful:
- every game that can be reconstructed from canonical historical data is exported;
- the COVID-disrupted 2020 season is intentionally omitted from the comparable archive;
- market spreads are attached from the frozen CFBD historical reference snapshot when available;
- a model pick is attached only when a stored historical OOS Prediction-v2 row exists;
- recommended bets come only from the previously selected FULL ATS logistic min3/.575 baseline;
- no later result is used to manufacture a missing prediction or recommendation.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from cfb_analytics.canonical.materialize import canonical_partition_dir
from cfb_analytics.derived.pregame import game_contexts
from cfb_analytics.raw.audit import discover_partitions

ARCHIVE_VERSION = "website-prediction-archive-v2"
ARCHIVE_SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)
DEFAULT_BENCHMARK = Path("data/processed/market_benchmark/prediction-v2-vs-clean-market-games.json")
DEFAULT_MARKET_LINES = Path("data/raw/market_lines/cfbd-market-spreads-2014-2025.json")
DEFAULT_RECOMMENDED_BETS = Path("data/processed/market_benchmark/full-ats-meta-gate-games.json")
DEFAULT_FALLBACK_BETS = Path("data/processed/market_benchmark/ats-logistic-deep-audit-games.json")
DEFAULT_OUTPUT_ROOT = Path("data/processed/website/prediction_archive")
MIN_GAMES = 3
RECOMMENDED_THRESHOLD = 0.575
WIN_PAYOUT_PER_UNIT_RISKED_MINUS_110 = 100.0 / 110.0


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _sign(value: float, tol: float = 1e-12) -> int:
    if value > tol:
        return 1
    if value < -tol:
        return -1
    return 0


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_oos_predictions(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = _read_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Expected list in historical benchmark games: {path}")
    out: dict[str, dict[str, Any]] = {}
    for row in payload:
        if not isinstance(row, dict) or int(row.get("minGames", -1)) != MIN_GAMES:
            continue
        gid = row.get("gameId")
        if gid is None or not _finite(row.get("modelHomeMargin")):
            continue
        key = str(gid)
        if key in out:
            raise ValueError(f"Duplicate min{MIN_GAMES} historical model row for gameId {key}")
        out[key] = row
    return out


def load_market_spreads(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = _read_json(path)
    if not isinstance(payload, dict) or not isinstance(payload.get("games"), list):
        raise ValueError(f"Invalid market spread snapshot: {path}")
    out: dict[str, dict[str, Any]] = {}
    for row in payload["games"]:
        if not isinstance(row, dict) or row.get("gameId") is None or not _finite(row.get("marketSpread")):
            continue
        key = str(row["gameId"])
        if key in out:
            raise ValueError(f"Duplicate market gameId {key}")
        out[key] = row
    return out


def load_recommended_bets(primary: Path, fallback: Path) -> tuple[dict[str, dict[str, Any]], str | None]:
    """Load the selected FULL ATS logistic min3/.575 historical recommendations.

    Prefer the FULL_BASELINE rows emitted by the meta-gate audit because they are
    already the exact 495 selected candidate bets. Fall back to the earlier deep
    audit and apply the frozen .575 confidence rule without tuning anything.
    """
    source = primary if primary.exists() else fallback if fallback.exists() else None
    if source is None:
        return {}, None
    payload = _read_json(source)
    if not isinstance(payload, list):
        raise ValueError(f"Expected list in recommended-bet source: {source}")

    out: dict[str, dict[str, Any]] = {}
    using_meta_gate = source == primary
    for row in payload:
        if not isinstance(row, dict) or int(row.get("minGames", -1)) != MIN_GAMES:
            continue
        if using_meta_gate:
            selected = row.get("variant") == "FULL_BASELINE"
        else:
            selected = (
                row.get("variant") == "FULL"
                and _finite(row.get("confidence"))
                and float(row["confidence"]) + 1e-12 >= RECOMMENDED_THRESHOLD
            )
        if not selected or row.get("gameId") is None:
            continue
        key = str(row["gameId"])
        if key in out:
            raise ValueError(f"Duplicate recommended bet for gameId {key}")
        out[key] = row
    return out, str(source)


def game_partition_map(raw_root: Path, processed_root: Path, season: int) -> dict[str, tuple[str, int]]:
    out: dict[str, tuple[str, int]] = {}
    for season_type, week in discover_partitions(raw_root, season):
        plays_path = canonical_partition_dir(processed_root, season, season_type, week) / "plays.json"
        if not plays_path.exists():
            continue
        rows = _read_json(plays_path)
        if not isinstance(rows, list):
            continue
        for play in rows:
            if not isinstance(play, dict) or play.get("gameId") is None:
                continue
            gid = str(play["gameId"])
            current = out.get(gid)
            value = (str(season_type), int(week))
            if current is not None and current != value:
                raise ValueError(f"Game {gid} appears in multiple historical partitions: {current} vs {value}")
            out[gid] = value
    return out


def _validate_identity(game_id: str, home: str, away: str, row: dict[str, Any] | None, label: str) -> None:
    if row is None:
        return
    row_home = row.get("homeTeam")
    row_away = row.get("awayTeam")
    if (row_home and str(row_home) != home) or (row_away and str(row_away) != away):
        raise ValueError(
            f"{label} identity mismatch for {game_id}: archive={away}@{home} "
            f"source={row_away}@{row_home}"
        )


def archive_record(
    *,
    season: int,
    season_type: str,
    week: int,
    game_id: str,
    context: dict[str, Any],
    prediction: dict[str, Any] | None,
    market: dict[str, Any] | None = None,
    recommended_bet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    home = str(context["homeTeam"])
    away = str(context["awayTeam"])
    home_score = float(context["homeScore"])
    away_score = float(context["awayScore"])
    actual_margin = home_score - away_score

    _validate_identity(game_id, home, away, prediction, "Prediction")
    _validate_identity(game_id, home, away, market, "Market")
    _validate_identity(game_id, home, away, recommended_bet, "Recommended-bet")

    market_margin: float | None = None
    market_provider: str | None = None
    if market is not None and _finite(market.get("marketSpread")):
        market_margin = float(market["marketSpread"])
        market_provider = str(market.get("provider") or "") or None
    elif prediction is not None and _finite(prediction.get("marketHomeMargin")):
        market_margin = float(prediction["marketHomeMargin"])
        market_provider = str(prediction.get("marketProvider") or "") or None

    record: dict[str, Any] = {
        "id": game_id,
        "season": int(season),
        "week": int(week),
        "seasonType": season_type,
        "homeTeam": home,
        "awayTeam": away,
        "actualHomeScore": int(home_score) if home_score.is_integer() else home_score,
        "actualAwayScore": int(away_score) if away_score.is_integer() else away_score,
        "actualHomeMargin": actual_margin,
        "marketHomeMargin": market_margin,
        "marketProvider": market_provider,
        "evidenceStatus": "historical-slate",
        "recommendedBet": recommended_bet is not None,
    }

    if prediction is not None:
        model_margin = float(prediction["modelHomeMargin"])
        model_sign = _sign(model_margin)
        actual_sign = _sign(actual_margin)
        winner_correct = None if model_sign == 0 or actual_sign == 0 else model_sign == actual_sign
        record.update(
            {
                "modelHomeMargin": model_margin,
                "predictedWinner": home if model_sign >= 0 else away,
                "winnerCorrect": winner_correct,
                "correct": winner_correct,
                "modelAbsoluteError": abs(model_margin - actual_margin),
                "evidenceStatus": "official-oos",
            }
        )

        if market_margin is not None:
            model_ats_pick = _sign(model_margin - market_margin)
            actual_cover = _sign(actual_margin - market_margin)
            ats_result = (
                "PUSH"
                if model_ats_pick == 0 or actual_cover == 0
                else "WIN" if model_ats_pick == actual_cover else "LOSS"
            )
            record.update(
                {
                    "modelAtsSide": None if model_ats_pick == 0 else ("HOME" if model_ats_pick > 0 else "AWAY"),
                    "atsCorrect": None if ats_result == "PUSH" else ats_result == "WIN",
                    "atsResult": ats_result,
                }
            )

    if recommended_bet is not None:
        picked = str(recommended_bet.get("pickedSide") or "").upper()
        result = str(recommended_bet.get("result") or "").upper()
        record.update(
            {
                "recommendedBetSide": picked if picked in {"HOME", "AWAY"} else None,
                "recommendedBetTeam": home if picked == "HOME" else away if picked == "AWAY" else None,
                "recommendedBetConfidence": (
                    float(recommended_bet["confidence"])
                    if _finite(recommended_bet.get("confidence"))
                    else None
                ),
                "recommendedBetResult": result if result in {"WIN", "LOSS", "PUSH"} else None,
            }
        )
    return record


def summarize_week(games: list[dict[str, Any]], *, recommended_source_present: bool) -> dict[str, Any]:
    model_games = [row for row in games if _finite(row.get("modelHomeMargin"))]
    winner_graded = [row for row in model_games if isinstance(row.get("winnerCorrect"), bool)]
    ats_games = [row for row in model_games if row.get("atsResult") in {"WIN", "LOSS", "PUSH"}]
    recommended = [row for row in games if row.get("recommendedBet") is True]

    ats_wins = sum(row.get("atsResult") == "WIN" for row in ats_games)
    ats_losses = sum(row.get("atsResult") == "LOSS" for row in ats_games)
    ats_pushes = sum(row.get("atsResult") == "PUSH" for row in ats_games)
    ats_decisions = ats_wins + ats_losses

    bet_wins = sum(row.get("recommendedBetResult") == "WIN" for row in recommended)
    bet_losses = sum(row.get("recommendedBetResult") == "LOSS" for row in recommended)
    bet_pushes = sum(row.get("recommendedBetResult") == "PUSH" for row in recommended)
    units = bet_wins * WIN_PAYOUT_PER_UNIT_RISKED_MINUS_110 - bet_losses

    return {
        "games": len(games),
        "modelGames": len(model_games),
        "marketGames": sum(_finite(row.get("marketHomeMargin")) for row in games),
        "modelMae": (
            sum(float(row["modelAbsoluteError"]) for row in model_games) / len(model_games)
            if model_games
            else None
        ),
        "winnerWins": sum(row.get("winnerCorrect") is True for row in winner_graded),
        "winnerLosses": sum(row.get("winnerCorrect") is False for row in winner_graded),
        "winnerAccuracy": (
            sum(row.get("winnerCorrect") is True for row in winner_graded) / len(winner_graded)
            if winner_graded
            else None
        ),
        "atsWins": ats_wins,
        "atsLosses": ats_losses,
        "atsPushes": ats_pushes,
        "atsAccuracy": ats_wins / ats_decisions if ats_decisions else None,
        "recommendedBetSourcePresent": recommended_source_present,
        "recommendedBets": len(recommended),
        "recommendedBetWins": bet_wins,
        "recommendedBetLosses": bet_losses,
        "recommendedBetPushes": bet_pushes,
        "recommendedBetUnits": units if recommended_source_present else None,
        "unitsConvention": "flat 1u risk at -110; win=+0.9091u loss=-1u push=0u",
    }


def export_archive(
    raw_root: Path,
    processed_root: Path,
    benchmark_path: Path,
    market_lines_path: Path,
    recommended_bets_path: Path,
    fallback_bets_path: Path,
    output_root: Path,
    *,
    overwrite: bool,
) -> dict[str, Any]:
    predictions = load_oos_predictions(benchmark_path)
    market = load_market_spreads(market_lines_path)
    recommended_bets, recommended_source = load_recommended_bets(recommended_bets_path, fallback_bets_path)
    season_summaries: list[dict[str, Any]] = []
    total_games = 0
    total_model_games = 0

    for season in ARCHIVE_SEASONS:
        contexts = game_contexts(raw_root, processed_root, season)
        partitions = game_partition_map(raw_root, processed_root, season)
        grouped: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
        missing_partition = 0

        for gid, context in contexts.items():
            partition = partitions.get(str(gid))
            if partition is None:
                missing_partition += 1
                continue
            season_type, week = partition
            prediction = predictions.get(str(gid))
            record = archive_record(
                season=season,
                season_type=season_type,
                week=week,
                game_id=str(gid),
                context=context,
                prediction=prediction,
                market=market.get(str(gid)),
                recommended_bet=recommended_bets.get(str(gid)),
            )
            grouped[week].append(record)
            total_games += 1
            total_model_games += int(prediction is not None)

        for week, games in sorted(grouped.items()):
            games.sort(key=lambda row: (str(row["homeTeam"]), str(row["awayTeam"]), str(row["id"])))
            destination = output_root / f"season={season}" / f"week={week}.json"
            if destination.exists() and not overwrite:
                raise FileExistsError(f"Archive output exists: {destination}; use --overwrite intentionally")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(
                    {
                        "schemaVersion": 2,
                        "archiveVersion": ARCHIVE_VERSION,
                        "season": season,
                        "week": week,
                        "label": f"{season} Week {week}",
                        "summary": summarize_week(games, recommended_source_present=recommended_source is not None),
                        "games": games,
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )

        season_summaries.append(
            {
                "season": season,
                "weeks": len(grouped),
                "games": sum(len(games) for games in grouped.values()),
                "marketGames": sum(
                    _finite(row.get("marketHomeMargin"))
                    for games in grouped.values()
                    for row in games
                ),
                "officialOosModelGames": sum(
                    row.get("evidenceStatus") == "official-oos"
                    for games in grouped.values()
                    for row in games
                ),
                "recommendedBets": sum(
                    row.get("recommendedBet") is True
                    for games in grouped.values()
                    for row in games
                ),
                "missingPartition": missing_partition,
            }
        )

    return {
        "version": ARCHIVE_VERSION,
        "seasons": list(ARCHIVE_SEASONS),
        "games": total_games,
        "officialOosModelGames": total_model_games,
        "benchmarkSourcePresent": benchmark_path.exists(),
        "marketSourcePresent": market_lines_path.exists(),
        "marketRows": len(market),
        "recommendedBetSource": recommended_source,
        "recommendedBets": len(recommended_bets),
        "seasonSummaries": season_summaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export week-by-week historical website archive")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--market-lines", type=Path, default=DEFAULT_MARKET_LINES)
    parser.add_argument("--recommended-bets", type=Path, default=DEFAULT_RECOMMENDED_BETS)
    parser.add_argument("--fallback-bets", type=Path, default=DEFAULT_FALLBACK_BETS)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report = export_archive(
        args.raw_root,
        args.processed_root,
        args.benchmark,
        args.market_lines,
        args.recommended_bets,
        args.fallback_bets,
        args.output_root,
        overwrite=args.overwrite,
    )
    print("WEBSITE PREDICTION ARCHIVE: BUILT")
    print(f"Version: {report['version']}")
    print(f"Historical games: {report['games']:,}")
    print(f"Official OOS model games attached: {report['officialOosModelGames']:,}")
    print(f"Market rows available: {report['marketRows']:,}")
    print(f"Recommended bets attached: {report['recommendedBets']:,}")
    print(f"Recommended-bet source: {report['recommendedBetSource'] or 'MISSING'}")
    for row in report["seasonSummaries"]:
        print(
            f" {row['season']}: weeks={row['weeks']:2d} games={row['games']:4d} "
            f"market={row['marketGames']:4d} model={row['officialOosModelGames']:4d} "
            f"bets={row['recommendedBets']:3d} missing_partition={row['missingPartition']}"
        )
    print(f"Archive root: {args.output_root}")


if __name__ == "__main__":
    main()
