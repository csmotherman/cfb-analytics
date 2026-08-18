"""Historical player/NIL draft challenge against 2019 LSU.

This module is intentionally separate from Prediction-v2. It builds a game dataset
from completed historical CFBD player seasons, era-adjusts player production within
position groups, assigns fictional SOAR NIL asking prices, constructs a seven-player
2019 LSU boss roster, calibrates player-roster power to historical game margins, and
benchmarks a fixed-budget two-offer-per-slot draft before any user-outcome tuning.

The NIL values are game mechanics only. They are not estimates of what any player
actually earned, could have earned, or would command in a real NIL marketplace.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist, mean
from typing import Any, Iterable

from cfb_analytics.sources.cfbd.client import CfbdClient, CfbdError

CHALLENGE_VERSION = "historical-player-nil-v1"
TARGET_SEASON = 2019
TARGET_TEAM = "LSU"
DEFAULT_SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)
EXCLUDED_SEASONS = (2020,)

SLOT_ORDER = ("QB", "RB", "WR", "FLEX", "DL", "LB", "DB")
SLOT_WEIGHTS = {
    "QB": 0.22,
    "RB": 0.10,
    "WR": 0.14,
    "FLEX": 0.10,
    "DL": 0.16,
    "LB": 0.12,
    "DB": 0.16,
}
OFFERS_PER_SLOT = 2
POOL_TOP_N_PER_SEASON = 10
WIN_THRESHOLD = 0.50
BUDGET_CANDIDATES = (14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0)
TARGET_ORACLE_WIN_RATE = 0.10

POSITION_ALIASES = {
    "QB": {"QB"},
    "RB": {"RB", "HB", "FB"},
    "WR": {"WR"},
    "TE": {"TE"},
    "DL": {"DL", "DE", "DT", "NT", "EDGE", "ED"},
    "LB": {"LB", "ILB", "OLB", "MLB"},
    "DB": {"DB", "CB", "S", "FS", "SS", "SAF"},
}

METRIC_WEIGHTS: dict[str, dict[str, float]] = {
    "QB": {
        "passYards": 0.25,
        "passTD": 0.20,
        "passINT": -0.12,
        "completionPct": 0.10,
        "rushYards": 0.15,
        "rushTD": 0.10,
        "totalOffenseYards": 0.08,
    },
    "RB": {
        "rushYards": 0.30,
        "rushTD": 0.20,
        "yardsPerCarry": 0.15,
        "recvYards": 0.15,
        "receptions": 0.08,
        "recvTD": 0.12,
    },
    "WR": {
        "recvYards": 0.35,
        "recvTD": 0.25,
        "receptions": 0.15,
        "yardsPerReception": 0.10,
        "rushYards": 0.08,
        "rushTD": 0.07,
    },
    "FLEX": {
        "scrimmageYards": 0.35,
        "totalTD": 0.25,
        "touches": 0.15,
        "yardsPerTouch": 0.15,
        "receptions": 0.10,
    },
    "DL": {
        "tacklesForLoss": 0.30,
        "sacks": 0.30,
        "tackles": 0.18,
        "forcedFumbles": 0.12,
        "passesDefended": 0.05,
        "defInterceptions": 0.05,
    },
    "LB": {
        "tackles": 0.30,
        "tacklesForLoss": 0.22,
        "sacks": 0.16,
        "defInterceptions": 0.12,
        "forcedFumbles": 0.10,
        "passesDefended": 0.10,
    },
    "DB": {
        "defInterceptions": 0.28,
        "passesDefended": 0.25,
        "tackles": 0.18,
        "forcedFumbles": 0.10,
        "tacklesForLoss": 0.09,
        "sacks": 0.10,
    },
}

NIL_PRICE_BANDS = {
    "QB": (1.6, 8.5),
    "RB": (0.7, 4.5),
    "WR": (1.0, 6.0),
    "TE": (0.7, 4.0),
    "DL": (1.0, 5.5),
    "LB": (0.8, 4.5),
    "DB": (0.9, 5.0),
}


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def _position_group(position: Any) -> str | None:
    token = str(position or "").upper().strip()
    for group, aliases in POSITION_ALIASES.items():
        if token in aliases:
            return group
    return None


def _slot_eligibility(position_group: str) -> tuple[str, ...]:
    if position_group == "QB":
        return ("QB",)
    if position_group == "RB":
        return ("RB", "FLEX")
    if position_group == "WR":
        return ("WR", "FLEX")
    if position_group == "TE":
        return ("FLEX",)
    if position_group in {"DL", "LB", "DB"}:
        return (position_group,)
    return ()


def _canonical_stat(category: Any, stat_type: Any) -> str | None:
    cat = _norm(category)
    stat = _norm(stat_type)
    yard_tokens = {"yd", "yds", "yard", "yards"}
    td_tokens = {"td", "tds", "touchdown", "touchdowns"}
    int_tokens = {"int", "ints", "interception", "interceptions"}

    if "passing" in cat:
        if stat in yard_tokens:
            return "passYards"
        if stat in td_tokens:
            return "passTD"
        if stat in int_tokens:
            return "passINT"
        if stat in {"cmp", "comp", "completions", "completion"}:
            return "passCompletions"
        if stat in {"att", "attempt", "attempts"}:
            return "passAttempts"

    if "rushing" in cat:
        if stat in yard_tokens:
            return "rushYards"
        if stat in td_tokens:
            return "rushTD"
        if stat in {"car", "carry", "carries", "att", "attempt", "attempts"}:
            return "rushCarries"

    if "receiving" in cat:
        if stat in yard_tokens:
            return "recvYards"
        if stat in td_tokens:
            return "recvTD"
        if stat in {"rec", "reception", "receptions", "catch", "catches"}:
            return "receptions"

    if "defensive" in cat or "defense" in cat:
        if stat in {"tot", "total", "tackle", "tackles", "totaltackles"}:
            return "tackles"
        if stat in {"tfl", "tacklesforloss", "tackleforloss"} or "tackleforloss" in stat:
            return "tacklesForLoss"
        if stat in {"sack", "sacks"}:
            return "sacks"
        if stat in int_tokens:
            return "defInterceptions"
        if stat in {"pd", "pbu", "passdefended", "passesdefended", "passbreakup", "passbreakups"}:
            return "passesDefended"
        if stat in {"ff", "forcedfumble", "forcedfumbles"}:
            return "forcedFumbles"

    return None


def _team_metadata(payload: Any) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(payload, list):
        return out
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("classification") or "").casefold() != "fbs":
            continue
        team = raw.get("school")
        if not team:
            continue
        logos = raw.get("logos")
        logo = None
        if isinstance(logos, list):
            logo = next((str(x) for x in logos if isinstance(x, str) and x.strip()), None)
        out[str(team)] = {
            "teamId": raw.get("id"),
            "conference": raw.get("conference"),
            "abbreviation": raw.get("abbreviation"),
            "logo": logo,
            "color": raw.get("color"),
            "alternateColor": raw.get("alternateColor", raw.get("alternate_color")),
        }
    return out


def aggregate_player_stats(
    season: int,
    payload: Any,
    metadata: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Collapse CFBD PlayerStat rows into one player-team-season record."""
    grouped: dict[str, dict[str, Any]] = {}
    if not isinstance(payload, list):
        return []

    for raw in payload:
        if not isinstance(raw, dict):
            continue
        team = str(raw.get("team") or "").strip()
        player = str(raw.get("player") or "").strip()
        if not team or not player or team not in metadata:
            continue
        position = str(raw.get("position") or "").upper().strip()
        position_group = _position_group(position)
        if not position_group:
            continue
        player_id = raw.get("playerId", raw.get("player_id"))
        stable_id = str(player_id) if player_id is not None else f"{team}:{position}:{player}"
        key = f"{season}:{stable_id}:{team}"
        row = grouped.setdefault(
            key,
            {
                "season": int(season),
                "playerId": player_id,
                "player": player,
                "team": team,
                "position": position,
                "positionGroup": position_group,
                "stats": defaultdict(float),
                **metadata[team],
            },
        )
        canonical = _canonical_stat(raw.get("category"), raw.get("statType", raw.get("stat_type")))
        value = _number(raw.get("stat"))
        if canonical and value is not None:
            row["stats"][canonical] += value

    result: list[dict[str, Any]] = []
    for row in grouped.values():
        stats = dict(row["stats"])
        attempts = stats.get("passAttempts", 0.0)
        completions = stats.get("passCompletions", 0.0)
        carries = stats.get("rushCarries", 0.0)
        receptions = stats.get("receptions", 0.0)
        rush_yards = stats.get("rushYards", 0.0)
        recv_yards = stats.get("recvYards", 0.0)
        rush_td = stats.get("rushTD", 0.0)
        recv_td = stats.get("recvTD", 0.0)
        touches = carries + receptions
        stats["completionPct"] = completions / attempts if attempts > 0 else 0.0
        stats["yardsPerCarry"] = rush_yards / carries if carries > 0 else 0.0
        stats["yardsPerReception"] = recv_yards / receptions if receptions > 0 else 0.0
        stats["scrimmageYards"] = rush_yards + recv_yards
        stats["totalTD"] = rush_td + recv_td
        stats["touches"] = touches
        stats["yardsPerTouch"] = stats["scrimmageYards"] / touches if touches > 0 else 0.0
        stats["totalOffenseYards"] = stats.get("passYards", 0.0) + rush_yards
        row["stats"] = stats
        row["slotEligibility"] = list(_slot_eligibility(row["positionGroup"]))
        result.append(row)
    return result


