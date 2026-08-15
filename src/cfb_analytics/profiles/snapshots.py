"""Build in-season team identity snapshots from derived team-game rows.

Archetype discovery must see how teams evolve, not only final-season averages.
For every team appearance after ``min_games`` this module builds two views:

* baseline: season-to-date through the current game;
* current: rolling recent-game window (default four games).

Percentiles are computed against teams observed in the same season/partition so
early-season states are never compared directly with final-season states.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from cfb_analytics.derived.games import derived_game_partition_dir
from cfb_analytics.raw.audit import discover_partitions
from .grades import grade_percentile, percentile_rank

SNAPSHOT_VERSION = "team-identity-snapshots-v1-research"
DEFAULT_SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)


def _rate(n: float, d: float) -> float | None:
    return n / d if d else None


def _sum(rows: list[dict[str, Any]], key: str) -> float:
    return sum(float(r.get(key) or 0.0) for r in rows)


def _profile_metrics(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    """Aggregate only dimensions with explicit, reconstructable denominators."""
    rush_e, rush_s = _sum(rows, "rushSuccessEligiblePlays"), _sum(rows, "rushSuccessfulPlays")
    pass_e, pass_s = _sum(rows, "passSuccessEligiblePlays"), _sum(rows, "passSuccessfulPlays")
    succ_e, succ_s = _sum(rows, "successEligiblePlays"), _sum(rows, "successfulPlays")
    exp_e, exp_n = _sum(rows, "explosiveEligiblePlays"), _sum(rows, "explosivePlays")
    rush_e_a, rush_s_a = _sum(rows, "rushSuccessEligiblePlaysAllowed"), _sum(rows, "rushSuccessfulPlaysAllowed")
    pass_e_a, pass_s_a = _sum(rows, "passSuccessEligiblePlaysAllowed"), _sum(rows, "passSuccessfulPlaysAllowed")
    exp_e_a, exp_n_a = _sum(rows, "explosiveEligiblePlaysAllowed"), _sum(rows, "explosivePlaysAllowed")
    third_e, third_s = _sum(rows, "down3SuccessEligiblePlays"), _sum(rows, "down3SuccessfulPlays")
    third_e_a, third_s_a = _sum(rows, "down3SuccessEligiblePlaysAllowed"), _sum(rows, "down3SuccessfulPlaysAllowed")
    opp_r, opp_p = _sum(rows, "resolvedPointOpportunities"), _sum(rows, "opportunityPoints")
    opp_r_a, opp_p_a = _sum(rows, "resolvedPointOpportunitiesAllowed"), _sum(rows, "opportunityPointsAllowed")
    poss, plays = _sum(rows, "validatedPossessions"), _sum(rows, "offensivePlays")
    style_denom = rush_e + pass_e
    return {
        "run_efficiency_off": _rate(rush_s, rush_e),
        "pass_efficiency_off": _rate(pass_s, pass_e),
        "success_off": _rate(succ_s, succ_e),
        "explosiveness_off": _rate(exp_n, exp_e),
        "finishing_off": _rate(opp_p, opp_r),
        "third_down_off": _rate(third_s, third_e),
        "run_efficiency_def": (1.0 - _rate(rush_s_a, rush_e_a)) if rush_e_a else None,
        "pass_efficiency_def": (1.0 - _rate(pass_s_a, pass_e_a)) if pass_e_a else None,
        "explosive_prevention": (1.0 - _rate(exp_n_a, exp_e_a)) if exp_e_a else None,
        "finishing_def": (-_rate(opp_p_a, opp_r_a)) if opp_r_a else None,
        "third_down_def": (1.0 - _rate(third_s_a, third_e_a)) if third_e_a else None,
        "rush_rate": _rate(rush_e, style_denom),
        "pass_rate": _rate(pass_e, style_denom),
        "plays_per_possession": _rate(plays, poss),
    }


DISCOVERY_DIRECTIONS = {key: True for key in _profile_metrics([])}


def build_identity_snapshots(
    team_games: list[dict[str, Any]], *, min_games: int = 4, recent_games: int = 4
) -> list[dict[str, Any]]:
    if min_games < 1 or recent_games < 1:
        raise ValueError("min_games and recent_games must be positive")
    by_team: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in team_games:
        if row.get("gameValidationStatus") not in (None, "PASS"):
            continue
        by_team[(int(row["season"]), str(row["team"]))].append(row)

    out: list[dict[str, Any]] = []
    order = {"regular": 0, "postseason": 1}
    for (season, team), games in sorted(by_team.items()):
        games.sort(key=lambda r: (order.get(str(r.get("seasonType", "regular")).lower(), 9), int(r.get("week") or 0), str(r.get("gameId"))))
        for i in range(min_games - 1, len(games)):
            through = games[: i + 1]
            recent = through[-recent_games:]
            current_game = games[i]
            baseline = _profile_metrics(through)
            current = _profile_metrics(recent)
            row: dict[str, Any] = {
                "season": season,
                "team": team,
                "seasonType": current_game.get("seasonType"),
                "week": current_game.get("week"),
                "throughGameId": current_game.get("gameId"),
                "gamesPlayed": len(through),
                "recentGames": len(recent),
                "snapshotVersion": SNAPSHOT_VERSION,
            }
            for key in DISCOVERY_DIRECTIONS:
                row[f"baseline_{key}"] = baseline.get(key)
                row[f"current_{key}"] = current.get(key)
            out.append(row)
    return out


def add_context_percentiles(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize current/baseline states within season + partition."""
    groups: dict[tuple[int, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(int(row["season"]), str(row.get("seasonType") or "regular"), int(row.get("week") or 0))].append(row)
    out: list[dict[str, Any]] = []
    for group in groups.values():
        for row in group:
            enriched = dict(row)
            for key, higher in DISCOVERY_DIRECTIONS.items():
                for prefix in ("baseline", "current"):
                    field = f"{prefix}_{key}"
                    pop = [x.get(field) for x in group if isinstance(x.get(field), (int, float))]
                    pct = percentile_rank(row.get(field), pop, higher_is_better=higher)
                    enriched[f"{field}_percentile"] = pct
                    enriched[f"{field}_grade"] = grade_percentile(pct)
                a = enriched.get(f"current_{key}_percentile")
                b = enriched.get(f"baseline_{key}_percentile")
                enriched[f"trend_{key}"] = (a - b) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None
            out.append(enriched)
    return out


def load_team_games(processed_root: Path, seasons: tuple[int, ...] = DEFAULT_SEASONS) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw_root = processed_root.parent / "raw"
    for season in seasons:
        for season_type, week in discover_partitions(raw_root, season):
            path = derived_game_partition_dir(processed_root, season, season_type, week) / "team_games.json"
            if path.exists():
                rows.extend(json.loads(path.read_text()))
    return rows


def materialize_identity_snapshots(processed_root: Path, *, min_games: int = 4, recent_games: int = 4) -> Path:
    rows = add_context_percentiles(build_identity_snapshots(load_team_games(processed_root), min_games=min_games, recent_games=recent_games))
    target = processed_root / "derived" / "profiles" / "identity_snapshots_v1.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(rows, separators=(",", ":")))
    print(f"IDENTITY SNAPSHOTS: {len(rows):,} states | seasons={len({r['season'] for r in rows})} | teams={len({(r['season'],r['team']) for r in rows})}")
    return target


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    p.add_argument("--min-games", type=int, default=4)
    p.add_argument("--recent-games", type=int, default=4)
    args = p.parse_args()
    materialize_identity_snapshots(args.processed_root, min_games=args.min_games, recent_games=args.recent_games)


if __name__ == "__main__":
    main()
