"""Integrity audits for raw FBS-vs-FBS partitions."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from cfb_analytics.raw.storage import partition_dir, verify_manifest


def _load(directory: Path, entity: str) -> list[dict[str, Any]]:
    path = directory / f"{entity}.json"
    if not path.exists():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path} is not a JSON list")
    return payload


def _profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    field_occurrences: Counter[str] = Counter()
    null_counts: Counter[str] = Counter()
    for row in rows:
        for key, value in row.items():
            field_occurrences[key] += 1
            if value is None:
                null_counts[key] += 1
    return {
        "fields": sorted(field_occurrences),
        "field_occurrences": dict(sorted(field_occurrences.items())),
        "null_counts": dict(sorted(null_counts.items())),
    }


def audit_partition(root: Path, season: int, season_type: str, week: int) -> dict[str, Any]:
    directory = partition_dir(root, season, season_type, week)
    games, drives, plays = (_load(directory, e) for e in ("games", "drives", "plays"))

    game_ids = [str(x.get("id")) for x in games]
    drive_ids = [str(x.get("id")) for x in drives]
    play_ids = [str(x.get("id")) for x in plays]
    game_set, drive_set, play_set = set(game_ids), set(drive_ids), set(play_ids)
    drive_game_set = {str(x.get("gameId")) for x in drives}
    play_game_set = {str(x.get("gameId")) for x in plays}
    play_drive_set = {str(x.get("driveId")) for x in plays if x.get("driveId") is not None}

    non_fbs_games = [
        str(g.get("id")) for g in games
        if str(g.get("homeClassification", "")).lower() != "fbs"
        or str(g.get("awayClassification", "")).lower() != "fbs"
    ]

    checks = {
        "manifests_valid": all(verify_manifest(directory, e) for e in ("games", "drives", "plays")),
        "fbs_vs_fbs_only": not non_fbs_games,
        "unique_game_ids": len(game_ids) == len(game_set),
        "unique_drive_ids": len(drive_ids) == len(drive_set),
        "unique_play_ids": len(play_ids) == len(play_set),
        "no_orphan_drive_games": not (drive_game_set - game_set),
        "no_orphan_play_games": not (play_game_set - game_set),
        "no_orphan_play_drives": not (play_drive_set - drive_set),
    }

    return {
        "partition": {"season": season, "season_type": season_type, "week": week},
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "counts": {"games": len(games), "drives": len(drives), "plays": len(plays)},
        "checks": checks,
        "duplicates": {
            "games": len(game_ids) - len(game_set),
            "drives": len(drive_ids) - len(drive_set),
            "plays": len(play_ids) - len(play_set),
        },
        "coverage": {
            "games_with_drives": len(game_set & drive_game_set),
            "games_without_drives": len(game_set - drive_game_set),
            "games_with_plays": len(game_set & play_game_set),
            "games_without_plays": len(game_set - play_game_set),
            "drives_referenced_by_plays": len(drive_set & play_drive_set),
            "drives_without_plays": len(drive_set - play_drive_set),
        },
        "orphans": {
            "drive_game_ids_missing_from_games": sorted(drive_game_set - game_set),
            "play_game_ids_missing_from_games": sorted(play_game_set - game_set),
            "play_drive_ids_missing_from_drives": sorted(play_drive_set - drive_set),
        },
        "non_fbs_game_ids": non_fbs_games,
        "schema": {"games": _profile(games), "drives": _profile(drives), "plays": _profile(plays)},
    }