def _eligible_for_slot(row: dict[str, Any], slot: str) -> bool:
    if slot not in row.get("slotEligibility", []):
        return False
    s = row.get("stats", {})
    if slot == "QB":
        return s.get("passYards", 0.0) >= 1200 or s.get("passAttempts", 0.0) >= 100
    if slot == "RB":
        return s.get("rushYards", 0.0) >= 500 or s.get("rushCarries", 0.0) >= 90
    if slot == "WR":
        return s.get("recvYards", 0.0) >= 450 or s.get("receptions", 0.0) >= 30
    if slot == "FLEX":
        return s.get("scrimmageYards", 0.0) >= 550 or s.get("touches", 0.0) >= 70
    if slot == "DL":
        return s.get("tacklesForLoss", 0.0) >= 4 or s.get("sacks", 0.0) >= 2 or s.get("tackles", 0.0) >= 20
    if slot == "LB":
        return s.get("tackles", 0.0) >= 35 or s.get("tacklesForLoss", 0.0) >= 4
    if slot == "DB":
        return s.get("tackles", 0.0) >= 20 or s.get("defInterceptions", 0.0) >= 2 or s.get("passesDefended", 0.0) >= 4
    return False


def _percentile(values: list[float], value: float, *, lower_is_better: bool = False) -> float:
    if not values:
        return 0.5
    ordered = sorted(values)
    less = sum(x < value for x in ordered)
    equal = sum(x == value for x in ordered)
    p = (less + 0.5 * equal) / len(ordered)
    return 1.0 - p if lower_is_better else p


