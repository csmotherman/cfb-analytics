"""Data-only prototype for the "Can You Beat 2019 LSU?" historical draft game.

Game loop (no website code here):

1. Spin a wheel that returns one historical FBS team-season.
2. Draft exactly one still-empty unit from that team-season.
3. Repeat until all seven units are filled.
4. Convert the seven selected unit strengths into a calibrated historical SRS-like
   team strength and estimate a neutral-field win probability versus 2019 LSU.
5. A probability strictly greater than 50% is a win.

The prototype intentionally keeps two concepts separate:

* unit grades are presentation/gameplay values derived from full-season team stats;
* the win probability is calibrated from historical SRS and actual FBS game margins.

This is retrospective historical-game data. It does not touch Prediction-v2 and is
not used by Beat the Model.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from cfb_analytics.sources.cfbd.client import CfbdClient, CfbdError

CHALLENGE_VERSION = "historical-unit-draft-v1"
TARGET_SEASON = 2019
TARGET_TEAM = "LSU"
DEFAULT_SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)
WHEEL_TOP_N_PER_SEASON = 35
ROUND_COUNT = 7
WIN_THRESHOLD = 0.50

CATEGORY_ORDER = (
    "playCalling",
    "rushingAttack",
    "passingAttack",
    "offensiveLine",
    "coverage",
    "defensiveLine",
    "linebackers",
)

CATEGORY_LABELS = {
    "playCalling": "Coach / Play Calling",
    "rushingAttack": "Rushing Attack",
    "passingAttack": "Passing Attack",
    "offensiveLine": "Offensive Line",
    "coverage": "Defensive Coverage",
    "defensiveLine": "Defensive Line",
    "linebackers": "Linebackers",
}

# (source path, weight, higher-is-better)
#
# SP+ subcomponents are used when the caller's CFBD access tier exposes them.
# Every category also has advanced-stat fallbacks so the prototype remains useful
# if opponent-adjusted ratings are unavailable. We deliberately keep the raw
# component list in the generated JSON so every grade is inspectable.
CATEGORY_SPECS: dict[str, tuple[tuple[str, float, bool], ...]] = {
    "playCalling": (
        ("sp.offense.standardDowns", 0.22, True),
        ("sp.offense.passingDowns", 0.18, True),
        ("sp.offense.success", 0.16, True),
        ("advanced.offense.standardDowns.successRate", 0.16, True),
        ("advanced.offense.passingDowns.successRate", 0.10, True),
        ("advanced.offense.pointsPerOpportunity", 0.18, True),
    ),
    "rushingAttack": (
        ("sp.offense.rushing", 0.30, True),
        ("advanced.offense.rushingPlays.successRate", 0.25, True),
        ("advanced.offense.rushingPlays.ppa", 0.20, True),
        ("advanced.offense.rushingPlays.explosiveness", 0.10, True),
        ("advanced.offense.secondLevelYards", 0.075, True),
        ("advanced.offense.openFieldYards", 0.075, True),
    ),
    "passingAttack": (
        ("sp.offense.passing", 0.36, True),
        ("advanced.offense.passingPlays.successRate", 0.22, True),
        ("advanced.offense.passingPlays.ppa", 0.27, True),
        ("advanced.offense.passingPlays.explosiveness", 0.15, True),
    ),
    "offensiveLine": (
        ("advanced.offense.lineYards", 0.24, True),
        ("advanced.offense.stuffRate", 0.24, False),
        ("advanced.offense.powerSuccess", 0.18, True),
        ("advanced.offense.rushingPlays.successRate", 0.12, True),
        ("sp.offense.rushing", 0.12, True),
        ("advanced.offense.successRate", 0.10, True),
    ),
    "coverage": (
        ("sp.defense.passing", 0.20, False),
        ("advanced.defense.passingPlays.successRate", 0.24, False),
        ("advanced.defense.passingPlays.ppa", 0.24, False),
        ("advanced.defense.passingPlays.explosiveness", 0.16, False),
        ("advanced.defense.havoc.db", 0.16, True),
    ),
    "defensiveLine": (
        ("sp.defense.rushing", 0.20, False),
        ("advanced.defense.rushingPlays.successRate", 0.18, False),
        ("advanced.defense.rushingPlays.ppa", 0.16, False),
        ("advanced.defense.stuffRate", 0.20, True),
        ("advanced.defense.havoc.frontSeven", 0.26, True),
    ),
    "linebackers": (
        ("sp.defense.success", 0.18, False),
        ("sp.defense.rushing", 0.14, False),
        ("advanced.defense.successRate", 0.18, False),
        ("advanced.defense.rushingPlays.successRate", 0.14, False),
        ("advanced.defense.pointsPerOpportunity", 0.16, False),
        ("advanced.defense.havoc.frontSeven", 0.20, True),
    ),
}


def _finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _number(value: Any) -> float | None:
    if _finite(value):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if text.endswith("%"):
            text = text[:-1]
            try:
                return float(text) / 100.0
            except ValueError:
                return None
        try:
            parsed = float(text)
        except ValueError:
            return None
        return parsed if math.isfinite(parsed) else None
    return None


def _dig(payload: Any, path: str) -> float | None:
    current = payload
    for key in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return _number(current)


def _mean_sd(values: Iterable[float]) -> tuple[float, float]:
    vals = [float(v) for v in values if _finite(v)]
    if not vals:
        return 0.0, 1.0
    mu = sum(vals) / len(vals)
    var = sum((v - mu) ** 2 for v in vals) / len(vals)
    return mu, math.sqrt(var) or 1.0


def _letter_grade(grade: float) -> str:
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
    if grade >= 67:
        return "D+"
    if grade >= 63:
        return "D"
    if grade >= 60:
        return "D-"
    return "F"


def _percentile_grades(values: list[float]) -> list[float]:
    """Return stable 1-99 presentation grades from within-season ranks."""
    if not values:
        return []
    ordered = sorted((value, idx) for idx, value in enumerate(values))
    n = len(ordered)
    out = [50.0] * n
    i = 0
    while i < n:
        j = i + 1
        while j < n and ordered[j][0] == ordered[i][0]:
            j += 1
        # Average rank for ties, with rank positions centered in their buckets.
        avg_rank = (i + (j - 1)) / 2.0
        pct = 100.0 * (avg_rank + 0.5) / n
        grade = min(99.0, max(1.0, pct))
        for k in range(i, j):
            out[ordered[k][1]] = grade
        i = j
    return out


def _season_category_scores(rows: list[dict[str, Any]]) -> None:
    """Attach seven era-normalized unit scores and 1-99 grades in place."""
    metric_paths = sorted({path for specs in CATEGORY_SPECS.values() for path, _, _ in specs})
    stats: dict[str, tuple[float, float]] = {}
    for path in metric_paths:
        values = [_dig(row, path) for row in rows]
        stats[path] = _mean_sd(v for v in values if v is not None)

    for row in rows:
        categories: dict[str, dict[str, Any]] = {}
        for category in CATEGORY_ORDER:
            numerator = 0.0
            denominator = 0.0
            components: list[dict[str, Any]] = []
            for path, weight, higher_is_better in CATEGORY_SPECS[category]:
                value = _dig(row, path)
                if value is None:
                    continue
                mu, sd = stats[path]
                z = (float(value) - mu) / sd
                if not higher_is_better:
                    z *= -1.0
                z = max(-3.5, min(3.5, z))
                numerator += weight * z
                denominator += weight
                components.append(
                    {
                        "metric": path,
                        "value": float(value),
                        "weight": weight,
                        "higherIsBetter": higher_is_better,
                        "seasonZ": z,
                    }
                )
            # At least two independent metrics are required. This lets SP+ fail open
            # while still preventing a single number from becoming an entire unit.
            score = numerator / denominator if denominator > 0 and len(components) >= 2 else None
            categories[category] = {
                "label": CATEGORY_LABELS[category],
                "z": score,
                "grade": None,
                "letter": None,
                "components": components,
            }
        row["categories"] = categories

    for category in CATEGORY_ORDER:
        eligible = [row for row in rows if _finite(row["categories"][category].get("z"))]
        grades = _percentile_grades([float(row["categories"][category]["z"]) for row in eligible])
        for row, grade in zip(eligible, grades):
            row["categories"][category]["grade"] = round(grade, 1)
            row["categories"][category]["letter"] = _letter_grade(grade)


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx > 0 and dy > 0 else 0.0


def fit_strength_model(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Calibrate a monotone seven-unit composite to historical SRS.

    We deliberately avoid unconstrained multivariate coefficients: overlapping
    defensive categories can otherwise produce a negative coefficient, which is a
    terrible game rule (a better unit should never lower your final team strength).
    Positive category/SRS correlations become normalized unit weights; a single
    linear scale then maps the weighted composite onto SRS points.
    """
    eligible = [
        row
        for row in rows
        if _finite(row.get("srs"))
        and all(_finite(row.get("categories", {}).get(cat, {}).get("z")) for cat in CATEGORY_ORDER)
    ]
    if len(eligible) < 50:
        raise ValueError(f"Not enough complete team-seasons to calibrate strength: {len(eligible)}")

    correlations: dict[str, float] = {}
    for category in CATEGORY_ORDER:
        xs = [float(row["categories"][category]["z"]) for row in eligible]
        ys = [float(row["srs"]) for row in eligible]
        correlations[category] = max(0.05, _pearson(xs, ys))
    total_corr = sum(correlations.values())
    weights = {category: correlations[category] / total_corr for category in CATEGORY_ORDER}

    composites = [
        sum(weights[cat] * float(row["categories"][cat]["z"]) for cat in CATEGORY_ORDER)
        for row in eligible
    ]
    targets = [float(row["srs"]) for row in eligible]
    mx = sum(composites) / len(composites)
    my = sum(targets) / len(targets)
    var = sum((x - mx) ** 2 for x in composites)
    cov = sum((x - mx) * (y - my) for x, y in zip(composites, targets))
    scale = cov / var if var > 0 else 1.0
    if scale <= 0:
        raise ValueError("Historical unit composite unexpectedly has non-positive SRS scale")
    intercept = my - scale * mx

    predictions = [intercept + scale * x for x in composites]
    residuals = [y - pred for y, pred in zip(targets, predictions)]
    rmse = math.sqrt(sum(e * e for e in residuals) / len(residuals))
    ss_tot = sum((y - my) ** 2 for y in targets)
    ss_res = sum(e * e for e in residuals)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {
        "version": "historical-unit-strength-srs-calibration-v1",
        "trainingTeamSeasons": len(eligible),
        "categoryWeights": weights,
        "categorySrsCorrelations": correlations,
        "intercept": intercept,
        "scale": scale,
        "rmse": rmse,
        "r2": r2,
    }


