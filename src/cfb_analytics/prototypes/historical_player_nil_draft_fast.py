"""Efficient runner for the player/NIL challenge build.

The underlying statistical contract lives in ``historical_player_nil_draft``. This
runner replaces only the historical team-lineup assignment routine with an exact
small search over the only overlapping roster slots (RB/WR/FLEX). QB, DL, LB and DB
have disjoint eligibility and can be selected independently. This avoids an
unnecessary 12^7 generic search while preserving the same lineup objective.
"""
from __future__ import annotations

from typing import Any

from cfb_analytics.prototypes import historical_player_nil_draft as base


def efficient_best_unique_lineup(candidates: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]] | None:
    lineup: dict[str, dict[str, Any]] = {}

    # These positions have disjoint source position groups, so their best player is
    # independent of every other fixed slot.
    for slot in ("QB", "DL", "LB", "DB"):
        options = sorted(candidates.get(slot, []), key=lambda p: float(p["powerZ"]), reverse=True)
        if not options:
            return None
        lineup[slot] = options[0]

    # RB and WR can also be eligible for FLEX. Enumerating only those three slots is
    # exact for uniqueness and tiny even when a team has a deep skill-position room.
    rb = sorted(candidates.get("RB", []), key=lambda p: float(p["powerZ"]), reverse=True)[:12]
    wr = sorted(candidates.get("WR", []), key=lambda p: float(p["powerZ"]), reverse=True)[:12]
    flex = sorted(candidates.get("FLEX", []), key=lambda p: float(p["powerZ"]), reverse=True)[:16]
    if not rb or not wr or not flex:
        return None

    best_score = -float("inf")
    best_skill: tuple[dict[str, Any], dict[str, Any], dict[str, Any]] | None = None
    for rb_player in rb:
        rb_id = str(rb_player["playerSeasonId"])
        for wr_player in wr:
            wr_id = str(wr_player["playerSeasonId"])
            if wr_id == rb_id:
                continue
            for flex_player in flex:
                flex_id = str(flex_player["playerSeasonId"])
                if flex_id in {rb_id, wr_id}:
                    continue
                score = (
                    base.SLOT_WEIGHTS["RB"] * float(rb_player["powerZ"])
                    + base.SLOT_WEIGHTS["WR"] * float(wr_player["powerZ"])
                    + base.SLOT_WEIGHTS["FLEX"] * float(flex_player["powerZ"])
                )
                if score > best_score:
                    best_score = score
                    best_skill = (rb_player, wr_player, flex_player)

    if best_skill is None:
        return None
    lineup["RB"], lineup["WR"], lineup["FLEX"] = best_skill
    return lineup


# Patch the generic helper before base.build_dataset calls build_team_lineups.
base._best_unique_lineup = efficient_best_unique_lineup


if __name__ == "__main__":
    base.main()
