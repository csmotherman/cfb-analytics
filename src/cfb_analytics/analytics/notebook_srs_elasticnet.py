"""Leakage-safe historical evaluation of the exact CFB Sandbox notebook model.

The model definition is copied from the uploaded notebook:

1. Per-game offensive metrics for each team:
   - success rate (50%/70%/100% down-based rule)
   - mean PPA/EPA per play
   - points per drive, with drive points clipped to [0, 8]
   - drive conversion rate (fraction of drives scoring > 0 points)
2. Home-minus-away differentials for score margin and those four metrics.
3. The notebook's iterative SRS algorithm is fit independently to:
   spread, SR_diff, EPA_diff, PPD_diff, DriveConv_diff.
4. Each SRS vector is standardized across teams (population std, ddof=0), and
   SRS_Overall is the row-wise mean of those five standardized ratings.
5. Matchup features are home-minus-away differences of the five standardized
   SRS ratings plus SRS_Overall (six total features).
6. StandardScaler + ElasticNet(alpha=0.1, l1_ratio=0.2, max_iter=5000).

The notebook computed full-season SRS before fitting the regression. Doing that for
historical target games would leak each target outcome into its own predictors. This
module preserves the notebook's model mathematics while materializing every historical
pregame SRS state from strictly earlier completed partitions only. The resulting rows
can therefore be compared fairly with Prediction v2's expanding-season OOS benchmark.

The notebook's later current-week cell passed unscaled features to a model trained on
scaled features. That inference mismatch is not reproduced here; the trained notebook
model itself explicitly uses StandardScaler for train/test and full-data fitting.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler

from cfb_analytics.analytics.prediction_v1_integrity_audit import MIN_GAMES_VALUES, finite
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    SITE_AWARE,
    TEST_SEASONS,
    eligible_site,
    fit_generic,
    load_data as load_prediction_v2_data,
    predict_generic,
    prepare_generic,
)
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.raw.storage import partition_dir

MODEL_VERSION = "cfb-sandbox-notebook-srs-elasticnet-v1"
NOTEBOOK_METRICS = ("spread", "SR_diff", "EPA_diff", "PPD_diff", "DriveConv_diff")
NOTEBOOK_FEATURES = tuple(f"SRSdiff_{metric}" for metric in NOTEBOOK_METRICS) + ("SRSdiff_Overall",)
ELASTIC_NET_ALPHA = 0.1
ELASTIC_NET_L1_RATIO = 0.2
ELASTIC_NET_MAX_ITER = 5000
SRS_MAX_ITER = 1000
SRS_TOLERANCE = 1e-6


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def partition_key(season_type: str, week: int) -> tuple[int, int]:
    normalized = str(season_type or "regular").lower()
    return (0 if normalized in {"regular", "regular_season"} else 1, int(week))


def _load_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError(f"Expected JSON list: {path}")
    return [row for row in payload if isinstance(row, dict)]


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    return None


def notebook_success(play: dict[str, Any]) -> float:
    """Replicate the notebook's nested np.where success definition exactly."""
    down = _number(play.get("down"))
    gained = _number(play.get("yardsGained"))
    distance = _number(play.get("distance"))
    if down is None or gained is None or distance is None:
        return 0.0
    if down == 1.0 and gained >= 0.5 * distance:
        return 1.0
    if down == 2.0 and gained >= 0.7 * distance:
        return 1.0
    if down >= 3.0 and gained >= distance:
        return 1.0
    return 0.0