def score_players(rows: list[dict[str, Any]]) -> None:
    """Add era-normalized score, cross-era grade, and power z for every eligible slot."""
    by_season_slot: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for slot in SLOT_ORDER:
            if _eligible_for_slot(row, slot):
                by_season_slot[(int(row["season"]), slot)].append(row)

    slot_scores: dict[str, list[tuple[dict[str, Any], float]]] = defaultdict(list)
    for (season, slot), group in by_season_slot.items():
        weights = METRIC_WEIGHTS[slot]
        metric_values = {
            metric: [float(r.get("stats", {}).get(metric, 0.0)) for r in group]
            for metric in weights
        }
        for row in group:
            score = 0.0
            total_abs = 0.0
            components: dict[str, float] = {}
            for metric, weight in weights.items():
                value = float(row.get("stats", {}).get(metric, 0.0))
                p = _percentile(metric_values[metric], value, lower_is_better=weight < 0)
                components[metric] = p
                score += abs(weight) * p
                total_abs += abs(weight)
            era_score = score / total_abs if total_abs else 0.5
            row.setdefault("slotRatings", {})[slot] = {
                "eraScore": era_score,
                "components": components,
            }
            slot_scores[slot].append((row, era_score))

    normal = NormalDist()
    for slot, pairs in slot_scores.items():
        values = [score for _, score in pairs]
        for row, score in pairs:
            p = _percentile(values, score)
            p_clip = min(0.99, max(0.01, p))
            grade = 1.0 + 98.0 * p
            rating = row["slotRatings"][slot]
            rating["percentile"] = p
            rating["grade"] = round(grade, 1)
            rating["letter"] = letter_grade(grade)
            rating["powerZ"] = normal.inv_cdf(p_clip)


def letter_grade(grade: float) -> str:
    if grade >= 97:
        return "A+"
    if grade >= 93:
        return "A"
    if grade >= 90:
        return "A-"
    if grade >= 87:
        return "B+"
    if grade >= 83:
        return "B"
    if grade >= 80:
        return "B-"
    if grade >= 77:
        return "C+"
    if grade >= 73:
        return "C"
    if grade >= 70:
        return "C-"
    if grade >= 60:
        return "D"
    return "F"


