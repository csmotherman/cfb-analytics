"""Week-aware CFBD acquisition orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from cfb_analytics.raw.storage import partition_dir, store_response, verify_manifest
from cfb_analytics.sources.cfbd.client import CfbdClient

ENTITIES = ("games", "drives", "plays")


def get_calendar(client: CfbdClient, season: int) -> list[dict]:
    response = client.calendar(season)
    if not isinstance(response.payload, list):
        raise ValueError(f"Unexpected calendar payload for {season}")
    return response.payload


def calendar_partitions(calendar: Iterable[dict]) -> list[tuple[str, int]]:
    found: set[tuple[str, int]] = set()
    for item in calendar:
        week = item.get("week")
        season_type = item.get("seasonType") or item.get("season_type")
        if week is None or season_type is None:
            raise ValueError(f"Calendar item missing week/season type: {item}")
        found.add((str(season_type).lower(), int(week)))
    return sorted(found, key=lambda x: (x[0], x[1]))


def acquire_week(
    client: CfbdClient,
    root: Path,
    season: int,
    season_type: str,
    week: int,
    *,
    refresh: bool = False,
) -> list[dict]:
    manifests: list[dict] = []
    directory = partition_dir(root, season, season_type, week)
    for entity in ENTITIES:
        if not refresh and verify_manifest(directory, entity):
            manifests.append(json.loads((directory / f"{entity}.manifest.json").read_text(encoding="utf-8")))
            continue
        response = getattr(client, entity)(season, week, season_type)
        manifests.append(
            store_response(
                root,
                season=season,
                season_type=season_type,
                week=week,
                entity=entity,
                response=response,
                refresh=refresh,
            )
        )
    return manifests


def acquire_season(client: CfbdClient, root: Path, season: int, *, refresh: bool = False) -> list[dict]:
    calendar = get_calendar(client, season)
    results: list[dict] = []
    for season_type, week in calendar_partitions(calendar):
        results.extend(acquire_week(client, root, season, season_type, week, refresh=refresh))
    return results
