"""Cross-play state transition diagnostics.

This module does not mutate or correct raw CFBD records. It asks whether
plausible structured values reconcile with the next chronological play.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from cfb_analytics.raw.audit import discover_partitions, partition_dir
from cfb_analytics.raw.sequence import _candidate_sort_key


def _load(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _scrimmage(play: dict[str, Any]) -> bool:
    down = play.get("down")
    return isinstance(down, (int, float)) and 1 <= down <= 4


def _context(play: dict[str, Any]) -> dict[str, Any]:
    return {k: play.get(k) for k in (
        "id", "driveId", "driveNumber", "playNumber", "offense", "defense",
        "offenseScore", "defenseScore", "period", "clock", "down", "distance",
        "yardsToGoal", "yardsGained", "scoring", "playType", "playText",
    )}


def _audit_pair(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    """Return conservative transition flags for adjacent candidate-ordered plays."""
    flags: list[str] = []
    same_drive = a.get("driveId") is not None and a.get("driveId") == b.get("driveId")
    same_offense = a.get("offense") is not None and a.get("offense") == b.get("offense")

    # Scores should not decrease for the same team across adjacent records.
    if same_offense:
        aos, bos = a.get("offenseScore"), b.get("offenseScore")
        ads, bds = a.get("defenseScore"), b.get("defenseScore")
        if all(isinstance(x, (int, float)) and x >= 0 for x in (aos, bos)) and bos < aos:
            flags.append("same_team_offense_score_decrease")
        if all(isinstance(x, (int, float)) and x >= 0 for x in (ads, bds)) and bds < ads:
            flags.append("same_team_defense_score_decrease")

    # Only infer down/distance/field-position transitions in the conservative case:
    # same CFBD drive, same offense, consecutive scrimmage downs, non-scoring play,
    # no obvious turnover/penalty/sack administrative semantics.
    if not (same_drive and same_offense and _scrimmage(a) and _scrimmage(b)):
        return flags
    if a.get("scoring") or b.get("scoring"):
        return flags
    text = f"{a.get('playType','')} {a.get('playText','')}".lower()
    blockers = ("penalty", "interception", "fumble", "sack", "timeout", "kick", "punt", "end period")
    if any(x in text for x in blockers):
        return flags

    down_a, down_b = int(a["down"]), int(b["down"])
    dist_a, dist_b = a.get("distance"), b.get("distance")
    ytg_a, ytg_b, gained = a.get("yardsToGoal"), b.get("yardsToGoal"), a.get("yardsGained")

    if all(isinstance(x, (int, float)) for x in (dist_a, gained)):
        if gained < dist_a and down_a < 4 and down_b != down_a + 1:
            flags.append("expected_next_down_mismatch")
        if gained >= dist_a and down_b != 1:
            flags.append("expected_first_down_mismatch")

    if all(isinstance(x, (int, float)) for x in (ytg_a, ytg_b, gained)) and 0 <= ytg_a <= 100 and 0 <= ytg_b <= 100 and -100 <= gained <= 100:
        expected = ytg_a - gained
        if expected >= 0 and abs(ytg_b - expected) > 1:
            flags.append("field_position_transition_mismatch")

    if all(isinstance(x, (int, float)) for x in (dist_a, dist_b, gained)) and gained < dist_a and down_a < 4:
        expected_dist = dist_a - gained
        if expected_dist >= 0 and abs(dist_b - expected_dist) > 1:
            flags.append("distance_transition_mismatch")
    return flags


def transition_audit(root: Path, seasons: Iterable[int], examples: int = 10) -> dict[str, Any]:
    counts = Counter(); by_season: dict[int, Counter] = defaultdict(Counter)
    samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    games = pairs = conservative_pairs = 0
    for season in seasons:
        for season_type, week in discover_partitions(root, season):
            d = partition_dir(root, season, season_type, week)
            game_rows = {str(g["id"]): g for g in _load(d / "games.json")}
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for p in _load(d / "plays.json"):
                grouped[str(p.get("gameId"))].append(p)
            for gid, raw_plays in grouped.items():
                games += 1
                ordered = sorted(raw_plays, key=_candidate_sort_key)
                for a, b in zip(ordered, ordered[1:]):
                    pairs += 1
                    if a.get("driveId") == b.get("driveId") and a.get("offense") == b.get("offense") and _scrimmage(a) and _scrimmage(b):
                        conservative_pairs += 1
                    for flag in _audit_pair(a, b):
                        counts[flag] += 1; by_season[season][flag] += 1
                        if len(samples[flag]) < examples:
                            g = game_rows.get(gid, {})
                            samples[flag].append({
                                "season": season, "season_type": season_type, "week": week,
                                "gameId": gid, "game": f"{g.get('awayTeam')} @ {g.get('homeTeam')}",
                                "previous": _context(a), "next": _context(b),
                            })
    return {
        "candidate_order": ["gameId", "driveNumber", "playNumber"],
        "games_scanned": games, "adjacent_pairs": pairs,
        "conservative_scrimmage_pairs": conservative_pairs,
        "counts": dict(counts),
        "by_season": {str(s): dict(c) for s, c in by_season.items()},
        "examples": dict(samples),
        "note": "Flags are reconciliation failures, not automatic corrections.",
    }


def concise_transitions(r: dict[str, Any]) -> str:
    c = r["counts"]
    lines = [
        "PLAY STATE TRANSITION AUDIT",
        f"Games scanned: {r['games_scanned']:,}",
        f"Adjacent candidate-ordered pairs: {r['adjacent_pairs']:,}",
        f"Conservative scrimmage pairs: {r['conservative_scrimmage_pairs']:,}", "",
        "Reconciliation flags:",
        f"  expected next-down mismatch ............ {c.get('expected_next_down_mismatch',0):,}",
        f"  expected first-down mismatch ........... {c.get('expected_first_down_mismatch',0):,}",
        f"  distance transition mismatch ........... {c.get('distance_transition_mismatch',0):,}",
        f"  field-position transition mismatch ..... {c.get('field_position_transition_mismatch',0):,}",
        f"  same-team offense-score decrease ....... {c.get('same_team_offense_score_decrease',0):,}",
        f"  same-team defense-score decrease ....... {c.get('same_team_defense_score_decrease',0):,}",
        "", "These are diagnostic flags, not corrections.",
        "Use --json --examples N to inspect contextual pairs.",
    ]
    return "\n".join(lines)
