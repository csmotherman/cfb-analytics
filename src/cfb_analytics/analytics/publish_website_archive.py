"""Publish the validated historical archive directly into the deployable website.

This is intentionally a packaging step, not a new model experiment. It consumes
existing frozen/local artifacts, validates the expected historical universe, and
writes the static JSON files used by the Next.js archive.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.website_prediction_archive import (
    ARCHIVE_SEASONS,
    DEFAULT_BENCHMARK,
    DEFAULT_FALLBACK_BETS,
    DEFAULT_MARKET_LINES,
    DEFAULT_RECOMMENDED_BETS,
    export_archive,
)

EXPECTED_HISTORICAL_GAMES = 8_510
EXPECTED_OFFICIAL_OOS_MODEL_GAMES = 3_977
EXPECTED_CLEAN_MARKET_ROWS = 12_666
EXPECTED_RECOMMENDED_BETS = 495


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolved(root: Path, relative: Path) -> Path:
    return relative if relative.is_absolute() else root / relative


def _clean_generated_seasons(output_root: Path) -> None:
    if not output_root.exists():
        return
    for season in ARCHIVE_SEASONS:
        directory = output_root / f"season={season}"
        if directory.exists():
            shutil.rmtree(directory)
    for name in ("index.json", "missing-market-lines.json"):
        path = output_root / name
        if path.exists():
            path.unlink()


def _week_files(output_root: Path, season: int) -> list[Path]:
    directory = output_root / f"season={season}"
    if not directory.exists():
        return []
    return sorted(
        directory.glob("week=*.json"),
        key=lambda path: int(path.stem.split("=", 1)[1]),
    )


def _validate_and_manifest(output_root: Path, report: dict[str, Any]) -> dict[str, Any]:
    if int(report["games"]) != EXPECTED_HISTORICAL_GAMES:
        raise ValueError(
            f"Refusing partial website archive: expected {EXPECTED_HISTORICAL_GAMES:,} "
            f"historical games, got {int(report['games']):,}"
        )
    if int(report["officialOosModelGames"]) != EXPECTED_OFFICIAL_OOS_MODEL_GAMES:
        raise ValueError(
            f"Refusing model-incomplete website archive: expected "
            f"{EXPECTED_OFFICIAL_OOS_MODEL_GAMES:,} official OOS model games, "
            f"got {int(report['officialOosModelGames']):,}"
        )
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
        rendered_games += season_games
        manifest_seasons.append(
            {
                "season": season,
                "weeks": weeks,
                "games": season_games,
                "marketGames": season_market,
                "modelGames": season_model,
            }
        )

    if rendered_games != EXPECTED_HISTORICAL_GAMES:
        raise ValueError(
            f"Published JSON row count mismatch: expected {EXPECTED_HISTORICAL_GAMES:,}, "
            f"found {rendered_games:,}"
        )

    market_attached = rendered_games - len(missing_market)
    manifest = {
        "schemaVersion": 1,
        "archiveVersion": report["version"],
        "seasons": manifest_seasons,
        "historicalGames": rendered_games,
        "marketGames": market_attached,
        "missingMarketGames": len(missing_market),
        "officialOosModelGames": int(report["officialOosModelGames"]),
        "recommendedBets": int(report["recommendedBets"]),
        "marketSemantics": "historical CFBD reference spread; first parseable formattedSpread provider in API order",
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "index.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (output_root / "missing-market-lines.json").write_text(
        json.dumps(missing_market, indent=2, sort_keys=True) + "\n"
    )
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
    return report, manifest


def main() -> None:
    root = project_root()
    parser = argparse.ArgumentParser(description="Publish the complete historical archive into website/data/archive")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=root / "website" / "data" / "archive",
        help="Deployable archive directory (default: website/data/archive)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not remove previously generated season directories before publishing",
    )
    args = parser.parse_args()

    report, manifest = publish(output_root=args.output_root, clean=not args.no_clean)
    print("WEBSITE ARCHIVE: PUBLISHED")
    print(f"Historical games: {manifest['historicalGames']:,}")
    print(f"Market spreads populated: {manifest['marketGames']:,}/{manifest['historicalGames']:,}")
    print(f"Missing source market lines: {manifest['missingMarketGames']:,}")
    print(f"Official OOS model calls: {manifest['officialOosModelGames']:,}")
    print(f"Recommended bets: {manifest['recommendedBets']:,}")
    print(f"Bet source: {report['recommendedBetSource']}")
    print(f"Output: {args.output_root}")
    if manifest["missingMarketGames"]:
        print(f"Missing-line audit: {args.output_root / 'missing-market-lines.json'}")


if __name__ == "__main__":
    main()
