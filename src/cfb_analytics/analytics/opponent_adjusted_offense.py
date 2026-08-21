"""Opponent-adjusted offensive rating prototype.

The published composite remains intentionally narrow:
* 50% opponent-adjusted points per resolved possession
* 30% opponent-adjusted success rate
* 20% opponent-adjusted scoring possessions per possession

Adjusted yards per drive is exposed as an additional diagnostic metric, but is
not yet included in the composite weight. Each game is adjusted against the
opponent's defensive performance in all OTHER FBS-vs-FBS games (leave-one-out).
"""
from __future__ import annotations

from dataclasses import dataclass
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any, Iterable

PPD_WEIGHT = 0.50
SUCCESS_WEIGHT = 0.30
SCORING_DRIVE_WEIGHT = 0.20


@dataclass(frozen=True)
class Totals:
    points: float = 0.0
    resolved_possessions: float = 0.0
    successes: float = 0.0
    success_plays: float = 0.0
    scoring_possessions: float = 0.0
    possessions: float = 0.0
    yards: float = 0.0
    yardage_possessions: float = 0.0

    def __add__(self, other: "Totals") -> "Totals":
        return Totals(
            self.points + other.points,
            self.resolved_possessions + other.resolved_possessions,
            self.successes + other.successes,
            self.success_plays + other.success_plays,
            self.scoring_possessions + other.scoring_possessions,
            self.possessions + other.possessions,
            self.yards + other.yards,
            self.yardage_possessions + other.yardage_possessions,
        )

    def __sub__(self, other: "Totals") -> "Totals":
        return Totals(
            self.points - other.points,
            self.resolved_possessions - other.resolved_possessions,
            self.successes - other.successes,
            self.success_plays - other.success_plays,
            self.scoring_possessions - other.scoring_possessions,
            self.possessions - other.possessions,
            self.yards - other.yards,
            self.yardage_possessions - other.yardage_possessions,
        )


