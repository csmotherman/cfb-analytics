"""Materialize fan-facing situational splits from validated canonical plays.

The output is intentionally granular by exact down, exact distance, and half so
the website can aggregate arbitrary distance sliders/buckets without replaying
play-by-play data. Rows are emitted for both offense and defense.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

from cfb_analytics.analytics.explosiveness import classify_explosive
from cfb_analytics.analytics.success import classify_success
from cfb_analytics.canonical.materialize import canonical_partition_dir
from cfb_analytics.derived.drives import derived_drive_partition_dir
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.raw.sequence import _candidate_sort_key

SITUATIONAL_SPLITS_VERSION = "situational-splits-v1-down-distance-half"
SEASONS = (2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025)


def _rate(n, d):
    return n / d if d else None


def _atomic(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    os.replace(tmp, path)


def _family(play):
    subtype = str(play.get("eventSubtype") or "").lower()
    if "rush" in subtype:
        return "rush"
    if "pass" in subtype or "sack" in subtype:
        return "pass"
    return None


def _half(play):
    period = play.get("period")
    if period in (1, 2):
        return 1
    if period in (3, 4):
        return 2
    return "OT"


def _touchdown(play):
    text = " ".join(
        str(play.get(k) or "")
        for k in ("sourcePlayType", "eventCategory", "eventSubtype", "playText")
    ).upper()
    return "TOUCHDOWN" in text


def _chronology_clean(play):
    # Match First-Down Generation v1 chronology semantics: the next clean snap
    # may carry other contextual modifiers, but explicit no-play rows do not
    # establish a real down reset.
    return (
        play.get("isScrimmagePlay") is True
        and play.get("isOffensivePlay") is True
        and not play.get("hasNoPlayContext", False)
    )


def _first_down_flags(plays, valid_drive_keys):
    """Return evidence-union first-down generation flags by in-memory play id."""
    by_drive = defaultdict(list)
    for play in plays:
        key = (str(play.get("gameId")), str(play.get("driveId")))
        if key in valid_drive_keys:
            by_drive[key].append(play)

    flags = {}
    for rows in by_drive.values():
        clean = [p for p in sorted(rows, key=_candidate_sort_key) if _chronology_clean(p)]
        for i, play in enumerate(clean):
            distance = play.get("distance")
            yards = play.get("analyticsYardsGained")
            structural = (
                isinstance(distance, (int, float))
                and not isinstance(distance, bool)
                and isinstance(yards, (int, float))
                and not isinstance(yards, bool)
                and distance > 0
                and yards >= distance
            )
            nxt = clean[i + 1] if i + 1 < len(clean) else None
            reset = nxt is not None and nxt.get("down") == 1
            flags[id(play)] = bool(structural or _touchdown(play) or reset)
    return flags


def build_situational_rows(plays, drives, season):
    valid_drive_keys = {
        (str(d.get("gameId")), str(d.get("driveId")))
        for d in drives
        if d.get("isPossessionDrive") is True
        and d.get("driveValidationStatus") == "PASS"
        and d.get("offense")
        and d.get("defense")
    }
    first_down = _first_down_flags(plays, valid_drive_keys)
    counts = defaultdict(lambda: defaultdict(float))

    for play in plays:
        drive_key = (str(play.get("gameId")), str(play.get("driveId")))
        if drive_key not in valid_drive_keys:
            continue
        success = classify_success(play)
        if success is None:
            continue
        down = play.get("down")
        distance = play.get("distance")
        if down not in (1, 2, 3, 4):
            continue
        if not isinstance(distance, (int, float)) or isinstance(distance, bool) or distance <= 0:
            continue

        family = _family(play)
        yards = play.get("analyticsYardsGained")
        yards = float(yards) if isinstance(yards, (int, float)) and not isinstance(yards, bool) else 0.0
        explosive = classify_explosive(play)
        fd = int(first_down.get(id(play), False))
        half = _half(play)

        for side, team in (("offense", play.get("offense")), ("defense", play.get("defense"))):
            if not team:
                continue
            key = (str(team), side, half, int(down), float(distance))
            c = counts[key]
            c["plays"] += 1
            c["successes"] += int(success)
            c["yards"] += yards
            c["firstDowns"] += fd
            if explosive is not None:
                c["explosiveEligiblePlays"] += 1
                c["explosivePlays"] += int(explosive)
            if family == "rush":
                c["rushPlays"] += 1
                c["rushSuccesses"] += int(success)
                c["rushYards"] += yards
            elif family == "pass":
                c["passPlays"] += 1
                c["passSuccesses"] += int(success)
                c["passYards"] += yards
            if down in (3, 4):
                c["conversionAttempts"] += 1
                c["conversions"] += fd

    out = []
    for (team, side, half, down, distance), c in sorted(
        counts.items(), key=lambda x: (x[0][0], x[0][1], str(x[0][2]), x[0][3], x[0][4])
    ):
        plays_n = int(c["plays"])
        rush_n = int(c["rushPlays"])
        pass_n = int(c["passPlays"])
        exp_n = int(c["explosiveEligiblePlays"])
        conv_att = int(c["conversionAttempts"])
        row = {
            "version": SITUATIONAL_SPLITS_VERSION,
            "season": season,
            "team": team,
            "side": side,
            "half": half,
            "down": down,
            "distance": int(distance) if distance.is_integer() else distance,
            "plays": plays_n,
            "successes": int(c["successes"]),
            "successRate": _rate(c["successes"], plays_n),
            "yards": c["yards"],
            "yardsPerPlay": _rate(c["yards"], plays_n),
            "firstDowns": int(c["firstDowns"]),
            "firstDownRate": _rate(c["firstDowns"], plays_n),
            "rushPlays": rush_n,
            "passPlays": pass_n,
            "rushRate": _rate(rush_n, rush_n + pass_n),
            "passRate": _rate(pass_n, rush_n + pass_n),
            "rushSuccesses": int(c["rushSuccesses"]),
            "passSuccesses": int(c["passSuccesses"]),
            "rushSuccessRate": _rate(c["rushSuccesses"], rush_n),
            "passSuccessRate": _rate(c["passSuccesses"], pass_n),
            "rushYards": c["rushYards"],
            "passYards": c["passYards"],
            "rushYardsPerPlay": _rate(c["rushYards"], rush_n),
            "passYardsPerPlay": _rate(c["passYards"], pass_n),
            "explosiveEligiblePlays": exp_n,
            "explosivePlays": int(c["explosivePlays"]),
            "explosivePlayRate": _rate(c["explosivePlays"], exp_n),
            "conversionAttempts": conv_att,
            "conversions": int(c["conversions"]),
            "conversionRate": _rate(c["conversions"], conv_att),
        }
        out.append(row)
    return out


def season_output_path(processed_root: Path, season: int) -> Path:
    return processed_root / "derived" / "situational_splits" / f"season={season}" / "situational_splits.json"


def materialize_season(raw_root: Path, processed_root: Path, season: int):
    rows = []
    for season_type, week in discover_partitions(raw_root, season):
        play_path = canonical_partition_dir(processed_root, season, season_type, week) / "plays.json"
        drive_path = derived_drive_partition_dir(processed_root, season, season_type, week) / "drives.json"
        if not play_path.exists() or not drive_path.exists():
            raise FileNotFoundError(f"Missing canonical plays or derived drives for {season} {season_type} week {week}")
        rows.extend(build_situational_rows(json.loads(play_path.read_text()), json.loads(drive_path.read_text()), season))

    merged = defaultdict(lambda: defaultdict(float))
    for row in rows:
        key = (row["team"], row["side"], row["half"], row["down"], float(row["distance"]))
        m = merged[key]
        for field in (
            "plays", "successes", "yards", "firstDowns", "rushPlays", "passPlays",
            "rushSuccesses", "passSuccesses", "rushYards", "passYards",
            "explosiveEligiblePlays", "explosivePlays", "conversionAttempts", "conversions",
        ):
            m[field] += row[field] or 0

    final = []
    for (team, side, half, down, distance), c in sorted(
        merged.items(), key=lambda x: (x[0][0], x[0][1], str(x[0][2]), x[0][3], x[0][4])
    ):
        plays_n = int(c["plays"])
        rush_n = int(c["rushPlays"])
        pass_n = int(c["passPlays"])
        exp_n = int(c["explosiveEligiblePlays"])
        conv_att = int(c["conversionAttempts"])
        final.append({
            "version": SITUATIONAL_SPLITS_VERSION,
            "season": season,
            "team": team,
            "side": side,
            "half": half,
            "down": down,
            "distance": int(distance) if distance.is_integer() else distance,
            "plays": plays_n,
            "successes": int(c["successes"]),
            "successRate": _rate(c["successes"], plays_n),
            "yards": c["yards"],
            "yardsPerPlay": _rate(c["yards"], plays_n),
            "firstDowns": int(c["firstDowns"]),
            "firstDownRate": _rate(c["firstDowns"], plays_n),
            "rushPlays": rush_n,
            "passPlays": pass_n,
            "rushRate": _rate(rush_n, rush_n + pass_n),
            "passRate": _rate(pass_n, rush_n + pass_n),
            "rushSuccesses": int(c["rushSuccesses"]),
            "passSuccesses": int(c["passSuccesses"]),
            "rushSuccessRate": _rate(c["rushSuccesses"], rush_n),
            "passSuccessRate": _rate(c["passSuccesses"], pass_n),
            "rushYards": c["rushYards"],
            "passYards": c["passYards"],
            "rushYardsPerPlay": _rate(c["rushYards"], rush_n),
            "passYardsPerPlay": _rate(c["passYards"], pass_n),
            "explosiveEligiblePlays": exp_n,
            "explosivePlays": int(c["explosivePlays"]),
            "explosivePlayRate": _rate(c["explosivePlays"], exp_n),
            "conversionAttempts": conv_att,
            "conversions": int(c["conversions"]),
            "conversionRate": _rate(c["conversions"], conv_att),
        })

    path = season_output_path(processed_root, season)
    _atomic(path, final)
    return path, final


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    seasons = SEASONS if args.all else ((args.season,) if args.season else ())
    if not seasons:
        parser.error("pass --season YYYY or --all")
    for season in seasons:
        path, rows = materialize_season(args.root, args.processed_root, season)
        print(f"SITUATIONAL SPLITS: {season} | {len(rows):,} rows | {path}")


if __name__ == "__main__":
    main()