def clipped_drive_points(drive: dict[str, Any]) -> float | None:
    start = _number(drive.get("startOffenseScore"))
    end = _number(drive.get("endOffenseScore"))
    if start is None or end is None:
        return None
    return min(8.0, max(0.0, end - start))


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def build_partition_game_metrics(
    games: list[dict[str, Any]],
    drives: list[dict[str, Any]],
    plays: list[dict[str, Any]],
    *,
    season: int,
    season_type: str,
    week: int,
) -> list[dict[str, Any]]:
    """Build the notebook's final_spreads_df-equivalent rows for one partition."""
    play_success: dict[tuple[str, str], list[float]] = defaultdict(list)
    play_ppa: dict[tuple[str, str], list[float]] = defaultdict(list)
    for play in plays:
        gid = play.get("gameId")
        offense = play.get("offense")
        if gid is None or offense is None:
            continue
        key = (str(gid), str(offense))
        play_success[key].append(notebook_success(play))
        ppa = _number(play.get("ppa"))
        if ppa is not None:
            play_ppa[key].append(ppa)

    drive_points: dict[tuple[str, str], list[float]] = defaultdict(list)
    drive_scored: dict[tuple[str, str], list[float]] = defaultdict(list)
    for drive in drives:
        gid = drive.get("gameId")
        offense = drive.get("offense")
        if gid is None or offense is None:
            continue
        key = (str(gid), str(offense))
        points = clipped_drive_points(drive)
        if points is not None:
            drive_points[key].append(points)
        # pandas: NaN > 0 evaluates False in the notebook's boolean column.
        drive_scored[key].append(1.0 if points is not None and points > 0.0 else 0.0)

    out: list[dict[str, Any]] = []
    for game in games:
        gid_raw = game.get("id") if game.get("id") is not None else game.get("gameId")
        home = game.get("homeTeam")
        away = game.get("awayTeam")
        home_points = _number(game.get("homePoints"))
        away_points = _number(game.get("awayPoints"))
        if gid_raw is None or not home or not away or home_points is None or away_points is None:
            continue
        gid = str(gid_raw)
        hk = (gid, str(home))
        ak = (gid, str(away))
        home_sr, away_sr = _mean(play_success[hk]), _mean(play_success[ak])
        home_epa, away_epa = _mean(play_ppa[hk]), _mean(play_ppa[ak])
        home_ppd, away_ppd = _mean(drive_points[hk]), _mean(drive_points[ak])
        home_dcr, away_dcr = _mean(drive_scored[hk]), _mean(drive_scored[ak])
        required = (home_sr, away_sr, home_epa, away_epa, home_ppd, away_ppd, home_dcr, away_dcr)
        if any(value is None or not math.isfinite(float(value)) for value in required):
            continue
        out.append(
            {
                "season": int(season),
                "seasonType": season_type,
                "week": int(week),
                "gameId": gid,
                "home_team": str(home),
                "away_team": str(away),
                "home_score": home_points,
                "away_score": away_points,
                "spread": home_points - away_points,
                "SR_diff": float(home_sr) - float(away_sr),
                "EPA_diff": float(home_epa) - float(away_epa),
                "PPD_diff": float(home_ppd) - float(away_ppd),
                "DriveConv_diff": float(home_dcr) - float(away_dcr),
            }
        )
    return out


def fit_notebook_srs(
    rows: list[dict[str, Any]],
    metrics: tuple[str, ...] = NOTEBOOK_METRICS,
    max_iter: int = SRS_MAX_ITER,
    tol: float = SRS_TOLERANCE,
) -> dict[str, dict[str, float]]:
    """Literal dependency-free translation of the notebook's compute_SRS loop."""
    teams = sorted({str(row["home_team"]) for row in rows} | {str(row["away_team"]) for row in rows})
    if not teams:
        return {}
    index = {team: i for i, team in enumerate(teams)}
    n = len(teams)
    games_matrix = np.zeros((n, n), dtype=float)
    margin_matrices = {metric: np.zeros((n, n), dtype=float) for metric in metrics}

    for row in rows:
        i, j = index[str(row["home_team"])], index[str(row["away_team"])]
        games_matrix[i, j] += 1.0
        games_matrix[j, i] += 1.0
        for metric in metrics:
            value = _number(row.get(metric))
            if value is None:
                continue
            margin_matrices[metric][i, j] += value
            margin_matrices[metric][j, i] -= value

    raw: dict[str, np.ndarray] = {}
    for metric in metrics:
        matrix = margin_matrices[metric]
        srs = np.zeros(n, dtype=float)
        previous = np.ones(n, dtype=float)
        for _ in range(max_iter):
            for i in range(n):
                opponents = np.where(games_matrix[i] > 0.0)[0]
                if len(opponents) == 0:
                    continue
                avg_margin = float(np.sum(matrix[i, opponents]) / np.sum(games_matrix[i, opponents]))
                # Exact notebook behavior: unweighted mean over DISTINCT opponents.
                avg_opp_srs = float(np.mean(srs[opponents]))
                srs[i] = avg_margin + avg_opp_srs
            srs -= float(np.mean(srs))
            if float(np.max(np.abs(srs - previous))) < tol:
                break
            previous = srs.copy()
        raw[metric] = srs

    standardized: dict[str, np.ndarray] = {}
    for metric, values in raw.items():
        mean = float(np.mean(values))
        std = float(np.std(values, ddof=0))
        standardized[metric] = (values - mean) / std if std > 0.0 else np.zeros(n, dtype=float)

    out: dict[str, dict[str, float]] = {}
    for team, i in index.items():
        row = {f"SRS_{metric}": float(standardized[metric][i]) for metric in metrics}
        row["SRS_Overall"] = sum(row[f"SRS_{metric}"] for metric in metrics) / len(metrics)
        out[team] = row
    return out


