"""CLI for raw CFBD acquisition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cfb_analytics.raw.acquire import acquire_season, acquire_week, calendar_partitions, get_calendar
from cfb_analytics.sources.cfbd.client import CfbdClient

DEFAULT_ROOT = Path("data/raw")
SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cfb-raw")
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    sub = p.add_subparsers(dest="command", required=True)

    cal = sub.add_parser("calendar")
    cal.add_argument("--season", type=int, required=True)

    week = sub.add_parser("week")
    week.add_argument("--season", type=int, required=True)
    week.add_argument("--season-type", required=True)
    week.add_argument("--week", type=int, required=True)
    week.add_argument("--refresh", action="store_true")

    season = sub.add_parser("season")
    season.add_argument("--season", type=int, required=True)
    season.add_argument("--refresh", action="store_true")

    backfill = sub.add_parser("backfill")
    backfill.add_argument("--refresh", action="store_true")
    return p


def main() -> None:
    args = parser().parse_args()
    with CfbdClient() as client:
        if args.command == "calendar":
            calendar = get_calendar(client, args.season)
            print(json.dumps({"season": args.season, "partitions": calendar_partitions(calendar)}, indent=2))
            return
        if args.command == "week":
            manifests = acquire_week(client, args.root, args.season, args.season_type, args.week, refresh=args.refresh)
        elif args.command == "season":
            manifests = acquire_season(client, args.root, args.season, refresh=args.refresh)
        else:
            manifests = []
            for season in SEASONS:
                manifests.extend(acquire_season(client, args.root, season, refresh=args.refresh))
        for manifest in manifests:
            print(f"{manifest['season']} {manifest['season_type']} W{manifest['week']:02d} {manifest['entity']}: {manifest['record_count']}")


if __name__ == "__main__":
    main()