def predict_hybrid_srs(strength_model: dict[str, Any], selections: dict[str, dict[str, Any]]) -> float:
    missing = [cat for cat in CATEGORY_ORDER if cat not in selections]
    if missing:
        raise ValueError(f"Hybrid team is missing categories: {', '.join(missing)}")
    weights = strength_model["categoryWeights"]
    composite = 0.0
    for category in CATEGORY_ORDER:
        z = selections[category].get("z")
        if not _finite(z):
            raise ValueError(f"Selection for {category} has no valid z score")
        composite += float(weights[category]) * float(z)
    return float(strength_model["intercept"]) + float(strength_model["scale"]) * composite


def _solve_2x2(a11: float, a12: float, a22: float, b1: float, b2: float) -> tuple[float, float] | None:
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-12:
        return None
    return ((b1 * a22 - b2 * a12) / det, (a11 * b2 - a12 * b1) / det)


def fit_margin_calibration(games: list[dict[str, Any]], srs_by_key: dict[str, float]) -> dict[str, Any]:
    """Fit margin ~= beta*SRS_diff + HFA using completed historical FBS games."""
    rows: list[tuple[float, float, float]] = []
    for game in games:
        if not isinstance(game, dict) or not game.get("completed"):
            continue
        if str(game.get("homeClassification") or "").lower() != "fbs":
            continue
        if str(game.get("awayClassification") or "").lower() != "fbs":
            continue
        hp = _number(game.get("homePoints"))
        ap = _number(game.get("awayPoints"))
        season = game.get("season")
        home = game.get("homeTeam")
        away = game.get("awayTeam")
        if hp is None or ap is None or season is None or not home or not away or hp == ap:
            continue
        hs = srs_by_key.get(f"{int(season)}::{home}")
        aws = srs_by_key.get(f"{int(season)}::{away}")
        if not (_finite(hs) and _finite(aws)):
            continue
        srs_diff = float(hs) - float(aws)
        home_field = 0.0 if bool(game.get("neutralSite")) else 1.0
        margin = float(hp) - float(ap)
        rows.append((srs_diff, home_field, margin))

    if len(rows) < 500:
        raise ValueError(f"Not enough historical FBS games for probability calibration: {len(rows)}")

    a11 = sum(x1 * x1 for x1, _, _ in rows)
    a12 = sum(x1 * x2 for x1, x2, _ in rows)
    a22 = sum(x2 * x2 for _, x2, _ in rows)
    b1 = sum(x1 * y for x1, _, y in rows)
    b2 = sum(x2 * y for _, x2, y in rows)
    solved = _solve_2x2(a11, a12, a22, b1, b2)
    if solved is None:
        raise ValueError("Historical margin calibration solve was singular")
    beta, hfa = solved
    if beta <= 0:
        raise ValueError(f"Historical SRS margin scale must be positive, got {beta}")

    residuals = [y - (beta * x1 + hfa * x2) for x1, x2, y in rows]
    residual_sd = math.sqrt(sum(e * e for e in residuals) / len(residuals))
    return {
        "version": "historical-srs-margin-probability-v1",
        "games": len(rows),
        "srsToMarginScale": beta,
        "homeFieldPoints": hfa,
        "residualSd": residual_sd,
        "neutralFieldRule": "expected margin = srsToMarginScale * (challengerSrs - opponentSrs)",
    }


