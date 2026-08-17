"""Download one clean CFBD market spread per game across historical seasons.

Spread convention used by this project:
    positive -> home team favored by that many points
    negative -> away team favored by that many points

Selection intentionally mirrors the manually verified historical getter: walk
CFBD's ``lines`` list in provider order and use the first ``formattedSpread``
that can be parsed against the listed home/away teams.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

BASE_URL = "https://api.collegefootballdata.com/lines"
DEFAULT_START_YEAR = 2014
DEFAULT_END_YEAR = 2025
SEASON_TYPES = ("regular", "postseason")
DEFAULT_JSON = Path("data/raw/market_lines/cfbd-market-spreads-2014-2025.json")
DEFAULT_CSV = Path("data/raw/market_lines/cfbd-market-spreads-2014-2025.csv")
SNAPSHOT_VERSION = "cfbd-market-first-formatted-v1"


def parse_spread_text(spread_text: Any, home: Any, away: Any) -> float | None:
    """Convert CFBD ``formattedSpread`` to signed home-based market margin.

    Examples:
        home="Michigan", away="Ohio State", spread="Michigan -7.5" -> +7.5
        home="Michigan", away="Ohio State", spread="Ohio State -3" -> -3.0

    ``NaN`` and infinite values are rejected even though Python can parse them
    as floats.
    """
    if not isinstance(spread_text, str) or not home or not away:
        return None

    try:
        value = float(spread_text.split()[-1].replace("+", ""))
    except (ValueError, TypeError, IndexError):
        return None

    if not math.isfinite(value):
        return None

    text_lower = spread_text.casefold()
    home_lower = str(home).casefold()
    away_lower = str(away).casefold()

    if home_lower in text_lower:
        return abs(value)
    if away_lower in text_lower:
        return -abs(value)
    return None


def _provider_name(line: dict[str, Any]) -> str:
    provider = line.get("provider")
    if isinstance(provider, dict):
        provider = provider.get("name")
    return str(provider or "").strip()


def select_first_market_spread(game: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first parseable formatted spread in CFBD provider order."""
    home = game.get("homeTeam")
    away = game.get("awayTeam")
    lines = game.get("lines")
    if not home or not away or not isinstance(lines, list):
        return None

    for provider_index, line in enumerate(lines):
        if not isinstance(line, dict):
            continue
        formatted = line.get("formattedSpread")
        spread = parse_spread_text(formatted, home, away)
        if spread is None:
            continue
        return {
            "provider": _provider_name(line),
            "providerIndex": provider_index,
            "formattedSpread": formatted,
            "marketSpread": float(spread),
        }
    return None


def _fetch_partition(
    client: httpx.Client,
    *,
    api_key: str,
    year: int,
    season_type: str,
) -> list[dict[str, Any]]:
    response = client.get(
        BASE_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        params={"year": year, "seasonType": season_type},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"Expected list from CFBD for {year} {season_type}")
    return [row for row in payload if isinstance(row, dict)]


def get_market_spreads(
    *,
    api_key: str,
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
) -> dict[str, Any]:
    """Get one clean market spread for each parseable game in the year range."""
    if not api_key:
        raise ValueError("CFBD_API_KEY is required")
    if end_year < start_year:
        raise ValueError("end_year must be >= start_year")

    rows: list[dict[str, Any]] = []
    requests_meta: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}

    with httpx.Client(timeout=60.0) as client:
        for year in range(start_year, end_year + 1):
            for season_type in SEASON_TYPES:
                games = _fetch_partition(
                    client,
                    api_key=api_key,
                    year=year,
                    season_type=season_type,
                )
                usable = 0

                for game in games:
                    gid_value = game.get("id", game.get("gameId"))
                    if gid_value is None:
                        continue

                    chosen = select_first_market_spread(game)
                    if chosen is None:
                        continue

                    gid = str(gid_value)
                    row = {
                        "season": year,
                        "seasonType": game.get("seasonType", season_type),
                        "week": int(game["week"]) if game.get("week") is not None else None,
                        "gameId": gid,
                        "homeTeam": game.get("homeTeam"),
                        "awayTeam": game.get("awayTeam"),
                        **chosen,
                    }

                    previous = seen.get(gid)
                    if previous is not None:
                        old_key = (
                            previous.get("homeTeam"),
                            previous.get("awayTeam"),
                            previous.get("marketSpread"),
                        )
                        new_key = (
                            row.get("homeTeam"),
                            row.get("awayTeam"),
                            row.get("marketSpread"),
                        )
                        if old_key != new_key:
                            raise ValueError(f"Conflicting duplicate CFBD gameId {gid}")
                        continue

                    seen[gid] = row
                    rows.append(row)
                    usable += 1

                requests_meta.append(
                    {
                        "season": year,
                        "seasonType": season_type,
                        "gamesReturned": len(games),
                        "gamesWithUsableSpread": usable,
                    }
                )
                print(
                    f"CFBD LINES {year} {season_type}: "
                    f"returned={len(games)} usable={usable}"
                )

    rows.sort(
        key=lambda row: (
            row["season"],
            0 if str(row.get("seasonType") or "").lower() == "regular" else 1,
            row.get("week") or 0,
            row["gameId"],
        )
    )

    return {
        "schemaVersion": 1,
        "snapshotVersion": SNAPSHOT_VERSION,
        "source": BASE_URL,
        "retrievedAtUtc": datetime.now(timezone.utc).isoformat(),
        "startYear": start_year,
        "endYear": end_year,
        "seasonTypes": list(SEASON_TYPES),
        "spreadConvention": "positive=home favored; negative=away favored",
        "selectionRule": "first parseable formattedSpread in CFBD provider order",
        "requests": requests_meta,
        "games": rows,
    }


def write_snapshot(
    snapshot: dict[str, Any],
    *,
    json_path: Path,
    csv_path: Path | None,
    overwrite: bool,
) -> None:
    if json_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {json_path}; use --overwrite intentionally")
    if csv_path is not None and csv_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {csv_path}; use --overwrite intentionally")

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")

    if csv_path is not None:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "season",
            "seasonType",
            "week",
            "gameId",
            "homeTeam",
            "awayTeam",
            "provider",
            "providerIndex",
            "formattedSpread",
            "marketSpread",
        ]
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(snapshot["games"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download clean CFBD market spreads for every game in a historical year range"
    )
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR)
    parser.add_argument("--end-year", type=int, default=DEFAULT_END_YEAR)
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    snapshot = get_market_spreads(
        api_key=os.environ.get("CFBD_API_KEY", ""),
        start_year=args.start_year,
        end_year=args.end_year,
    )
    write_snapshot(
        snapshot,
        json_path=args.output,
        csv_path=args.csv_output,
        overwrite=args.overwrite,
    )

    print(f"Saved {len(snapshot['games'])} clean market spreads")
    print(f"JSON: {args.output}")
    print(f"CSV: {args.csv_output}")


if __name__ == "__main__":
    main()
