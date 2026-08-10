"""Diagnostic audit of competing raw play-order signals.

This module never reorders or mutates raw data. It measures agreement between
source array order, drive/play numbers, game clock, wallclock, and play IDs so
we can choose a canonical chronology from evidence rather than assumption.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from cfb_analytics.raw.audit import discover_partitions, partition_dir


def _load(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _clock_seconds(play: dict[str, Any]) -> int | None:
    clock = play.get("clock")
    if not isinstance(clock, dict):
        return None
    m, s = clock.get("minutes"), clock.get("seconds")
    if not isinstance(m, (int, float)) or not isinstance(s, (int, float)):
        return None
    return int(m) * 60 + int(s)


def _wallclock_key(value: Any) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _play_id_numeric(play: dict[str, Any]) -> int | None:
    value = play.get("id")
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _pairwise_disagreements(plays: list[dict[str, Any]]) -> Counter[str]:
    counts = Counter()
    for a, b in zip(plays, plays[1:]):
        counts["adjacent_pairs"] += 1
        if a.get("driveNumber") is not None and b.get("driveNumber") is not None:
            if b.get("driveNumber") < a.get("driveNumber"):
                counts["source_drive_number_regression"] += 1
        if a.get("driveId") == b.get("driveId") and a.get("playNumber") is not None and b.get("playNumber") is not None:
            if b.get("playNumber") < a.get("playNumber"):
                counts["source_play_number_regression_same_drive"] += 1
            elif b.get("playNumber") == a.get("playNumber"):
                counts["duplicate_adjacent_play_number_same_drive"] += 1
        pa, pb = a.get("period"), b.get("period")
        if isinstance(pa, (int, float)) and isinstance(pb, (int, float)):
            if pb < pa:
                counts["source_period_regression"] += 1
            elif pb == pa:
                ca, cb = _clock_seconds(a), _clock_seconds(b)
                if ca is not None and cb is not None and cb > ca:
                    counts["source_clock_regression_same_period"] += 1
        wa, wb = _wallclock_key(a.get("wallclock")), _wallclock_key(b.get("wallclock"))
        if wa is not None and wb is not None and wb < wa:
            counts["source_wallclock_regression"] += 1
        ia, ib = _play_id_numeric(a), _play_id_numeric(b)
        if ia is not None and ib is not None and ib < ia:
            counts["source_play_id_regression"] += 1
    return counts


def _game_summary(plays: list[dict[str, Any]]) -> dict[str, Any]:
    source_counts = _pairwise_disagreements(plays)
    drive_play_numbers: dict[str, list[int]] = defaultdict(list)
    clocks = Counter()
    wallclock_missing = 0
    play_id_missing = 0
    for p in plays:
        if p.get("driveId") is not None and isinstance(p.get("playNumber"), (int, float)):
            drive_play_numbers[str(p.get("driveId"))].append(int(p.get("playNumber")))
        key = (p.get("period"), _clock_seconds(p))
        if key[1] is not None:
            clocks[key] += 1
        if _wallclock_key(p.get("wallclock")) is None:
            wallclock_missing += 1
        if _play_id_numeric(p) is None:
            play_id_missing += 1

    duplicate_play_numbers = 0
    noncontiguous_play_numbers = 0
    for nums in drive_play_numbers.values():
        duplicate_play_numbers += len(nums) - len(set(nums))
        uniq = sorted(set(nums))
        if uniq and uniq != list(range(min(uniq), max(uniq) + 1)):
            noncontiguous_play_numbers += 1

    return {
        "plays": len(plays),
        "drives_seen": len(drive_play_numbers),
        "duplicate_play_numbers_within_drive": duplicate_play_numbers,
        "drives_with_noncontiguous_play_numbers": noncontiguous_play_numbers,
        "same_period_clock_ties": sum(n for n in clocks.values() if n > 1),
        "wallclock_missing": wallclock_missing,
        "play_id_missing": play_id_missing,
        **source_counts,
    }


def sequence_audit(root: Path, seasons: Iterable[int], examples: int = 10) -> dict[str, Any]:
    totals = Counter()
    by_season: dict[str, Counter[str]] = {}
    problematic_games: list[dict[str, Any]] = []
    games_scanned = 0

    for season in seasons:
        season_counts = Counter()
        for st, wk in discover_partitions(root, season):
            d = partition_dir(root, season, st, wk)
            games = {str(g["id"]): g for g in _load(d / "games.json")}
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for play in _load(d / "plays.json"):
                grouped[str(play.get("gameId"))].append(play)
            for game_id, plays in grouped.items():
                games_scanned += 1
                s = _game_summary(plays)
                for k, v in s.items():
                    if isinstance(v, int):
                        totals[k] += v
                        season_counts[k] += v
                conflict_keys = [
                    "source_drive_number_regression",
                    "source_play_number_regression_same_drive",
                    "source_period_regression",
                    "source_clock_regression_same_period",
                    "source_wallclock_regression",
                    "source_play_id_regression",
                    "duplicate_play_numbers_within_drive",
                ]
                if any(s.get(k, 0) for k in conflict_keys) and len(problematic_games) < examples:
                    game = games.get(game_id, {})
                    problematic_games.append({
                        "season": season,
                        "season_type": st,
                        "week": wk,
                        "gameId": game_id,
                        "game": f"{game.get('awayTeam')} @ {game.get('homeTeam')}",
                        "summary": s,
                        "first_source_records": [
                            {k: p.get(k) for k in ("id", "driveId", "driveNumber", "playNumber", "period", "clock", "wallclock", "playType", "playText")}
                            for p in plays[:12]
                        ],
                    })
        by_season[str(season)] = season_counts

    return {
        "games_scanned": games_scanned,
        "totals": dict(totals),
        "by_season": {s: dict(c) for s, c in by_season.items()},
        "examples": problematic_games,
        "interpretation": {
            "source_array_order": "Measured only; not assumed authoritative.",
            "play_number": "Measured within drive; not assumed globally chronological.",
            "clock": "Expected to count down within a period, but ties are normal and require another signal.",
            "wallclock": "Potential tie-breaker only when present and parseable.",
            "play_id": "Treated as an opaque source identifier until evidence proves ordering semantics.",
        },
    }


def concise_sequence(report: dict[str, Any]) -> str:
    t = report["totals"]
    lines = [
        "RAW PLAY SEQUENCE AUDIT",
        f"Games scanned: {report['games_scanned']:,}",
        "",
        "Source-order disagreements:",
        f"  drive-number regressions .............. {t.get('source_drive_number_regression', 0):,}",
        f"  play-number regressions (same drive) .. {t.get('source_play_number_regression_same_drive', 0):,}",
        f"  period regressions ..................... {t.get('source_period_regression', 0):,}",
        f"  clock regressions (same period) ........ {t.get('source_clock_regression_same_period', 0):,}",
        f"  wallclock regressions .................. {t.get('source_wallclock_regression', 0):,}",
        f"  play-id regressions .................... {t.get('source_play_id_regression', 0):,}",
        "",
        "Ordering ambiguity:",
        f"  duplicate play numbers within drives .. {t.get('duplicate_play_numbers_within_drive', 0):,}",
        f"  drives with noncontiguous play numbers . {t.get('drives_with_noncontiguous_play_numbers', 0):,}",
        f"  same-period clock ties ................. {t.get('same_period_clock_ties', 0):,}",
        f"  missing wallclock values ............... {t.get('wallclock_missing', 0):,}",
        f"  missing/non-numeric play IDs ........... {t.get('play_id_missing', 0):,}",
        "",
        "No ordering signal is promoted to canonical by this audit.",
        "Use --json --examples N to inspect conflicting games.",
    ]
    return "\n".join(lines)