def _star_volume(row: dict[str, Any]) -> float:
    s = row.get("stats", {})
    group = row.get("positionGroup")
    if group == "QB":
        return s.get("passYards", 0.0) + 0.55 * s.get("rushYards", 0.0) + 120.0 * s.get("passTD", 0.0)
    if group in {"RB", "WR", "TE"}:
        return s.get("scrimmageYards", 0.0) + 90.0 * s.get("totalTD", 0.0) + 4.0 * s.get("receptions", 0.0)
    return (
        8.0 * s.get("tackles", 0.0)
        + 35.0 * s.get("tacklesForLoss", 0.0)
        + 55.0 * s.get("sacks", 0.0)
        + 80.0 * s.get("defInterceptions", 0.0)
        + 45.0 * s.get("forcedFumbles", 0.0)
        + 25.0 * s.get("passesDefended", 0.0)
    )


def assign_nil_prices(rows: list[dict[str, Any]]) -> None:
    """Assign fictional SOAR NIL asks from grade, position premium, and star volume."""
    by_group: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row.get("slotRatings"):
            by_group[row["positionGroup"]].append(_star_volume(row))

    for row in rows:
        ratings = row.get("slotRatings") or {}
        if not ratings:
            continue
        max_grade = max(float(r["grade"]) for r in ratings.values())
        group = row["positionGroup"]
        volumes = by_group.get(group, [])
        star_index = _percentile(volumes, _star_volume(row)) if volumes else 0.5
        quality = min(1.0, max(0.0, (max_grade - 72.0) / 27.0))
        floor, ceiling = NIL_PRICE_BANDS[group]
        mix = 0.65 * (quality**1.65) + 0.35 * (star_index**1.45)
        ask = floor + (ceiling - floor) * mix
        row["nilAskMillions"] = round(max(floor, min(ceiling, ask)), 1)
        row["nilMarketIndex"] = round(star_index, 4)
        row["nilDisclaimer"] = "Fictional SOAR game value; not a historical or real-world NIL valuation."


def compact_player(row: dict[str, Any], slot: str) -> dict[str, Any]:
    rating = row["slotRatings"][slot]
    stats = {
        key: round(float(value), 3)
        for key, value in row.get("stats", {}).items()
        if _number(value) is not None and abs(float(value)) > 1e-12
    }
    stable = row.get("playerId")
    if stable is None:
        stable = hashlib.sha1(f"{row['season']}|{row['team']}|{row['player']}|{row['position']}".encode()).hexdigest()[:14]
    return {
        "id": f"{row['season']}:{stable}:{row['team']}:{slot}",
        "playerSeasonId": f"{row['season']}:{stable}:{row['team']}",
        "playerId": row.get("playerId"),
        "player": row["player"],
        "season": row["season"],
        "team": row["team"],
        "position": row["position"],
        "positionGroup": row["positionGroup"],
        "slot": slot,
        "conference": row.get("conference"),
        "teamId": row.get("teamId"),
        "abbreviation": row.get("abbreviation"),
        "logo": row.get("logo"),
        "color": row.get("color"),
        "alternateColor": row.get("alternateColor"),
        "grade": rating["grade"],
        "letter": rating["letter"],
        "powerZ": rating["powerZ"],
        "eraScore": rating["eraScore"],
        "nilAskMillions": row["nilAskMillions"],
        "stats": stats,
    }


def build_slot_pools(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    pools: dict[str, list[dict[str, Any]]] = {}
    for slot in SLOT_ORDER:
        chosen: list[dict[str, Any]] = []
        by_season: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            if slot not in (row.get("slotRatings") or {}):
                continue
            if int(row["season"]) == TARGET_SEASON and str(row["team"]).casefold() == TARGET_TEAM.casefold():
                continue
            by_season[int(row["season"])].append(row)
        for season in DEFAULT_SEASONS:
            ranked = sorted(
                by_season.get(season, []),
                key=lambda r: (float(r["slotRatings"][slot]["grade"]), float(r["slotRatings"][slot]["eraScore"])),
                reverse=True,
            )
            chosen.extend(ranked[:POOL_TOP_N_PER_SEASON])
        compact = [compact_player(row, slot) for row in chosen]
        compact.sort(key=lambda r: (int(r["season"]), -float(r["grade"]), str(r["player"])))
        pools[slot] = compact
    return pools


def _best_unique_lineup(candidates: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]] | None:
    """Max-weight unique-player lineup; candidates should be small (e.g. one team)."""
    best_score = -float("inf")
    best: dict[str, dict[str, Any]] | None = None

    def walk(i: int, used: set[str], current: dict[str, dict[str, Any]], score: float) -> None:
        nonlocal best_score, best
        if i == len(SLOT_ORDER):
            if score > best_score:
                best_score = score
                best = dict(current)
            return
        slot = SLOT_ORDER[i]
        for player in candidates.get(slot, [])[:12]:
            psid = str(player["playerSeasonId"])
            if psid in used:
                continue
            used.add(psid)
            current[slot] = player
            walk(i + 1, used, current, score + SLOT_WEIGHTS[slot] * float(player["powerZ"]))
            current.pop(slot, None)
            used.remove(psid)

    walk(0, set(), {}, 0.0)
    return best


