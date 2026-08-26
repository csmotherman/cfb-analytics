"""Preseason feature construction for a target season Y.

Every function here takes only data that would have existed before the first
game of season Y: prior-season team_games/ratings, the recruiting class
entering Y, the roster as of preseason Y (no season-Y games), player-season
stats through Y-1, and the transfer-portal cycle heading into Y. Nothing here
reads season-Y team_games, player_season_stats, or any outcome field.

Track A (long-history) features: recruiting-independent, available every
COMPLETE_SEASONS year: prior power ratings + program/conference baselines.

Track B (modern-personnel) features: recruiting (2010+), returning production
/ QB continuity (needs roster+player_season_stats for Y-1, available from
Y=2014 target seasons on), transfer portal (needs portal.json for Y, available
from Y=2022 target seasons on -- portal.json itself starts at season=2021,
which covers the cycle into the 2021 season, so the first *target* season with
a portal feature is 2022 since we need the Y-1 season's departures captured
too... in practice we use portal.json[Y] directly, which covers the offseason
into Y, so Y=2021 is technically the first season with a portal snapshot, but
that snapshot's coverage is partial/early in CFBD's tracking; we mark 2021 as
usable but flag lower confidence in the report).
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from .common import (
    load_player_season_stats,
    load_portal,
    load_recruiting_team_ranks,
    load_roster,
    normalize_name,
    pivot_player_season_stats,
)

PRODUCTION_KEYS = (
    "passing.ATT", "passing.YDS",
    "rushing.CAR", "rushing.YDS",
    "receiving.REC", "receiving.YDS",
    "defensive.TOT", "defensive.TFL", "defensive.SACKS", "defensive.PD",
)


@lru_cache(maxsize=None)
def recruiting_features(team: str, target_season: int) -> dict[str, Any]:
    ranks = {y: load_recruiting_team_ranks(y) for y in (target_season, target_season - 1, target_season - 2)}
    points = {y: ranks[y].get(team, {}).get("points") for y in ranks}
    vals = [v for v in points.values() if v is not None]
    cur = points[target_season]
    two = [points[target_season], points[target_season - 1]]
    two = [v for v in two if v is not None]
    three = vals
    return {
        "recruiting_current": cur,
        "recruiting_2yr_avg": sum(two) / len(two) if two else None,
        "recruiting_3yr_avg": sum(three) / len(three) if three else None,
        "recruiting_current_rank": ranks[target_season].get(team, {}).get("rank"),
    }


@lru_cache(maxsize=None)
def _team_roster_ids(season: int, team: str) -> frozenset[str]:
    return frozenset(str(r["id"]) for r in load_roster(season) if str(r.get("team")) == team and r.get("id"))


@lru_cache(maxsize=None)
def _team_prior_production(prev_season: int, team: str) -> tuple[dict[str, float], dict[str, dict[str, float]]]:
    """(team totals per stat key, per-player pivoted stats for that team) from prev_season."""
    pivoted = pivot_player_season_stats([r for r in load_player_season_stats(prev_season) if str(r.get("team")) == team])
    totals: dict[str, float] = {k: 0.0 for k in PRODUCTION_KEYS}
    for player in pivoted.values():
        for k in PRODUCTION_KEYS:
            totals[k] += float(player.get(k, 0.0) or 0.0)
    return totals, pivoted


@lru_cache(maxsize=None)
def returning_production_features(team: str, target_season: int) -> dict[str, Any]:
    """Requires roster(target_season), roster(target_season-1), player_season_stats(target_season-1)."""
    prev = target_season - 1
    roster_now = _team_roster_ids(target_season, team)
    roster_prev = _team_roster_ids(prev, team)
    if not roster_now or not roster_prev:
        return {f"returning_{k.replace('.', '_')}_share": None for k in PRODUCTION_KEYS} | {
            "returning_players_count": None, "prior_roster_count": None, "data_available": False,
        }
    totals, pivoted_prev = _team_prior_production(prev, team)
    returning_ids = roster_now & roster_prev
    returning_totals: dict[str, float] = {k: 0.0 for k in PRODUCTION_KEYS}
    for pid in returning_ids:
        player = pivoted_prev.get(pid)
        if not player:
            continue
        for k in PRODUCTION_KEYS:
            returning_totals[k] += float(player.get(k, 0.0) or 0.0)
    out: dict[str, Any] = {"returning_players_count": len(returning_ids), "prior_roster_count": len(roster_prev), "data_available": True}
    for k in PRODUCTION_KEYS:
        team_total = totals[k]
        out[f"returning_{k.replace('.', '_')}_share"] = (returning_totals[k] / team_total) if team_total > 0 else None
    return out


@lru_cache(maxsize=None)
def qb_continuity_features(team: str, target_season: int) -> dict[str, Any]:
    """Identify the prior-season starter (highest passing.ATT on the team) and whether he returns."""
    prev = target_season - 1
    totals, pivoted_prev = _team_prior_production(prev, team)
    roster_now = _team_roster_ids(target_season, team)
    if not pivoted_prev or not roster_now:
        return {
            "qb_returning_flag": None, "qb_prior_passing_yards": None,
            "qb_prior_pass_att_share": None, "data_available": False,
        }
    qb_candidates = [(pid, p) for pid, p in pivoted_prev.items() if p.get("position") == "QB" and p.get("passing.ATT", 0)]
    if not qb_candidates:
        return {
            "qb_returning_flag": 0, "qb_prior_passing_yards": 0.0,
            "qb_prior_pass_att_share": 0.0, "data_available": True,
        }
    starter_id, starter = max(qb_candidates, key=lambda kv: kv[1].get("passing.ATT", 0.0))
    team_att = totals.get("passing.ATT", 0.0)
    returning = starter_id in roster_now
    return {
        "qb_returning_flag": 1 if returning else 0,
        "qb_prior_passing_yards": starter.get("passing.YDS", 0.0) if returning else 0.0,
        "qb_prior_pass_att_share": (starter.get("passing.ATT", 0.0) / team_att) if returning and team_att > 0 else 0.0,
        "data_available": True,
    }


@lru_cache(maxsize=None)
def _portal_value_index(season_prev: int) -> dict[tuple[str, str], dict[str, float]]:
    """(normalized_name, team) -> prior-season production dict, for matching portal rows to stats."""
    idx: dict[tuple[str, str], dict[str, float]] = {}
    for pid, p in pivot_player_season_stats(load_player_season_stats(season_prev)).items():
        name = p.get("player")
        team = p.get("team")
        if not name or not team:
            continue
        idx[(normalize_name(name), str(team))] = p
    return idx


@lru_cache(maxsize=None)
def portal_features(team: str, target_season: int) -> dict[str, Any]:
    """Net transfer-portal production, matched by normalized name + origin/destination team."""
    rows = load_portal(target_season)
    if not rows:
        return {"portal_available": False}
    prior_idx = _portal_value_index(target_season - 1)
    out_totals = {k: 0.0 for k in PRODUCTION_KEYS}
    in_totals = {k: 0.0 for k in PRODUCTION_KEYS}
    out_matched = out_unmatched = in_matched = in_unmatched = 0
    for row in rows:
        name = normalize_name(f"{row.get('firstName', '')} {row.get('lastName', '')}")
        origin, destination = row.get("origin"), row.get("destination")
        if origin == team:
            stats = prior_idx.get((name, origin))
            if stats:
                out_matched += 1
                for k in PRODUCTION_KEYS:
                    out_totals[k] += float(stats.get(k, 0.0) or 0.0)
            else:
                out_unmatched += 1
        if destination == team:
            stats = prior_idx.get((name, origin)) if origin else None
            if stats:
                in_matched += 1
                for k in PRODUCTION_KEYS:
                    in_totals[k] += float(stats.get(k, 0.0) or 0.0)
            else:
                in_unmatched += 1
    team_prior_totals, _ = _team_prior_production(target_season - 1, team)
    out: dict[str, Any] = {
        "portal_available": True,
        "portal_out_matched": out_matched, "portal_out_unmatched": out_unmatched,
        "portal_in_matched": in_matched, "portal_in_unmatched": in_unmatched,
    }
    for k in PRODUCTION_KEYS:
        base = team_prior_totals.get(k, 0.0)
        net = in_totals[k] - out_totals[k]
        out[f"portal_net_{k.replace('.', '_')}_share"] = (net / base) if base > 0 else None
    return out


TRANSFER_QB_PRODUCTIVE_ATT_THRESHOLD = 100


@lru_cache(maxsize=None)
def transfer_qb_features(team: str, target_season: int) -> dict[str, Any]:
    """Incoming transfer QB, evaluated on his PRIOR season's actual production at his old team.

    Only populated when the team's own prior-season starter did NOT return (see
    qb_continuity_features) -- if the incumbent is back, an incoming QB transfer
    is presumptively a backup, not the starter, and would just be noise here.
    Matched by normalized name + portal-reported origin school against
    player_season_stats(target_season-1), same join approach as portal_features,
    but scoped to position=='QB' only and picking the single most-productive
    (highest prior passing attempts) incoming name match, since a team's QB
    portal cycle rarely has more than one real starter-caliber name in it.
    """
    incumbent = qb_continuity_features(team, target_season)
    if not incumbent.get("data_available"):
        return {"transfer_qb_available": False}
    if incumbent.get("qb_returning_flag") == 1:
        return {"transfer_qb_available": True, "transfer_qb_incoming_flag": 0, "transfer_qb_prior_passing_yards": 0.0, "transfer_qb_prior_pass_att": 0.0}

    rows = load_portal(target_season)
    if not rows:
        return {"transfer_qb_available": False}
    prior_idx = _portal_value_index(target_season - 1)

    best: dict[str, float] | None = None
    for row in rows:
        if row.get("destination") != team or row.get("position") != "QB":
            continue
        origin = row.get("origin")
        if not origin:
            continue
        name = normalize_name(f"{row.get('firstName', '')} {row.get('lastName', '')}")
        stats = prior_idx.get((name, origin))
        if not stats or stats.get("position") != "QB":
            continue
        atts = float(stats.get("passing.ATT", 0.0) or 0.0)
        if best is None or atts > best.get("passing.ATT", 0.0):
            best = stats

    if best is None:
        return {"transfer_qb_available": True, "transfer_qb_incoming_flag": 0, "transfer_qb_prior_passing_yards": 0.0, "transfer_qb_prior_pass_att": 0.0}

    atts = float(best.get("passing.ATT", 0.0) or 0.0)
    yards = float(best.get("passing.YDS", 0.0) or 0.0)
    return {
        "transfer_qb_available": True,
        "transfer_qb_incoming_flag": 1 if atts >= TRANSFER_QB_PRODUCTIVE_ATT_THRESHOLD else 0,
        "transfer_qb_prior_passing_yards": yards,
        "transfer_qb_prior_pass_att": atts,
    }