def neutral_win_probability(challenger_srs: float, opponent_srs: float, calibration: dict[str, Any]) -> float:
    beta = float(calibration["srsToMarginScale"])
    sd = float(calibration["residualSd"])
    margin = beta * (float(challenger_srs) - float(opponent_srs))
    if sd <= 0:
        return 1.0 if margin > 0 else 0.0 if margin < 0 else 0.5
    return 0.5 * (1.0 + math.erf(margin / (sd * math.sqrt(2.0))))


def _coach_map(payload: Any, season: int) -> dict[str, dict[str, Any]]:
    candidates: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    if not isinstance(payload, list):
        return {}
    for raw in payload:
        if not isinstance(raw, dict) or int(raw.get("year", -1)) != int(season):
            continue
        team = raw.get("team")
        coach = raw.get("coach")
        school = team.get("school") if isinstance(team, dict) else None
        if not school or not isinstance(coach, dict):
            continue
        candidates[str(school)].append(raw)

    out: dict[str, dict[str, Any]] = {}
    for school, rows in candidates.items():
        best = max(rows, key=lambda row: int(row.get("games") or 0))
        coach = best.get("coach") or {}
        out[school] = {
            "id": coach.get("id"),
            "name": " ".join(
                part for part in (str(coach.get("firstName") or "").strip(), str(coach.get("lastName") or "").strip()) if part
            ) or None,
            "games": best.get("games"),
            "wins": best.get("wins"),
            "losses": best.get("losses"),
            "ties": best.get("ties"),
            "winPercentage": best.get("winPercentage"),
            "srs": best.get("srs"),
            "spOverall": best.get("spOverall"),
            "spOffense": best.get("spOffense"),
            "spDefense": best.get("spDefense"),
        }
    return out


