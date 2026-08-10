"""Cross-play state transition diagnostics.

This module does not mutate or correct raw CFBD records. It asks whether
plausible structured values reconcile with the next chronological play and
profiles penalty context around every mismatch.
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


def _penalty_signal(play: dict[str, Any]) -> str | None:
    """Describe how a play exposes penalty semantics, if at all."""
    play_type = str(play.get("playType") or "").lower()
    play_text = str(play.get("playText") or "").lower()
    type_hit = "penalty" in play_type
    text_hit = "penalty" in play_text
    if type_hit and text_hit:
        return "playtype_and_text"
    if type_hit:
        return "playtype_only"
    if text_hit:
        return "text_only"
    return None


def _penalty_context(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    a_signal, b_signal = _penalty_signal(a), _penalty_signal(b)
    if a_signal and b_signal:
        location = "both"
    elif a_signal:
        location = "previous"
    elif b_signal:
        location = "next"
    else:
        location = "none"
    return {"location": location, "previous_signal": a_signal, "next_signal": b_signal}


def _audit_pair(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    """Return conservative transition flags for adjacent candidate-ordered plays."""
    flags: list[str] = []
    same_drive = a.get("driveId") is not None and a.get("driveId") == b.get("driveId")
    same_offense = a.get("offense") is not None and a.get("offense") == b.get("offense")

    if same_offense:
        aos, bos = a.get("offenseScore"), b.get("offenseScore")
        ads, bds = a.get("defenseScore"), b.get("defenseScore")
        if all(isinstance(x, (int, float)) and x >= 0 for x in (aos, bos)) and bos < aos:
            flags.append("same_team_offense_score_decrease")
        if all(isinstance(x, (int, float)) and x >= 0 for x in (ads, bds)) and bds < ads:
            flags.append("same_team_defense_score_decrease")

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

    expected_down: int | None = None
    if all(isinstance(x, (int, float)) for x in (dist_a, gained)):
        if gained < dist_a and down_a < 4:
            expected_down = down_a + 1
            if down_b != expected_down:
                flags.append("expected_next_down_mismatch")
        elif gained >= dist_a:
            expected_down = 1
            if down_b != 1:
                flags.append("expected_first_down_mismatch")

    if expected_down is not None and down_b == expected_down and all(isinstance(x, (int, float)) for x in (dist_a, dist_b, gained)):
        if gained < dist_a and down_a < 4:
            expected_dist = dist_a - gained
            if expected_dist >= 0 and abs(dist_b - expected_dist) > 1:
                flags.append("distance_transition_mismatch")

    if all(isinstance(x, (int, float)) for x in (ytg_a, ytg_b, gained)) and 0 <= ytg_a <= 100 and 0 <= ytg_b <= 100 and -100 <= gained <= 100:
        expected = ytg_a - gained
        if expected >= 0 and abs(ytg_b - expected) > 1:
            flags.append("field_position_transition_mismatch")
    return flags


def transition_audit(root: Path, seasons: Iterable[int], examples: int = 10) -> dict[str, Any]:
    counts = Counter(); by_season: dict[int, Counter] = defaultdict(Counter)
    samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    penalty_by_flag: dict[str, Counter] = defaultdict(Counter)
    penalty_signal_by_flag: dict[str, Counter] = defaultdict(Counter)
    games = pairs = conservative_pairs = 0
    flagged_pairs: set[tuple[str, str, str]] = set()
    flagged_pairs_with_penalty: set[tuple[str, str, str]] = set()

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
                    flags = _audit_pair(a, b)
                    if not flags:
                        continue
                    penalty = _penalty_context(a, b)
                    pair_key = (gid, str(a.get("id")), str(b.get("id")))
                    flagged_pairs.add(pair_key)
                    if penalty["location"] != "none":
                        flagged_pairs_with_penalty.add(pair_key)
                    for flag in flags:
                        counts[flag] += 1; by_season[season][flag] += 1
                        penalty_by_flag[flag][penalty["location"]] += 1
                        for side in ("previous_signal", "next_signal"):
                            signal = penalty[side]
                            if signal:
                                penalty_signal_by_flag[flag][f"{side}:{signal}"] += 1
                        if len(samples[flag]) < examples:
                            g = game_rows.get(gid, {})
                            samples[flag].append({
                                "season": season, "season_type": season_type, "week": week,
                                "gameId": gid, "game": f"{g.get('awayTeam')} @ {g.get('homeTeam')}",
                                "penalty_context": penalty,
                                "previous": _context(a), "next": _context(b),
                            })
    return {
        "candidate_order": ["gameId", "driveNumber", "playNumber"],
        "games_scanned": games, "adjacent_pairs": pairs,
        "conservative_scrimmage_pairs": conservative_pairs,
        "flagged_unique_pairs": len(flagged_pairs),
        "flagged_unique_pairs_with_penalty_context": len(flagged_pairs_with_penalty),
        "counts": dict(counts),
        "penalty_context_by_flag": {k: dict(v) for k, v in penalty_by_flag.items()},
        "penalty_signal_by_flag": {k: dict(v) for k, v in penalty_signal_by_flag.items()},
        "by_season": {str(s): dict(c) for s, c in by_season.items()},
        "examples": dict(samples),
        "note": "Flags are reconciliation failures, not automatic corrections. Penalty context checks both adjacent plays by playType and playText.",
    }


def concise_transitions(r: dict[str, Any]) -> str:
    c = r["counts"]
    labels = (
        ("expected_next_down_mismatch", "expected next-down mismatch"),
        ("expected_first_down_mismatch", "expected first-down mismatch"),
        ("distance_transition_mismatch", "distance transition mismatch"),
        ("field_position_transition_mismatch", "field-position transition mismatch"),
        ("same_team_offense_score_decrease", "same-team offense-score decrease"),
        ("same_team_defense_score_decrease", "same-team defense-score decrease"),
    )
    lines = [
        "PLAY STATE TRANSITION AUDIT",
        f"Games scanned: {r['games_scanned']:,}",
        f"Adjacent candidate-ordered pairs: {r['adjacent_pairs']:,}",
        f"Conservative scrimmage pairs: {r['conservative_scrimmage_pairs']:,}",
        f"Unique flagged pairs: {r['flagged_unique_pairs']:,}",
        f"Flagged pairs with penalty context: {r['flagged_unique_pairs_with_penalty_context']:,}", "",
        "Reconciliation flags:",
    ]
    for key, label in labels:
        total = c.get(key, 0)
        pc = r["penalty_context_by_flag"].get(key, {})
        penalty = total - pc.get("none", 0)
        pct = (100 * penalty / total) if total else 0
        lines.append(f"  {label:.<40} {total:>7,}  penalty-nearby={penalty:>6,} ({pct:5.1f}%)")
    lines.extend([
        "", "Penalty-nearby means either adjacent record contains 'penalty' in playType or playText.",
        "These remain diagnostic flags, not corrections.",
        "Use --json --examples N for previous/next penalty location and detection source.",
    ])
    return "\n".join(lines)
