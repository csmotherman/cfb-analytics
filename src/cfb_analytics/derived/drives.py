"""Derive drive-level records from canonical play-by-play.

Canonical plays are the analytical source of truth. Drive IDs already present on
plays define grouping. Ownership uses a conservative hierarchy:
1) clean offensive scrimmage plays;
2) other offensive plays in the drive;
3) neighboring resolved drives in the same game when they agree on the two-team
   alternation implied by possession sequence.
Unresolved or conflicting ownership remains explicitly flagged.
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

DRIVE_SCHEMA_VERSION = "drive-v3"


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
    best = counts.most_common(1)[0][1]
    winners = {value for value, count in counts.items() if count == best}
    return next(value for value in clean if value in winners)


def _num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _ownership_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        r for r in rows
        if r.get("isOffensivePlay") is True
        and r.get("isScrimmagePlay") is True
        and not r.get("hasNoPlayContext", False)
    ]


def _fallback_offensive_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        r for r in rows
        if r.get("isOffensivePlay") is True
        and not r.get("hasNoPlayContext", False)
        and r.get("offense") is not None
        and r.get("defense") is not None
    ]


def derive_drive(game_id: str, drive_id: str, rows: list[dict[str, Any]], season: int, season_type: str, week: int) -> dict[str, Any]:
    ordered = sorted(rows, key=_candidate_sort_key)
    first, last = ordered[0], ordered[-1]
    drive_numbers = [r.get("driveNumber") for r in ordered if r.get("driveNumber") is not None]
    drive_number_set = set(drive_numbers)

    ownership = _ownership_rows(ordered)
    fallback = _fallback_offensive_rows(ordered)
    primary_offenses = [r.get("offense") for r in ownership if r.get("offense") is not None]
    primary_defenses = [r.get("defense") for r in ownership if r.get("defense") is not None]
    fallback_offenses = [r.get("offense") for r in fallback if r.get("offense") is not None]
    fallback_defenses = [r.get("defense") for r in fallback if r.get("defense") is not None]

    offense = _mode(primary_offenses) if primary_offenses else _mode(fallback_offenses)
    defense = _mode(primary_defenses) if primary_defenses else _mode(fallback_defenses)
    source = "clean_offensive_scrimmage_plays" if primary_offenses and primary_defenses else (
        "other_offensive_plays" if fallback_offenses and fallback_defenses else "unresolved"
    )

    offensive = [r for r in ordered if r.get("isOffensivePlay") is True and not r.get("hasNoPlayContext", False)]
    scrimmage = [r for r in ordered if r.get("isScrimmagePlay") is True and not r.get("hasNoPlayContext", False)]
    corrected = [r for r in ordered if r.get("analyticsYardsWasCorrected")]
    yards = [r.get("analyticsYardsGained") for r in offensive if _num(r.get("analyticsYardsGained"))]

    issues = []
    if primary_offenses and len(set(primary_offenses)) > 1: issues.append("MULTIPLE_OWNERSHIP_OFFENSES")
    if primary_defenses and len(set(primary_defenses)) > 1: issues.append("MULTIPLE_OWNERSHIP_DEFENSES")
    if not primary_offenses and fallback_offenses and len(set(fallback_offenses)) > 1: issues.append("MULTIPLE_FALLBACK_OFFENSES")
    if not primary_defenses and fallback_defenses and len(set(fallback_defenses)) > 1: issues.append("MULTIPLE_FALLBACK_DEFENSES")
    if len(drive_number_set) > 1: issues.append("MULTIPLE_DRIVE_NUMBERS")
    if offense is None: issues.append("MISSING_OWNERSHIP_OFFENSE")
    if defense is None: issues.append("MISSING_OWNERSHIP_DEFENSE")

    return {
        "season": season,
        "seasonType": season_type,
        "week": week,
        "gameId": game_id,
        "driveId": drive_id,
        "driveNumber": _mode(drive_numbers),
        "offense": offense,
        "defense": defense,
        "ownershipEvidencePlayCount": len(ownership),
        "fallbackOwnershipEvidencePlayCount": len(fallback),
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
        "driveOwnershipSource": source,
        "driveValidationStatus": "PASS" if not issues else "REVIEW",
        "driveValidationIssues": issues,
    }


def _resolve_neighbor_ownership(drives: list[dict[str, Any]]) -> None:
    by_game: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for d in drives:
        by_game[str(d["gameId"])].append(d)
    for game_drives in by_game.values():
        game_drives.sort(key=lambda x: (x["driveNumber"] if isinstance(x.get("driveNumber"),(int,float)) else 10**9, x["driveId"]))
        teams = {d.get("offense") for d in game_drives if d.get("offense") is not None} | {d.get("defense") for d in game_drives if d.get("defense") is not None}
        teams.discard(None)
        if len(teams) != 2:
            continue
        team_a, team_b = sorted(teams)
        for i,d in enumerate(game_drives):
            if d.get("offense") is not None and d.get("defense") is not None:
                continue
            candidates = []
            prev = game_drives[i-1] if i>0 else None
            nxt = game_drives[i+1] if i+1<len(game_drives) else None
            if prev and prev.get("offense") in teams:
                candidates.append(team_b if prev["offense"]==team_a else team_a)
            if nxt and nxt.get("offense") in teams:
                candidates.append(team_b if nxt["offense"]==team_a else team_a)
            if candidates and len(set(candidates))==1:
                offense=candidates[0]; defense=team_b if offense==team_a else team_a
                d["offense"]=offense; d["defense"]=defense; d["driveOwnershipSource"]="neighbor_drive_inference"
                d["driveValidationIssues"]=[x for x in d["driveValidationIssues"] if x not in {"MISSING_OWNERSHIP_OFFENSE","MISSING_OWNERSHIP_DEFENSE"}]
                d["driveValidationStatus"]="PASS" if not d["driveValidationIssues"] else "REVIEW"


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
    _resolve_neighbor_ownership(drives)
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
    totals=Counter(); issues=Counter(); duplicate_keys=0; seen=set(); partitions=0; games=set(); sources=Counter()
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
                seen.add(key); games.add(str(d.get("gameId"))); sources[d.get("driveOwnershipSource")]+=1
                for issue in d.get("driveValidationIssues",[]): issues[issue]+=1
    expected_assigned=totals["plays"]-totals["missing_drive_id_plays"]
    checks={
        "all_drives_unique": duplicate_keys==0,
        "play_membership_reconciles": totals["assigned_plays"]==expected_assigned,
        "no_multiple_ownership_offense_drives": issues["MULTIPLE_OWNERSHIP_OFFENSES"]==0,
        "no_multiple_ownership_defense_drives": issues["MULTIPLE_OWNERSHIP_DEFENSES"]==0,
        "no_multiple_drive_number_drives": issues["MULTIPLE_DRIVE_NUMBERS"]==0,
    }
    return {"status":"PASS" if all(checks.values()) else "REVIEW","partitions":partitions,"games_with_drives":len(games),"totals":dict(totals),"issues":dict(issues),"ownership_sources":dict(sources),"duplicate_drive_keys":duplicate_keys,"checks":checks}


def concise_drive_audit(r: dict[str, Any]) -> str:
    t=r["totals"]
    lines=[f"DERIVED DRIVE CORPUS AUDIT: {r['status']}",f"Partitions: {r['partitions']}",f"Games with drives: {r['games_with_drives']:,}",f"Derived drives: {t.get('drives',0):,}",f"Canonical plays: {t.get('plays',0):,}",f"Assigned to drives: {t.get('assigned_plays',0):,}",f"Missing driveId plays: {t.get('missing_drive_id_plays',0):,}","","Ownership sources:"]
    for k,v in sorted(r.get("ownership_sources",{}).items(),key=lambda x:-x[1]): lines.append(f"  {str(k):.<34} {v:>7,}")
    lines.append(""); lines.append("Checks:")
    for k,v in r["checks"].items(): lines.append(f"  {'PASS' if v else 'FAIL'} {k}")
    lines.append(""); lines.append("Drive validation issues:")
    if r["issues"]:
        for k,v in sorted(r["issues"].items(),key=lambda x:-x[1]): lines.append(f"  {k:.<34} {v:>7,}")
    else: lines.append("  None")
    return "\n".join(lines)
