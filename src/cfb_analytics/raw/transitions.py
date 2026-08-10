"""Cross-play state transition diagnostics.

This module never mutates raw CFBD data. It checks whether adjacent plays
reconcile and profiles football context around every mismatch so validator
limitations can be separated from unexplained source inconsistencies.
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


def _combined(play: dict[str, Any]) -> str:
    return f"{play.get('playType','')} {play.get('playText','')}".lower()


def _penalty_signal(play: dict[str, Any]) -> str | None:
    play_type = str(play.get("playType") or "").lower()
    play_text = str(play.get("playText") or "").lower()
    type_hit = "penalty" in play_type
    text_hit = "penalty" in play_text
    if type_hit and text_hit: return "playtype_and_text"
    if type_hit: return "playtype_only"
    if text_hit: return "text_only"
    return None


def _penalty_context(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    aa, bb = _penalty_signal(a), _penalty_signal(b)
    location = "both" if aa and bb else "previous" if aa else "next" if bb else "none"
    return {"location": location, "previous_signal": aa, "next_signal": bb}


def _football_context(a: dict[str, Any], b: dict[str, Any]) -> set[str]:
    """Tag situations that can invalidate naïve state-transition expectations."""
    tags: set[str] = set()
    ta, tb = _combined(a), _combined(b)
    joined = f"{ta} {tb}"
    if _penalty_signal(a) or _penalty_signal(b): tags.add("penalty")
    if "incomplete" in joined: tags.add("incomplete_pass")
    if "sack" in joined: tags.add("sack")
    if "interception" in joined: tags.add("interception")
    if "fumble" in joined: tags.add("fumble")
    if any(x in joined for x in ("kickoff", "punt", "field goal", "extra point", "pat ")): tags.add("special_teams")
    if any(x in joined for x in ("end period", "end of quarter", "end of half", "end of game")): tags.add("period_boundary")
    if any(x in joined for x in ("review", "replay", "overturned", "confirmed", "stands")): tags.add("review")
    if any(x in joined for x in ("no play", "no-play")): tags.add("no_play")
    if a.get("scoring") or b.get("scoring") or "touchdown" in joined or " td" in joined: tags.add("scoring")
    if a.get("offense") and b.get("offense") and a.get("offense") != b.get("offense"): tags.add("possession_change")
    if a.get("driveId") != b.get("driveId"): tags.add("drive_change")
    if a.get("period") != b.get("period"): tags.add("period_change")
    if any(isinstance(p.get("yardsToGoal"), (int, float)) and p.get("yardsToGoal") <= p.get("distance", -1) for p in (a, b)):
        tags.add("goal_to_go")
    if any(x in joined for x in ("timeout", "time out")): tags.add("timeout")
    if not tags: tags.add("ordinary_unexplained")
    return tags


def _audit_pair(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
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
    blockers = ("penalty", "interception", "fumble", "sack", "timeout", "kick", "punt", "end period")
    if any(x in _combined(a) for x in blockers):
        return flags

    down_a, down_b = int(a["down"]), int(b["down"])
    dist_a, dist_b = a.get("distance"), b.get("distance")
    ytg_a, ytg_b, gained = a.get("yardsToGoal"), b.get("yardsToGoal"), a.get("yardsGained")
    expected_down: int | None = None
    if all(isinstance(x, (int, float)) for x in (dist_a, gained)):
        if gained < dist_a and down_a < 4:
            expected_down = down_a + 1
            if down_b != expected_down: flags.append("expected_next_down_mismatch")
        elif gained >= dist_a:
            expected_down = 1
            if down_b != 1: flags.append("expected_first_down_mismatch")
    if expected_down is not None and down_b == expected_down and all(isinstance(x, (int, float)) for x in (dist_a, dist_b, gained)):
        if gained < dist_a and down_a < 4:
            expected_dist = dist_a - gained
            if expected_dist >= 0 and abs(dist_b - expected_dist) > 1: flags.append("distance_transition_mismatch")
    if all(isinstance(x, (int, float)) for x in (ytg_a, ytg_b, gained)) and 0 <= ytg_a <= 100 and 0 <= ytg_b <= 100 and -100 <= gained <= 100:
        expected = ytg_a - gained
        if expected >= 0 and abs(ytg_b - expected) > 1: flags.append("field_position_transition_mismatch")
    return flags


def transition_audit(root: Path, seasons: Iterable[int], examples: int = 10) -> dict[str, Any]:
    counts = Counter(); by_season: dict[int, Counter] = defaultdict(Counter)
    samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    penalty_by_flag: dict[str, Counter] = defaultdict(Counter)
    context_by_flag: dict[str, Counter] = defaultdict(Counter)
    pair_context = Counter(); games = pairs = conservative_pairs = 0
    flagged_pairs: set[tuple[str, str, str]] = set()

    for season in seasons:
        for season_type, week in discover_partitions(root, season):
            d = partition_dir(root, season, season_type, week)
            game_rows = {str(g["id"]): g for g in _load(d / "games.json")}
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for p in _load(d / "plays.json"): grouped[str(p.get("gameId"))].append(p)
            for gid, raw_plays in grouped.items():
                games += 1; ordered = sorted(raw_plays, key=_candidate_sort_key)
                for a, b in zip(ordered, ordered[1:]):
                    pairs += 1
                    if a.get("driveId") == b.get("driveId") and a.get("offense") == b.get("offense") and _scrimmage(a) and _scrimmage(b): conservative_pairs += 1
                    flags = _audit_pair(a, b)
                    if not flags: continue
                    contexts = _football_context(a, b); penalty = _penalty_context(a, b)
                    pair_key = (gid, str(a.get("id")), str(b.get("id")))
                    if pair_key not in flagged_pairs:
                        flagged_pairs.add(pair_key)
                        for ctx in contexts: pair_context[ctx] += 1
                    for flag in flags:
                        counts[flag] += 1; by_season[season][flag] += 1
                        penalty_by_flag[flag][penalty["location"]] += 1
                        for ctx in contexts: context_by_flag[flag][ctx] += 1
                        if len(samples[flag]) < examples:
                            g = game_rows.get(gid, {})
                            samples[flag].append({"season": season, "season_type": season_type, "week": week, "gameId": gid, "game": f"{g.get('awayTeam')} @ {g.get('homeTeam')}", "contexts": sorted(contexts), "penalty_context": penalty, "previous": _context(a), "next": _context(b)})
    return {"candidate_order": ["gameId", "driveNumber", "playNumber"], "games_scanned": games, "adjacent_pairs": pairs, "conservative_scrimmage_pairs": conservative_pairs, "flagged_unique_pairs": len(flagged_pairs), "counts": dict(counts), "pair_context_counts": dict(pair_context), "context_by_flag": {k: dict(v) for k, v in context_by_flag.items()}, "penalty_context_by_flag": {k: dict(v) for k, v in penalty_by_flag.items()}, "by_season": {str(s): dict(c) for s, c in by_season.items()}, "examples": dict(samples), "note": "Context tags are diagnostic and non-exclusive; ordinary_unexplained means no known special context was detected."}


def concise_transitions(r: dict[str, Any]) -> str:
    c = r["counts"]; ctx = r["pair_context_counts"]
    labels = (("expected_next_down_mismatch", "expected next-down mismatch"),("expected_first_down_mismatch", "expected first-down mismatch"),("distance_transition_mismatch", "distance transition mismatch"),("field_position_transition_mismatch", "field-position transition mismatch"),("same_team_offense_score_decrease", "same-team offense-score decrease"),("same_team_defense_score_decrease", "same-team defense-score decrease"))
    lines = ["PLAY STATE TRANSITION AUDIT", f"Games scanned: {r['games_scanned']:,}", f"Adjacent candidate-ordered pairs: {r['adjacent_pairs']:,}", f"Conservative scrimmage pairs: {r['conservative_scrimmage_pairs']:,}", f"Unique flagged pairs: {r['flagged_unique_pairs']:,}", "", "Flagged-pair football context (non-exclusive):"]
    for key in ("penalty","incomplete_pass","sack","interception","fumble","special_teams","scoring","possession_change","drive_change","period_boundary","period_change","review","no_play","goal_to_go","timeout","ordinary_unexplained"):
        lines.append(f"  {key:.<38} {ctx.get(key,0):>7,}")
    lines.append("\nReconciliation flags:")
    for key,label in labels:
        total=c.get(key,0); ordinary=r["context_by_flag"].get(key,{}).get("ordinary_unexplained",0)
        lines.append(f"  {label:.<40} {total:>7,}  ordinary-unexplained={ordinary:>6,}")
    lines.extend(["", "Context tags may overlap; ordinary_unexplained has no detected special context.", "Use --json --examples N to inspect contextual pairs."])
    return "\n".join(lines)
