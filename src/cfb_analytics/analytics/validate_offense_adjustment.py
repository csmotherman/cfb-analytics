"""Out-of-sample validation for raw, one-pass, and least-squares offense models.

Uses deterministic game-level K-fold cross-validation. Both team rows from the
same game are assigned to the same fold, preventing mirror-row leakage.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from typing import Any
import numpy as np

from cfb_analytics.analytics.opponent_adjusted_offense import (
    Totals, _eligible_rows, calculate_opponent_adjusted_offense,
    defensive_totals, metrics, offensive_totals,
)
from cfb_analytics.analytics.least_squares_offense import METRICS, _solve_metric

FIELD_NAMES = {
    "ppd": "points per drive",
    "ypd": "yards per drive",
    "success": "success rate",
    "scoring": "scoring drive rate",
}


def _game_id(row: dict[str, Any]) -> str:
    return str(row.get("gameId") or row.get("game_id"))


def _fold_for_game(game_id: str, folds: int, seed: str) -> int:
    digest = hashlib.sha256(f"{seed}:{game_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % folds


def _aggregate(rows: list[dict[str, Any]], *, defense: bool) -> dict[int, Totals]:
    out: dict[int, Totals] = {}
    for row in rows:
        tid = int(row["team_id"])
        total = defensive_totals(row) if defense else offensive_totals(row)
        out[tid] = out.get(tid, Totals()) + total
    return out


def _national_baseline(rows: list[dict[str, Any]], metric_idx: int) -> float:
    total = Totals()
    for row in rows:
        total = total + offensive_totals(row)
    value = metrics(total)[metric_idx]
    if value is None:
        raise ValueError("National baseline unavailable")
    return float(value)


def _metric_from_totals(total: Totals, metric_idx: int) -> float | None:
    value = metrics(total)[metric_idx]
    return None if value is None else float(value)


def _evaluate_fold(train: list[dict[str, Any]], test: list[dict[str, Any]]) -> dict[str, list[tuple[float,float,float,float,float]]]:
    """Return metric -> (actual, raw_pred, one_pass_pred, ls_pred, weight)."""
    raw_offense = _aggregate(train, defense=False)
    raw_defense = _aggregate(train, defense=True)
    one_pass_rows = calculate_opponent_adjusted_offense(train, int(train[0]["season"]))
    one_pass = {int(r["team_id"]): r for r in one_pass_rows}
    ls = {name: _solve_metric(train, name) for name in METRICS}
    out = {name: [] for name in METRICS}

    one_pass_fields = {
        "ppd": "adjusted_points_per_drive",
        "ypd": "adjusted_yards_per_drive",
        "success": "adjusted_success_rate",
        "scoring": "adjusted_scoring_drive_rate",
    }
    for name, (idx, weight_attr) in METRICS.items():
        national = _national_baseline(train, idx)
        solved = ls[name]
        for row in test:
            tid, oid = int(row["team_id"]), int(row["opponent_id"])
            if tid not in raw_offense or oid not in raw_defense or tid not in one_pass:
                continue
            if tid not in solved["offense_effect"] or oid not in solved["defense_effect"]:
                continue
            off = offensive_totals(row)
            actual = metrics(off)[idx]
            weight = float(getattr(off, weight_attr))
            team_raw = _metric_from_totals(raw_offense[tid], idx)
            opp_allow = _metric_from_totals(raw_defense[oid], idx)
            if actual is None or team_raw is None or opp_allow is None or weight <= 0:
                continue
            # Raw predicts the team's training average regardless of opponent.
            raw_pred = team_raw
            # V1 neutral offense plus the held-out opponent's training defensive
            # allowance relative to the national environment.
            neutral = float(one_pass[tid][one_pass_fields[name]])
            one_pred = neutral + (opp_allow - national)
            ls_pred = float(solved["baseline"] + solved["offense_effect"][tid] - solved["defense_effect"][oid])
            out[name].append((float(actual), raw_pred, one_pred, ls_pred, weight))
    return out


def _errors(obs: list[tuple[float,float,float,float,float]]) -> dict[str, dict[str,float]]:
    if not obs:
        return {m: {"mae": float("nan"), "rmse": float("nan")} for m in ("raw","one_pass","least_squares")}
    actual = np.asarray([x[0] for x in obs]); weights = np.asarray([x[4] for x in obs])
    result = {}
    for label, pos in (("raw",1),("one_pass",2),("least_squares",3)):
        pred = np.asarray([x[pos] for x in obs]); err = pred-actual
        result[label] = {
            "mae": float(np.average(np.abs(err), weights=weights)),
            "rmse": float(math.sqrt(np.average(err**2, weights=weights))),
        }
    return result


def cross_validate(rows: list[dict[str, Any]], season: int, folds: int = 5, seed: str = "cfb-analytics-v1") -> dict[str, Any]:
    rows = _eligible_rows(rows, season)
    if folds < 2:
        raise ValueError("folds must be >= 2")
    games = sorted({_game_id(r) for r in rows})
    bucket = {gid: _fold_for_game(gid, folds, seed) for gid in games}
    combined = {name: [] for name in METRICS}
    fold_counts = []
    for fold in range(folds):
        train = [r for r in rows if bucket[_game_id(r)] != fold]
        test = [r for r in rows if bucket[_game_id(r)] == fold]
        if not train or not test:
            continue
        fold_result = _evaluate_fold(train, test)
        fold_counts.append({"fold": fold, "train_rows": len(train), "test_rows": len(test), "test_games": len({_game_id(r) for r in test})})
        for name in METRICS:
            combined[name].extend(fold_result[name])
    return {
        "season": season,
        "folds": folds,
        "games": len(games),
        "fold_counts": fold_counts,
        "metrics": {name: {"observations": len(combined[name]), "errors": _errors(combined[name])} for name in METRICS},
    }


def load(path: Path):
    with path.open(encoding="utf-8") as h:
        return json.load(h)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Out-of-sample test of raw, one-pass, and LS offense adjustment")
    p.add_argument("--season", type=int, default=2025)
    p.add_argument("--input", type=Path)
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seed", default="cfb-analytics-v1")
    a = p.parse_args(argv)
    path = a.input or Path(f"data/canonical/season={a.season}/team_games.json")
    result = cross_validate(load(path), a.season, a.folds, a.seed)
    print(f"\nOpponent Adjustment Out-of-Sample Validation — {a.season}")
    print(f"Game-level {result['folds']}-fold CV | {result['games']} FBS-vs-FBS games")
    print("Lower MAE/RMSE is better. Errors are opportunity-weighted.\n")
    for name in ("ppd","ypd","success","scoring"):
        block = result["metrics"][name]
        print(f"{FIELD_NAMES[name].upper()}  ({block['observations']} held-out team-games)")
        for model in ("raw","one_pass","least_squares"):
            e = block["errors"][model]
            print(f"  {model:<14} MAE {e['mae']:.5f}   RMSE {e['rmse']:.5f}")
        raw_rmse = block["errors"]["raw"]["rmse"]
        for model in ("one_pass","least_squares"):
            rmse = block["errors"][model]["rmse"]
            gain = (raw_rmse-rmse)/raw_rmse*100 if raw_rmse else float("nan")
            print(f"    {model:<13} RMSE improvement vs raw: {gain:+.2f}%")
        print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