def build_team_lineups(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_team_season: dict[tuple[int, str], dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        for slot in SLOT_ORDER:
            if slot in (row.get("slotRatings") or {}):
                by_team_season[(int(row["season"]), str(row["team"]))][slot].append(compact_player(row, slot))

    out: dict[str, dict[str, Any]] = {}
    for (season, team), slot_map in by_team_season.items():
        if any(not slot_map.get(slot) for slot in SLOT_ORDER):
            continue
        for slot in SLOT_ORDER:
            slot_map[slot].sort(key=lambda p: float(p["powerZ"]), reverse=True)
        lineup = _best_unique_lineup(slot_map)
        if not lineup:
            continue
        composite = sum(SLOT_WEIGHTS[slot] * float(lineup[slot]["powerZ"]) for slot in SLOT_ORDER)
        out[f"{season}::{team}"] = {
            "season": season,
            "team": team,
            "composite": composite,
            "lineup": lineup,
        }
    return out


def _solve_2x2(a11: float, a12: float, a22: float, b1: float, b2: float) -> tuple[float, float] | None:
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-12:
        return None
    return ((b1 * a22 - b2 * a12) / det, (a11 * b2 - a12 * b1) / det)


def fit_margin_calibration(games: list[dict[str, Any]], team_lineups: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows: list[tuple[float, float, float]] = []
    for game in games:
        if not isinstance(game, dict) or not game.get("completed"):
            continue
        if str(game.get("homeClassification") or "").casefold() != "fbs":
            continue
        if str(game.get("awayClassification") or "").casefold() != "fbs":
            continue
        season = game.get("season")
        home = game.get("homeTeam")
        away = game.get("awayTeam")
        hp = _number(game.get("homePoints"))
        ap = _number(game.get("awayPoints"))
        if season is None or not home or not away or hp is None or ap is None:
            continue
        home_lineup = team_lineups.get(f"{int(season)}::{home}")
        away_lineup = team_lineups.get(f"{int(season)}::{away}")
        if not home_lineup or not away_lineup:
            continue
        diff = float(home_lineup["composite"]) - float(away_lineup["composite"])
        hfa = 0.0 if bool(game.get("neutralSite")) else 1.0
        rows.append((diff, hfa, hp - ap))

    if len(rows) < 400:
        raise ValueError(f"Not enough completed games with player-roster composites: {len(rows)}")
    a11 = sum(x1 * x1 for x1, _, _ in rows)
    a12 = sum(x1 * x2 for x1, x2, _ in rows)
    a22 = sum(x2 * x2 for _, x2, _ in rows)
    b1 = sum(x1 * y for x1, _, y in rows)
    b2 = sum(x2 * y for _, x2, y in rows)
    solved = _solve_2x2(a11, a12, a22, b1, b2)
    if solved is None:
        raise ValueError("Player-roster margin calibration is singular")
    beta, home_field = solved
    if beta <= 0:
        raise ValueError(f"Player-roster power should have positive margin scale, got {beta}")
    residuals = [y - (beta * x1 + home_field * x2) for x1, x2, y in rows]
    residual_sd = math.sqrt(sum(e * e for e in residuals) / len(residuals))
    return {
        "version": "historical-player-roster-margin-v1",
        "games": len(rows),
        "rosterPowerToMargin": beta,
        "homeFieldPoints": home_field,
        "residualSd": residual_sd,
        "neutralFieldRule": "expected margin = rosterPowerToMargin * (challengerRosterPower - LSU2019RosterPower)",
    }


def roster_power(lineup: dict[str, dict[str, Any]]) -> float:
    return sum(SLOT_WEIGHTS[slot] * float(lineup[slot]["powerZ"]) for slot in SLOT_ORDER)


def evaluate_lineup(
    lineup: dict[str, dict[str, Any]],
    boss_lineup: dict[str, dict[str, Any]],
    calibration: dict[str, Any],
) -> dict[str, Any]:
    challenger = roster_power(lineup)
    boss = roster_power(boss_lineup)
    margin = float(calibration["rosterPowerToMargin"]) * (challenger - boss)
    sd = float(calibration["residualSd"])
    probability = 0.5 if sd <= 0 and margin == 0 else (1.0 if sd <= 0 and margin > 0 else 0.0 if sd <= 0 else NormalDist().cdf(margin / sd))
    return {
        "challengerRosterPower": challenger,
        "bossRosterPower": boss,
        "expectedNeutralMargin": margin,
        "winProbability": probability,
        "win": probability > WIN_THRESHOLD,
    }


def _board_for_seed(slot_pools: dict[str, list[dict[str, Any]]], rng: random.Random) -> dict[str, list[dict[str, Any]]]:
    board: dict[str, list[dict[str, Any]]] = {}
    for slot in SLOT_ORDER:
        pool = slot_pools[slot]
        if len(pool) < OFFERS_PER_SLOT:
            raise ValueError(f"Pool too small for {slot}: {len(pool)}")
        board[slot] = rng.sample(pool, OFFERS_PER_SLOT)
    return board


def _best_board_lineup(board: dict[str, list[dict[str, Any]]], budget: float) -> dict[str, dict[str, Any]] | None:
    best_score = -float("inf")
    best: dict[str, dict[str, Any]] | None = None

    def walk(i: int, spent: float, used: set[str], current: dict[str, dict[str, Any]], score: float) -> None:
        nonlocal best_score, best
        if spent > budget + 1e-9:
            return
        if i == len(SLOT_ORDER):
            if score > best_score:
                best_score = score
                best = dict(current)
            return
        slot = SLOT_ORDER[i]
        for player in board[slot]:
            psid = str(player["playerSeasonId"])
            if psid in used:
                continue
            used.add(psid)
            current[slot] = player
            walk(
                i + 1,
                spent + float(player["nilAskMillions"]),
                used,
                current,
                score + SLOT_WEIGHTS[slot] * float(player["powerZ"]),
            )
            current.pop(slot, None)
            used.remove(psid)

    walk(0, 0.0, set(), {}, 0.0)
    return best


def _simple_board_lineup(board: dict[str, list[dict[str, Any]]], budget: float) -> dict[str, dict[str, Any]] | None:
    """Simple sequential strategy: buy first A-level value unless reserving cash says no."""
    lineup: dict[str, dict[str, Any]] = {}
    spent = 0.0
    used: set[str] = set()
    minimum_by_slot = {slot: min(float(p["nilAskMillions"]) for p in board[slot]) for slot in SLOT_ORDER}
    for idx, slot in enumerate(SLOT_ORDER):
        options = [p for p in board[slot] if str(p["playerSeasonId"]) not in used]
        if not options:
            return None
        reserve = sum(minimum_by_slot[s] for s in SLOT_ORDER[idx + 1 :])
        first, second = options[0], options[-1]
        first_value = float(first["grade"]) / max(0.1, float(first["nilAskMillions"]))
        second_value = float(second["grade"]) / max(0.1, float(second["nilAskMillions"]))
        prefer_first = float(first["grade"]) >= 93.0 and first_value >= second_value * 0.92
        ordered = [first, second] if prefer_first else [second, first]
        chosen = next((p for p in ordered if spent + float(p["nilAskMillions"]) + reserve <= budget + 1e-9), None)
        if chosen is None:
            chosen = min(options, key=lambda p: float(p["nilAskMillions"]))
            if spent + float(chosen["nilAskMillions"]) + reserve > budget + 1e-9:
                return None
        lineup[slot] = chosen
        used.add(str(chosen["playerSeasonId"]))
        spent += float(chosen["nilAskMillions"])
    return lineup


def benchmark_budgets(
    slot_pools: dict[str, list[dict[str, Any]]],
    boss_lineup: dict[str, dict[str, Any]],
    calibration: dict[str, Any],
    *,
    simulations: int = 5000,
    seed: int = 2019,
) -> dict[str, Any]:
    rng = random.Random(seed)
    boards = [_board_for_seed(slot_pools, rng) for _ in range(simulations)]
    sweep: list[dict[str, Any]] = []
    for budget in BUDGET_CANDIDATES:
        oracle_probs: list[float] = []
        baseline_probs: list[float] = []
        oracle_feasible = 0
        baseline_feasible = 0
        for board in boards:
            oracle = _best_board_lineup(board, budget)
            if oracle is not None:
                oracle_feasible += 1
                oracle_probs.append(float(evaluate_lineup(oracle, boss_lineup, calibration)["winProbability"]))
            baseline = _simple_board_lineup(board, budget)
            if baseline is not None:
                baseline_feasible += 1
                baseline_probs.append(float(evaluate_lineup(baseline, boss_lineup, calibration)["winProbability"]))

        def summary(values: list[float], feasible: int) -> dict[str, Any]:
            if not values:
                return {"feasibleRate": 0.0, "winRate": 0.0, "meanWinProbability": 0.0, "maxWinProbability": 0.0}
            return {
                "feasibleRate": feasible / simulations,
                "winRate": sum(v > WIN_THRESHOLD for v in values) / simulations,
                "conditionalWinRate": sum(v > WIN_THRESHOLD for v in values) / len(values),
                "meanWinProbability": mean(values),
                "maxWinProbability": max(values),
            }

        sweep.append(
            {
                "budgetMillions": budget,
                "oracle": summary(oracle_probs, oracle_feasible),
                "simpleStrategy": summary(baseline_probs, baseline_feasible),
            }
        )

    eligible = [row for row in sweep if row["oracle"]["feasibleRate"] >= 0.85 and row["oracle"]["maxWinProbability"] > 0.50]
    if not eligible:
        eligible = [row for row in sweep if row["oracle"]["maxWinProbability"] > 0.50] or sweep
    chosen = min(
        eligible,
        key=lambda row: (
            abs(float(row["oracle"]["winRate"]) - TARGET_ORACLE_WIN_RATE),
            -float(row["oracle"]["feasibleRate"]),
            float(row["budgetMillions"]),
        ),
    )
    return {
        "simulations": simulations,
        "seed": seed,
        "targetOracleWinRate": TARGET_ORACLE_WIN_RATE,
        "budgetSweep": sweep,
        "selectedBudgetMillions": chosen["budgetMillions"],
        "selected": chosen,
        "selectionRule": "Choose the budget nearest a 10% perfect-information win rate among budgets with >=85% oracle feasibility; no user outcomes are used.",
    }


def _fetch_optional(client: CfbdClient, path: str, params: dict[str, Any]) -> Any:
    try:
        return client.get_json(path, params).payload
    except CfbdError:
        return []


def build_dataset(
    client: CfbdClient,
    *,
    seasons: tuple[int, ...] = DEFAULT_SEASONS,
    simulations: int = 5000,
    seed: int = 2019,
) -> dict[str, Any]:
    metadata = _team_metadata(client.teams().payload)
    all_players: list[dict[str, Any]] = []
    all_games: list[dict[str, Any]] = []
    source_status: dict[str, Any] = {}

    for season in seasons:
        player_payload = client.get_json(
            "/stats/player/season",
            {"year": season, "seasonType": "both"},
        ).payload
        games_payload = _fetch_optional(
            client,
            "/games",
            {"year": season, "seasonType": "both", "classification": "fbs"},
        )
        season_players = aggregate_player_stats(season, player_payload, metadata)
        all_players.extend(season_players)
        if isinstance(games_payload, list):
            all_games.extend(game for game in games_payload if isinstance(game, dict))
        source_status[str(season)] = {
            "playerStatRows": len(player_payload) if isinstance(player_payload, list) else 0,
            "playerSeasons": len(season_players),
            "games": len(games_payload) if isinstance(games_payload, list) else 0,
        }

    score_players(all_players)
    assign_nil_prices(all_players)
    slot_pools = build_slot_pools(all_players)
    team_lineups = build_team_lineups(all_players)
    boss_record = team_lineups.get(f"{TARGET_SEASON}::{TARGET_TEAM}")
    if not boss_record:
        raise ValueError("Could not construct complete 2019 LSU seven-player boss roster")
    boss_lineup = boss_record["lineup"]
    calibration = fit_margin_calibration(all_games, team_lineups)
    difficulty = benchmark_budgets(
        slot_pools,
        boss_lineup,
        calibration,
        simulations=simulations,
        seed=seed,
    )
    budget = float(difficulty["selectedBudgetMillions"])

    boss_compact = {
        slot: {
            **boss_lineup[slot],
            "bossSlot": slot,
        }
        for slot in SLOT_ORDER
    }
    return {
        "schemaVersion": 1,
        "challengeVersion": CHALLENGE_VERSION,
        "status": "data-prototype-playable",
        "title": f"Can ${budget:g}M in NIL Beat the 2019 LSU Tigers?",
        "subtitle": "Seven historical stars. One fictional SOAR NIL budget. Beat Burrow's Tigers.",
        "seasons": list(seasons),
        "excludedSeasons": list(EXCLUDED_SEASONS),
        "target": {
            "season": TARGET_SEASON,
            "team": TARGET_TEAM,
            "rosterPower": boss_record["composite"],
            "lineup": boss_compact,
            "logo": metadata.get(TARGET_TEAM, {}).get("logo"),
            "conference": metadata.get(TARGET_TEAM, {}).get("conference"),
        },
        "rules": {
            "budgetMillions": budget,
            "requiredPlayers": len(SLOT_ORDER),
            "slots": list(SLOT_ORDER),
            "slotWeights": SLOT_WEIGHTS,
            "offersPerSlot": OFFERS_PER_SLOT,
            "maxOffers": OFFERS_PER_SLOT * len(SLOT_ORDER),
            "passRule": "Each roster slot can pass its first portal offer once; the second offer for that slot is final.",
            "winThreshold": WIN_THRESHOLD,
            "site": "neutral",
            "nilDisclaimer": "SOAR NIL asks are fictional game values derived from historical production and position scarcity. They are not real or historical NIL valuations.",
        },
        "grading": {
            "version": "era-adjusted-player-percentile-v1",
            "description": "Player metrics are ranked against same-season peers at the offered roster slot, combined by fixed position-specific weights, then converted to a cross-season percentile and 1-99 SOAR grade.",
            "metricWeights": METRIC_WEIGHTS,
        },
        "nilPricing": {
            "version": "soar-fictional-nil-ask-v1",
            "priceBandsMillions": NIL_PRICE_BANDS,
            "description": "Price blends player grade, position premium, and raw star-volume percentile to create strategic bargains; values are fictional gameplay currency.",
        },
        "matchupCalibration": calibration,
        "difficultyBenchmark": difficulty,
        "slotPools": slot_pools,
        "sourceStatus": source_status,
        "dataNotes": [
            "Only completed historical season production is used.",
            "2020 is excluded to match the existing SOAR historical support policy.",
            "Defensive grades are production-based statistical ratings, not film/scouting grades.",
            "The game is separate from Prediction-v2 and does not alter any prospective model artifact.",
            "Difficulty is calibrated by pre-user simulation only; user outcomes are not used to tune the budget.",
        ],
    }


def write_dataset(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_dataset(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def demo(dataset: dict[str, Any], *, seed: int = 42) -> str:
    rng = random.Random(seed)
    board = _board_for_seed(dataset["slotPools"], rng)
    budget = float(dataset["rules"]["budgetMillions"])
    lineup = _best_board_lineup(board, budget)
    if lineup is None:
        return f"{dataset['title']}\nseed={seed}\nNo feasible seven-player lineup under ${budget:g}M."
    result = evaluate_lineup(lineup, dataset["target"]["lineup"], dataset["matchupCalibration"])
    spent = sum(float(lineup[s]["nilAskMillions"]) for s in SLOT_ORDER)
    lines = [dataset["title"], f"seed={seed}", f"budget=${budget:g}M", ""]
    for slot in SLOT_ORDER:
        player = lineup[slot]
        lines.append(
            f"{slot}: {player['season']} {player['player']} ({player['team']}) "
            f"{player['letter']} {float(player['grade']):.1f} | ${float(player['nilAskMillions']):.1f}M"
        )
    lines.extend(
        [
            "",
            f"spent=${spent:.1f}M",
            f"expected neutral margin={float(result['expectedNeutralMargin']):+.2f}",
            f"chance to beat LSU={float(result['winProbability']) * 100.0:.1f}%",
            "WIN" if result["win"] else "LOSS",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("data/prototypes/beat-2019-lsu/player-nil-v1.json"))
    parser.add_argument("--simulations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.build:
        with CfbdClient() as client:
            payload = build_dataset(client, simulations=args.simulations)
        write_dataset(args.output, payload)
        selected = payload["difficultyBenchmark"]["selected"]
        print("HISTORICAL PLAYER NIL DRAFT: PASS")
        print(f"output={args.output}")
        print(f"title={payload['title']}")
        print(f"budget=${payload['rules']['budgetMillions']:g}M")
        print("bossRosterPower=", payload["target"]["rosterPower"])
        print("marginGames=", payload["matchupCalibration"]["games"])
        for slot in SLOT_ORDER:
            print(f"pool[{slot}]={len(payload['slotPools'][slot])}")
        print("oracleFeasibleRate=", selected["oracle"]["feasibleRate"])
        print("oracleWinRate=", selected["oracle"]["winRate"])
        print("oracleMaxP=", selected["oracle"]["maxWinProbability"])
        print("simpleWinRate=", selected["simpleStrategy"]["winRate"])

    if args.demo:
        payload = load_dataset(args.output)
        print(demo(payload, seed=args.seed))

    if not args.build and not args.demo:
        parser.error("choose --build and/or --demo")


if __name__ == "__main__":
    main()
