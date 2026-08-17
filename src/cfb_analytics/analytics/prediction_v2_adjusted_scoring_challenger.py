"""Opponent-adjusted scoring challenger for locked Prediction v2.

This research module does not mutate Prediction v2. It adds leakage-safe scoring
features built strictly from completed partitions before each target game and
evaluates them on the same outer-season OOS protocol as the locked benchmark.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from cfb_analytics.analytics.prediction_v1_integrity_audit import (
    MIN_GAMES_VALUES,
    finite,
    load_raw_games,
)
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    TEST_SEASONS,
    eligible_site,
    fit_generic,
    load_data,
    predict_generic,
    prepare_generic,
)
from cfb_analytics.analytics.prediction_v2 import PREDICTION_V2_FEATURES
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

CHALLENGER_VERSION = "prediction-v2-adjusted-scoring-v1"
RAW_MARGIN_FEATURE = "rawScoringMargin"
ADJ_MARGIN_FEATURE = "adjustedScoringMargin"
ADJ_OFFENSE_FEATURE = "adjustedScoringOffenseEdge"
ADJ_DEFENSE_FEATURE = "adjustedScoringDefenseEdge"

BASE_FEATURES = tuple(PREDICTION_V2_FEATURES)
VARIANTS: dict[str, tuple[str, ...]] = {
    "raw-ppg-margin": BASE_FEATURES + (RAW_MARGIN_FEATURE,),
    "adjusted-scoring-margin": BASE_FEATURES + (ADJ_MARGIN_FEATURE,),
    "adjusted-scoring-split": BASE_FEATURES
    + (ADJ_OFFENSE_FEATURE, ADJ_DEFENSE_FEATURE),
}


def partition_key(row: dict[str, Any]) -> tuple[int, int]:
    season_type = str(row.get("seasonType") or "regular").lower()
    return (
        0 if season_type in {"regular", "regular_season"} else 1,
        int(row.get("week") or 0),
    )


def _score_game(
    row: dict[str, Any],
    raw_games: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    gid = str(row.get("gameId"))
    raw = raw_games.get(gid)
    if raw is None:
        raise ValueError(f"Missing authoritative raw score for game {gid}")
    if not finite(raw.get("homeScore")) or not finite(raw.get("awayScore")):
        raise ValueError(f"Missing finite authoritative raw score for game {gid}")
    if raw.get("homeTeam") != row.get("homeTeam") or raw.get("awayTeam") != row.get("awayTeam"):
        raise ValueError(f"Raw/model home-away identity mismatch for game {gid}")
    neutral = row.get("isNeutralSite")
    if not isinstance(neutral, bool):
        raise ValueError(f"Missing neutral-site flag for game {gid}")
    return {
        "gameId": gid,
        "homeTeam": str(row["homeTeam"]),
        "awayTeam": str(row["awayTeam"]),
        "homePoints": float(raw["homeScore"]),
        "awayPoints": float(raw["awayScore"]),
        "isNeutralSite": neutral,
    }


def fit_adjusted_scoring(
    games: list[dict[str, Any]],
    *,
    ridge: float = 1e-6,
    tolerance: float = 1e-10,
    max_iterations: int = 10000,
) -> dict[str, Any]:
    """Fit score = base + offense(team) - defense(opponent) + site*hfa/2.

    Each completed game contributes two scoring observations. For a non-neutral
    game, the home observation uses +0.5 site and the away observation -0.5,
    so the fitted ``homeFieldAdvantage`` contributes directly to expected margin.
    A tiny ridge penalty on offense/defense ratings resolves disconnected and
    otherwise unidentified schedule components without touching the intercept or
    site coefficient.
    """
    if ridge <= 0.0 or tolerance <= 0.0 or max_iterations < 1:
        raise ValueError("ridge, tolerance, and max_iterations must be positive")

    observations: list[tuple[str, str, float, float]] = []
    for game in games:
        home = game.get("homeTeam")
        away = game.get("awayTeam")
        hp = game.get("homePoints")
        ap = game.get("awayPoints")
        neutral = game.get("isNeutralSite")
        if (
            not home
            or not away
            or home == away
            or not finite(hp)
            or not finite(ap)
            or not isinstance(neutral, bool)
        ):
            continue
        site = 0.0 if neutral else 0.5
        observations.append((str(home), str(away), float(hp), site))
        observations.append((str(away), str(home), float(ap), -site))

    teams = sorted({team for team, opponent, _, _ in observations for team in (team, opponent)})
    if not observations:
        return {
            "basePoints": None,
            "homeFieldAdvantage": 0.0,
            "offense": {},
            "defense": {},
            "games": 0,
            "observations": 0,
            "teams": 0,
            "iterations": 0,
            "converged": True,
            "maxDelta": 0.0,
            "fitRmse": None,
        }

    by_offense: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    by_defense: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    for team, opponent, points, site in observations:
        by_offense[team].append((opponent, points, site))
        by_defense[opponent].append((team, points, site))

    base = sum(points for _, _, points, _ in observations) / len(observations)
    hfa = 0.0
    offense = {team: 0.0 for team in teams}
    defense = {team: 0.0 for team in teams}
    converged = False
    max_delta = float("inf")
    iteration = 0

    for iteration in range(1, max_iterations + 1):
        old_base = base
        old_hfa = hfa
        old_offense = dict(offense)
        old_defense = dict(defense)

        for team in teams:
            rows = by_offense.get(team, [])
            numerator = sum(
                points - base + defense[opponent] - site * hfa
                for opponent, points, site in rows
            )
            offense[team] = numerator / (len(rows) + ridge) if rows else 0.0

        for team in teams:
            rows = by_defense.get(team, [])
            numerator = sum(
                base + offense[scoring_team] + site * hfa - points
                for scoring_team, points, site in rows
            )
            defense[team] = numerator / (len(rows) + ridge) if rows else 0.0

        base = sum(
            points - offense[team] + defense[opponent] - site * hfa
            for team, opponent, points, site in observations
        ) / len(observations)

        site_denominator = sum(site * site for _, _, _, site in observations)
        if site_denominator:
            hfa = sum(
                site * (points - base - offense[team] + defense[opponent])
                for team, opponent, points, site in observations
            ) / site_denominator
        else:
            hfa = 0.0

        max_delta = max(
            abs(base - old_base),
            abs(hfa - old_hfa),
            max(abs(offense[t] - old_offense[t]) for t in teams),
            max(abs(defense[t] - old_defense[t]) for t in teams),
        )
        if max_delta <= tolerance:
            converged = True
            break

    squared = []
    for team, opponent, points, site in observations:
        pred = base + offense[team] - defense[opponent] + site * hfa
        squared.append((pred - points) ** 2)

    return {
        "basePoints": base,
        "homeFieldAdvantage": hfa,
        "offense": offense,
        "defense": defense,
        "games": len(observations) // 2,
        "observations": len(observations),
        "teams": len(teams),
        "iterations": iteration,
        "converged": converged,
        "maxDelta": max_delta,
        "fitRmse": math.sqrt(sum(squared) / len(squared)),
    }


def _raw_margin(
    home: str,
    away: str,
    points_for: dict[str, float],
    points_against: dict[str, float],
    games_played: dict[str, int],
) -> float | None:
    if games_played.get(home, 0) <= 0 or games_played.get(away, 0) <= 0:
        return None
    home_ppg = points_for[home] / games_played[home]
    home_ppga = points_against[home] / games_played[home]
    away_ppg = points_for[away] / games_played[away]
    away_ppga = points_against[away] / games_played[away]
    home_expected = (home_ppg + away_ppga) / 2.0
    away_expected = (away_ppg + home_ppga) / 2.0
    return home_expected - away_expected


def add_scoring_features(
    rows: list[dict[str, Any]],
    raw_games: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach pregame raw and adjusted scoring features to one season's rows."""
    partitions: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        partitions[partition_key(row)].append(row)

    history: list[dict[str, Any]] = []
    points_for: dict[str, float] = defaultdict(float)
    points_against: dict[str, float] = defaultdict(float)
    games_played: dict[str, int] = defaultdict(int)
    out: list[dict[str, Any]] = []

    for key in sorted(partitions):
        fitted = fit_adjusted_scoring(history)
        offense = fitted["offense"]
        defense = fitted["defense"]
        base = fitted["basePoints"]
        hfa = float(fitted["homeFieldAdvantage"])

        for base_row in partitions[key]:
            row = dict(base_row)
            home = str(row.get("homeTeam"))
            away = str(row.get("awayTeam"))
            neutral = row.get("isNeutralSite")

            raw_margin = _raw_margin(
                home,
                away,
                points_for,
                points_against,
                games_played,
            )

            home_off = offense.get(home)
            away_off = offense.get(away)
            home_def = defense.get(home)
            away_def = defense.get(away)

            off_edge = (
                float(home_off) - float(away_off)
                if finite(home_off) and finite(away_off)
                else None
            )
            def_edge = (
                float(home_def) - float(away_def)
                if finite(home_def) and finite(away_def)
                else None
            )
            adj_margin = (
                float(off_edge)
                + float(def_edge)
                + (0.0 if neutral is True else hfa)
                if finite(off_edge) and finite(def_edge) and isinstance(neutral, bool)
                else None
            )

            home_expected = None
            away_expected = None
            if (
                finite(base)
                and finite(home_off)
                and finite(away_off)
                and finite(home_def)
                and finite(away_def)
                and isinstance(neutral, bool)
            ):
                site = 0.0 if neutral else hfa / 2.0
                home_expected = float(base) + float(home_off) - float(away_def) + site
                away_expected = float(base) + float(away_off) - float(home_def) - site

            row.update(
                {
                    RAW_MARGIN_FEATURE: raw_margin,
                    ADJ_MARGIN_FEATURE: adj_margin,
                    ADJ_OFFENSE_FEATURE: off_edge,
                    ADJ_DEFENSE_FEATURE: def_edge,
                    "adjustedScoringExpectedHomePoints": home_expected,
                    "adjustedScoringExpectedAwayPoints": away_expected,
                    "adjustedScoringBasePoints": base,
                    "adjustedScoringHfa": hfa,
                    "adjustedScoringGamesBefore": len(history),
                    "adjustedScoringConverged": fitted["converged"],
                    "adjustedScoringMaxDelta": fitted["maxDelta"],
                    "adjustedScoringFitRmse": fitted["fitRmse"],
                    "adjustedScoringVersion": CHALLENGER_VERSION,
                }
            )
            out.append(row)

        for completed in partitions[key]:
            game = _score_game(completed, raw_games)
            history.append(game)
            home = game["homeTeam"]
            away = game["awayTeam"]
            hp = float(game["homePoints"])
            ap = float(game["awayPoints"])
            points_for[home] += hp
            points_against[home] += ap
            games_played[home] += 1
            points_for[away] += ap
            points_against[away] += hp
            games_played[away] += 1

    return out


