"""Derive drive-level records from canonical play-by-play.

Canonical plays are the analytical source of truth. Raw drive data is not used
to construct derived drives. Drive IDs already present on plays define grouping;
inconsistencies are surfaced in validation fields rather than silently repaired.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from cfb_analytics.canonical.materialize import canonical_partition_dir
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.raw.sequence import _candidate_sort_key

DRIVE_SCHEMA_VERSION = "drive-v1"


def derived_drive_partition_dir(root: Path, season: int, season_type: str, week: int) -> Path:
    return root / "derived" / "drives" / f"season={season}" / f"season_type={season_type}" / f"week={week:02d}"


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _mode(values: list[Any]) -> Any:
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    counts = Counter(clean)
    top = counts.most_common()
    best = top[0][1]
    winners = {value for value, count in top if count == best}
    for value in clean:
        if value in winners:
            return value
    return clean[0]


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def derive_drive(game_id: str, drive_id: str, rows: list[dict[str, Any]], season: int, season_type: str, week: int) -> dict[str, Any]:
    ordered = sorted(rows, key=_candidate_sort_key)
    first, last = ordered[0], ordered[-1]
    offenses = [r.get("offense") for r in ordered if r.get("offense") is not None]
    defenses = [r.get("defense") for r in ordered if r.get("defense") is not None]
    drive_numbers = [r.get("driveNumber") for r in ordered if r.get("driveNumber") is not None]
    offense_set, defense_set = set(offenses), set(defenses)
    drive_number_set = set(drive_numbers)

    offensive = [r for r in ordered if r.get("isOffensivePlay") is True and not r.get("hasNoPlayContext", False)]
    scrimmage = [r for r in ordered if r.get("isScrimmagePlay") is True and not r.get("hasNoPlayContext", False)]
    corrected = [r for r in ordered if r.get("analyticsYardsWasCorrected")]
    yards = [r.get("analyticsYardsGained") for r in offensive if _num(r.get("analyticsYardsGained"))]

    issues = []
    if len(offense_set) > 1: issues.append("MULTIPLE_OFFENSES")
    if len(defense_set) > 1: issues.append("MULTIPLE_DEFENSES")
    if len(drive_number_set) > 1: issues.append("MULTIPLE_DRIVE_NUMBERS")
    if not offenses: issues.append("MISSING_OFFENSE")
    if not defenses: issues.append("MISSING_DEFENSE")

    return {
        "season": season,
        "seasonType": season_type,
        "week": week,
        "gameId": game_id,
        "driveId": drive_id,
        "driveNumber": _mode(drive_numbers),
        "offense": _mode(offenses),
        "defense": _mode(defenses),
        "playCount": len(ordered),
        "offensivePlayCount": len(offensive),
        "scrimmagePlayCount": len(scrimmage),
        "analyticsYardsGained": sum(yards),
        "correctedPlayCount": len(corrected),
        "startPeriod": first.get("period"),
        "startClock": first.get("clock"),
        "startDown": first.get("down"),
        "startDistance": first.get("distance"),
        "startYardsToGoal": first.get("yardsToGoal"),
        "endPeriod": last.get("period"),
        "endClock": last.get("clock"),
        "endDown": last.get("down"),
        "endDistance": last.get("distance"),
        "endYardsToGoal": last.get("yardsToGoal"),
        "startOffenseScore": first.get("offenseScore"),
        "startDefenseScore": first.get("defenseScore"),
        "endOffenseScoreObserved": last.get("offenseScore"),
        "endDefenseScoreObserved": last.get("defenseScore"),
        "firstPlayId": first.get("id"),
        "lastPlayId": last.get("id"),
        "driveSchemaVersion": DRIVE_SCHEMA_VERSION,
        "driveValidationStatus": "PASS" if not issues else "REVIEW",
        "driveValidationIssues": issues,
    }


def derive_partition_drives(canonical_rows: list[dict[str, Any]], season: int, season_type: str, week: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    missing_drive_id = 0
    for row in canonical_rows:
        game_id = row.get("gameId")
        drive_id = row.get("driveId")
        if game_id is None or drive_id is None:
            missing_drive_id += 1
            continue
        groups[(str(game_id), str(drive_id))].append(row)
    drives = [derive_drive(g, d, rows, season, season_type, week) for (g, d), rows in groups.items()]
    drives.sort(key=lambda x: (x["gameId"], x["driveNumber"] if isinstance(x["driveNumber"], (int,float)) else 10**9, x["driveId"]))
    return drives, {"plays_without_drive_id": missing_drive_id, "plays_with_drive_id": len(canonical_rows)-missing_drive_id}


def materialize_drive_partition(processed_root: Path, season: int, season_type: str, week: int, refresh: bool=False) -> dict[str, Any]:
    source_path = canonical_partition_dir(processed_root, season, season_type, week) / "plays.json"
    if not source_path.exists(): raise FileNotFoundError(f"Canonical plays missing: {source_path}")
    target_dir = derived_drive_partition_dir(processed_root, season, season_type, week)
    target_path = target_dir / "drives.json"
    manifest_path = target_dir / "drives.manifest.json"
    source_bytes = source_path.read_bytes(); source_sha = _sha256(source_bytes)
    if not refresh and target_path.exists() and manifest_path.exists():
        manifest=json.loads(manifest_path.read_text())
        if manifest.get("canonical_plays_sha256")==source_sha and manifest.get("drive_schema_version")==DRIVE_SCHEMA_VERSION:
            return {**manifest,"status":"REUSED"}
    rows=json.loads(source_bytes)
    drives, coverage=derive_partition_drives(rows,season,season_type,week)
    payload=json.dumps(drives,ensure_ascii=False,separators=(",", ":")).encode()
    review=sum(d["driveValidationStatus"]!="PASS" for d in drives)
    manifest={
        "entity":"drives","layer":"derived","season":season,"season_type":season_type,"week":week,
        "drive_count":len(drives),"canonical_play_count":len(rows),**coverage,
        "review_drive_count":review,"canonical_plays_sha256":source_sha,"derived_drives_sha256":_sha256(payload),
        "drive_schema_version":DRIVE_SCHEMA_VERSION,"source":"canonical_play_by_play","format":"json"
    }
    _atomic_write(target_path,payload); _atomic_write(manifest_path,json.dumps(manifest,indent=2,sort_keys=True).encode())
    return {**manifest,"status":"WRITTEN"}


def materialize_drive_corpus(raw_root: Path, processed_root: Path, seasons: Iterable[int], refresh: bool=False) -> list[dict[str, Any]]:
    out=[]
    for season in seasons:
        for season_type,week in discover_partitions(raw_root,season):
            out.append(materialize_drive_partition(processed_root,season,season_type,week,refresh))
    return out


def drive_corpus_audit(raw_root: Path, processed_root: Path, seasons: Iterable[int]) -> dict[str, Any]:
    totals=Counter(); issues=Counter(); duplicate_keys=0; seen=set(); partitions=0; games=set()
    for season in seasons:
        for season_type,week in discover_partitions(raw_root,season):
            partitions+=1
            p=derived_drive_partition_dir(processed_root,season,season_type,week)/"drives.json"
            cp=canonical_partition_dir(processed_root,season,season_type,week)/"plays.json"
            if not p.exists(): raise FileNotFoundError(f"Derived drives missing: {p}")
            drives=json.loads(p.read_text()); plays=json.loads(cp.read_text())
            totals["drives"]+=len(drives); totals["plays"]+=len(plays)
            assigned=sum(d.get("playCount",0) for d in drives); totals["assigned_plays"]+=assigned
            totals["missing_drive_id_plays"]+=sum(r.get("driveId") is None for r in plays)
            for d in drives:
                key=(str(d.get("gameId")),str(d.get("driveId")))
                if key in seen: duplicate_keys+=1
                seen.add(key); games.add(str(d.get("gameId")))
                for issue in d.get("driveValidationIssues",[]): issues[issue]+=1
    expected_assigned=totals["plays"]-totals["missing_drive_id_plays"]
    checks={
        "all_drives_unique": duplicate_keys==0,
        "play_membership_reconciles": totals["assigned_plays"]==expected_assigned,
        "no_multiple_offense_drives": issues["MULTIPLE_OFFENSES"]==0,
        "no_multiple_defense_drives": issues["MULTIPLE_DEFENSES"]==0,
        "no_multiple_drive_number_drives": issues["MULTIPLE_DRIVE_NUMBERS"]==0,
    }
    return {"status":"PASS" if all(checks.values()) else "REVIEW","partitions":partitions,"games_with_drives":len(games),"totals":dict(totals),"issues":dict(issues),"duplicate_drive_keys":duplicate_keys,"checks":checks}


def concise_drive_audit(r: dict[str, Any]) -> str:
    t=r["totals"]
    lines=[f"DERIVED DRIVE CORPUS AUDIT: {r['status']}",f"Partitions: {r['partitions']}",f"Games with drives: {r['games_with_drives']:,}",f"Derived drives: {t.get('drives',0):,}",f"Canonical plays: {t.get('plays',0):,}",f"Assigned to drives: {t.get('assigned_plays',0):,}",f"Missing driveId plays: {t.get('missing_drive_id_plays',0):,}","","Checks:"]
    for k,v in r["checks"].items(): lines.append(f"  {'PASS' if v else 'FAIL'} {k}")
    lines.append(""); lines.append("Drive validation issues:")
    if r["issues"]:
        for k,v in sorted(r["issues"].items(),key=lambda x:-x[1]): lines.append(f"  {k:.<34} {v:>7,}")
    else: lines.append("  None")
    return "\n".join(lines)
