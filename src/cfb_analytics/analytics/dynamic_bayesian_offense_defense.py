"""Leakage-safe dynamic Gaussian offense/defense model-family screen.

This is an exploratory post-discovery experiment.  It does NOT modify the frozen
2026 ATS logistic artifact.

Predeclared state families:
- POINTS_OD: evolving scoring offense vs scoring defense
- YPP_OD: evolving yards/play offense vs yards/play defense
- SUCCESS_OD: evolving success-rate offense vs success-rate defense
- MULTI_OD: all three state families together

Every target partition is scored before any result from that partition updates
state.  Outer-season calibration/ATS models train only on seasons earlier than
the official test season.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from cfb_analytics.analytics.ats_logistic_deep_audit import (
    calibration_summary,
    coefficient_rows,
    coefficient_stability,
    fit_logistic,
    make_game_record,
    predict_home_cover,
    summarize_bets,
    threshold_rows,
)
from cfb_analytics.analytics.full_ats_plus_kalman_challenger import selection_overlap
from cfb_analytics.analytics.market_edge_model_zoo import (
    MARKET_CONTEXT_FEATURES,
    MODEL_FEATURES,
    attach_market,
    finite,
    grade_margin_predictions,
)
from cfb_analytics.analytics.prediction_v1_site_aware_challenger import (
    TEST_SEASONS,
    eligible_site,
    load_data,
    partition_key,
)
from cfb_analytics.analytics.prediction_v2_clean_market_benchmark import (
    DEFAULT_LINES,
    clean_market_rows,
)
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS
from cfb_analytics.derived.pregame import load_team_games

VERSION = "dynamic-bayesian-offense-defense-v1"
DEFAULT_REPORT = Path("data/processed/market_benchmark/dynamic-bayesian-offense-defense.json")
DEFAULT_GAMES = Path("data/processed/market_benchmark/dynamic-bayesian-offense-defense-games.json")
MIN_GAMES = 3
THRESHOLD = 0.575
BASELINE = "FULL_BASELINE"
OFFSEASON_CARRY = 0.50
POINTS_HFA = 2.5

# Fixed scale-aware priors/noise values.  These are predeclared, not selected
# from the historical test outcomes.
STATE_SPECS: dict[str, dict[str, float]] = {
    "POINTS_OD": {
        "center": 28.0,
        "initialVariance": 100.0,
        "processVariance": 4.0,
        "observationVariance": 14.0 ** 2,
    },
    "YPP_OD": {
        "center": 5.5,
        "initialVariance": 1.0,
        "processVariance": 0.04,
        "observationVariance": 4.0,
    },
    "SUCCESS_OD": {
        "center": 0.42,
        "initialVariance": 0.01,
        "processVariance": 0.0004,
        "observationVariance": 0.0144,
    },
}

FAMILY_FEATURES: dict[str, tuple[str, ...]] = {
    name: (
        f"{name}_homeMatchup",
        f"{name}_awayMatchup",
        f"{name}_uncertainty",
    )
    for name in STATE_SPECS
}
FAMILY_FEATURES["MULTI_OD"] = tuple(
    feature
    for name in ("POINTS_OD", "YPP_OD", "SUCCESS_OD")
    for feature in FAMILY_FEATURES[name]
)
FAMILIES = tuple(FAMILY_FEATURES)

BASELINE_FEATURES = tuple(MODEL_FEATURES)
AUGMENTED_FEATURES = {
    name: BASELINE_FEATURES + FAMILY_FEATURES[name]
    for name in FAMILIES
}
STANDALONE_ATS_FEATURES = {
    name: FAMILY_FEATURES[name] + tuple(MARKET_CONTEXT_FEATURES)
    for name in FAMILIES
}

EXPECTED_BASELINE = {
    "bets": 495,
    "wins": 265,
    "losses": 220,
    "pushes": 10,
}


@dataclass
class GaussianODState:
    """Independent Gaussian offense/defense states for one game-level metric.

    Observation model:
        y = center + offense(team) - defense(opponent) + noise

    A larger defense state therefore means a stronger defense (lower opponent
    observation).  We intentionally track only marginal variances, not the full
    cross-team covariance matrix; this keeps the state model small and auditable.
    """

    center: float
    initial_variance: float
    process_variance: float
    observation_variance: float
    offense_mean: dict[str, float] = field(default_factory=dict)
    defense_mean: dict[str, float] = field(default_factory=dict)
    offense_var: dict[str, float] = field(default_factory=dict)
    defense_var: dict[str, float] = field(default_factory=dict)

    def ensure(self, team: str) -> None:
        self.offense_mean.setdefault(team, 0.0)
        self.defense_mean.setdefault(team, 0.0)
        self.offense_var.setdefault(team, self.initial_variance)
        self.defense_var.setdefault(team, self.initial_variance)

    def offseason(self) -> None:
        for team in list(self.offense_mean):
            self.offense_mean[team] *= OFFSEASON_CARRY
            self.defense_mean[team] *= OFFSEASON_CARRY
            added = self.initial_variance * (1.0 - OFFSEASON_CARRY)
            self.offense_var[team] += added
            self.defense_var[team] += added

    def drift_period(self) -> None:
        for team in list(self.offense_var):
            self.offense_var[team] += self.process_variance
            self.defense_var[team] += self.process_variance

    def predict(self, home: str, away: str) -> tuple[float, float, float]:
        self.ensure(home)
        self.ensure(away)
        home_matchup = self.center + self.offense_mean[home] - self.defense_mean[away]
        away_matchup = self.center + self.offense_mean[away] - self.defense_mean[home]
        uncertainty = math.sqrt(
            self.offense_var[home]
            + self.defense_var[away]
            + self.offense_var[away]
            + self.defense_var[home]
            + 2.0 * self.observation_variance
        )
        return home_matchup, away_matchup, uncertainty

    def update_partition(self, observations: list[tuple[str, str, float]]) -> None:
        """Apply all observations from a completed rating period.

        Deltas are computed from one pre-partition snapshot so update ordering
        cannot change the information set used by another game in the period.
        """
        if not observations:
            return
        teams = {team for team, opp, _ in observations for team in (team, opp)}
        for team in teams:
            self.ensure(team)

        om = dict(self.offense_mean)
        dm = dict(self.defense_mean)
        ov = dict(self.offense_var)
        dv = dict(self.defense_var)
        off_delta: defaultdict[str, float] = defaultdict(float)
        def_delta: defaultdict[str, float] = defaultdict(float)
        off_reduction: defaultdict[str, float] = defaultdict(float)
        def_reduction: defaultdict[str, float] = defaultdict(float)

        for team, opponent, value in observations:
            residual = (float(value) - self.center) - (om[team] - dm[opponent])
            s = ov[team] + dv[opponent] + self.observation_variance
            if s <= 0.0 or not math.isfinite(s):
                raise ValueError("Invalid Gaussian O/D observation variance")
            ko = ov[team] / s
            kd = dv[opponent] / s
            off_delta[team] += ko * residual
            def_delta[opponent] -= kd * residual
            off_reduction[team] += ov[team] * ko
            def_reduction[opponent] += dv[opponent] * kd

        for team in teams:
            self.offense_mean[team] = om[team] + off_delta[team]
            self.defense_mean[team] = dm[team] + def_delta[team]
            self.offense_var[team] = max(1e-12, ov[team] - off_reduction[team])
            self.defense_var[team] = max(1e-12, dv[team] - def_reduction[team])


def _state(name: str) -> GaussianODState:
    spec = STATE_SPECS[name]
    return GaussianODState(
        center=float(spec["center"]),
        initial_variance=float(spec["initialVariance"]),
        process_variance=float(spec["processVariance"]),
        observation_variance=float(spec["observationVariance"]),
    )


def _rate(numerator: Any, denominator: Any) -> float | None:
    if not finite(numerator) or not finite(denominator) or float(denominator) <= 0.0:
        return None
    return float(numerator) / float(denominator)


def _team_game_map(
    raw_root: Path,
    processed_root: Path,
    season: int,
) -> dict[tuple[str, str], dict[str, Any]]:
    rows = load_team_games(raw_root, processed_root, season)
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        gid = row.get("gameId")
        team = row.get("team")
        if gid is None or not team:
            continue
        key = (str(gid), str(team))
        if key in out:
            raise ValueError(f"Duplicate team-game row: {key}")
        out[key] = row
    return out


def build_od_signals(
    data: dict[int, list[dict[str, Any]]],
    raw_root: Path,
    processed_root: Path,
) -> tuple[dict[str, dict[str, tuple[float, float, float]]], dict[str, int]]:
    """Return family -> gameId -> pregame (home matchup, away matchup, uncertainty)."""
    states = {name: _state(name) for name in STATE_SPECS}
    out = {name: {} for name in STATE_SPECS}
    missing = {"points": 0, "ypp": 0, "success": 0}
    first_season = True

    for season in sorted(DEFAULT_SEASONS):
        if season not in data:
            continue
        if not first_season:
            for state in states.values():
                state.offseason()
        first_season = False

        team_games = _team_game_map(raw_root, processed_root, season)
        partitions: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
        for row in data[season]:
            partitions[partition_key(row)].append(row)

        for key in sorted(partitions):
            for state in states.values():
                state.drift_period()
            games = sorted(partitions[key], key=lambda row: str(row.get("gameId")))

            # Score the full rating period before using any current-period result.
            for row in games:
                gid = str(row.get("gameId"))
                home = row.get("homeTeam")
                away = row.get("awayTeam")
                if not home or not away:
                    continue
                home = str(home)
                away = str(away)
                for name, state in states.items():
                    out[name][gid] = state.predict(home, away)

            points_obs: list[tuple[str, str, float]] = []
            ypp_obs: list[tuple[str, str, float]] = []
            success_obs: list[tuple[str, str, float]] = []
            for row in games:
                gid = str(row.get("gameId"))
                home = row.get("homeTeam")
                away = row.get("awayTeam")
                if not home or not away:
                    continue
                home = str(home)
                away = str(away)

                hs = row.get("target_homeScore")
                aas = row.get("target_awayScore")
                if finite(hs) and finite(aas):
                    half_hfa = 0.0 if row.get("isNeutralSite") is True else POINTS_HFA / 2.0
                    points_obs.append((home, away, float(hs) - half_hfa))
                    points_obs.append((away, home, float(aas) + half_hfa))
                else:
                    missing["points"] += 1

                home_game = team_games.get((gid, home))
                away_game = team_games.get((gid, away))
                if home_game is None or away_game is None:
                    missing["ypp"] += 1
                    missing["success"] += 1
                    continue

                hypp = _rate(home_game.get("offensiveYards"), home_game.get("offensivePlays"))
                aypp = _rate(away_game.get("offensiveYards"), away_game.get("offensivePlays"))
                if hypp is not None and aypp is not None:
                    ypp_obs.extend(((home, away, hypp), (away, home, aypp)))
                else:
                    missing["ypp"] += 1

                hsr = _rate(home_game.get("successfulPlays"), home_game.get("successEligiblePlays"))
                asr = _rate(away_game.get("successfulPlays"), away_game.get("successEligiblePlays"))
                if hsr is not None and asr is not None:
                    success_obs.extend(((home, away, hsr), (away, home, asr)))
                else:
                    missing["success"] += 1

            states["POINTS_OD"].update_partition(points_obs)
            states["YPP_OD"].update_partition(ypp_obs)
            states["SUCCESS_OD"].update_partition(success_obs)

    return out, missing


def _attach_state_features(
    row: dict[str, Any],
    signals: dict[str, dict[str, tuple[float, float, float]]],
) -> dict[str, Any]:
    gid = str(row.get("gameId"))
    out = dict(row)
    for family in STATE_SPECS:
        pair = signals[family].get(gid)
        if pair is None:
            raise ValueError(f"Missing {family} pregame signal for game {gid}")
        out[f"{family}_homeMatchup"] = float(pair[0])
        out[f"{family}_awayMatchup"] = float(pair[1])
        out[f"{family}_uncertainty"] = float(pair[2])
    return out


def _fit_margin(rows: list[dict[str, Any]], features: tuple[str, ...]) -> Any:
    x = np.asarray([[float(row[name]) for name in features] for row in rows], dtype=float)
    y = np.asarray([float(row["target_margin"]) for row in rows], dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Non-finite dynamic O/D margin data")
    model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    model.fit(x, y)
    return model


def _predict_margin(model: Any, rows: list[dict[str, Any]], features: tuple[str, ...]) -> np.ndarray:
    x = np.asarray([[float(row[name]) for name in features] for row in rows], dtype=float)
    return np.asarray(model.predict(x), dtype=float)


def _summary_at_threshold(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    return summarize_bets(threshold_rows(list(rows), THRESHOLD))


def _check_baseline(summary: dict[str, Any]) -> None:
    observed = {key: int(summary[key]) for key in EXPECTED_BASELINE}
    if observed != EXPECTED_BASELINE:
        raise ValueError(
            "FULL baseline reproduction failed; refusing dynamic O/D comparison. "
            f"expected={EXPECTED_BASELINE} observed={observed}"
        )


def _pooled_variant(rows: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    selected = [row for row in rows if row["variant"] == variant]
    cal = calibration_summary(selected)
    return {"variant": variant, **_summary_at_threshold(selected), "brier": cal["brier"], "calibration": cal}


def _recent_variant(rows: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    selected = [row for row in rows if row["variant"] == variant and int(row["season"]) >= 2023]
    cal = calibration_summary(selected)
    return {"variant": variant, **_summary_at_threshold(selected), "brier": cal["brier"]}


def _delta(left: Any, right: Any, scale: float = 1.0) -> float | None:
    if left is None or right is None:
        return None
    return (float(left) - float(right)) * scale


def run(
    lines: Path,
    raw_root: Path,
    processed_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = load_data(raw_root, processed_root)
    signals, missing_observations = build_od_signals(data, raw_root, processed_root)
    market = clean_market_rows(lines)
    market_by_id = {str(row["gameId"]): row for row in market}

    attached: dict[int, list[dict[str, Any]]] = {}
    for season in DEFAULT_SEASONS:
        rows: list[dict[str, Any]] = []
        for base in data[season]:
            market_row = market_by_id.get(str(base.get("gameId")))
            if market_row is None:
                continue
            row = attach_market(base, market_row)
            row = _attach_state_features(row, signals)
            needed = set(BASELINE_FEATURES)
            for features in FAMILY_FEATURES.values():
                needed.update(features)
            if all(finite(row.get(name)) for name in needed):
                rows.append(row)
        attached[season] = rows

    eligible = {
        season: [row for row in attached[season] if eligible_site(row, MIN_GAMES)]
        for season in DEFAULT_SEASONS
    }

    baseline_games: list[dict[str, Any]] = []
    augmented_games: list[dict[str, Any]] = []
    standalone_games: list[dict[str, Any]] = []
    margin_games: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []
    added_coefficients: list[dict[str, Any]] = []

    for test_season in TEST_SEASONS:
        train = [
            row
            for season in DEFAULT_SEASONS
            if season < test_season
            for row in eligible[season]
        ]
        test = eligible[test_season]
        if not train or not test:
            raise ValueError(f"Empty dynamic O/D fold for {test_season}")

        baseline_model = fit_logistic(train, BASELINE_FEATURES)
        baseline_prob = predict_home_cover(baseline_model, test, BASELINE_FEATURES)
        fold_baseline: list[dict[str, Any]] = []
        for row, prob in zip(test, baseline_prob):
            record = make_game_record(
                row,
                min_games=MIN_GAMES,
                season=test_season,
                variant=BASELINE,
                probability_home_cover=float(prob),
            )
            fold_baseline.append(record)
            baseline_games.append(record)

        baseline_summary = _summary_at_threshold(fold_baseline)
        baseline_brier = calibration_summary(fold_baseline)["brier"]

        for family in FAMILIES:
            state_features = FAMILY_FEATURES[family]
            augmented_name = f"FULL_PLUS_{family}"
            standalone_name = f"STANDALONE_{family}"

            # Standalone state-space margin diagnostic.
            margin_model = _fit_margin(train, state_features)
            margin_pred = _predict_margin(margin_model, test, state_features)
            for row, pred in zip(test, margin_pred):
                margin_games.append({
                    "season": int(test_season),
                    "family": family,
                    "gameId": str(row["gameId"]),
                    "actualHomeMargin": float(row["target_margin"]),
                    "marketHomeMargin": float(row["marketHomeMargin"]),
                    "predictedHomeMargin": float(pred),
                })

            # Standalone direct ATS probability from state + market context.
            standalone_features = STANDALONE_ATS_FEATURES[family]
            standalone_model = fit_logistic(train, standalone_features)
            standalone_prob = predict_home_cover(standalone_model, test, standalone_features)
            fold_standalone: list[dict[str, Any]] = []
            for row, prob in zip(test, standalone_prob):
                record = make_game_record(
                    row,
                    min_games=MIN_GAMES,
                    season=test_season,
                    variant=standalone_name,
                    probability_home_cover=float(prob),
                )
                fold_standalone.append(record)
                standalone_games.append(record)

            # Main incremental test: exact FULL baseline + only this family.
            augmented_features = AUGMENTED_FEATURES[family]
            augmented_model = fit_logistic(train, augmented_features)
            augmented_prob = predict_home_cover(augmented_model, test, augmented_features)
            fold_augmented: list[dict[str, Any]] = []
            for row, prob in zip(test, augmented_prob):
                record = make_game_record(
                    row,
                    min_games=MIN_GAMES,
                    season=test_season,
                    variant=augmented_name,
                    probability_home_cover=float(prob),
                )
                fold_augmented.append(record)
                augmented_games.append(record)

            added_coefficients.extend(
                coef
                for coef in coefficient_rows(
                    augmented_model,
                    augmented_features,
                    MIN_GAMES,
                    test_season,
                    augmented_name,
                )
                if coef["feature"] in state_features
            )

            aug_summary = _summary_at_threshold(fold_augmented)
            aug_brier = calibration_summary(fold_augmented)["brier"]
            stand_summary = _summary_at_threshold(fold_standalone)
            stand_brier = calibration_summary(fold_standalone)["brier"]
            folds.append({
                "season": int(test_season),
                "family": family,
                "trainN": len(train),
                "testN": len(test),
                "baseline": {**baseline_summary, "brier": baseline_brier},
                "augmented": {**aug_summary, "brier": aug_brier},
                "standaloneAts": {**stand_summary, "brier": stand_brier},
                "deltaAccuracyPP": _delta(aug_summary["accuracy"], baseline_summary["accuracy"], 100.0),
                "deltaRoiPP": _delta(aug_summary["roiMinus110"], baseline_summary["roiMinus110"], 100.0),
                "deltaBrier": _delta(aug_brier, baseline_brier),
            })

    baseline_pooled = _pooled_variant(baseline_games, BASELINE)
    _check_baseline(baseline_pooled)

    pooled_augmented: list[dict[str, Any]] = []
    pooled_standalone: list[dict[str, Any]] = []
    pooled_margin: list[dict[str, Any]] = []
    recent: list[dict[str, Any]] = []
    overlaps: list[dict[str, Any]] = []

    baseline_recent = _recent_variant(baseline_games, BASELINE)
    for family in FAMILIES:
        augmented_name = f"FULL_PLUS_{family}"
        standalone_name = f"STANDALONE_{family}"
        aug = _pooled_variant(augmented_games, augmented_name)
        stand = _pooled_variant(standalone_games, standalone_name)
        pooled_augmented.append({
            "family": family,
            "baseline": baseline_pooled,
            "augmented": aug,
            "deltaAccuracyPP": _delta(aug["accuracy"], baseline_pooled["accuracy"], 100.0),
            "deltaRoiPP": _delta(aug["roiMinus110"], baseline_pooled["roiMinus110"], 100.0),
            "deltaBrier": _delta(aug["brier"], baseline_pooled["brier"]),
        })
        pooled_standalone.append({"family": family, **stand})

        mg = [row for row in margin_games if row["family"] == family]
        grade_rows = [
            {"target_margin": row["actualHomeMargin"], "marketHomeMargin": row["marketHomeMargin"]}
            for row in mg
        ]
        pooled_margin.append({
            "family": family,
            **grade_margin_predictions(
                grade_rows,
                np.asarray([row["predictedHomeMargin"] for row in mg], dtype=float),
            ),
        })

        aug_recent = _recent_variant(augmented_games, augmented_name)
        recent.append({
            "family": family,
            "baseline": baseline_recent,
            "augmented": aug_recent,
            "deltaAccuracyPP": _delta(aug_recent["accuracy"], baseline_recent["accuracy"], 100.0),
            "deltaRoiPP": _delta(aug_recent["roiMinus110"], baseline_recent["roiMinus110"], 100.0),
            "deltaBrier": _delta(aug_recent["brier"], baseline_recent["brier"]),
        })

        aug_rows = [row for row in augmented_games if row["variant"] == augmented_name]
        overlaps.append({
            "family": family,
            **selection_overlap(baseline_games, aug_rows),
        })

    report = {
        "schemaVersion": 1,
        "version": VERSION,
        "status": "EXPLORATORY_POST_DISCOVERY_MODEL_FAMILY_SCREEN",
        "researchQuestion": "Do separate evolving Gaussian offense/defense states improve the existing FULL ATS logistic?",
        "minGames": MIN_GAMES,
        "confidenceThreshold": THRESHOLD,
        "testSeasons": list(TEST_SEASONS),
        "offseasonCarry": OFFSEASON_CARRY,
        "pointsHfa": POINTS_HFA,
        "stateSpecs": STATE_SPECS,
        "families": {name: list(features) for name, features in FAMILY_FEATURES.items()},
        "yppSemantics": "existing derived team-game offensiveYards/offensivePlays; intentionally not retuned to another denominator",
        "missingObservationGames": missing_observations,
        "baselineExpectedDiscoveryRecord": EXPECTED_BASELINE,
        "baselineReproduction": "PASS",
        "baselinePooled": baseline_pooled,
        "pooledMargin": pooled_margin,
        "pooledStandaloneAts": pooled_standalone,
        "pooledFullAugmentation": pooled_augmented,
        "recent2023To2025": recent,
        "folds": folds,
        "selectionOverlap": overlaps,
        "addedCoefficientRows": added_coefficients,
        "addedCoefficientStability": coefficient_stability(added_coefficients),
    }

    all_games = baseline_games + augmented_games + standalone_games
    return report, all_games


def _pct(value: Any) -> str:
    return "NA" if value is None else f"{float(value):.3%}"


def _write(path: Path, payload: Any, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output exists: {path}; use --overwrite intentionally")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dynamic Bayesian offense/defense model-family screen")
    parser.add_argument("--lines", type=Path, default=DEFAULT_LINES)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--games-output", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    report, games = run(args.lines, args.raw_root, args.processed_root)
    print("DYNAMIC BAYESIAN OFFENSE/DEFENSE — EXPLORATORY")
    print(f"Version: {VERSION}")
    print(f"minGames={MIN_GAMES} ATS threshold={THRESHOLD:.3f}")
    print("All current-partition predictions are made before current-partition state updates.")
    print("BASELINE REPRODUCTION: PASS (265-220-10, 495 bets)\n")

    print("=== STANDALONE MARGIN VS MARKET ===")
    for row in sorted(report["pooledMargin"], key=lambda r: float(r["deltaMaeVsMarket"])):
        print(
            f"{row['family']:<12} n={row['n']:4d} MAE={row['mae']:.4f} market={row['marketMae']:.4f} "
            f"dMAE={row['deltaMaeVsMarket']:+.4f} RMSE={row['rmse']:.4f} "
            f"dRMSE={row['deltaRmseVsMarket']:+.4f}"
        )

    print("\n=== STANDALONE DIRECT ATS at 0.575 ===")
    for row in report["pooledStandaloneAts"]:
        print(
            f"{row['family']:<12} bets={row['bets']:3d} ATS={row['wins']}-{row['losses']}-{row['pushes']} "
            f"({_pct(row['accuracy'])}) ROI={_pct(row['roiMinus110'])} Brier={row['brier']:.6f}"
        )

    base = report["baselinePooled"]
    print("\n=== FULL ATS AUGMENTATION — PRIMARY TEST ===")
    print(
        f"BASELINE     bets={base['bets']:3d} ATS={base['wins']}-{base['losses']}-{base['pushes']} "
        f"({_pct(base['accuracy'])}) ROI={_pct(base['roiMinus110'])} Brier={base['brier']:.6f}"
    )
    for row in report["pooledFullAugmentation"]:
        aug = row["augmented"]
        print(
            f"+{row['family']:<11} bets={aug['bets']:3d} ATS={aug['wins']}-{aug['losses']}-{aug['pushes']} "
            f"({_pct(aug['accuracy'])}) ROI={_pct(aug['roiMinus110'])} Brier={aug['brier']:.6f} | "
            f"dATS={row['deltaAccuracyPP']:+.3f}pp dROI={row['deltaRoiPP']:+.3f}pp dBrier={row['deltaBrier']:+.6f}"
        )

    print("\n=== SEASON STABILITY — FULL AUGMENTATION ===")
    for family in FAMILIES:
        print(f"{family}:")
        for fold in [r for r in report["folds"] if r["family"] == family]:
            b = fold["baseline"]
            a = fold["augmented"]
            print(
                f"  {fold['season']}: BASE {b['wins']}-{b['losses']}-{b['pushes']} {_pct(b['accuracy'])} "
                f"| AUG {a['wins']}-{a['losses']}-{a['pushes']} {_pct(a['accuracy'])} "
                f"dATS={fold['deltaAccuracyPP'] if fold['deltaAccuracyPP'] is not None else float('nan'):+.3f}pp "
                f"dBrier={fold['deltaBrier'] if fold['deltaBrier'] is not None else float('nan'):+.6f}"
            )

    print("\n=== RECENT 2023-2025 — FULL AUGMENTATION ===")
    for row in report["recent2023To2025"]:
        b, a = row["baseline"], row["augmented"]
        print(
            f"{row['family']:<12} BASE {b['wins']}-{b['losses']}-{b['pushes']} {_pct(b['accuracy'])} ROI={_pct(b['roiMinus110'])} "
            f"| AUG {a['wins']}-{a['losses']}-{a['pushes']} {_pct(a['accuracy'])} ROI={_pct(a['roiMinus110'])} "
            f"dATS={row['deltaAccuracyPP']:+.3f}pp dBrier={row['deltaBrier']:+.6f}"
        )

    print("\n=== BET SELECTION OVERLAP ===")
    for row in report["selectionOverlap"]:
        print(
            f"{row['family']:<12} both={row['bothBet']} same={row['bothSameSide']} opposite={row['bothOppositeSide']} "
            f"base_only={row['baselineOnly']} aug_only={row['challengerOnly']}"
        )
        bo = row["baselineOnlyPerformance"]
        ao = row["challengerOnlyPerformance"]
        print(
            f"  base-only {bo['wins']}-{bo['losses']}-{bo['pushes']} {_pct(bo['accuracy'])} ROI={_pct(bo['roiMinus110'])} | "
            f"aug-only {ao['wins']}-{ao['losses']}-{ao['pushes']} {_pct(ao['accuracy'])} ROI={_pct(ao['roiMinus110'])}"
        )

    print("\n=== ADDED COEFFICIENT STABILITY ===")
    for row in sorted(
        report["addedCoefficientStability"],
        key=lambda r: (str(r["variant"]), -abs(float(r["mean"]))),
    ):
        print(
            f"{row['variant']:<24} {row['feature']:<34} mean={row['mean']:+.4f} std={row['std']:.4f} "
            f"sign=+{row['positiveFolds']}/-{row['negativeFolds']}"
        )

    print(f"\nMissing observation games: {report['missingObservationGames']}")
    _write(args.output, report, args.overwrite)
    _write(args.games_output, games, args.overwrite)
    print(f"Report: {args.output}")
    print(f"Per-game probabilities: {args.games_output}")
    print("WARNING: Historical outcomes are already discovery data; no positive row is untouched confirmation evidence.")


if __name__ == "__main__":
    main()