def notebook_matchup_features(
    ratings: dict[str, dict[str, float]],
    home: str,
    away: str,
) -> dict[str, float] | None:
    h = ratings.get(str(home))
    a = ratings.get(str(away))
    if h is None or a is None:
        return None
    out: dict[str, float] = {}
    for metric in NOTEBOOK_METRICS:
        out[f"SRSdiff_{metric}"] = float(h[f"SRS_{metric}"]) - float(a[f"SRS_{metric}"])
    out["SRSdiff_Overall"] = float(h["SRS_Overall"]) - float(a["SRS_Overall"])
    return out


def build_season_pregame_rows(raw_root: Path, season: int) -> list[dict[str, Any]]:
    """Replay one season partition-by-partition with no target-partition leakage."""
    history: list[dict[str, Any]] = []
    games_before: Counter[str] = Counter()
    out: list[dict[str, Any]] = []

    partitions = sorted(discover_partitions(raw_root, season), key=lambda item: partition_key(item[0], item[1]))
    for season_type, week in partitions:
        directory = partition_dir(raw_root, season, season_type, week)
        games = _load_json(directory / "games.json")
        drives = _load_json(directory / "drives.json")
        plays = _load_json(directory / "plays.json")

        ratings = fit_notebook_srs(history)
        for game in games:
            gid_raw = game.get("id") if game.get("id") is not None else game.get("gameId")
            home, away = game.get("homeTeam"), game.get("awayTeam")
            hp, ap = _number(game.get("homePoints")), _number(game.get("awayPoints"))
            if gid_raw is None or not home or not away or hp is None or ap is None:
                continue
            features = notebook_matchup_features(ratings, str(home), str(away))
            row: dict[str, Any] = {
                "modelVersion": MODEL_VERSION,
                "season": int(season),
                "seasonType": season_type,
                "week": int(week),
                "gameId": str(gid_raw),
                "homeTeam": str(home),
                "awayTeam": str(away),
                "homeGamesPlayedBefore": int(games_before[str(home)]),
                "awayGamesPlayedBefore": int(games_before[str(away)]),
                "target_margin": hp - ap,
                "target_homeWin": hp > ap,
                "historyGamesBefore": len(history),
            }
            for feature in NOTEBOOK_FEATURES:
                row[feature] = features.get(feature) if features is not None else None
            out.append(row)

        completed = build_partition_game_metrics(
            games,
            drives,
            plays,
            season=season,
            season_type=season_type,
            week=week,
        )
        history.extend(completed)
        for row in completed:
            games_before[str(row["home_team"])] += 1
            games_before[str(row["away_team"])] += 1
    return out


def load_notebook_data(raw_root: Path) -> dict[int, list[dict[str, Any]]]:
    data: dict[int, list[dict[str, Any]]] = {}
    print("Building leakage-safe notebook SRS rows from saved raw partitions.", flush=True)
    for season in DEFAULT_SEASONS:
        data[season] = build_season_pregame_rows(raw_root, season)
        print(f" NOTEBOOK {season}: {len(data[season]):,} target rows", flush=True)
    return data


def eligible_notebook(row: dict[str, Any], min_games: int) -> bool:
    return bool(
        int(row.get("homeGamesPlayedBefore") or 0) >= min_games
        and int(row.get("awayGamesPlayedBefore") or 0) >= min_games
        and finite(row.get("target_margin"))
        and all(finite(row.get(feature)) for feature in NOTEBOOK_FEATURES)
    )


