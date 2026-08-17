"""Export the 2014-2025 historical slate for the focused prediction website.

The website archive is deliberately truthful:
- every game that can be reconstructed from canonical historical data is exported;
- a model pick is attached only when a stored historical OOS Prediction-v2 row exists;
- seasons/weeks without a supported model prediction remain historical-slate entries;
- no later result is used to manufacture a missing prediction or explanation.

This lets the website browse every available season/week while preserving the
scientific meaning of the model record.
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

ARCHIVE_VERSION = "website-prediction-archive-v1"
ARCHIVE_SEASONS = tuple(range(2014, 2026))
DEFAULT_BENCHMARK = Path("data/processed/market_benchmark/prediction-v2-vs-clean-market-games.json")
DEFAULT_OUTPUT_ROOT = Path("data/processed/website/prediction_archive")
MIN_GAMES = 3


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _sign(value: float, tol: float = 1e-12) -> int:
    if value > tol:
        return 1
    if value < -tol:
        return -1
    return 0


def load_oos_predictions(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text())
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


def game_partition_map(raw_root: Path, processed_root: Path, season: int) -> dict[str, tuple[str, int]]:
    out: dict[str, tuple[str, int]] = {}
    for season_type, week in discover_partitions(raw_root, season):
        plays_path = canonical_partition_dir(processed_root, season, season_type, week) / "plays.json"
        if not plays_path.exists():
            continue
        rows = json.loads(plays_path.read_text())
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


def archive_record(
    *,
    season: int,
    season_type: str,
    week: int,
    game_id: str,
    context: dict[str, Any],
    prediction: dict[str, Any] | None,
) -> dict[str, Any]:
    home = str(context["homeTeam"])
    away = str(context["awayTeam"])
    home_score = float(context["homeScore"])
    away_score = float(context["awayScore"])
    actual_margin = home_score - away_score
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
        "evidenceStatus": "historical-slate",
    }

    if prediction is not None:
        pred_home = prediction.get("homeTeam")
        pred_away = prediction.get("awayTeam")
        if pred_home and str(pred_home) != home or pred_away and str(pred_away) != away:
            raise ValueError(
                f"Historical prediction identity mismatch for {game_id}: "
                f"archive={away}@{home} prediction={pred_away}@{pred_home}"
            )
        model_margin = float(prediction["modelHomeMargin"])
        model_sign = _sign(model_margin)
        actual_sign = _sign(actual_margin)
        record.update(
            {
                "modelHomeMargin": model_margin,
                "predictedWinner": home if model_sign >= 0 else away,
                "correct": None if model_sign == 0 or actual_sign == 0 else model_sign == actual_sign,
                "evidenceStatus": "official-oos",
            }
        )
    return record


def export_archive(
    raw_root: Path,
    processed_root: Path,
    benchmark_path: Path,
    output_root: Path,
    *,
    overwrite: bool,
) -> dict[str, Any]:
    predictions = load_oos_predictions(benchmark_path)
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
            )
            grouped[week].append(record)
            total_games += 1
            total_model_games += int(prediction is not None)

        for week, games in sorted(grouped.items()):
            games.sort(key=lambda row: (str(row["awayTeam"]), str(row["homeTeam"]), str(row["id"])))
            destination = output_root / f"season={season}" / f"week={week}.json"
            if destination.exists() and not overwrite:
                raise FileExistsError(f"Archive output exists: {destination}; use --overwrite intentionally")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "archiveVersion": ARCHIVE_VERSION,
                        "season": season,
                        "week": week,
                        "label": f"{season} Week {week}",
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
                "officialOosModelGames": sum(
                    row.get("evidenceStatus") == "official-oos"
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
        "seasonSummaries": season_summaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export week-by-week historical website archive")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report = export_archive(
        args.raw_root,
        args.processed_root,
        args.benchmark,
        args.output_root,
        overwrite=args.overwrite,
    )
    print("WEBSITE PREDICTION ARCHIVE: BUILT")
    print(f"Version: {report['version']}")
    print(f"Historical games: {report['games']:,}")
    print(f"Official OOS model games attached: {report['officialOosModelGames']:,}")
    print(f"Benchmark source present: {report['benchmarkSourcePresent']}")
    for row in report["seasonSummaries"]:
        print(
            f" {row['season']}: weeks={row['weeks']:2d} games={row['games']:4d} "
            f"model={row['officialOosModelGames']:4d} missing_partition={row['missingPartition']}"
        )
    print(f"Archive root: {args.output_root}")


if __name__ == "__main__":
    main()
