"""Leakage-safe pregame team snapshots from prior team-game rows only."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.derived.games import derived_game_partition_dir
from cfb_analytics.derived.seasons import derive_team_seasons

PREGAME_SNAPSHOT_VERSION = "pregame-snapshot-v1"


def _partition_key(row: dict[str, Any]) -> tuple[int, int]:
    st = str(row.get("seasonType") or "regular").lower()
    rank = 0 if st in {"regular", "regular_season"} else 1
    return rank, int(row.get("week") or 0)


def build_pregame_snapshots(team_games: list[dict[str, Any]], season: int) -> list[dict[str, Any]]:
    """Build one snapshot per team-game using only earlier partitions."""
    rows = [r for r in team_games if r.get("season") == season]
    by_partition: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_partition[_partition_key(row)].append(row)

    history: list[dict[str, Any]] = []
    out: list[dict[str, Any]] = []
    for key in sorted(by_partition):
        current = by_partition[key]
        aggregates = {r["team"]: r for r in derive_team_seasons(history, season)} if history else {}
        for game in current:
            agg = aggregates.get(game.get("team"))
            snap = {
                "season": season,
                "seasonType": game.get("seasonType"),
                "week": game.get("week"),
                "gameId": game.get("gameId"),
                "team": game.get("team"),
                "opponent": game.get("opponent"),
                "gamesPlayedBefore": int(agg.get("games", 0)) if agg else 0,
                "historyAvailable": agg is not None,
                "pregameSnapshotVersion": PREGAME_SNAPSHOT_VERSION,
            }
            if agg:
                for name, value in agg.items():
                    if name not in {"season", "team", "games"}:
                        snap[name] = value
            out.append(snap)
        history.extend(current)
    return out


def pregame_snapshot_audit(team_games: list[dict[str, Any]], snapshots: list[dict[str, Any]], season: int) -> dict[str, Any]:
    games = [r for r in team_games if r.get("season") == season]
    expected_keys = {(str(r.get("gameId")), r.get("team")) for r in games}
    actual_keys = {(str(r.get("gameId")), r.get("team")) for r in snapshots}

    prior_counts: dict[tuple[str, tuple[int, int]], int] = {}
    teams = {r.get("team") for r in games}
    for team in teams:
        prior = 0
        for key in sorted({_partition_key(r) for r in games}):
            prior_counts[(team, key)] = prior
            prior += sum(r.get("team") == team and _partition_key(r) == key for r in games)

    counts_ok = all(
        s.get("gamesPlayedBefore") == prior_counts.get((s.get("team"), _partition_key(s)), 0)
        for s in snapshots
    )
    version_ok = all(s.get("pregameSnapshotVersion") == PREGAME_SNAPSHOT_VERSION for s in snapshots)
    checks = {
        "one_snapshot_per_team_game": len(snapshots) == len(games),
        "snapshot_keys_match_team_games": actual_keys == expected_keys,
        "games_played_before_is_prior_only": counts_ok,
        "version_present": version_ok,
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "season": season,
        "team_game_rows": len(games),
        "snapshot_rows": len(snapshots),
        "zero_history_snapshots": sum(s.get("gamesPlayedBefore") == 0 for s in snapshots),
        "checks": checks,
    }


def concise_pregame_snapshot_audit(result: dict[str, Any]) -> str:
    lines = [
        f"PREGAME SNAPSHOT v1 AUDIT: {result['status']}",
        f"Season: {result['season']}",
        f"Team-game rows: {result['team_game_rows']:,}",
        f"Snapshot rows: {result['snapshot_rows']:,}",
        f"Zero-history snapshots: {result['zero_history_snapshots']:,}",
        "",
        "Checks:",
    ]
    lines += [f"{name}: {'PASS' if ok else 'FAIL'}" for name, ok in result["checks"].items()]
    return "\n".join(lines)


def load_team_games(raw_root: Path, processed_root: Path, season: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for season_type, week in discover_partitions(raw_root, season):
        path = derived_game_partition_dir(processed_root, season, season_type, week) / "team_games.json"
        rows.extend(json.loads(path.read_text()))
    return rows


def materialize_pregame_season(raw_root: Path, processed_root: Path, season: int) -> dict[str, Any]:
    games = load_team_games(raw_root, processed_root, season)
    snapshots = build_pregame_snapshots(games, season)
    target = processed_root / "derived" / "pregame" / f"season={season}"
    target.mkdir(parents=True, exist_ok=True)
    path = target / "team_pregame.json"
    path.write_text(json.dumps(snapshots, ensure_ascii=False, separators=(",", ":")))
    audit = pregame_snapshot_audit(games, snapshots, season)
    return {**audit, "path": str(path)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Materialize leakage-safe pregame snapshots")
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    result = materialize_pregame_season(args.raw_root, args.processed_root, args.season)
    print(concise_pregame_snapshot_audit(result))


if __name__ == "__main__":
    main()