def fit_notebook_model(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Cannot fit notebook model on zero rows")
    x = np.asarray([[float(row[feature]) for feature in NOTEBOOK_FEATURES] for row in rows], dtype=float)
    y = np.asarray([float(row["target_margin"]) for row in rows], dtype=float)
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    model = ElasticNet(
        alpha=ELASTIC_NET_ALPHA,
        l1_ratio=ELASTIC_NET_L1_RATIO,
        max_iter=ELASTIC_NET_MAX_ITER,
    )
    model.fit(x_scaled, y)
    return {"scaler": scaler, "model": model}


def predict_notebook(model_bundle: dict[str, Any], row: dict[str, Any]) -> float:
    x = np.asarray([[float(row[feature]) for feature in NOTEBOOK_FEATURES]], dtype=float)
    scaled = model_bundle["scaler"].transform(x)
    return float(model_bundle["model"].predict(scaled)[0])


def _metrics(rows: list[dict[str, Any]], prediction_field: str) -> dict[str, float]:
    if not rows:
        return {"n": 0, "mae": float("nan"), "rmse": float("nan"), "winner": float("nan")}
    absolute: list[float] = []
    squared: list[float] = []
    correct = 0
    for row in rows:
        actual = float(row["actualHomeMargin"])
        predicted = float(row[prediction_field])
        absolute.append(abs(predicted - actual))
        squared.append((predicted - actual) ** 2)
        correct += int((predicted > 0.0) == (actual > 0.0))
    n = len(rows)
    return {
        "n": n,
        "mae": sum(absolute) / n,
        "rmse": math.sqrt(sum(squared) / n),
        "winner": correct / n,
    }


def compare_with_prediction_v2(
    raw_root: Path,
    processed_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    notebook = load_notebook_data(raw_root)
    v2 = load_prediction_v2_data(raw_root, processed_root)

    fold_summaries: list[dict[str, Any]] = []
    joined_games: list[dict[str, Any]] = []

    for min_games in MIN_GAMES_VALUES:
        notebook_eligible = {
            season: [row for row in notebook[season] if eligible_notebook(row, min_games)]
            for season in DEFAULT_SEASONS
        }
        v2_eligible = {
            season: [row for row in v2[season] if eligible_site(row, min_games)]
            for season in DEFAULT_SEASONS
        }

        for test_season in TEST_SEASONS:
            notebook_train = [
                row for season in DEFAULT_SEASONS if season < test_season for row in notebook_eligible[season]
            ]
            v2_train = [
                row for season in DEFAULT_SEASONS if season < test_season for row in v2_eligible[season]
            ]
            notebook_test_by_id = {str(row["gameId"]): row for row in notebook_eligible[test_season]}
            v2_test_by_id = {str(row["gameId"]): row for row in v2_eligible[test_season]}
            common_ids = sorted(set(notebook_test_by_id) & set(v2_test_by_id))
            if not common_ids:
                raise ValueError(f"No common notebook/v2 rows for {test_season} min{min_games}")

            notebook_model = fit_notebook_model(notebook_train)
            v2_model = fit_generic(prepare_generic(v2_train, SITE_AWARE))

            fold_games: list[dict[str, Any]] = []
            for gid in common_ids:
                nrow = notebook_test_by_id[gid]
                vrow = v2_test_by_id[gid]
                actual = float(vrow["target_margin"])
                if abs(actual - float(nrow["target_margin"])) > 1e-9:
                    raise ValueError(f"Target mismatch for {test_season} game {gid}")
                notebook_prediction = predict_notebook(notebook_model, nrow)
                v2_prediction = predict_generic(v2_model, vrow)
                joined = {
                    "minGames": int(min_games),
                    "season": int(test_season),
                    "seasonType": vrow.get("seasonType"),
                    "week": int(vrow.get("week") or 0),
                    "gameId": gid,
                    "homeTeam": vrow.get("homeTeam"),
                    "awayTeam": vrow.get("awayTeam"),
                    "actualHomeMargin": actual,
                    "notebookHomeMargin": notebook_prediction,
                    "predictionV2HomeMargin": v2_prediction,
                    "notebookAbsoluteError": abs(notebook_prediction - actual),
                    "predictionV2AbsoluteError": abs(v2_prediction - actual),
                }
                fold_games.append(joined)
                joined_games.append(joined)

            notebook_score = _metrics(fold_games, "notebookHomeMargin")
            v2_score = _metrics(fold_games, "predictionV2HomeMargin")
            fold_summaries.append(
                {
                    "minGames": int(min_games),
                    "season": int(test_season),
                    "commonN": len(common_ids),
                    "notebookEligibleN": len(notebook_test_by_id),
                    "predictionV2EligibleN": len(v2_test_by_id),
                    "notebookTrainN": len(notebook_train),
                    "predictionV2TrainN": len(v2_train),
                    "notebook": notebook_score,
                    "predictionV2": v2_score,
                    "deltaMae": notebook_score["mae"] - v2_score["mae"],
                    "deltaRmse": notebook_score["rmse"] - v2_score["rmse"],
                    "deltaWinnerPP": (notebook_score["winner"] - v2_score["winner"]) * 100.0,
                }
            )

    pooled: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        games = [row for row in joined_games if row["minGames"] == min_games]
        notebook_score = _metrics(games, "notebookHomeMargin")
        v2_score = _metrics(games, "predictionV2HomeMargin")
        pooled.append(
            {
                "minGames": int(min_games),
                "n": len(games),
                "notebook": notebook_score,
                "predictionV2": v2_score,
                "deltaMae": notebook_score["mae"] - v2_score["mae"],
                "deltaRmse": notebook_score["rmse"] - v2_score["rmse"],
                "deltaWinnerPP": (notebook_score["winner"] - v2_score["winner"]) * 100.0,
            }
        )

    report = {
        "schemaVersion": 1,
        "modelVersion": MODEL_VERSION,
        "notebookFeatures": list(NOTEBOOK_FEATURES),
        "elasticNet": {
            "alpha": ELASTIC_NET_ALPHA,
            "l1Ratio": ELASTIC_NET_L1_RATIO,
            "maxIter": ELASTIC_NET_MAX_ITER,
            "standardScaler": True,
        },
        "srs": {
            "metrics": list(NOTEBOOK_METRICS),
            "maxIter": SRS_MAX_ITER,
            "tolerance": SRS_TOLERANCE,
            "opponentAverage": "unweighted-distinct-opponents",
            "standardization": "population-ddof-0",
        },
        "testSeasons": list(TEST_SEASONS),
        "evaluation": "expanding-season OOS; target partition excluded from notebook SRS state",
        "pooled": pooled,
        "folds": fold_summaries,
    }
    return report, joined_games


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare exact CFB Sandbox notebook model with Prediction v2")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/notebook_srs_elasticnet_vs_prediction_v2.json"),
    )
    parser.add_argument(
        "--games-output",
        type=Path,
        default=Path("data/processed/notebook_srs_elasticnet_vs_prediction_v2_games.json"),
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = compare_with_prediction_v2(args.raw_root, args.processed_root)
    print("CFB SANDBOX NOTEBOOK MODEL VS PREDICTION V2")
    print(f"Notebook model: {MODEL_VERSION}")
    print("Features: " + ", ".join(NOTEBOOK_FEATURES))
    print(
        f"ElasticNet(alpha={ELASTIC_NET_ALPHA}, l1_ratio={ELASTIC_NET_L1_RATIO}, "
        f"max_iter={ELASTIC_NET_MAX_ITER}) + StandardScaler"
    )
    print("Negative notebook-v2 MAE/RMSE delta means the notebook model is better.\n")

    for row in report["folds"]:
        n, v = row["notebook"], row["predictionV2"]
        print(
            f"min{row['minGames']} {row['season']}: common={row['commonN']:,} "
            f"(notebook={row['notebookEligibleN']:,}, v2={row['predictionV2EligibleN']:,}) | "
            f"NOTEBOOK MAE {n['mae']:.4f} RMSE {n['rmse']:.4f} WIN {n['winner']:.3%} | "
            f"V2 MAE {v['mae']:.4f} RMSE {v['rmse']:.4f} WIN {v['winner']:.3%} | "
            f"dMAE {row['deltaMae']:+.4f} dRMSE {row['deltaRmse']:+.4f} "
            f"dWin {row['deltaWinnerPP']:+.3f}pp"
        )

    print("\nPOOLED COMMON SAMPLE")
    for row in report["pooled"]:
        n, v = row["notebook"], row["predictionV2"]
        print(
            f"min{row['minGames']}: n={row['n']:,} | "
            f"NOTEBOOK MAE {n['mae']:.4f} RMSE {n['rmse']:.4f} WIN {n['winner']:.3%} | "
            f"V2 MAE {v['mae']:.4f} RMSE {v['rmse']:.4f} WIN {v['winner']:.3%} | "
            f"dMAE {row['deltaMae']:+.4f} dRMSE {row['deltaRmse']:+.4f} "
            f"dWin {row['deltaWinnerPP']:+.3f}pp"
        )

    for path, payload in ((args.output, report), (args.games_output, games)):
        if path.exists() and not args.overwrite:
            raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Report: {args.output}")
    print(f"Matched games: {args.games_output}")


if __name__ == "__main__":
    main()