def _team_metadata(payload: Any) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(payload, list):
        return out
    for raw in payload:
        if not isinstance(raw, dict) or str(raw.get("classification") or "").lower() != "fbs":
            continue
        school = raw.get("school")
        if not school:
            continue
        logos = raw.get("logos")
        logo = None
        if isinstance(logos, list):
            logo = next((str(value) for value in logos if isinstance(value, str) and value.strip()), None)
        out[str(school)] = {
            "teamId": raw.get("id"),
            "abbreviation": raw.get("abbreviation"),
            "conference": raw.get("conference"),
            "color": raw.get("color"),
            "alternateColor": raw.get("alternateColor", raw.get("alternate_color")),
            "logo": logo,
        }
    return out


def _sp_map(payload: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, list):
        return {}
    return {
        str(raw.get("team")): raw
        for raw in payload
        if isinstance(raw, dict) and raw.get("team")
    }


def _srs_map(payload: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, list):
        return {}
    return {
        str(raw.get("team")): raw
        for raw in payload
        if isinstance(raw, dict) and raw.get("team") and _finite(raw.get("rating"))
    }


def _advanced_rows(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    return [raw for raw in payload if isinstance(raw, dict) and raw.get("team")]


def _player_stats_for_target(payload: Any) -> list[dict[str, Any]]:
    """Keep a compact inspectable copy of target player season stats."""
    rows: list[dict[str, Any]] = []
    if not isinstance(payload, list):
        return rows
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        rows.append(
            {
                "playerId": raw.get("playerId"),
                "player": raw.get("player"),
                "position": raw.get("position"),
                "category": raw.get("category"),
                "statType": raw.get("statType"),
                "stat": raw.get("stat"),
            }
        )
    rows.sort(key=lambda row: (str(row.get("player") or ""), str(row.get("category") or ""), str(row.get("statType") or "")))
    return rows


def _target_player_highlights(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Best-effort player leader extraction while retaining raw target rows too."""
    patterns = {
        "passing": ("passing", ("yd", "yard")),
        "rushing": ("rushing", ("yd", "yard")),
        "receiving": ("receiving", ("yd", "yard")),
        "sacks": ("defensive", ("sack",)),
        "tacklesForLoss": ("defensive", ("tfl", "loss")),
        "interceptions": ("defensive", ("int", "interception")),
        "tackles": ("defensive", ("tackle",)),
    }
    out: dict[str, list[dict[str, Any]]] = {}
    for label, (category_hint, stat_hints) in patterns.items():
        candidates: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            cat = str(row.get("category") or "").casefold()
            stat_type = str(row.get("statType") or "").casefold()
            if category_hint not in cat and category_hint not in stat_type:
                continue
            if not any(hint in stat_type or hint in cat for hint in stat_hints):
                continue
            value = _number(row.get("stat"))
            if value is None:
                continue
            candidates.append((value, row))
        candidates.sort(key=lambda pair: pair[0], reverse=True)
        out[label] = [
            {**row, "numericStat": value}
            for value, row in candidates[:3]
        ]
    return out


def _fetch_optional(client: CfbdClient, path: str, params: dict[str, Any]) -> Any:
    try:
        return client.get_json(path, params).payload
    except CfbdError:
        return []


def build_dataset(
    client: CfbdClient,
    *,
    seasons: tuple[int, ...] = DEFAULT_SEASONS,
    wheel_top_n: int = WHEEL_TOP_N_PER_SEASON,
    difficulty_simulations: int = 5000,
    difficulty_seed: int = 2019,
) -> dict[str, Any]:
    metadata = _team_metadata(client.teams().payload)
    all_rows: list[dict[str, Any]] = []
    all_games: list[dict[str, Any]] = []
    source_status: dict[str, dict[str, str]] = {}

    for season in seasons:
        advanced_payload = client.team_season_advanced_stats(
            season,
            exclude_garbage_time=True,
        ).payload
        sp_payload = _fetch_optional(client, "/ratings/sp", {"year": season, "classification": "fbs"})
        srs_payload = _fetch_optional(client, "/ratings/srs", {"year": season})
        coaches_payload = _fetch_optional(client, "/coaches/seasons", {"year": season})
        games_payload = _fetch_optional(
            client,
            "/games",
            {"year": season, "seasonType": "both", "classification": "fbs"},
        )

        advanced = _advanced_rows(advanced_payload)
        sp_by_team = _sp_map(sp_payload)
        srs_by_team = _srs_map(srs_payload)
        coaches_by_team = _coach_map(coaches_payload, season)
        season_rows: list[dict[str, Any]] = []

        source_status[str(season)] = {
            "advanced": "ok" if advanced else "missing",
            "sp": "ok" if sp_by_team else "missing-fail-open",
            "srs": "ok" if srs_by_team else "coach-fallback",
            "coaches": "ok" if coaches_by_team else "missing-fail-open",
            "games": "ok" if isinstance(games_payload, list) and games_payload else "missing",
        }

        for raw in advanced:
            team = str(raw.get("team"))
            coach = coaches_by_team.get(team, {})
            srs_row = srs_by_team.get(team, {})
            srs = _number(srs_row.get("rating"))
            if srs is None:
                srs = _number(coach.get("srs"))
            row = {
                "season": season,
                "team": team,
                "conference": raw.get("conference") or metadata.get(team, {}).get("conference"),
                "advanced": raw,
                "sp": sp_by_team.get(team, {}),
                "srs": srs,
                "srsApiRank": srs_row.get("ranking"),
                "coach": coach or None,
                **metadata.get(team, {}),
            }
            season_rows.append(row)

        _season_category_scores(season_rows)
        ranked = sorted(
            [row for row in season_rows if _finite(row.get("srs"))],
            key=lambda row: float(row["srs"]),
            reverse=True,
        )
        for rank, row in enumerate(ranked, 1):
            row["srsRank"] = rank
        all_rows.extend(season_rows)
        if isinstance(games_payload, list):
            all_games.extend(game for game in games_payload if isinstance(game, dict))

    strength_model = fit_strength_model(all_rows)
    srs_by_key = {
        f"{int(row['season'])}::{row['team']}": float(row["srs"])
        for row in all_rows
        if _finite(row.get("srs"))
    }
    margin_calibration = fit_margin_calibration(all_games, srs_by_key)

    target_candidates = [
        row
        for row in all_rows
        if int(row.get("season", -1)) == TARGET_SEASON
        and str(row.get("team", "")).casefold() == TARGET_TEAM.casefold()
    ]
    if len(target_candidates) != 1:
        raise ValueError(f"Expected one {TARGET_SEASON} {TARGET_TEAM} row, found {len(target_candidates)}")
    target = target_candidates[0]

    wheel_pool = [
        row
        for row in all_rows
        if row is not target
        and _finite(row.get("srs"))
        and int(row.get("srsRank") or 9999) <= int(wheel_top_n)
        and all(_finite(row.get("categories", {}).get(cat, {}).get("z")) for cat in CATEGORY_ORDER)
    ]
    wheel_pool.sort(key=lambda row: (int(row["season"]), int(row.get("srsRank") or 9999), str(row["team"])))
    if len(wheel_pool) < 100:
        raise ValueError(f"Wheel pool unexpectedly small: {len(wheel_pool)}")

    raw_target_players = _fetch_optional(
        client,
        "/stats/player/season",
        {"year": TARGET_SEASON, "team": TARGET_TEAM, "seasonType": "both"},
    )
    target_player_stats = _player_stats_for_target(raw_target_players)

    # Drop the large source payloads from public/test rows while preserving every
    # category's metric audit trail. The resulting artifact is intentionally small
    # enough to inspect and later mirror into SOAR.
    def compact(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "season": row["season"],
            "team": row["team"],
            "conference": row.get("conference"),
            "teamId": row.get("teamId"),
            "abbreviation": row.get("abbreviation"),
            "logo": row.get("logo"),
            "color": row.get("color"),
            "alternateColor": row.get("alternateColor"),
            "srs": row.get("srs"),
            "srsRank": row.get("srsRank"),
            "coach": row.get("coach"),
            "categories": row.get("categories"),
        }

    compact_pool = [compact(row) for row in wheel_pool]
    compact_target = compact(target)
    compact_target["playerStats"] = target_player_stats
    compact_target["playerHighlights"] = _target_player_highlights(target_player_stats)

    dataset: dict[str, Any] = {
        "schemaVersion": 1,
        "challengeVersion": CHALLENGE_VERSION,
        "title": "Can You Beat the 2019 LSU Tigers?",
        "status": "data-prototype-only",
        "seasons": list(seasons),
        "excludedSeasons": [2020],
        "rules": {
            "rounds": ROUND_COUNT,
            "categories": [
                {"key": category, "label": CATEGORY_LABELS[category]}
                for category in CATEGORY_ORDER
            ],
            "wheel": "uniform random draw without replacement from eligible historical team-seasons",
            "mustDraftOneOpenCategoryPerSpin": True,
            "rerolls": 0,
            "site": "neutral",
            "winCondition": "estimated neutral-field win probability must be > 0.50",
            "winThreshold": WIN_THRESHOLD,
        },
        "wheelEligibility": {
            "topSrsPerSeason": wheel_top_n,
            "targetExcluded": True,
            "eligibleTeamSeasons": len(compact_pool),
            "reason": "Top historical team-seasons keep the game difficult but not dominated by unusable spins.",
        },
        "target": compact_target,
        "strengthModel": strength_model,
        "marginCalibration": margin_calibration,
        "wheelPool": compact_pool,
        "sourceStatus": source_status,
        "dataNotes": [
            "All unit grades use completed full-season historical data.",
            "Grades are normalized within each season before cross-era drafting.",
            "Offensive-line v1 uses line yards, stuff rate, power success, rushing success and optional SP rushing context; explicit sack/TFL-allowed splitting is a planned v2 refinement.",
            "Coverage/DL/LB are statistical unit proxies, not individual position-group scouting grades.",
            "The win-probability layer is calibrated to historical SRS and completed FBS game margins; it is separate from Prediction-v2.",
        ],
    }
    dataset["difficultyBenchmark"] = benchmark_difficulty(
        dataset,
        simulations=difficulty_simulations,
        seed=difficulty_seed,
    )
    return dataset


def _selection_from_row(row: dict[str, Any], category: str) -> dict[str, Any]:
    unit = row["categories"][category]
    return {
        "category": category,
        "label": CATEGORY_LABELS[category],
        "season": row["season"],
        "team": row["team"],
        "coach": row.get("coach"),
        "grade": unit.get("grade"),
        "letter": unit.get("letter"),
        "z": unit.get("z"),
    }


def evaluate_selections(dataset: dict[str, Any], selections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    strength = predict_hybrid_srs(dataset["strengthModel"], selections)
    target_srs = float(dataset["target"]["srs"])
    probability = neutral_win_probability(strength, target_srs, dataset["marginCalibration"])
    margin = float(dataset["marginCalibration"]["srsToMarginScale"]) * (strength - target_srs)
    return {
        "estimatedHybridSrs": strength,
        "targetSrs": target_srs,
        "expectedNeutralMargin": margin,
        "winProbability": probability,
        "win": probability > float(dataset["rules"]["winThreshold"]),
    }


def greedy_draft(dataset: dict[str, Any], spins: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    open_categories = set(CATEGORY_ORDER)
    selections: dict[str, dict[str, Any]] = {}
    weights = dataset["strengthModel"]["categoryWeights"]
    for row in spins:
        choices = []
        for category in open_categories:
            unit = row.get("categories", {}).get(category, {})
            if not _finite(unit.get("z")):
                continue
            value = float(weights[category]) * float(unit["z"])
            choices.append((value, category))
        if not choices:
            raise ValueError(f"Spin has no draftable open category: {row.get('season')} {row.get('team')}")
        _, chosen = max(choices)
        selections[chosen] = _selection_from_row(row, chosen)
        open_categories.remove(chosen)
    return selections, evaluate_selections(dataset, selections)


def _oracle_assignment(dataset: dict[str, Any], spins: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Best possible one-to-one assignment after seeing all seven spins.

    This is an upper-bound difficulty benchmark, not a player-facing strategy.
    """
    weights = dataset["strengthModel"]["categoryWeights"]
    # DP over category bitmasks: state -> (weighted score, assignment dict).
    states: dict[int, tuple[float, dict[str, int]]] = {0: (0.0, {})}
    for spin_idx, row in enumerate(spins):
        next_states: dict[int, tuple[float, dict[str, int]]] = {}
        for mask, (score, assignment) in states.items():
            for cat_idx, category in enumerate(CATEGORY_ORDER):
                bit = 1 << cat_idx
                if mask & bit:
                    continue
                z = row.get("categories", {}).get(category, {}).get("z")
                if not _finite(z):
                    continue
                new_mask = mask | bit
                new_score = score + float(weights[category]) * float(z)
                current = next_states.get(new_mask)
                if current is None or new_score > current[0]:
                    next_assignment = dict(assignment)
                    next_assignment[category] = spin_idx
                    next_states[new_mask] = (new_score, next_assignment)
        states = next_states
    full_mask = (1 << len(CATEGORY_ORDER)) - 1
    if full_mask not in states:
        raise ValueError("Could not assign all seven categories to the seven spins")
    assignment = states[full_mask][1]
    selections = {
        category: _selection_from_row(spins[spin_idx], category)
        for category, spin_idx in assignment.items()
    }
    return selections, evaluate_selections(dataset, selections)


def benchmark_difficulty(dataset: dict[str, Any], *, simulations: int = 5000, seed: int = 2019) -> dict[str, Any]:
    pool = dataset["wheelPool"]
    if simulations <= 0:
        raise ValueError("difficulty simulations must be positive")
    if len(pool) < ROUND_COUNT:
        raise ValueError("wheel pool is too small")
    rng = random.Random(seed)
    greedy_probs: list[float] = []
    oracle_probs: list[float] = []
    for _ in range(simulations):
        spins = rng.sample(pool, ROUND_COUNT)
        _, greedy = greedy_draft(dataset, spins)
        _, oracle = _oracle_assignment(dataset, spins)
        greedy_probs.append(float(greedy["winProbability"]))
        oracle_probs.append(float(oracle["winProbability"]))

    def summarize(values: list[float]) -> dict[str, Any]:
        ordered = sorted(values)
        n = len(ordered)
        return {
            "winRate": sum(value > WIN_THRESHOLD for value in values) / n,
            "meanWinProbability": mean(values),
            "medianWinProbability": ordered[n // 2],
            "p90WinProbability": ordered[min(n - 1, int(0.90 * n))],
            "maxWinProbability": ordered[-1],
        }

    return {
        "simulations": simulations,
        "seed": seed,
        "greedyVisibleGradeStrategy": summarize(greedy_probs),
        "perfectForesightUpperBound": summarize(oracle_probs),
        "interpretation": "If the upper-bound win rate is near zero, the wheel is too hard; if the greedy win rate is very high, it is too easy.",
    }


def spin(dataset: dict[str, Any], *, seed: int, count: int = ROUND_COUNT) -> list[dict[str, Any]]:
    pool = dataset["wheelPool"]
    if count > len(pool):
        raise ValueError("spin count exceeds wheel pool")
    return random.Random(seed).sample(pool, count)


def write_dataset(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_dataset(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def concise_demo(dataset: dict[str, Any], *, seed: int) -> str:
    spins = spin(dataset, seed=seed)
    selections, result = greedy_draft(dataset, spins)
    lines = [
        dataset["title"],
        f"Prototype seed: {seed}",
        "",
    ]
    for idx, row in enumerate(spins, 1):
        drafted = next(sel for sel in selections.values() if sel["season"] == row["season"] and sel["team"] == row["team"])
        lines.append(
            f"Spin {idx}: {row['season']} {row['team']} -> {drafted['label']} {drafted['letter']} ({drafted['grade']:.1f})"
        )
    lines.extend(
        [
            "",
            f"Estimated hybrid SRS: {result['estimatedHybridSrs']:.2f}",
            f"2019 LSU SRS: {result['targetSrs']:.2f}",
            f"Expected neutral margin: {result['expectedNeutralMargin']:+.2f}",
            f"Chance to beat 2019 LSU: {result['winProbability'] * 100.0:.1f}%",
            "WIN" if result["win"] else "LOSS",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true", help="Fetch CFBD historical inputs and build the prototype JSON")
    parser.add_argument("--data", type=Path, default=Path("data/prototypes/beat-2019-lsu/challenge-v1.json"))
    parser.add_argument("--demo", action="store_true", help="Run a deterministic seven-spin greedy demo from an existing JSON")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--difficulty-sims", type=int, default=5000)
    parser.add_argument("--wheel-top-n", type=int, default=WHEEL_TOP_N_PER_SEASON)
    args = parser.parse_args()

    if args.build:
        with CfbdClient() as client:
            payload = build_dataset(
                client,
                wheel_top_n=args.wheel_top_n,
                difficulty_simulations=args.difficulty_sims,
            )
        write_dataset(args.data, payload)
        print("HISTORICAL UNIT DRAFT DATA: PASS")
        print(f"output={args.data}")
        print(f"wheel={len(payload['wheelPool'])}")
        print(f"target={payload['target']['season']} {payload['target']['team']} srs={payload['target']['srs']:.2f}")
        print("greedyWinRate=", payload["difficultyBenchmark"]["greedyVisibleGradeStrategy"]["winRate"])
        print("oracleWinRate=", payload["difficultyBenchmark"]["perfectForesightUpperBound"]["winRate"])

    if args.demo:
        payload = load_dataset(args.data)
        print(concise_demo(payload, seed=args.seed))

    if not args.build and not args.demo:
        parser.error("choose --build and/or --demo")


if __name__ == "__main__":
    main()
