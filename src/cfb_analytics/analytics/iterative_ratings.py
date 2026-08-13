"""Leakage-safe iterative offense/defense ratings over the pregame schedule graph."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.model_feature_contract import iterative_matchup_value
from cfb_analytics.derived.pregame import (
    _pk,
    build_matchup_features,
    build_model_dataset,
    build_pregame_snapshots,
    game_contexts,
    load_team_games,
)

ITERATIVE_RATINGS_VERSION = "iterative-ratings-v2-directional"

SPECS = (
    ("Success", "successfulPlays", "successEligiblePlays"),
    ("Explosive", "explosivePlays", "explosiveEligiblePlays"),
    ("YardsPerPlay", "offensiveYards", "offensivePlays"),
    ("YardsPerPossession", "offensiveYards", "validatedPossessions"),
    ("Finishing", "opportunityPoints", "resolvedPointOpportunities"),
    ("FieldPosition", "startOwnYardLineTotal", "fieldPositionPossessions"),
)

ITERATIVE_FEATURES = tuple(
    feature
    for name, *_ in SPECS
    for feature in (f"home_iterative{name}Edge", f"away_iterative{name}Edge")
)


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _observations(rows: list[dict[str, Any]], spec: tuple[str, str, str]) -> list[tuple[str, str, float, float]]:
    _, numerator, denominator = spec
    out = []
    for row in rows:
        team, opponent = row.get("team"), row.get("opponent")
        if not team or not opponent or not _num(row.get(numerator)) or not _num(row.get(denominator)):
            continue
        weight = float(row[denominator])
        if weight <= 0:
            continue
        out.append((str(team), str(opponent), float(row[numerator]) / weight, weight))
    return out


def fit_metric_ratings(
    rows: list[dict[str, Any]],
    spec: tuple[str, str, str],
    shrinkage: float = 50.0,
    damping: float = 1.0,
    tolerance: float = 1e-7,
    max_iterations: int = 2000,
) -> dict[str, Any]:
    """Fit y = mean + offense(team) - defense(opponent) by block coordinate descent.

    Shrinkage makes the offense/defense solution identifiable and stabilizes sparse
    schedules. Ratings are centered only after convergence; the intercept is shifted
    by the same amount so fitted game values are unchanged.
    """
    if shrinkage < 0:
        raise ValueError("shrinkage must be nonnegative")
    if not 0 < damping <= 1:
        raise ValueError("damping must be in (0, 1]")
    if tolerance <= 0 or max_iterations < 1:
        raise ValueError("tolerance and max_iterations must be positive")

    obs = _observations(rows, spec)
    if not obs:
        return {
            "leagueMean": None,
            "offense": {},
            "defense": {},
            "iterations": 0,
            "converged": True,
            "maxDelta": 0.0,
        }

    total_weight = sum(weight for *_, weight in obs)
    league_mean = sum(value * weight for _, _, value, weight in obs) / total_weight
    teams = sorted({team for team, _, _, _ in obs} | {opp for _, opp, _, _ in obs})
    offense = {team: 0.0 for team in teams}
    defense = {team: 0.0 for team in teams}
    by_offense: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    by_defense: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for team, opponent, value, weight in obs:
        by_offense[team].append((opponent, value, weight))
        by_defense[opponent].append((team, value, weight))

    converged = False
    max_delta = float("inf")
    iteration = 0
    for iteration in range(1, max_iterations + 1):
        new_offense = dict(offense)
        for team, games in by_offense.items():
            weight = sum(w for _, _, w in games)
            raw = sum(w * (value - league_mean + defense[opponent]) for opponent, value, w in games)
            target = raw / (weight + shrinkage)
            new_offense[team] = offense[team] + damping * (target - offense[team])

        new_defense = dict(defense)
        for team, games in by_defense.items():
            weight = sum(w for _, _, w in games)
            raw = sum(w * (league_mean + new_offense[opponent] - value) for opponent, value, w in games)
            target = raw / (weight + shrinkage)
            new_defense[team] = defense[team] + damping * (target - defense[team])

        max_delta = max(
            max(abs(new_offense[t] - offense[t]) for t in teams),
            max(abs(new_defense[t] - defense[t]) for t in teams),
        )
        offense, defense = new_offense, new_defense
        if max_delta <= tolerance:
            converged = True
            break

    off_mean = sum(offense.values()) / len(offense)
    def_mean = sum(defense.values()) / len(defense)
    offense = {team: value - off_mean for team, value in offense.items()}
    defense = {team: value - def_mean for team, value in defense.items()}
    league_mean = league_mean + off_mean - def_mean

    return {
        "leagueMean": league_mean,
        "offense": offense,
        "defense": defense,
        "iterations": iteration,
        "converged": converged,
        "maxDelta": max_delta,
    }


def fit_all_ratings(rows: list[dict[str, Any]], **kwargs: Any) -> dict[str, dict[str, Any]]:
    return {spec[0]: fit_metric_ratings(rows, spec, **kwargs) for spec in SPECS}


def build_iterative_rating_snapshots(team_games: list[dict[str, Any]], season: int, **kwargs: Any) -> list[dict[str, Any]]:
    rows = [r for r in team_games if r.get("season") == season]
    partitions: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        partitions[_pk(row)].append(row)

    history: list[dict[str, Any]] = []
    games_played: Counter[str] = Counter()
    out: list[dict[str, Any]] = []
    for key in sorted(partitions):
        fitted = fit_all_ratings(history, **kwargs) if history else {}
        for game in partitions[key]:
            team = str(game.get("team"))
            snap: dict[str, Any] = {
                "season": season,
                "seasonType": game.get("seasonType"),
                "week": game.get("week"),
                "gameId": game.get("gameId"),
                "team": game.get("team"),
                "opponent": game.get("opponent"),
                "gamesPlayedBefore": games_played[team],
                "iterativeRatingsVersion": ITERATIVE_RATINGS_VERSION,
            }
            for name, *_ in SPECS:
                result = fitted.get(name, {})
                snap[f"iterative{name}Offense"] = result.get("offense", {}).get(team)
                snap[f"iterative{name}Defense"] = result.get("defense", {}).get(team)
                snap[f"iterative{name}LeagueMean"] = result.get("leagueMean")
                snap[f"iterative{name}Converged"] = bool(result.get("converged", True))
                snap[f"iterative{name}Iterations"] = int(result.get("iterations", 0))
                snap[f"iterative{name}MaxDelta"] = float(result.get("maxDelta", 0.0))
            out.append(snap)
        for game in partitions[key]:
            games_played[str(game.get("team"))] += 1
        history.extend(partitions[key])
    return out


def build_iterative_model_dataset(base_rows: list[dict[str, Any]], rating_snapshots: list[dict[str, Any]], season: int) -> list[dict[str, Any]]:
    by_game: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for snap in rating_snapshots:
        if snap.get("season") == season:
            by_game[str(snap.get("gameId"))].append(snap)

    out = []
    for base in base_rows:
        if base.get("season") != season:
            continue
        pair = by_game.get(str(base.get("gameId")), [])
        if len(pair) != 2:
            continue
        by_team = {row.get("team"): row for row in pair}
        home = by_team.get(base.get("homeTeam"))
        away = by_team.get(base.get("awayTeam"))
        if not home or not away:
            continue
        row = dict(base)
        row["iterativeRatingsVersion"] = ITERATIVE_RATINGS_VERSION
        row["homeIterativeGamesPlayedBefore"] = home.get("gamesPlayedBefore", 0)
        row["awayIterativeGamesPlayedBefore"] = away.get("gamesPlayedBefore", 0)
        for name, *_ in SPECS:
            ho, hd = home.get(f"iterative{name}Offense"), home.get(f"iterative{name}Defense")
            ao, ad = away.get(f"iterative{name}Offense"), away.get(f"iterative{name}Defense")
            row[f"home_iterative{name}Offense"] = ho
            row[f"home_iterative{name}Defense"] = hd
            row[f"away_iterative{name}Offense"] = ao
            row[f"away_iterative{name}Defense"] = ad
            row[f"home_iterative{name}Edge"] = iterative_matchup_value(ho, ad) if _num(ho) and _num(ad) else None
            row[f"away_iterative{name}Edge"] = iterative_matchup_value(ao, hd) if _num(ao) and _num(hd) else None
        out.append(row)
    return out


def eligible_iterative_row(row: dict[str, Any], min_games: int) -> bool:
    return (
        int(row.get("homeIterativeGamesPlayedBefore", 0)) >= min_games
        and int(row.get("awayIterativeGamesPlayedBefore", 0)) >= min_games
        and row.get("target_homeWin") in (0, 1)
        and _num(row.get("target_margin"))
        and all(_num(row.get(feature)) for feature in ITERATIVE_FEATURES)
    )


def iterative_ratings_audit(team_games: list[dict[str, Any]], rating_snapshots: list[dict[str, Any]], model_rows: list[dict[str, Any]], season: int) -> dict[str, Any]:
    games = [r for r in team_games if r.get("season") == season]
    expected_keys = {(str(r.get("gameId")), r.get("team")) for r in games}
    actual_keys = {(str(r.get("gameId")), r.get("team")) for r in rating_snapshots}
    nonconverged = [
        (r.get("gameId"), r.get("team"), name, r.get(f"iterative{name}Iterations"), r.get(f"iterative{name}MaxDelta"))
        for r in rating_snapshots
        for name, *_ in SPECS
        if r.get(f"iterative{name}Converged") is not True
    ]
    checks = {
        "one_rating_snapshot_per_team_game": len(rating_snapshots) == len(games),
        "rating_keys_match_team_games": actual_keys == expected_keys,
        "version_present": all(r.get("iterativeRatingsVersion") == ITERATIVE_RATINGS_VERSION for r in rating_snapshots),
        "games_played_is_prior_only": all(
            int(r.get("gamesPlayedBefore", -1))
            == sum(1 for g in games if g.get("team") == r.get("team") and _pk(g) < _pk(r))
            for r in rating_snapshots
        ),
        "all_reported_solvers_converged": not nonconverged,
        "model_rows_preserved": len(model_rows) == len({str(r.get("gameId")) for r in games}),
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "season": season,
        "rating_snapshot_rows": len(rating_snapshots),
        "model_rows": len(model_rows),
        "eligible_min3": sum(eligible_iterative_row(r, 3) for r in model_rows),
        "eligible_min4": sum(eligible_iterative_row(r, 4) for r in model_rows),
        "nonconverged_solver_snapshots": len(nonconverged),
        "worst_nonconverged": max(nonconverged, key=lambda x: float(x[4] or 0.0), default=None),
        "checks": checks,
    }


def concise(result: dict[str, Any]) -> str:
    lines = [
        f"ITERATIVE RATINGS v2 DIRECTIONAL AUDIT: {result['status']}",
        f"Season: {result['season']}",
        f"Rating snapshot rows: {result['rating_snapshot_rows']:,}",
        f"Model rows: {result['model_rows']:,}",
        f"Eligible (3+ prior games each): {result['eligible_min3']:,}",
        f"Eligible (4+ prior games each): {result['eligible_min4']:,}",
        f"Non-converged solver snapshots: {result['nonconverged_solver_snapshots']:,}",
        "",
        "Checks:",
    ]
    lines += [f"{name}: {'PASS' if ok else 'FAIL'}" for name, ok in result["checks"].items()]
    if result.get("worst_nonconverged") is not None:
        lines += ["", f"Worst non-converged: {result['worst_nonconverged']}"]
    return "\n".join(lines)


def materialize_iterative_model_dataset(raw_root: Path, processed_root: Path, season: int) -> dict[str, Any]:
    games = load_team_games(raw_root, processed_root, season)
    pregame = build_pregame_snapshots(games, season)
    matchups = build_matchup_features(pregame, season)
    base = build_model_dataset(matchups, game_contexts(raw_root, processed_root, season), season)
    ratings = build_iterative_rating_snapshots(games, season)
    rows = build_iterative_model_dataset(base, ratings, season)
    path = processed_root / "derived" / "iterative_ratings" / f"season={season}" / "games.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
    return {**iterative_ratings_audit(games, ratings, rows, season), "path": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    print(concise(materialize_iterative_model_dataset(args.raw_root, args.processed_root, args.season)))


if __name__ == "__main__":
    main()