def load_challenger_data(
    raw_root: Path,
    processed_root: Path,
) -> dict[int, list[dict[str, Any]]]:
    base = load_data(raw_root, processed_root)
    out: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        raw_games, conflicts = load_raw_games(raw_root, season)
        if conflicts:
            raise ValueError(f"Conflicting raw game scores in {season}: {conflicts[:5]}")
        out[season] = add_scoring_features(base[season], raw_games)
    return out


def eligible_variant(
    row: dict[str, Any],
    min_games: int,
    features: tuple[str, ...],
) -> bool:
    return eligible_site(row, min_games) and all(finite(row.get(f)) for f in features)


def _score_rows(
    model: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, float]:
    absolute: list[float] = []
    squared: list[float] = []
    correct = 0
    for row in rows:
        prediction = predict_generic(model, row)
        actual = float(row["target_margin"])
        absolute.append(abs(prediction - actual))
        squared.append((prediction - actual) ** 2)
        correct += int((prediction > 0.0) == bool(row["target_homeWin"]))
    n = len(rows)
    return {
        "n": n,
        "mae": sum(absolute) / n,
        "rmse": math.sqrt(sum(squared) / n),
        "winner": correct / n,
    }


def evaluate(
    data: dict[int, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    per_game: list[dict[str, Any]] = []

    for min_games in MIN_GAMES_VALUES:
        base_eligible = {
            season: [row for row in data[season] if eligible_site(row, min_games)]
            for season in DEFAULT_SEASONS
        }

        variant_eligible: dict[str, dict[int, list[dict[str, Any]]]] = {}
        for name, features in VARIANTS.items():
            variant_eligible[name] = {
                season: [
                    row
                    for row in data[season]
                    if eligible_variant(row, min_games, features)
                ]
                for season in DEFAULT_SEASONS
            }
            for season in DEFAULT_SEASONS:
                base_ids = {str(row["gameId"]) for row in base_eligible[season]}
                variant_ids = {
                    str(row["gameId"]) for row in variant_eligible[name][season]
                }
                if base_ids != variant_ids:
                    missing = sorted(base_ids - variant_ids)[:10]
                    extra = sorted(variant_ids - base_ids)[:10]
                    raise ValueError(
                        f"Common-sample mismatch {name} {season} min{min_games}: "
                        f"base={len(base_ids)} challenger={len(variant_ids)} "
                        f"missing={missing} extra={extra}"
                    )

        for test_season in TEST_SEASONS:
            base_train = [
                row
                for season in DEFAULT_SEASONS
                if season < test_season
                for row in base_eligible[season]
            ]
            base_test = base_eligible[test_season]
            base_model = fit_generic(prepare_generic(base_train, BASE_FEATURES))
            base_score = _score_rows(base_model, base_test)

            for name, features in VARIANTS.items():
                train = [
                    row
                    for season in DEFAULT_SEASONS
                    if season < test_season
                    for row in variant_eligible[name][season]
                ]
                test = variant_eligible[name][test_season]
                challenger = fit_generic(prepare_generic(train, features))
                score = _score_rows(challenger, test)
                results.append(
                    {
                        "variant": name,
                        "features": list(features),
                        "minGames": int(min_games),
                        "season": int(test_season),
                        "n": len(test),
                        "baseMae": base_score["mae"],
                        "baseRmse": base_score["rmse"],
                        "baseWinner": base_score["winner"],
                        "challengerMae": score["mae"],
                        "challengerRmse": score["rmse"],
                        "challengerWinner": score["winner"],
                        "deltaMae": score["mae"] - base_score["mae"],
                        "deltaRmse": score["rmse"] - base_score["rmse"],
                        "deltaWinnerPP": (score["winner"] - base_score["winner"]) * 100.0,
                    }
                )

                for row in test:
                    per_game.append(
                        {
                            "variant": name,
                            "minGames": int(min_games),
                            "season": int(test_season),
                            "seasonType": row.get("seasonType"),
                            "week": int(row.get("week") or 0),
                            "gameId": str(row["gameId"]),
                            "homeTeam": row.get("homeTeam"),
                            "awayTeam": row.get("awayTeam"),
                            "actualHomeMargin": float(row["target_margin"]),
                            "basePrediction": predict_generic(base_model, row),
                            "challengerPrediction": predict_generic(challenger, row),
                            RAW_MARGIN_FEATURE: row.get(RAW_MARGIN_FEATURE),
                            ADJ_MARGIN_FEATURE: row.get(ADJ_MARGIN_FEATURE),
                            ADJ_OFFENSE_FEATURE: row.get(ADJ_OFFENSE_FEATURE),
                            ADJ_DEFENSE_FEATURE: row.get(ADJ_DEFENSE_FEATURE),
                        }
                    )

    return results, per_game


def summarize_pooled(per_game: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        for variant in VARIANTS:
            rows = [
                row
                for row in per_game
                if row["minGames"] == min_games and row["variant"] == variant
            ]
            if not rows:
                continue
            base_abs = []
            base_sq = []
            ch_abs = []
            ch_sq = []
            base_win = 0
            ch_win = 0
            for row in rows:
                actual = float(row["actualHomeMargin"])
                base_pred = float(row["basePrediction"])
                ch_pred = float(row["challengerPrediction"])
                base_abs.append(abs(base_pred - actual))
                base_sq.append((base_pred - actual) ** 2)
                ch_abs.append(abs(ch_pred - actual))
                ch_sq.append((ch_pred - actual) ** 2)
                actual_home = actual > 0.0
                base_win += int((base_pred > 0.0) == actual_home)
                ch_win += int((ch_pred > 0.0) == actual_home)
            n = len(rows)
            base_mae = sum(base_abs) / n
            ch_mae = sum(ch_abs) / n
            base_rmse = math.sqrt(sum(base_sq) / n)
            ch_rmse = math.sqrt(sum(ch_sq) / n)
            out.append(
                {
                    "variant": variant,
                    "minGames": int(min_games),
                    "n": n,
                    "baseMae": base_mae,
                    "challengerMae": ch_mae,
                    "deltaMae": ch_mae - base_mae,
                    "baseRmse": base_rmse,
                    "challengerRmse": ch_rmse,
                    "deltaRmse": ch_rmse - base_rmse,
                    "baseWinner": base_win / n,
                    "challengerWinner": ch_win / n,
                    "deltaWinnerPP": ((ch_win - base_win) / n) * 100.0,
                }
            )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate adjusted scoring challenger vs locked Prediction v2")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/prediction_v2_adjusted_scoring_challenger.json"),
    )
    parser.add_argument(
        "--games-output",
        type=Path,
        default=Path("data/processed/prediction_v2_adjusted_scoring_challenger_games.json"),
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    data = load_challenger_data(args.raw_root, args.processed_root)
    results, games = evaluate(data)
    pooled = summarize_pooled(games)

    print("PREDICTION V2 ADJUSTED SCORING CHALLENGER")
    for row in pooled:
        print(
            f"{row['variant']} min{row['minGames']}: n={row['n']} "
            f"base_MAE={row['baseMae']:.4f} challenger_MAE={row['challengerMae']:.4f} "
            f"dMAE={row['deltaMae']:+.4f} "
            f"base_RMSE={row['baseRmse']:.4f} challenger_RMSE={row['challengerRmse']:.4f} "
            f"dRMSE={row['deltaRmse']:+.4f} "
            f"base_win={row['baseWinner']:.3%} challenger_win={row['challengerWinner']:.3%} "
            f"dWin={row['deltaWinnerPP']:+.3f}pp"
        )

    report = {
        "schemaVersion": 1,
        "challengerVersion": CHALLENGER_VERSION,
        "baseFeatures": list(BASE_FEATURES),
        "variants": {name: list(features) for name, features in VARIANTS.items()},
        "testSeasons": list(TEST_SEASONS),
        "results": results,
        "pooled": pooled,
    }
    for path, payload in ((args.output, report), (args.games_output, games)):
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print(f"Report: {args.output}")
    print(f"Per-game: {args.games_output}")


if __name__ == "__main__":
    main()
