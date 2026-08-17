"""Leakage-safe dynamic rating model screen against the historical market.

Predeclared dynamic families:
- classic Elo
- margin-of-victory Elo
- Glicko-1-style rating + rating deviation
- Gaussian Kalman/state-space latent team strength

Every target partition is scored before any result from that partition updates a
rating.  Dynamic states may use all completed prior games, while outer-season
margin calibration and ATS classifiers train only on seasons earlier than the
outer test season.

This is exploratory model-family discovery, not promotion evidence.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from cfb_analytics.analytics.market_edge_model_zoo import (
    BREAK_EVEN_MINUS_110,
    _predict_home_cover_probability,
    _roi_minus_110,
    _sign,
    attach_market,
    finite,
    grade_classifier,
    grade_margin_predictions,
)
from cfb_analytics.analytics.prediction_v1_integrity_audit import MIN_GAMES_VALUES
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    TEST_SEASONS,
    eligible_site,
    load_data,
    partition_key,
)
from cfb_analytics.analytics.prediction_v2_clean_market_benchmark import DEFAULT_LINES, clean_market_rows
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

VERSION = "dynamic-market-edge-zoo-v1"
DEFAULT_REPORT = Path("data/processed/market_benchmark/dynamic-market-edge-zoo.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/dynamic-market-edge-zoo-games.json")
THRESHOLDS = (0.55, 0.575, 0.60)
OFFSEASON_CARRY = 0.50
ELO_K = 20.0
ELO_HFA = 55.0
GLICKO_INITIAL_RD = 350.0
GLICKO_RD_DRIFT = 50.0
KALMAN_INITIAL_VARIANCE = 100.0
KALMAN_PROCESS_VARIANCE = 4.0
KALMAN_OBSERVATION_VARIANCE = 14.0 ** 2
KALMAN_HFA = 2.5

DYNAMIC_MODELS = ("ELO", "MOV_ELO", "GLICKO", "KALMAN")


@dataclass
class EloState:
    ratings: dict[str, float] = field(default_factory=dict)
    mov: bool = False

    def rating(self, team: str) -> float:
        return self.ratings.setdefault(team, 1500.0)

    def offseason(self) -> None:
        for team in list(self.ratings):
            self.ratings[team] = 1500.0 + OFFSEASON_CARRY * (self.ratings[team] - 1500.0)

    def predict(self, home: str, away: str, neutral: bool) -> tuple[float, float]:
        hfa = 0.0 if neutral else ELO_HFA
        strength = self.rating(home) + hfa - self.rating(away)
        return strength, 0.0

    def update(self, home: str, away: str, margin: float, neutral: bool) -> None:
        rh = self.rating(home)
        ra = self.rating(away)
        hfa = 0.0 if neutral else ELO_HFA
        exp_home = 1.0 / (1.0 + 10.0 ** (-(rh + hfa - ra) / 400.0))
        actual_home = 1.0 if margin > 0 else (0.0 if margin < 0 else 0.5)
        mult = 1.0
        if self.mov:
            # Predeclared bounded MOV multiplier.  It changes update magnitude,
            # never the pregame score of the game being updated.
            mult = math.log1p(abs(margin)) / math.log(8.0) if margin else 0.5
            mult = min(2.5, max(0.5, mult))
        delta = ELO_K * mult * (actual_home - exp_home)
        self.ratings[home] = rh + delta
        self.ratings[away] = ra - delta


@dataclass
class GlickoState:
    ratings: dict[str, float] = field(default_factory=dict)
    rds: dict[str, float] = field(default_factory=dict)

    @staticmethod
    def _g(rd: float) -> float:
        q = math.log(10.0) / 400.0
        return 1.0 / math.sqrt(1.0 + 3.0 * q * q * rd * rd / (math.pi * math.pi))

    def ensure(self, team: str) -> None:
        self.ratings.setdefault(team, 1500.0)
        self.rds.setdefault(team, GLICKO_INITIAL_RD)

    def offseason(self) -> None:
        for team in list(self.ratings):
            self.ratings[team] = 1500.0 + OFFSEASON_CARRY * (self.ratings[team] - 1500.0)
            self.rds[team] = min(GLICKO_INITIAL_RD, math.sqrt(self.rds[team] ** 2 + GLICKO_RD_DRIFT ** 2))

    def drift_period(self) -> None:
        for team in list(self.rds):
            self.rds[team] = min(GLICKO_INITIAL_RD, math.sqrt(self.rds[team] ** 2 + GLICKO_RD_DRIFT ** 2))

    def predict(self, home: str, away: str, neutral: bool) -> tuple[float, float]:
        self.ensure(home); self.ensure(away)
        hfa = 0.0 if neutral else ELO_HFA
        strength = self.ratings[home] + hfa - self.ratings[away]
        uncertainty = math.sqrt(self.rds[home] ** 2 + self.rds[away] ** 2)
        return strength, uncertainty

    def update_partition(self, games: list[tuple[str, str, float, bool]]) -> None:
        q = math.log(10.0) / 400.0
        by_team: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
        for home, away, margin, neutral in games:
            self.ensure(home); self.ensure(away)
            hfa = 0.0 if neutral else ELO_HFA
            # Effective opponent ratings encode home advantage while the stored
            # team ratings remain site-neutral.
            by_team[home].append((self.ratings[away] - hfa, self.rds[away], 1.0 if margin > 0 else (0.0 if margin < 0 else 0.5)))
            by_team[away].append((self.ratings[home] + hfa, self.rds[home], 1.0 if margin < 0 else (0.0 if margin > 0 else 0.5)))

        new_ratings = dict(self.ratings)
        new_rds = dict(self.rds)
        for team, opponents in by_team.items():
            r = self.ratings[team]
            rd = self.rds[team]
            terms = []
            score_terms = []
            for opp_r, opp_rd, score in opponents:
                g = self._g(opp_rd)
                e = 1.0 / (1.0 + 10.0 ** (-g * (r - opp_r) / 400.0))
                terms.append(g * g * e * (1.0 - e))
                score_terms.append(g * (score - e))
            d2 = 1.0 / (q * q * sum(terms)) if sum(terms) > 0 else float("inf")
            precision = 1.0 / (rd * rd) + (0.0 if math.isinf(d2) else 1.0 / d2)
            new_rd = math.sqrt(1.0 / precision)
            new_r = r + q / precision * sum(score_terms)
            new_ratings[team] = new_r
            new_rds[team] = min(GLICKO_INITIAL_RD, new_rd)
        self.ratings = new_ratings
        self.rds = new_rds


@dataclass
class KalmanState:
    means: dict[str, float] = field(default_factory=dict)
    variances: dict[str, float] = field(default_factory=dict)

    def ensure(self, team: str) -> None:
        self.means.setdefault(team, 0.0)
        self.variances.setdefault(team, KALMAN_INITIAL_VARIANCE)

    def offseason(self) -> None:
        for team in list(self.means):
            self.means[team] *= OFFSEASON_CARRY
            self.variances[team] += KALMAN_INITIAL_VARIANCE * (1.0 - OFFSEASON_CARRY)

    def drift_period(self) -> None:
        for team in list(self.variances):
            self.variances[team] += KALMAN_PROCESS_VARIANCE

    def predict(self, home: str, away: str, neutral: bool) -> tuple[float, float]:
        self.ensure(home); self.ensure(away)
        hfa = 0.0 if neutral else KALMAN_HFA
        mean = self.means[home] - self.means[away] + hfa
        sd = math.sqrt(self.variances[home] + self.variances[away] + KALMAN_OBSERVATION_VARIANCE)
        return mean, sd

    def update(self, home: str, away: str, margin: float, neutral: bool) -> None:
        self.ensure(home); self.ensure(away)
        hfa = 0.0 if neutral else KALMAN_HFA
        pred = self.means[home] - self.means[away] + hfa
        residual = margin - pred
        vh = self.variances[home]
        va = self.variances[away]
        s = vh + va + KALMAN_OBSERVATION_VARIANCE
        kh = vh / s
        ka = va / s
        self.means[home] += kh * residual
        self.means[away] -= ka * residual
        self.variances[home] = max(1e-9, vh * (1.0 - kh))
        self.variances[away] = max(1e-9, va * (1.0 - ka))


def build_dynamic_signals(data: dict[int, list[dict[str, Any]]]) -> dict[str, dict[str, tuple[float, float]]]:
    """Return model -> gameId -> (strength, uncertainty), pregame only."""
    states: dict[str, Any] = {
        "ELO": EloState(mov=False),
        "MOV_ELO": EloState(mov=True),
        "GLICKO": GlickoState(),
        "KALMAN": KalmanState(),
    }
    out: dict[str, dict[str, tuple[float, float]]] = {name: {} for name in DYNAMIC_MODELS}
    first_season = True

    for season in sorted(DEFAULT_SEASONS):
        if season not in data:
            continue
        if not first_season:
            for state in states.values():
                state.offseason()
        first_season = False

        partitions: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
        for row in data[season]:
            partitions[partition_key(row)].append(row)

        for key in sorted(partitions):
            # Time/uncertainty evolves before the new rating period, but no
            # current-partition outcome has been observed yet.
            states["GLICKO"].drift_period()
            states["KALMAN"].drift_period()
            games = sorted(partitions[key], key=lambda row: str(row.get("gameId")))
            valid_updates: list[tuple[str, str, float, bool]] = []
            for row in games:
                gid = row.get("gameId")
                home = row.get("homeTeam")
                away = row.get("awayTeam")
                margin = row.get("target_margin")
                neutral = row.get("isNeutralSite")
                if gid is None or not home or not away or not finite(margin) or not isinstance(neutral, bool):
                    continue
                home = str(home); away = str(away)
                for name, state in states.items():
                    out[name][str(gid)] = state.predict(home, away, neutral)
                valid_updates.append((home, away, float(margin), neutral))

            # Update only after every game in this partition has been scored.
            for home, away, margin, neutral in valid_updates:
                states["ELO"].update(home, away, margin, neutral)
                states["MOV_ELO"].update(home, away, margin, neutral)
                states["KALMAN"].update(home, away, margin, neutral)
            states["GLICKO"].update_partition(valid_updates)
    return out


def _dynamic_matrix(rows: list[dict[str, Any]], model: str, ats: bool) -> np.ndarray:
    values = []
    for row in rows:
        base = [float(row[f"{model}_strength"]), float(row[f"{model}_uncertainty"])]
        if ats:
            base.extend([
                float(row["marketHomeMargin"]),
                float(row["marketAbsSpread"]),
                float(row["marketHomeFavorite"]),
                float(row["weekNumber"]),
                float(row["neutralSite"]),
            ])
        values.append(base)
    matrix = np.asarray(values, dtype=float)
    if not np.isfinite(matrix).all():
        raise ValueError(f"Non-finite dynamic matrix for {model}")
    return matrix


def _fit_margin(train: list[dict[str, Any]], model: str):
    x = _dynamic_matrix(train, model, ats=False)
    y = np.asarray([float(row["target_margin"]) for row in train], dtype=float)
    fitted = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    fitted.fit(x, y)
    return fitted


def _fit_ats(train: list[dict[str, Any]], model: str):
    no_push = [row for row in train if _sign(float(row["target_margin"]) - float(row["marketHomeMargin"])) != 0]
    x = _dynamic_matrix(no_push, model, ats=True)
    y = np.asarray([1 if float(row["target_margin"]) > float(row["marketHomeMargin"]) else 0 for row in no_push], dtype=int)
    fitted = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000, random_state=42))
    fitted.fit(x, y)
    return fitted


def _ats_probability(fitted: Any, rows: list[dict[str, Any]], model: str) -> np.ndarray:
    probs = np.asarray(fitted.predict_proba(_dynamic_matrix(rows, model, ats=True)), dtype=float)
    classes = list(fitted.classes_)
    return probs[:, classes.index(1)]


def _aggregate_classifier(folds: list[dict[str, Any]]) -> dict[str, Any]:
    wins = sum(int(r["wins"]) for r in folds)
    losses = sum(int(r["losses"]) for r in folds)
    pushes = sum(int(r["pushes"]) for r in folds)
    decisions = wins + losses
    return {
        "wins": wins, "losses": losses, "pushes": pushes, "decisions": decisions,
        "accuracy": wins / decisions if decisions else None,
        "roiMinus110": _roi_minus_110(wins, losses),
    }


def run(lines: Path, raw_root: Path, processed_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = load_data(raw_root, processed_root)
    signals = build_dynamic_signals(data)
    market = clean_market_rows(lines)
    market_by_id = {str(row["gameId"]): row for row in market}

    attached: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        rows: list[dict[str, Any]] = []
        for base in data[season]:
            gid = str(base.get("gameId"))
            market_row = market_by_id.get(gid)
            if market_row is None:
                continue
            row = attach_market(base, market_row)
            complete = True
            for model in DYNAMIC_MODELS:
                pair = signals[model].get(gid)
                if pair is None:
                    complete = False; break
                row[f"{model}_strength"] = float(pair[0])
                row[f"{model}_uncertainty"] = float(pair[1])
            if complete:
                rows.append(row)
        attached[season] = rows

    margin_folds: list[dict[str, Any]] = []
    ats_folds: list[dict[str, Any]] = []
    per_game: list[dict[str, Any]] = []

    for min_games in MIN_GAMES_VALUES:
        eligible = {season: [row for row in attached[season] if eligible_site(row, min_games)] for season in DEFAULT_SEASONS}
        for test_season in TEST_SEASONS:
            train = [row for season in DEFAULT_SEASONS if season < test_season for row in eligible[season]]
            test = eligible[test_season]
            if not train or not test:
                raise ValueError(f"Empty dynamic fold min{min_games} {test_season}")
            for model in DYNAMIC_MODELS:
                margin_model = _fit_margin(train, model)
                margin_pred = np.asarray(margin_model.predict(_dynamic_matrix(test, model, ats=False)), dtype=float)
                margin_summary = grade_margin_predictions(test, margin_pred)
                margin_folds.append({"minGames": min_games, "season": test_season, "model": model, "trainN": len(train), **margin_summary})

                ats_model = _fit_ats(train, model)
                p_home = _ats_probability(ats_model, test, model)
                for threshold in THRESHOLDS:
                    ats_folds.append({"minGames": min_games, "season": test_season, "model": model, "trainN": len(train), **grade_classifier(test, p_home, threshold)})

                for row, pred, p in zip(test, margin_pred, p_home):
                    per_game.append({
                        "minGames": min_games, "season": test_season, "model": model,
                        "gameId": str(row["gameId"]), "homeTeam": row.get("homeTeam"), "awayTeam": row.get("awayTeam"),
                        "marketHomeMargin": float(row["marketHomeMargin"]), "actualHomeMargin": float(row["target_margin"]),
                        "dynamicStrength": float(row[f"{model}_strength"]), "dynamicUncertainty": float(row[f"{model}_uncertainty"]),
                        "calibratedMargin": float(pred), "homeCoverProbability": float(p),
                    })

    pooled_margin: list[dict[str, Any]] = []
    pooled_ats: list[dict[str, Any]] = []
    for min_games in MIN_GAMES_VALUES:
        for model in DYNAMIC_MODELS:
            games = [r for r in per_game if r["minGames"] == min_games and r["model"] == model]
            converted = [{"target_margin": r["actualHomeMargin"], "marketHomeMargin": r["marketHomeMargin"]} for r in games]
            pooled_margin.append({"minGames": min_games, "model": model, **grade_margin_predictions(converted, np.asarray([r["calibratedMargin"] for r in games]))})
            for threshold in THRESHOLDS:
                folds = [r for r in ats_folds if r["minGames"] == min_games and r["model"] == model and abs(float(r["confidenceThreshold"]) - threshold) <= 1e-12]
                pooled_ats.append({"minGames": min_games, "model": model, "confidenceThreshold": threshold, **_aggregate_classifier(folds)})

    report = {
        "schemaVersion": 1,
        "version": VERSION,
        "status": "EXPLORATORY_DYNAMIC_MODEL_FAMILY_SCREEN",
        "testSeasons": list(TEST_SEASONS),
        "minGamesValues": list(MIN_GAMES_VALUES),
        "thresholds": list(THRESHOLDS),
        "breakEvenMinus110": BREAK_EVEN_MINUS_110,
        "parameters": {
            "offseasonCarry": OFFSEASON_CARRY,
            "eloK": ELO_K, "eloHfa": ELO_HFA,
            "glickoInitialRd": GLICKO_INITIAL_RD, "glickoRdDrift": GLICKO_RD_DRIFT,
            "kalmanInitialVariance": KALMAN_INITIAL_VARIANCE,
            "kalmanProcessVariance": KALMAN_PROCESS_VARIANCE,
            "kalmanObservationVariance": KALMAN_OBSERVATION_VARIANCE,
            "kalmanHfa": KALMAN_HFA,
        },
        "pooledMargin": pooled_margin,
        "pooledAts": pooled_ats,
        "marginFolds": margin_folds,
        "atsFolds": ats_folds,
    }
    return report, per_game


def _write(path: Path, payload: Any, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _pct(v: Any) -> str:
    return "NA" if v is None else f"{float(v):.3%}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Dynamic rating market-edge model zoo")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = run(args.lines, args.raw_root, args.processed_root)
    print("DYNAMIC MARKET EDGE MODEL ZOO — EXPLORATORY")
    print(f"Version: {VERSION}")
    print(f"-110 break-even: {BREAK_EVEN_MINUS_110:.3%}")
    print("All current-partition predictions are made before current-partition rating updates.\n")
    for min_games in MIN_GAMES_VALUES:
        print(f"=== min{min_games} MARGIN ===")
        rows = [r for r in report["pooledMargin"] if r["minGames"] == min_games]
        rows.sort(key=lambda r: float(r["deltaMaeVsMarket"]))
        for r in rows:
            print(f"{r['model']:<10} n={r['n']:4d} MAE={r['mae']:.4f} market={r['marketMae']:.4f} dMAE={r['deltaMaeVsMarket']:+.4f} RMSE={r['rmse']:.4f} dRMSE={r['deltaRmseVsMarket']:+.4f} ATS={r['atsWins']}-{r['atsLosses']}-{r['atsPushes']} ({_pct(r['atsAccuracy'])}) ROI={_pct(r['roiMinus110'])}")
        print(f"=== min{min_games} DIRECT ATS ===")
        rows = [r for r in report["pooledAts"] if r["minGames"] == min_games]
        rows.sort(key=lambda r: (-(float(r["roiMinus110"]) if r["roiMinus110"] is not None else -999), -r["decisions"]))
        for r in rows:
            print(f"{r['model']:<10} conf>={r['confidenceThreshold']:.3f} ATS={r['wins']}-{r['losses']}-{r['pushes']} ({_pct(r['accuracy'])}) ROI={_pct(r['roiMinus110'])} decisions={r['decisions']}")
        print()

    print("=== SEASON STABILITY at conf>=0.575 ===")
    for min_games in MIN_GAMES_VALUES:
        for model in DYNAMIC_MODELS:
            folds = [r for r in report["atsFolds"] if r["minGames"] == min_games and r["model"] == model and abs(float(r["confidenceThreshold"]) - 0.575) <= 1e-12]
            profitable = sum(1 for r in folds if r["roiMinus110"] is not None and r["roiMinus110"] > 0)
            detail = " ".join(f"{r['season']}:{r['wins']}-{r['losses']}({_pct(r['roiMinus110'])})" for r in folds)
            print(f"min{min_games} {model:<10} profitable={profitable}/{len(folds)} | {detail}")

    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"Report: {args.output}")
    print(f"Per-game predictions: {args.games_output}")
    print("WARNING: many-model discovery screen; freeze any survivor before confirmation/prospective use.")


if __name__ == "__main__":
    main()
