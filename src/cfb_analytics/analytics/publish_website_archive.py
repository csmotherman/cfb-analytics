"""Publish the validated archive and Beat the Model website data.

The historical model/market artifacts remain an internal accountability layer.
The consumer product generated from them is Beat the Model: weekly power rankings,
a deterministic Official 15 slate, and a current play dataset where users pick
before seeing The Model's answer.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.beat_the_model import publish_beat_the_model
from cfb_analytics.analytics.website_prediction_archive import (
    ARCHIVE_SEASONS,
    DEFAULT_BENCHMARK,
    DEFAULT_FALLBACK_BETS,
    DEFAULT_MARKET_LINES,
    DEFAULT_RECOMMENDED_BETS,
    export_archive,
)

EXPECTED_HISTORICAL_GAMES = 8_510
EXPECTED_STORED_MATURE_OOS_MODEL_GAMES = 3_977
EXPECTED_CLEAN_MARKET_ROWS = 12_666
EXPECTED_RECOMMENDED_BETS = 495


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolved(root: Path, relative: Path) -> Path:
    return relative if relative.is_absolute() else root / relative


def _clean_generated_seasons(output_root: Path) -> None:
    if output_root.exists():
        for season in ARCHIVE_SEASONS:
            directory = output_root / f"season={season}"
            if directory.exists():
                shutil.rmtree(directory)
        for name in ("index.json", "missing-market-lines.json"):
            path = output_root / name
            if path.exists():
                path.unlink()

    btm_root = output_root.parent / "beat-the-model"
    if btm_root.exists():
        shutil.rmtree(btm_root)


def _week_files(output_root: Path, season: int) -> list[Path]:
    directory = output_root / f"season={season}"
    if not directory.exists():
        return []
    return sorted(
        directory.glob("week=*.json"),
        key=lambda path: int(path.stem.split("=", 1)[1]),
    )


def _validate_prediction_counts(report: dict[str, Any]) -> None:
    mature = int(report.get("matureOosModelGames", -1))
    early_generated = int(report.get("earlyPriorGeneratedGames", -1))
    early_overlap = int(report.get("earlyPriorOverlapGames", -1))
    early_supplement = int(report.get("earlyPriorSupplementGames", -1))
    combined = int(report.get("combinedOosModelGames", -1))
    attached = int(report.get("officialOosModelGames", -1))

    if mature != EXPECTED_STORED_MATURE_OOS_MODEL_GAMES:
        raise ValueError(
            "Stored mature Prediction-v2 benchmark changed: expected "
            f"{EXPECTED_STORED_MATURE_OOS_MODEL_GAMES:,}, got {mature:,}"
        )
    if early_generated <= 0:
        raise ValueError("Refusing archive publish without reconstructed early-prior OOS predictions")
    if early_overlap < 0 or early_supplement <= 0:
        raise ValueError("Early-prior reconstruction did not fill any previously blank mature OOS games")
    if early_overlap + early_supplement != early_generated:
        raise ValueError("Early-prior accounting mismatch: generated rows must equal overlap + supplement")
    if combined != mature + early_supplement:
        raise ValueError("Combined OOS accounting mismatch: combined must equal mature + early supplement")
    if attached != combined:
        raise ValueError(f"Rendered OOS model count mismatch: combined={combined:,} attached={attached:,}")

    season_rows = {
        int(row.get("season", -1)): row
        for row in report.get("seasonSummaries", [])
        if isinstance(row, dict)
    }
    if int(season_rows.get(2025, {}).get("earlyPriorModelGames", 0)) <= 0:
        raise ValueError(
            "2025 early-prior supplement is empty; Week 1 should not remain limited to the mature minGames=3 benchmark"
        )


def _validate_and_manifest(output_root: Path, report: dict[str, Any]) -> dict[str, Any]:
    if int(report["games"]) != EXPECTED_HISTORICAL_GAMES:
        raise ValueError(
            f"Refusing partial website archive: expected {EXPECTED_HISTORICAL_GAMES:,} "
            f"historical games, got {int(report['games']):,}"
        )
    _validate_prediction_counts(report)
    if not report.get("marketSourcePresent"):
        raise ValueError("Refusing archive publish without the frozen clean CFBD market-spread source")
    if int(report["marketRows"]) != EXPECTED_CLEAN_MARKET_ROWS:
        raise ValueError(
            f"Unexpected clean market snapshot size: expected {EXPECTED_CLEAN_MARKET_ROWS:,}, "
            f"got {int(report['marketRows']):,}"
        )
    if int(report["recommendedBets"]) != EXPECTED_RECOMMENDED_BETS:
        raise ValueError(
            f"Refusing archive publish without the selected historical bet set: expected "
            f"{EXPECTED_RECOMMENDED_BETS} recommendations, got {int(report['recommendedBets'])}"
        )

    missing_market: list[dict[str, Any]] = []
    manifest_seasons: list[dict[str, Any]] = []
    rendered_games = 0

    for season in ARCHIVE_SEASONS:
        weeks: list[int] = []
        season_games = 0
        season_market = 0
        season_model = 0
        season_early = 0
        for file in _week_files(output_root, season):
            payload = json.loads(file.read_text())
            week = int(payload["week"])
            games = payload.get("games", [])
            if not isinstance(games, list):
                raise ValueError(f"Invalid games payload in {file}")
            weeks.append(week)
            season_games += len(games)
            for game in games:
                if not isinstance(game, dict):
                    continue
                if isinstance(game.get("marketHomeMargin"), (int, float)):
                    season_market += 1
                else:
                    missing_market.append(
                        {
                            "season": season,
                            "week": week,
                            "gameId": str(game.get("id")),
                            "homeTeam": game.get("homeTeam"),
                            "awayTeam": game.get("awayTeam"),
                        }
                    )
                if isinstance(game.get("modelHomeMargin"), (int, float)):
                    season_model += 1
                if game.get("predictionSource") == "prediction-v2-early-prior-walk-forward-oos":
                    season_early += 1
        rendered_games += season_games
        manifest_seasons.append(
            {
                "season": season,
                "weeks": weeks,
                "games": season_games,
                "marketGames": season_market,
                "modelGames": season_model,
                "earlyPriorModelGames": season_early,
            }
        )

    if rendered_games != EXPECTED_HISTORICAL_GAMES:
        raise ValueError(
            f"Published JSON row count mismatch: expected {EXPECTED_HISTORICAL_GAMES:,}, "
            f"found {rendered_games:,}"
        )

    market_attached = rendered_games - len(missing_market)
    manifest = {
        "schemaVersion": 3,
        "archiveVersion": report["version"],
        "seasons": manifest_seasons,
        "historicalGames": rendered_games,
        "marketGames": market_attached,
        "missingMarketGames": len(missing_market),
        "storedMatureOosModelGames": int(report["matureOosModelGames"]),
        "earlyPriorGeneratedGames": int(report["earlyPriorGeneratedGames"]),
        "earlyPriorOverlapGames": int(report["earlyPriorOverlapGames"]),
        "earlyPriorSupplementGames": int(report["earlyPriorSupplementGames"]),
        "officialOosModelGames": int(report["officialOosModelGames"]),
        "recommendedBets": int(report["recommendedBets"]),
        "marketSemantics": "internal historical CFBD reference spread; retained for audit, not surfaced by Beat the Model",
        "predictionSemantics": (
            "stored mature minGames=3 Prediction-v2 OOS calls, supplemented only when missing by the frozen "
            "early-prior rule reconstructed with earlier-season-only training"
        ),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "index.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (output_root / "missing-market-lines.json").write_text(json.dumps(missing_market, indent=2, sort_keys=True) + "\n")
    return manifest


def publish(*, output_root: Path, clean: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    root = project_root()
    raw_root = root / "data" / "raw"
    processed_root = root / "data" / "processed"
    benchmark = _resolved(root, DEFAULT_BENCHMARK)
    market_lines = _resolved(root, DEFAULT_MARKET_LINES)
    recommended_bets = _resolved(root, DEFAULT_RECOMMENDED_BETS)
    fallback_bets = _resolved(root, DEFAULT_FALLBACK_BETS)

    for label, path in (
        ("Prediction-v2 benchmark games", benchmark),
        ("clean CFBD market spread snapshot", market_lines),
    ):
        if not path.exists():
            raise FileNotFoundError(f"Missing {label}: {path}")
    if not recommended_bets.exists() and not fallback_bets.exists():
        raise FileNotFoundError(
            "Missing historical recommended-bet source. Build either "
            f"{recommended_bets} or {fallback_bets} first."
        )

    if clean:
        _clean_generated_seasons(output_root)

    report = export_archive(
        raw_root,
        processed_root,
        benchmark,
        market_lines,
        recommended_bets,
        fallback_bets,
        output_root,
        overwrite=True,
    )
    manifest = _validate_and_manifest(output_root, report)

    website_data_root = output_root.parent
    btm_report = publish_beat_the_model(
        raw_root=raw_root,
        processed_root=processed_root,
        archive_root=output_root,
        website_data_root=website_data_root,
        target_season=2026,
    )
    manifest["beatTheModel"] = btm_report
    (output_root / "index.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return report, manifest


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Publish the historical archive and Beat the Model website data")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=root / "website" / "data" / "archive",
        help="Deployable archive directory (default: website/data/archive)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not remove previously generated archive/Beat the Model data before publishing",
    )
    args = parser.parse_args()

    report, manifest = publish(output_root=args.output_root, clean=not args.no_clean)
    btm = manifest["beatTheModel"]

    print("BEAT THE MODEL WEBSITE DATA: PUBLISHED")
    print(f"Historical games retained for audit: {manifest['historicalGames']:,}")
    print(f"Combined historical OOS model calls: {manifest['officialOosModelGames']:,}")
    print(f"Historical BTM slates generated: {btm['historicalSlates']:,}")
    print(f"Historical BTM games selected: {btm['historicalSelectedGames']:,}")
    print(f"2026 Week 1 teams ranked from 2025 final ratings: {btm['currentRankedTeams']:,}")
    print(f"2026 Week 1 Official 15 games currently published: {btm['currentSlateGames']:,}")
    print(f"Current game status: {btm['currentStatus']}")
    print(f"Output: {args.output_root.parent}")
    print("Internal audit sources remain preserved; market/ATS data is not part of the public Beat the Model UI.")
    if manifest["missingMarketGames"]:
        print(f"Internal missing-line audit: {args.output_root / 'missing-market-lines.json'}")
    if report.get("recommendedBetSource"):
        print(f"Internal historical audit source: {report['recommendedBetSource']}")


if __name__ == "__main__":
    main()