def _number(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Missing numeric field {key!r} for game {row.get('gameId')} / {row.get('team')}")
    return float(value)


def _scoring_possessions(row: dict[str, Any], *, allowed: bool) -> float:
    suffix = "Allowed" if allowed else ""
    return sum(
        _number(row, f"{name}{suffix}")
        for name in ("possessionTouchdowns", "possessionFieldGoals", "otherScoringPossessions")
    )


def offensive_totals(row: dict[str, Any]) -> Totals:
    return Totals(
        points=_number(row, "possessionPoints"),
        resolved_possessions=_number(row, "resolvedPointPossessions"),
        successes=_number(row, "successfulPlays"),
        success_plays=_number(row, "successEligiblePlays"),
        scoring_possessions=_scoring_possessions(row, allowed=False),
        possessions=_number(row, "validatedPossessions"),
        yards=_number(row, "possessionYards"),
        yardage_possessions=_number(row, "yardagePossessions"),
    )


def defensive_totals(row: dict[str, Any]) -> Totals:
    return Totals(
        points=_number(row, "possessionPointsAllowed"),
        resolved_possessions=_number(row, "resolvedPointPossessionsAllowed"),
        successes=_number(row, "successfulPlaysAllowed"),
        success_plays=_number(row, "successEligiblePlaysAllowed"),
        scoring_possessions=_scoring_possessions(row, allowed=True),
        possessions=_number(row, "validatedDefensivePossessions"),
        yards=_number(row, "possessionYardsAllowed"),
        yardage_possessions=_number(row, "yardagePossessionsAllowed"),
    )


def _rate(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator > 0 else None


def metrics(totals: Totals) -> tuple[float | None, float | None, float | None, float | None]:
    return (
        _rate(totals.points, totals.resolved_possessions),
        _rate(totals.successes, totals.success_plays),
        _rate(totals.scoring_possessions, totals.possessions),
        _rate(totals.yards, totals.yardage_possessions),
    )


def _weighted_mean(values: Iterable[tuple[float, float]]) -> float:
    pairs = [(value, weight) for value, weight in values if weight > 0 and math.isfinite(value)]
    denominator = sum(weight for _, weight in pairs)
    if denominator <= 0:
        raise ValueError("Cannot compute weighted mean with zero total weight")
    return sum(value * weight for value, weight in pairs) / denominator


def _z_scores(values: dict[int, float]) -> dict[int, float]:
    population = list(values.values())
    sigma = pstdev(population)
    if sigma == 0:
        return {key: 0.0 for key in values}
    mu = fmean(population)
    return {key: (value - mu) / sigma for key, value in values.items()}


def _rank(values: dict[int, float]) -> dict[int, int]:
    ordered = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    return {team_id: rank for rank, (team_id, _) in enumerate(ordered, start=1)}


def _eligible_rows(rows: list[dict[str, Any]], season: int) -> list[dict[str, Any]]:
    filtered = []
    for row in rows:
        if int(row.get("season", -1)) != season:
            continue
        if str(row.get("classification", "")).lower() != "fbs":
            continue
        if str(row.get("opponent_classification", "")).lower() != "fbs":
            continue
        if row.get("gameValidationStatus") not in (None, "PASS"):
            continue
        filtered.append(row)
    return filtered


def calculate_opponent_adjusted_offense(rows: list[dict[str, Any]], season: int) -> list[dict[str, Any]]:
    """Return national offense rankings with auditable raw/adjusted components."""
    rows = _eligible_rows(rows, season)
    if not rows:
        raise ValueError(f"No eligible FBS-vs-FBS team-game rows found for {season}")

    defense_by_team: dict[int, Totals] = {}
    defense_game_by_key: dict[tuple[int, str], Totals] = {}
    offense_by_team: dict[int, Totals] = {}
    national_offense = Totals()
    team_names: dict[int, str] = {}

    for row in rows:
        team_id = int(row["team_id"])
        game_id = str(row.get("gameId") or row.get("game_id"))
        team_names[team_id] = str(row["team"])
        off = offensive_totals(row)
        defense = defensive_totals(row)
        national_offense = national_offense + off
        offense_by_team[team_id] = offense_by_team.get(team_id, Totals()) + off
        defense_by_team[team_id] = defense_by_team.get(team_id, Totals()) + defense
        defense_game_by_key[(team_id, game_id)] = defense

    national_ppd, national_success, national_scoring, national_ypd = metrics(national_offense)
    if None in (national_ppd, national_success, national_scoring, national_ypd):
        raise ValueError("National baselines could not be calculated")

    game_adjustments: dict[int, list[dict[str, float]]] = {}
    for row in rows:
        team_id = int(row["team_id"])
        opponent_id = int(row["opponent_id"])
        game_id = str(row.get("gameId") or row.get("game_id"))
        if opponent_id not in defense_by_team:
            continue

        opponent_game_defense = defense_game_by_key.get((opponent_id, game_id))
        if opponent_game_defense is None:
            opponent_game_defense = offensive_totals(row)

        opponent_loo = defense_by_team[opponent_id] - opponent_game_defense
        opp_ppd, opp_success, opp_scoring, opp_ypd = metrics(opponent_loo)
        if None in (opp_ppd, opp_success, opp_scoring, opp_ypd):
            continue

        off = offensive_totals(row)
        team_ppd, team_success, team_scoring, team_ypd = metrics(off)
        if None in (team_ppd, team_success, team_scoring, team_ypd):
            continue

        game_adjustments.setdefault(team_id, []).append({
            "adj_ppd": float(team_ppd) - float(opp_ppd) + float(national_ppd),
            "adj_success": float(team_success) - float(opp_success) + float(national_success),
            "adj_scoring": float(team_scoring) - float(opp_scoring) + float(national_scoring),
            "adj_ypd": float(team_ypd) - float(opp_ypd) + float(national_ypd),
            "ppd_weight": off.resolved_possessions,
            "success_weight": off.success_plays,
            "scoring_weight": off.possessions,
            "ypd_weight": off.yardage_possessions,
        })

    adjusted_ppd: dict[int, float] = {}
    adjusted_success: dict[int, float] = {}
    adjusted_scoring: dict[int, float] = {}
    adjusted_ypd: dict[int, float] = {}
    games_used: dict[int, int] = {}

    for team_id, games in game_adjustments.items():
        if not games:
            continue
        adjusted_ppd[team_id] = _weighted_mean((g["adj_ppd"], g["ppd_weight"]) for g in games)
        adjusted_success[team_id] = _weighted_mean((g["adj_success"], g["success_weight"]) for g in games)
        adjusted_scoring[team_id] = _weighted_mean((g["adj_scoring"], g["scoring_weight"]) for g in games)
        adjusted_ypd[team_id] = _weighted_mean((g["adj_ypd"], g["ypd_weight"]) for g in games)
        games_used[team_id] = len(games)

    common = set(adjusted_ppd) & set(adjusted_success) & set(adjusted_scoring) & set(adjusted_ypd)
    adjusted_ppd = {k: adjusted_ppd[k] for k in common}
    adjusted_success = {k: adjusted_success[k] for k in common}
    adjusted_scoring = {k: adjusted_scoring[k] for k in common}
    adjusted_ypd = {k: adjusted_ypd[k] for k in common}

    raw_ppd: dict[int, float] = {}
    raw_success: dict[int, float] = {}
    raw_scoring: dict[int, float] = {}
    raw_ypd: dict[int, float] = {}
    for team_id in common:
        team_ppd, team_success, team_scoring, team_ypd = metrics(offense_by_team[team_id])
        if None in (team_ppd, team_success, team_scoring, team_ypd):
            raise ValueError(f"Raw metrics could not be calculated for team {team_id}")
        raw_ppd[team_id] = float(team_ppd)
        raw_success[team_id] = float(team_success)
        raw_scoring[team_id] = float(team_scoring)
        raw_ypd[team_id] = float(team_ypd)

    z_ppd = _z_scores(adjusted_ppd)
    z_success = _z_scores(adjusted_success)
    z_scoring = _z_scores(adjusted_scoring)
    ppd_rank = _rank(adjusted_ppd)
    success_rank = _rank(adjusted_success)
    scoring_rank = _rank(adjusted_scoring)
    ypd_rank = _rank(adjusted_ypd)

    rating = {
        team_id: PPD_WEIGHT * z_ppd[team_id]
        + SUCCESS_WEIGHT * z_success[team_id]
        + SCORING_DRIVE_WEIGHT * z_scoring[team_id]
        for team_id in common
    }
    overall_rank = _rank(rating)

    output = []
    for team_id in sorted(common, key=lambda value: overall_rank[value]):
        output.append({
            "season": season,
            "rank": overall_rank[team_id],
            "team": team_names.get(team_id, str(team_id)),
            "team_id": team_id,
            "rating": rating[team_id],
            "raw_points_per_drive": raw_ppd[team_id],
            "adjusted_points_per_drive": adjusted_ppd[team_id],
            "points_per_drive_adjustment": adjusted_ppd[team_id] - raw_ppd[team_id],
            "points_per_drive_rank": ppd_rank[team_id],
            "raw_success_rate": raw_success[team_id],
            "adjusted_success_rate": adjusted_success[team_id],
            "success_rate_adjustment": adjusted_success[team_id] - raw_success[team_id],
            "success_rate_rank": success_rank[team_id],
            "raw_scoring_drive_rate": raw_scoring[team_id],
            "adjusted_scoring_drive_rate": adjusted_scoring[team_id],
            "scoring_drive_rate_adjustment": adjusted_scoring[team_id] - raw_scoring[team_id],
            "scoring_drive_rate_rank": scoring_rank[team_id],
            "raw_yards_per_drive": raw_ypd[team_id],
            "adjusted_yards_per_drive": adjusted_ypd[team_id],
            "yards_per_drive_adjustment": adjusted_ypd[team_id] - raw_ypd[team_id],
            "yards_per_drive_rank": ypd_rank[team_id],
            "games_used": games_used[team_id],
        })

    if not output:
        raise ValueError("No teams had enough leave-one-out opponent data to rank")
    return output


def load_team_games(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON array in {path}")
    return payload


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _format_row(row: dict[str, Any]) -> str:
    return (
        f"{row['rank']:>3}  {row['team']:<24.24} "
        f"RATING {row['rating']:>6.3f}  "
        f"PPD {row['adjusted_points_per_drive']:>5.2f} (#{row['points_per_drive_rank']:<3})  "
        f"YPD {row['adjusted_yards_per_drive']:>5.1f} (#{row['yards_per_drive_rank']:<3})  "
        f"SR {row['adjusted_success_rate'] * 100:>5.1f}% (#{row['success_rate_rank']:<3})  "
        f"SCORE% {row['adjusted_scoring_drive_rate'] * 100:>5.1f}% (#{row['scoring_drive_rate_rank']:<3})  "
        f"G {row['games_used']}"
    )


def _format_diagnostic_row(row: dict[str, Any]) -> str:
    return (
        f"{row['rank']:>3}  {row['team']:<20.20} "
        f"PPD {row['raw_points_per_drive']:>5.2f}->{row['adjusted_points_per_drive']:>5.2f} ({row['points_per_drive_adjustment']:+.2f})  "
        f"YPD {row['raw_yards_per_drive']:>5.1f}->{row['adjusted_yards_per_drive']:>5.1f} ({row['yards_per_drive_adjustment']:+.1f})  "
        f"SR {row['raw_success_rate'] * 100:>5.1f}->{row['adjusted_success_rate'] * 100:>5.1f}% ({row['success_rate_adjustment'] * 100:+.1f}pp)  "
        f"SCORE {row['raw_scoring_drive_rate'] * 100:>5.1f}->{row['adjusted_scoring_drive_rate'] * 100:>5.1f}% ({row['scoring_drive_rate_adjustment'] * 100:+.1f}pp)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test opponent-adjusted offensive rankings")
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--team", default="Michigan")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--diagnostics", action="store_true", help="Print raw -> adjusted metrics and schedule adjustment magnitude")
    args = parser.parse_args(argv)

    input_path = args.input or Path(f"data/canonical/season={args.season}/team_games.json")
    rows = calculate_opponent_adjusted_offense(load_team_games(input_path), args.season)

    print(f"\nOpponent-Adjusted Offense — {args.season}")
    print("Composite: 50% Adj PPD | 30% Adj Success Rate | 20% Adj Scoring Drive %")
    print("Adj YPD shown separately; not yet included in composite rating.")
    print("FBS vs FBS only; opponent defensive baseline excludes the graded game.\n")
    shown = rows[: max(0, args.top)]
    for row in shown:
        print(_format_row(row))

    target = next((row for row in rows if str(row["team"]).casefold() == args.team.casefold()), None)
    if target is not None and target not in shown:
        print(f"\n{args.team}:")
        print(_format_row(target))
    elif target is None:
        print(f"\n{args.team!r} was not found in the eligible ranking set.")

    if args.diagnostics:
        print("\nRaw -> Adjusted Diagnostics")
        print("Positive delta = schedule adjustment helped the offense; negative = hurt it.\n")
        diagnostic_rows = list(shown)
        if target is not None and target not in diagnostic_rows:
            diagnostic_rows.append(target)
        for row in diagnostic_rows:
            print(_format_diagnostic_row(row))

    if args.output:
        write_csv(rows, args.output)
        print(f"\nWrote {len(rows)} teams to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
