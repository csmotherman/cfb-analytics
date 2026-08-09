from __future__ import annotations

import argparse

from cfb_analytics.clean.drives import clean_drives
from cfb_analytics.clean.games import clean_games
from cfb_analytics.clean.plays import clean_plays
from cfb_analytics.config import SETTINGS
from cfb_analytics.io import read_parquet, write_parquet
from cfb_analytics.validate.drives import validate_drives
from cfb_analytics.validate.games import validate_games
from cfb_analytics.validate.plays import validate_plays
from cfb_analytics.validate.relations import validate_relations


def build_clean_season(season: int) -> None:
    raw_dir = SETTINGS.raw_dir(season)
    clean_dir = SETTINGS.clean_dir(season)

    games = clean_games(read_parquet(raw_dir / "games.parquet"))
    drives = clean_drives(read_parquet(raw_dir / "drives.parquet"))
    plays = clean_plays(read_parquet(raw_dir / "plays.parquet"))

    reports = [
        validate_games(games),
        validate_drives(drives),
        validate_plays(plays),
        validate_relations(games, drives, plays),
    ]
    for report in reports:
        report.raise_for_errors()
        for warning in report.warnings:
            print(f"WARNING: {warning}")

    write_parquet(games, clean_dir / "games.parquet")
    write_parquet(drives, clean_dir / "drives.parquet")
    write_parquet(plays, clean_dir / "plays.parquet")

    print(f"Validated and saved clean season {season}")
    print(f"games={len(games):,} drives={len(drives):,} plays={len(plays):,}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, required=True)
    args = parser.parse_args()
    build_clean_season(args.season)


if __name__ == "__main__":
    main()
