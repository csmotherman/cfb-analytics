"""Team-year wheel version of the historical player/NIL challenge.

Game loop inspired by a simple roster-wheel mechanic, but implemented with SOAR's
own historical CFB data and model contract:

* seven hidden team-seasons are drawn without replacement;
* one team-season is revealed per spin;
* the user signs exactly one actual historical player from that roster;
* the seven signings must fill QB, RB, WR, FLEX, DL, LB and DB exactly once;
* a shared fictional SOAR NIL cap applies to the whole roster;
* after the seventh signing, the game compares the user's roster with the best
  mathematically possible roster from those exact seven spins.

Difficulty is frozen before user outcomes. The NIL cap is selected by Monte Carlo so
that, among playable seven-spin boards, the *oracle* (perfect-information best roster)
beats 2019 LSU only about 1 run in 1,000. Impossible-to-complete boards are rejected
before the first spin, and the simulation uses that same playable-run condition.

This module is completely separate from Prediction-v2.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist, mean
from typing import Any

from cfb_analytics.prototypes import historical_player_nil_draft as base
from cfb_analytics.prototypes import historical_player_nil_draft_fast as fast
from cfb_analytics.sources.cfbd.client import CfbdClient

CHALLENGE_VERSION = "historical-player-team-year-wheel-v2"
WHEEL_SPINS = 7
TARGET_PLAYABLE_ORACLE_WIN_RATE = 0.001
MIN_RAW_FEASIBLE_RATE = 0.50
PRICE_UNIT = 10  # 0.1M increments
DEFAULT_SIMULATIONS = 50_000
DEFAULT_SEED = 7319

# Keep the already-reviewed fictional release market. Only the total cap is selected
# by the new wheel simulation.
RELEASE_PRICE_BANDS = {
    "QB": (1.0, 5.5),
    "RB": (0.4, 2.8),
    "WR": (0.6, 3.8),
    "TE": (0.4, 2.5),
    "DL": (0.6, 3.4),
    "LB": (0.5, 2.8),
    "DB": (0.5, 3.2),
}


def _compact_wheel_player(row: dict[str, Any]) -> dict[str, Any]:
    ratings: dict[str, dict[str, Any]] = {}
    for slot in base.SLOT_ORDER:
        rating = (row.get("slotRatings") or {}).get(slot)
        if not rating:
            continue
        ratings[slot] = {
            "grade": round(float(rating["grade"]), 1),
            "letter": str(rating["letter"]),
            "powerZ": float(rating["powerZ"]),
            "eraScore": round(float(rating["eraScore"]), 6),
        }
    stats = {
        key: round(float(value), 3)
        for key, value in (row.get("stats") or {}).items()
        if base._number(value) is not None and abs(float(value)) > 1e-12
    }
    stable = row.get("playerId")
    if stable is None:
        import hashlib

        stable = hashlib.sha1(
            f"{row['season']}|{row['team']}|{row['player']}|{row['position']}".encode()
        ).hexdigest()[:14]
    return {
        "playerSeasonId": f"{row['season']}:{stable}:{row['team']}",
        "playerId": row.get("playerId"),
        "player": row["player"],
        "season": int(row["season"]),
        "team": row["team"],
        "position": row["position"],
        "positionGroup": row["positionGroup"],
        "eligibleSlots": [slot for slot in base.SLOT_ORDER if slot in ratings],
        "ratings": ratings,
        "conference": row.get("conference"),
        "teamId": row.get("teamId"),
        "abbreviation": row.get("abbreviation"),
        "logo": row.get("logo"),
        "color": row.get("color"),
        "alternateColor": row.get("alternateColor"),
        "nilAskMillions": float(row["nilAskMillions"]),
        "stats": stats,
    }


def build_wheel_entries(
    rows: list[dict[str, Any]],
    team_lineups: dict[str, dict[str, Any]],
    srs_by_key: dict[str, float],
) -> list[dict[str, Any]]:
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if not row.get("slotRatings"):
            continue
        key = f"{int(row['season'])}::{row['team']}"
        if key not in team_lineups:
            continue
        if int(row["season"]) == base.TARGET_SEASON and str(row["team"]).casefold() == base.TARGET_TEAM.casefold():
            continue
        by_key[key].append(row)

    entries: list[dict[str, Any]] = []
    for key, team_rows in by_key.items():
        lineup = team_lineups[key]
        season = int(lineup["season"])
        team = str(lineup["team"])
        compact = [_compact_wheel_player(row) for row in team_rows]
        compact.sort(
            key=lambda p: (
                -max(float(r["grade"]) for r in p["ratings"].values()),
                float(p["nilAskMillions"]),
                str(p["player"]),
            )
        )
        if not compact:
            continue
        entries.append(
            {
                "id": key,
                "season": season,
                "team": team,
                "conference": compact[0].get("conference"),
                "teamId": compact[0].get("teamId"),
                "abbreviation": compact[0].get("abbreviation"),
                "logo": compact[0].get("logo"),
                "color": compact[0].get("color"),
                "alternateColor": compact[0].get("alternateColor"),
                "srs": srs_by_key.get(key),
                "rosterCount": len(compact),
                "roster": compact,
            }
        )
    entries.sort(key=lambda row: (int(row["season"]), str(row["team"])))
    if len(entries) < 50:
        raise ValueError(f"Wheel pool unexpectedly small: {len(entries)} complete team-seasons")
    return entries


def _pareto_options(entry: dict[str, Any]) -> dict[str, list[tuple[int, float, str]]]:
    """Return nondominated (cost, weighted power, playerSeasonId) choices per slot."""
    out: dict[str, list[tuple[int, float, str]]] = {}
    for slot in base.SLOT_ORDER:
        best_by_cost: dict[int, tuple[float, str]] = {}
        for player in entry["roster"]:
            rating = (player.get("ratings") or {}).get(slot)
            if not rating:
                continue
            cost = int(round(float(player["nilAskMillions"]) * PRICE_UNIT))
            power = float(base.SLOT_WEIGHTS[slot]) * float(rating["powerZ"])
            current = best_by_cost.get(cost)
            if current is None or power > current[0]:
                best_by_cost[cost] = (power, str(player["playerSeasonId"]))
        frontier: list[tuple[int, float, str]] = []
        best_power = -float("inf")
        for cost in sorted(best_by_cost):
            power, psid = best_by_cost[cost]
            if power > best_power + 1e-12:
                frontier.append((cost, power, psid))
                best_power = power
        out[slot] = frontier
    return out


def _prune(states: list[tuple[int, float]]) -> list[tuple[int, float]]:
    if not states:
        return []
    best_by_cost: dict[int, float] = {}
    for cost, power in states:
        if power > best_by_cost.get(cost, -float("inf")):
            best_by_cost[cost] = power
    frontier: list[tuple[int, float]] = []
    best_power = -float("inf")
    for cost in sorted(best_by_cost):
        power = best_by_cost[cost]
        if power > best_power + 1e-12:
            frontier.append((cost, power))
            best_power = power
    return frontier


def _draw_frontier(
    draw: list[int],
    options_by_entry: list[dict[str, list[tuple[int, float, str]]]],
) -> list[tuple[int, float]]:
    """Exact Pareto frontier for one player from each spin and every slot exactly once."""
    states: dict[int, list[tuple[int, float]]] = {0: [(0, 0.0)]}
    for entry_idx in draw:
        options = options_by_entry[entry_idx]
        next_states: dict[int, list[tuple[int, float]]] = defaultdict(list)
        for mask, frontier in states.items():
            for slot_idx, slot in enumerate(base.SLOT_ORDER):
                bit = 1 << slot_idx
                if mask & bit:
                    continue
                for player_cost, player_power, _ in options.get(slot, []):
                    for cost, power in frontier:
                        next_states[mask | bit].append((cost + player_cost, power + player_power))
        states = {mask: _prune(values) for mask, values in next_states.items()}
    return states.get((1 << len(base.SLOT_ORDER)) - 1, [])


def _result_probability(power: float, boss_power: float, calibration: dict[str, Any]) -> float:
    margin = float(calibration["rosterPowerToMargin"]) * (power - boss_power)
    sd = float(calibration["residualSd"])
    if sd <= 0:
        return 1.0 if margin > 0 else 0.0 if margin < 0 else 0.5
    return NormalDist().cdf(margin / sd)


def benchmark_team_year_wheel(
    entries: list[dict[str, Any]],
    boss_power: float,
    calibration: dict[str, Any],
    *,
    simulations: int = DEFAULT_SIMULATIONS,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    if len(entries) < WHEEL_SPINS:
        raise ValueError("Not enough wheel entries")
    rng = random.Random(seed)
    options_by_entry = [_pareto_options(entry) for entry in entries]
    draws = [rng.sample(range(len(entries)), WHEEL_SPINS) for _ in range(simulations)]

    min_completion_costs: list[int | None] = []
    min_winning_costs: list[int | None] = []
    for idx, draw in enumerate(draws, start=1):
        frontier = _draw_frontier(draw, options_by_entry)
        if frontier:
            min_completion_costs.append(min(cost for cost, _ in frontier))
            winning = [cost for cost, power in frontier if power > boss_power + 1e-12]
            min_winning_costs.append(min(winning) if winning else None)
        else:
            min_completion_costs.append(None)
            min_winning_costs.append(None)
        if idx % 5000 == 0:
            print(f"wheel benchmark frontiers={idx}/{simulations}", flush=True)

    # Search every 0.1M cap in a generous range. The cap is a simulation output,
    # not a hand-picked product number.
    max_seen = max((cost for cost in min_completion_costs if cost is not None), default=300)
    max_candidate = max(300, max_seen + 80)
    sweep: list[dict[str, Any]] = []
    for budget_units in range(40, max_candidate + 1):
        feasible = sum(cost is not None and cost <= budget_units for cost in min_completion_costs)
        wins = sum(cost is not None and cost <= budget_units for cost in min_winning_costs)
        feasible_rate = feasible / simulations
        conditional_win = wins / feasible if feasible else 0.0
        sweep.append(
            {
                "budgetMillions": budget_units / PRICE_UNIT,
                "feasibleRate": feasible_rate,
                "oracleWinRate": wins / simulations,
                "playableOracleWinRate": conditional_win,
                "feasibleRuns": feasible,
                "oracleWins": wins,
            }
        )

    eligible = [
        row
        for row in sweep
        if float(row["feasibleRate"]) >= MIN_RAW_FEASIBLE_RATE and int(row["oracleWins"]) > 0
    ]
    if not eligible:
        raise ValueError("No budget candidate produced a playable and beatable wheel")
    selected = min(
        eligible,
        key=lambda row: (
            abs(float(row["playableOracleWinRate"]) - TARGET_PLAYABLE_ORACLE_WIN_RATE),
            abs(float(row["oracleWinRate"]) - TARGET_PLAYABLE_ORACLE_WIN_RATE),
            -float(row["feasibleRate"]),
            float(row["budgetMillions"]),
        ),
    )
    selected_units = int(round(float(selected["budgetMillions"]) * PRICE_UNIT))

    probabilities: list[float] = []
    for idx, draw in enumerate(draws, start=1):
        frontier = _draw_frontier(draw, options_by_entry)
        affordable = [power for cost, power in frontier if cost <= selected_units]
        if affordable:
            probabilities.append(_result_probability(max(affordable), boss_power, calibration))
        if idx % 5000 == 0:
            print(f"wheel benchmark selected-cap pass={idx}/{simulations}", flush=True)

    selected = {
        **selected,
        "meanBestPossibleWinProbability": mean(probabilities) if probabilities else 0.0,
        "maxBestPossibleWinProbability": max(probabilities) if probabilities else 0.0,
        "minBestPossibleWinProbability": min(probabilities) if probabilities else 0.0,
        "oneInApproximately": (
            round(1.0 / float(selected["playableOracleWinRate"]))
            if float(selected["playableOracleWinRate"]) > 0
            else None
        ),
    }
    return {
        "version": "team-year-wheel-oracle-cap-v1",
        "simulations": simulations,
        "seed": seed,
        "spinsPerRun": WHEEL_SPINS,
        "drawWithoutReplacement": True,
        "targetPlayableOracleWinRate": TARGET_PLAYABLE_ORACLE_WIN_RATE,
        "targetDescription": "Among budget-feasible seven-spin runs, the best mathematically possible roster should beat 2019 LSU about 1 run in 1,000.",
        "rawFeasibilityFloorForSelection": MIN_RAW_FEASIBLE_RATE,
        "selectedBudgetMillions": selected["budgetMillions"],
        "selected": selected,
        "budgetSweep": sweep,
        "playableRunRule": "If a seven-team draw has no valid seven-player roster under the cap, redraw the hidden seven-team board before the first spin.",
        "noUserOutcomeTuning": True,
    }


def build_dataset(
    client: CfbdClient,
    *,
    seasons: tuple[int, ...] = base.DEFAULT_SEASONS,
    simulations: int = DEFAULT_SIMULATIONS,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    base.NIL_PRICE_BANDS = dict(RELEASE_PRICE_BANDS)
    metadata = base._team_metadata(client.teams().payload)
    all_players: list[dict[str, Any]] = []
    all_games: list[dict[str, Any]] = []
    srs_by_key: dict[str, float] = {}
    source_status: dict[str, Any] = {}

    for season in seasons:
        teams, srs_map = fast._srs_for_season(client, season, metadata)
        srs_by_key.update({f"{season}::{team}": rating for team, rating in srs_map.items()})
        season_players: list[dict[str, Any]] = []
        raw_rows = 0
        for team in teams:
            payload = client.get_json(
                "/stats/player/season",
                {"year": season, "team": team, "seasonType": "both"},
            ).payload
            if isinstance(payload, list):
                raw_rows += len(payload)
            season_players.extend(base.aggregate_player_stats(season, payload, metadata))
        games = base._fetch_optional(
            client,
            "/games",
            {"year": season, "seasonType": "both", "classification": "fbs"},
        )
        all_players.extend(season_players)
        if isinstance(games, list):
            all_games.extend(game for game in games if isinstance(game, dict))
        source_status[str(season)] = {
            "teamsFetched": teams,
            "teamCount": len(teams),
            "playerStatRows": raw_rows,
            "playerSeasons": len(season_players),
            "srsTeams": len(srs_map),
            "games": len(games) if isinstance(games, list) else 0,
        }
        print(
            f"season={season} teams={len(teams)} playerRows={raw_rows} players={len(season_players)}",
            flush=True,
        )

    base.score_players(all_players)
    base.assign_nil_prices(all_players)
    base._best_unique_lineup = fast.efficient_best_unique_lineup
    team_lineups = base.build_team_lineups(all_players)
    boss_record = team_lineups.get(f"{base.TARGET_SEASON}::{base.TARGET_TEAM}")
    if not boss_record:
        raise ValueError("Could not construct complete 2019 LSU seven-player boss roster")
    calibration = fast.fit_two_stage_margin_calibration(team_lineups, srs_by_key, all_games)
    wheel_entries = build_wheel_entries(all_players, team_lineups, srs_by_key)
    difficulty = benchmark_team_year_wheel(
        wheel_entries,
        float(boss_record["composite"]),
        calibration,
        simulations=simulations,
        seed=seed,
    )
    budget = float(difficulty["selectedBudgetMillions"])

    return {
        "schemaVersion": 2,
        "challengeVersion": CHALLENGE_VERSION,
        "status": "data-prototype-playable",
        "title": f"Can ${budget:g}M in NIL Beat the 2019 LSU Tigers?",
        "subtitle": "Spin a team and year. Sign one historical player. Seven spins to build the impossible roster.",
        "seasons": list(seasons),
        "excludedSeasons": list(base.EXCLUDED_SEASONS),
        "target": {
            "season": base.TARGET_SEASON,
            "team": base.TARGET_TEAM,
            "rosterPower": float(boss_record["composite"]),
            "lineup": {
                slot: {**boss_record["lineup"][slot], "bossSlot": slot}
                for slot in base.SLOT_ORDER
            },
            "logo": metadata.get(base.TARGET_TEAM, {}).get("logo"),
            "conference": metadata.get(base.TARGET_TEAM, {}).get("conference"),
        },
        "rules": {
            "budgetMillions": budget,
            "spins": WHEEL_SPINS,
            "requiredPlayers": WHEEL_SPINS,
            "slots": list(base.SLOT_ORDER),
            "slotWeights": base.SLOT_WEIGHTS,
            "oneSigningPerSpin": True,
            "drawWithoutReplacement": True,
            "winThreshold": base.WIN_THRESHOLD,
            "site": "neutral",
            "playableRunRule": difficulty["playableRunRule"],
            "nilDisclaimer": "SOAR NIL asks are fictional gameplay values derived from historical production and position scarcity. They are not real or historical NIL valuations.",
        },
        "grading": {
            "version": "era-adjusted-player-percentile-v1",
            "description": "Player metrics are ranked against same-season peers at the offered roster slot, then normalized across supported seasons into a 1-99 SOAR production grade.",
            "metricWeights": base.METRIC_WEIGHTS,
        },
        "nilPricing": {
            "version": "soar-fictional-nil-ask-v1",
            "priceBandsMillions": base.NIL_PRICE_BANDS,
            "selectedCapMethod": "Monte Carlo oracle calibration on seven random complete team-seasons; cap selected before user outcomes.",
        },
        "matchupCalibration": calibration,
        "difficultyBenchmark": difficulty,
        "wheel": {
            "entryCount": len(wheel_entries),
            "entries": wheel_entries,
        },
        "sourceStatus": source_status,
        "dataNotes": [
            "Each spin reveals one complete historical team-season roster from the SOAR player pool.",
            "The user signs exactly one player from each spin and must fill QB, RB, WR, FLEX, DL, LB and DB.",
            "The best-possible comparison is an exact budget-constrained optimization over the same seven team-seasons the user drew.",
            "The displayed 1-in-N difficulty is measured on playable boards before any user outcomes exist.",
            "The current wheel pool uses complete team-seasons among the top 10 SRS FBS teams fetched per supported season.",
            "2020 is excluded to match the existing SOAR historical support policy.",
            "Defensive grades are production-based statistical ratings, not film/scouting grades.",
            "The game is separate from Prediction-v2 and does not alter any prospective model artifact.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("data/prototypes/beat-2019-lsu/team-year-wheel-v2.json"))
    parser.add_argument("--simulations", type=int, default=DEFAULT_SIMULATIONS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    if not args.build:
        parser.error("--build is required")
    client = CfbdClient()
    payload = build_dataset(client, simulations=args.simulations, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    selected = payload["difficultyBenchmark"]["selected"]
    print("TEAM-YEAR PLAYER NIL WHEEL: PASS")
    print(f"output={args.output}")
    print(f"title={payload['title']}")
    print(f"wheelEntries={payload['wheel']['entryCount']}")
    print(f"budget=${payload['rules']['budgetMillions']:g}M")
    print(f"simulations={payload['difficultyBenchmark']['simulations']}")
    print(f"rawFeasibleRate={selected['feasibleRate']}")
    print(f"oracleWinRate={selected['oracleWinRate']}")
    print(f"playableOracleWinRate={selected['playableOracleWinRate']}")
    print(f"oneInApproximately={selected['oneInApproximately']}")
    print(f"meanBestPossibleP={selected['meanBestPossibleWinProbability']}")
    print(f"maxBestPossibleP={selected['maxBestPossibleWinProbability']}")


if __name__ == "__main__":
    main()
