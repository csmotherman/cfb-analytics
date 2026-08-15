"""Leakage-safe opponent-adjusted drive PPD research model.

This layer uses only validated possession drives with resolvable offensive score
state.  It intentionally measures offensive points scored on possessions rather
than final team score, so defensive/special-teams scores are not credited to the
offense.

Research contract
-----------------
Observed drive PPD is fit as::

    observed_ppd = league_mean + offense_strength - defense_strength

where higher offense strength is better and higher defense strength is better.
Pregame snapshots are fit only from partitions strictly before the current
partition.  Postgame residuals are materialized separately and are target-side
diagnostics, never pregame features.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from cfb_analytics.derived.drives import derived_drive_partition_dir
from cfb_analytics.derived.pregame import _pk
from cfb_analytics.raw.audit import discover_partitions

DRIVE_PPD_VERSION = "drive-ppd-v1-research"
DEFAULT_SHRINKAGE_POSSESSIONS = 25.0


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def resolved_drive_points(drive: dict[str, Any]) -> float | None:
    """Return offensive points observed on one validated possession drive.

    Score deltas outside [0, 8] are treated as unresolved rather than guessed.
    This accommodates field goals, touchdowns with conversion, and ordinary
    scoreless possessions while rejecting broken score-state transitions.
    """
    if drive.get("isPossessionDrive") is not True or drive.get("driveValidationStatus") != "PASS":
        return None
    start = drive.get("startOffenseScore")
    end = drive.get("endOffenseScoreObserved")
    if not _num(start) or not _num(end):
        return None
    points = float(end) - float(start)
    if points < 0 or points > 8:
        return None
    return points


def build_team_game_drive_rows(drives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate resolved validated possessions into one row per team-game."""
    groups: dict[tuple[int, str, int, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    all_valid: Counter[tuple[int, str, int, str, str, str]] = Counter()
    for d in drives:
        if d.get("isPossessionDrive") is not True or d.get("driveValidationStatus") != "PASS":
            continue
        season = int(d.get("season") or 0)
        season_type = str(d.get("seasonType") or "regular")
        week = int(d.get("week") or 0)
        game_id = str(d.get("gameId"))
        offense = d.get("offense")
        defense = d.get("defense")
        if not season or not game_id or not offense or not defense:
            continue
        key = (season, season_type, week, game_id, str(offense), str(defense))
        all_valid[key] += 1
        points = resolved_drive_points(d)
        if points is not None:
            groups[key].append({"points": points, "drive": d})

    out: list[dict[str, Any]] = []
    for key in sorted(all_valid):
        season, season_type, week, game_id, offense, defense = key
        resolved = groups.get(key, [])
        points = sum(x["points"] for x in resolved)
        resolved_possessions = len(resolved)
        validated_possessions = all_valid[key]
        out.append({
            "season": season,
            "seasonType": season_type,
            "week": week,
            "gameId": game_id,
            "team": offense,
            "opponent": defense,
            "validatedPossessions": validated_possessions,
            "resolvedPointPossessions": resolved_possessions,
            "unresolvedPointPossessions": validated_possessions - resolved_possessions,
            "offensiveDrivePoints": points,
            "offensivePPD": points / resolved_possessions if resolved_possessions else None,
            "drivePpdVersion": DRIVE_PPD_VERSION,
        })
    return out


def fit_ppd_ratings(
    rows: list[dict[str, Any]],
    shrinkage_possessions: float = DEFAULT_SHRINKAGE_POSSESSIONS,
    damping: float = 1.0,
    tolerance: float = 1e-8,
    max_iterations: int = 2000,
) -> dict[str, Any]:
    """Fit observed PPD = mean + offense(team) - defense(opponent).

    Each team-game is weighted by resolved possessions.  Shrinkage is expressed
    in possession-equivalent units and pulls early ratings toward league average.
    """
    if shrinkage_possessions < 0:
        raise ValueError("shrinkage_possessions must be nonnegative")
    if not 0 < damping <= 1:
        raise ValueError("damping must be in (0, 1]")
    if tolerance <= 0 or max_iterations < 1:
        raise ValueError("tolerance and max_iterations must be positive")

    obs: list[tuple[str, str, float, float]] = []
    for row in rows:
        team, opponent = row.get("team"), row.get("opponent")
        ppd, possessions = row.get("offensivePPD"), row.get("resolvedPointPossessions")
        if team and opponent and team != opponent and _num(ppd) and _num(possessions) and float(possessions) > 0:
            obs.append((str(team), str(opponent), float(ppd), float(possessions)))

    if not obs:
        return {
            "leagueMean": None,
            "offense": {},
            "defense": {},
            "iterations": 0,
            "converged": True,
            "maxDelta": 0.0,
            "observations": 0,
            "possessions": 0.0,
            "version": DRIVE_PPD_VERSION,
        }

    total_weight = sum(w for *_, w in obs)
    league_mean = sum(value * w for _, _, value, w in obs) / total_weight
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
            target = raw / (weight + shrinkage_possessions)
            new_offense[team] = offense[team] + damping * (target - offense[team])

        new_defense = dict(defense)
        for team, games in by_defense.items():
            weight = sum(w for _, _, w in games)
            raw = sum(w * (league_mean + new_offense[opponent] - value) for opponent, value, w in games)
            target = raw / (weight + shrinkage_possessions)
            new_defense[team] = defense[team] + damping * (target - defense[team])

        max_delta = max(
            max(abs(new_offense[t] - offense[t]) for t in teams),
            max(abs(new_defense[t] - defense[t]) for t in teams),
        )
        offense, defense = new_offense, new_defense
        if max_delta <= tolerance:
            converged = True
            break

    # Identifiability: center both latent effects at zero and absorb means into
    # the intercept while preserving fitted values.
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
        "observations": len(obs),
        "possessions": total_weight,
        "version": DRIVE_PPD_VERSION,
    }


def expected_ppd(fitted: dict[str, Any], offense: str, defense: str) -> float | None:
    mean = fitted.get("leagueMean")
    off = fitted.get("offense", {}).get(str(offense))
    deff = fitted.get("defense", {}).get(str(defense))
    if not (_num(mean) and _num(off) and _num(deff)):
        return None
    return float(mean) + float(off) - float(deff)


def _raw_prior_ppd(history: list[dict[str, Any]], team: str, defensive: bool = False) -> tuple[float | None, int, float]:
    relevant = [r for r in history if (r.get("opponent") if defensive else r.get("team")) == team]
    points = sum(float(r.get("offensiveDrivePoints") or 0.0) for r in relevant)
    possessions = sum(int(r.get("resolvedPointPossessions") or 0) for r in relevant)
    games = len({str(r.get("gameId")) for r in relevant})
    return (points / possessions if possessions else None, games, float(possessions))


def build_pregame_ppd_snapshots(rows: list[dict[str, Any]], season: int, **fit_kwargs: Any) -> list[dict[str, Any]]:
    """Create leakage-safe team-game PPD snapshots from prior partitions only."""
    season_rows = [r for r in rows if r.get("season") == season]
    parts: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in season_rows:
        parts[_pk(row)].append(row)

    history: list[dict[str, Any]] = []
    out: list[dict[str, Any]] = []
    for key in sorted(parts):
        fitted = fit_ppd_ratings(history, **fit_kwargs)
        mean = fitted.get("leagueMean")
        for game in parts[key]:
            team = str(game.get("team"))
            opponent = str(game.get("opponent"))
            off = fitted.get("offense", {}).get(team)
            deff = fitted.get("defense", {}).get(team)
            raw_off, games_off, poss_off = _raw_prior_ppd(history, team, defensive=False)
            raw_def, games_def, poss_def = _raw_prior_ppd(history, team, defensive=True)
            out.append({
                "season": season,
                "seasonType": game.get("seasonType"),
                "week": game.get("week"),
                "gameId": game.get("gameId"),
                "team": team,
                "opponent": opponent,
                "gamesPlayedBefore": games_off,
                "defensiveGamesPlayedBefore": games_def,
                "resolvedOffensivePossessionsBefore": poss_off,
                "resolvedDefensivePossessionsBefore": poss_def,
                "rawOffensivePPDBefore": raw_off,
                "rawDefensivePPDAllowedBefore": raw_def,
                "ppdLeagueMeanBefore": mean,
                "opponentAdjustedOffensePPDAboveAverage": off,
                "opponentAdjustedDefensePPDPreventedAboveAverage": deff,
                "expectedOffensivePPDVsAverageDefense": float(mean) + float(off) if _num(mean) and _num(off) else None,
                "expectedDefensivePPDAllowedVsAverageOffense": float(mean) - float(deff) if _num(mean) and _num(deff) else None,
                "ppdFitIterations": fitted.get("iterations"),
                "ppdFitConverged": fitted.get("converged"),
                "ppdFitObservations": fitted.get("observations"),
                "ppdFitPossessions": fitted.get("possessions"),
                "drivePpdVersion": DRIVE_PPD_VERSION,
            })
        history.extend(parts[key])
    return out


def build_matchup_ppd(snapshots: list[dict[str, Any]], season: int) -> list[dict[str, Any]]:
    """Orient team snapshots into one expected-PPD row per game."""
    by_game: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in snapshots:
        if row.get("season") == season:
            by_game[str(row.get("gameId"))].append(row)

    out: list[dict[str, Any]] = []
    for game_id, pair in sorted(by_game.items()):
        if len(pair) != 2:
            continue
        a, b = pair
        if a.get("team") == b.get("team"):
            continue
        # Team rows already identify their opponent, so preserve that orientation.
        home = None
        away = None
        # Home/away is intentionally unresolved here; orient_matchup_ppd handles
        # it later from a model row that knows canonical home/away identity.
        mean = a.get("ppdLeagueMeanBefore")
        if not _num(mean) or b.get("ppdLeagueMeanBefore") != mean:
            mean = a.get("ppdLeagueMeanBefore") if _num(a.get("ppdLeagueMeanBefore")) else b.get("ppdLeagueMeanBefore")
        a_off = a.get("opponentAdjustedOffensePPDAboveAverage")
        a_def = a.get("opponentAdjustedDefensePPDPreventedAboveAverage")
        b_off = b.get("opponentAdjustedOffensePPDAboveAverage")
        b_def = b.get("opponentAdjustedDefensePPDPreventedAboveAverage")
        a_expected = float(mean) + float(a_off) - float(b_def) if all(_num(x) for x in (mean, a_off, b_def)) else None
        b_expected = float(mean) + float(b_off) - float(a_def) if all(_num(x) for x in (mean, b_off, a_def)) else None
        out.append({
            "season": season,
            "seasonType": a.get("seasonType"),
            "week": a.get("week"),
            "gameId": game_id,
            "team1": a.get("team"),
            "team2": b.get("team"),
            "team1OpponentAdjustedOffensePPDAboveAverage": a_off,
            "team1OpponentAdjustedDefensePPDPreventedAboveAverage": a_def,
            "team2OpponentAdjustedOffensePPDAboveAverage": b_off,
            "team2OpponentAdjustedDefensePPDPreventedAboveAverage": b_def,
            "team1ExpectedOffensivePPD": a_expected,
            "team1ExpectedDefensivePPDAllowed": b_expected,
            "team2ExpectedOffensivePPD": b_expected,
            "team2ExpectedDefensivePPDAllowed": a_expected,
            "expectedPPDDifferenceTeam1MinusTeam2": float(a_expected) - float(b_expected) if _num(a_expected) and _num(b_expected) else None,
            "ppdLeagueMeanBefore": mean,
            "team1GamesPlayedBefore": a.get("gamesPlayedBefore"),
            "team2GamesPlayedBefore": b.get("gamesPlayedBefore"),
            "drivePpdVersion": DRIVE_PPD_VERSION,
        })
    return out


def orient_matchup_ppd(matchup: dict[str, Any], home_team: str, away_team: str) -> dict[str, Any] | None:
    """Orient a matchup row to canonical home/away teams."""
    t1, t2 = matchup.get("team1"), matchup.get("team2")
    if {t1, t2} != {home_team, away_team}:
        return None
    home_is_1 = t1 == home_team
    hp = "team1" if home_is_1 else "team2"
    ap = "team2" if home_is_1 else "team1"
    home_expected = matchup.get(f"{hp}ExpectedOffensivePPD")
    away_expected = matchup.get(f"{ap}ExpectedOffensivePPD")
    return {
        "homeOpponentAdjustedOffensePPDAboveAverage": matchup.get(f"{hp}OpponentAdjustedOffensePPDAboveAverage"),
        "homeOpponentAdjustedDefensePPDPreventedAboveAverage": matchup.get(f"{hp}OpponentAdjustedDefensePPDPreventedAboveAverage"),
        "awayOpponentAdjustedOffensePPDAboveAverage": matchup.get(f"{ap}OpponentAdjustedOffensePPDAboveAverage"),
        "awayOpponentAdjustedDefensePPDPreventedAboveAverage": matchup.get(f"{ap}OpponentAdjustedDefensePPDPreventedAboveAverage"),
        "homeExpectedOffensivePPD": home_expected,
        "homeExpectedDefensivePPDAllowed": away_expected,
        "awayExpectedOffensivePPD": away_expected,
        "awayExpectedDefensivePPDAllowed": home_expected,
        "expectedPPDEdge": float(home_expected) - float(away_expected) if _num(home_expected) and _num(away_expected) else None,
        "ppdLeagueMeanBefore": matchup.get("ppdLeagueMeanBefore"),
        "drivePpdVersion": DRIVE_PPD_VERSION,
    }


def expected_score(expected_offensive_ppd: float | None, expected_possessions: float | None) -> float | None:
    if not _num(expected_offensive_ppd) or not _num(expected_possessions):
        return None
    return float(expected_offensive_ppd) * float(expected_possessions)


def attach_postgame_residuals(
    matchup_rows: list[dict[str, Any]],
    team_game_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Create target-side PPD-over-expectation diagnostics.

    These rows MUST NOT be fed into pregame features because they contain current
    game outcomes.
    """
    by_game_obs: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in team_game_rows:
        by_game_obs[str(row.get("gameId"))][str(row.get("team"))] = row
    out: list[dict[str, Any]] = []
    for matchup in matchup_rows:
        gid = str(matchup.get("gameId"))
        t1, t2 = str(matchup.get("team1")), str(matchup.get("team2"))
        r1, r2 = by_game_obs.get(gid, {}).get(t1), by_game_obs.get(gid, {}).get(t2)
        if not r1 or not r2:
            continue
        e1, e2 = matchup.get("team1ExpectedOffensivePPD"), matchup.get("team2ExpectedOffensivePPD")
        a1, a2 = r1.get("offensivePPD"), r2.get("offensivePPD")
        row = dict(matchup)
        row.update({
            "team1ActualOffensivePPD": a1,
            "team2ActualOffensivePPD": a2,
            "team1OffensivePPDAboveExpectation": float(a1) - float(e1) if _num(a1) and _num(e1) else None,
            "team2OffensivePPDAboveExpectation": float(a2) - float(e2) if _num(a2) and _num(e2) else None,
            "team1DefensivePPDAboveExpectation": float(e2) - float(a2) if _num(a2) and _num(e2) else None,
            "team2DefensivePPDAboveExpectation": float(e1) - float(a1) if _num(a1) and _num(e1) else None,
            "postgameTargetDiagnostic": True,
        })
        out.append(row)
    return out


def load_drive_corpus(raw_root: Path, processed_root: Path, seasons: list[int] | tuple[int, ...]) -> list[dict[str, Any]]:
    drives: list[dict[str, Any]] = []
    for season in seasons:
        for season_type, week in discover_partitions(raw_root, season):
            path = derived_drive_partition_dir(processed_root, season, season_type, week) / "drives.json"
            if not path.exists():
                raise FileNotFoundError(f"Derived drives missing: {path}")
            drives.extend(json.loads(path.read_text()))
    return drives


def materialize_season(
    raw_root: Path,
    processed_root: Path,
    season: int,
    shrinkage_possessions: float = DEFAULT_SHRINKAGE_POSSESSIONS,
) -> dict[str, Any]:
    drives = load_drive_corpus(raw_root, processed_root, [season])
    team_games = build_team_game_drive_rows(drives)
    snapshots = build_pregame_ppd_snapshots(team_games, season, shrinkage_possessions=shrinkage_possessions)
    matchups = build_matchup_ppd(snapshots, season)
    postgame = attach_postgame_residuals(matchups, team_games)

    root = processed_root / "derived" / "drive_ppd" / f"season={season}"
    root.mkdir(parents=True, exist_ok=True)
    (root / "team_games.json").write_text(json.dumps(team_games, ensure_ascii=False, separators=(",", ":")))
    (root / "pregame.json").write_text(json.dumps(snapshots, ensure_ascii=False, separators=(",", ":")))
    (root / "matchups.json").write_text(json.dumps(matchups, ensure_ascii=False, separators=(",", ":")))
    (root / "postgame_diagnostics.json").write_text(json.dumps(postgame, ensure_ascii=False, separators=(",", ":")))

    resolved = sum(int(r.get("resolvedPointPossessions") or 0) for r in team_games)
    unresolved = sum(int(r.get("unresolvedPointPossessions") or 0) for r in team_games)
    points = sum(float(r.get("offensiveDrivePoints") or 0.0) for r in team_games)
    checks = {
        "one_snapshot_per_team_game": len(snapshots) == len(team_games),
        "matchups_have_two_distinct_teams": all(r.get("team1") != r.get("team2") for r in matchups),
        "no_postgame_targets_in_matchups": all("Actual" not in k and "AboveExpectation" not in k for r in matchups for k in r),
        "resolved_possessions_positive": resolved > 0,
        "points_nonnegative": points >= 0,
    }
    manifest = {
        "season": season,
        "version": DRIVE_PPD_VERSION,
        "shrinkagePossessions": shrinkage_possessions,
        "teamGameRows": len(team_games),
        "snapshotRows": len(snapshots),
        "matchupRows": len(matchups),
        "postgameRows": len(postgame),
        "resolvedPointPossessions": resolved,
        "unresolvedPointPossessions": unresolved,
        "offensiveDrivePoints": points,
        "pointsPerResolvedPossession": points / resolved if resolved else None,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "REVIEW",
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS

    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--shrinkage-possessions", type=float, default=DEFAULT_SHRINKAGE_POSSESSIONS)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    seasons = list(DEFAULT_SEASONS) if args.all else ([args.season] if args.season else [])
    if not seasons:
        parser.error("choose --season YYYY or --all")
    for season in seasons:
        result = materialize_season(args.raw_root, args.processed_root, int(season), args.shrinkage_possessions)
        print(
            f"DRIVE PPD {season}: {result['status']} | rows={result['teamGameRows']:,} | "
            f"resolved poss={result['resolvedPointPossessions']:,} | PPD={result['pointsPerResolvedPossession']:.3f}"
        )


if __name__ == "__main__":
    main()
