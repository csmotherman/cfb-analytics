"""Diagnostic audits for raw CFBD play chronology.

Raw files are never modified. The candidate chronology is evaluated as
(gameId, driveNumber, playNumber); promotion to canonical requires evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from cfb_analytics.raw.audit import discover_partitions, partition_dir


def _load(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _clock_seconds(play: dict[str, Any]) -> int | None:
    clock=play.get("clock")
    if not isinstance(clock,dict): return None
    m,s=clock.get("minutes"),clock.get("seconds")
    if not isinstance(m,(int,float)) or not isinstance(s,(int,float)): return None
    return int(m)*60+int(s)


def _wallclock_key(value: Any) -> float | None:
    if not isinstance(value,str) or not value: return None
    try: return datetime.fromisoformat(value.replace("Z","+00:00")).timestamp()
    except ValueError: return None


def _play_id_numeric(play: dict[str, Any]) -> int | None:
    try: return int(str(play.get("id")))
    except (TypeError,ValueError): return None


def _pairwise_disagreements(plays: list[dict[str, Any]]) -> Counter[str]:
    c=Counter()
    for a,b in zip(plays,plays[1:]):
        c["adjacent_pairs"]+=1
        if isinstance(a.get("driveNumber"),(int,float)) and isinstance(b.get("driveNumber"),(int,float)) and b["driveNumber"]<a["driveNumber"]: c["source_drive_number_regression"]+=1
        if a.get("driveId")==b.get("driveId") and isinstance(a.get("playNumber"),(int,float)) and isinstance(b.get("playNumber"),(int,float)):
            if b["playNumber"]<a["playNumber"]: c["source_play_number_regression_same_drive"]+=1
            elif b["playNumber"]==a["playNumber"]: c["duplicate_adjacent_play_number_same_drive"]+=1
        pa,pb=a.get("period"),b.get("period")
        if isinstance(pa,(int,float)) and isinstance(pb,(int,float)):
            if pb<pa: c["source_period_regression"]+=1
            elif pb==pa:
                ca,cb=_clock_seconds(a),_clock_seconds(b)
                if ca is not None and cb is not None and cb>ca: c["source_clock_regression_same_period"]+=1
        wa,wb=_wallclock_key(a.get("wallclock")),_wallclock_key(b.get("wallclock"))
        if wa is not None and wb is not None and wb<wa: c["source_wallclock_regression"]+=1
        ia,ib=_play_id_numeric(a),_play_id_numeric(b)
        if ia is not None and ib is not None and ib<ia: c["source_play_id_regression"]+=1
    return c


def _game_summary(plays: list[dict[str, Any]]) -> dict[str, Any]:
    source=_pairwise_disagreements(plays); nums:dict[str,list[int]]=defaultdict(list); clocks=Counter(); wall_missing=id_missing=0
    for p in plays:
        if p.get("driveId") is not None and isinstance(p.get("playNumber"),(int,float)): nums[str(p["driveId"])].append(int(p["playNumber"]))
        key=(p.get("period"),_clock_seconds(p))
        if key[1] is not None: clocks[key]+=1
        wall_missing += _wallclock_key(p.get("wallclock")) is None
        id_missing += _play_id_numeric(p) is None
    dup=noncontig=0
    for values in nums.values():
        dup += len(values)-len(set(values)); uniq=sorted(set(values))
        if uniq and uniq != list(range(min(uniq),max(uniq)+1)): noncontig+=1
    return {"plays":len(plays),"drives_seen":len(nums),"duplicate_play_numbers_within_drive":dup,"drives_with_noncontiguous_play_numbers":noncontig,"same_period_clock_ties":sum(n for n in clocks.values() if n>1),"wallclock_missing":wall_missing,"play_id_missing":id_missing,**source}


def sequence_audit(root: Path, seasons: Iterable[int], examples: int=10) -> dict[str,Any]:
    totals=Counter(); by_season={}; problematic=[]; games_scanned=0; corpus_games=0; no_play_games=[]
    for season in seasons:
        sc=Counter()
        for st,wk in discover_partitions(root,season):
            d=partition_dir(root,season,st,wk); games={str(g["id"]):g for g in _load(d/"games.json")}; corpus_games+=len(games)
            grouped:dict[str,list[dict[str,Any]]]=defaultdict(list)
            for p in _load(d/"plays.json"): grouped[str(p.get("gameId"))].append(p)
            for gid,g in games.items():
                if gid not in grouped: no_play_games.append({"season":season,"season_type":st,"week":wk,"gameId":gid,"game":f"{g.get('awayTeam')} @ {g.get('homeTeam')}"})
            for gid,plays in grouped.items():
                games_scanned+=1; s=_game_summary(plays)
                for k,v in s.items():
                    if isinstance(v,int): totals[k]+=v; sc[k]+=v
                keys=("source_drive_number_regression","source_play_number_regression_same_drive","source_period_regression","source_clock_regression_same_period","source_wallclock_regression","source_play_id_regression","duplicate_play_numbers_within_drive")
                if any(s.get(k,0) for k in keys) and len(problematic)<examples:
                    g=games.get(gid,{}); problematic.append({"season":season,"season_type":st,"week":wk,"gameId":gid,"game":f"{g.get('awayTeam')} @ {g.get('homeTeam')}","summary":s,"first_source_records":[{k:p.get(k) for k in ("id","driveId","driveNumber","playNumber","period","clock","wallclock","playType","playText")} for p in plays[:12]]})
        by_season[str(season)]=sc
    return {"corpus_games":corpus_games,"games_scanned":games_scanned,"games_without_plays":len(no_play_games),"games_without_plays_examples":no_play_games[:examples],"totals":dict(totals),"by_season":{s:dict(c) for s,c in by_season.items()},"examples":problematic}


def _candidate_sort_key(p: dict[str,Any]) -> tuple[int,int,int]:
    dn=p.get("driveNumber"); pn=p.get("playNumber")
    return (int(dn) if isinstance(dn,(int,float)) else 10**9, int(pn) if isinstance(pn,(int,float)) else 10**9, _play_id_numeric(p) or 10**30)


def _validate_candidate_game(plays:list[dict[str,Any]], drives:list[dict[str,Any]]) -> Counter[str]:
    c=Counter(); ordered=sorted(plays,key=_candidate_sort_key)
    drive_ids_by_number:dict[int,set[str]]=defaultdict(set); numbers_by_drive:dict[str,set[int]]=defaultdict(set); drive_rows={str(d.get("id")):d for d in drives}
    for p in plays:
        dn=p.get("driveNumber"); did=p.get("driveId")
        if isinstance(dn,(int,float)) and did is not None:
            drive_ids_by_number[int(dn)].add(str(did)); numbers_by_drive[str(did)].add(int(dn))
    c["drive_numbers_with_multiple_drive_ids"] += sum(len(v)>1 for v in drive_ids_by_number.values())
    c["drive_ids_with_multiple_drive_numbers"] += sum(len(v)>1 for v in numbers_by_drive.values())
    dnums=sorted(drive_ids_by_number)
    if dnums and dnums != list(range(min(dnums),max(dnums)+1)): c["games_with_drive_number_gaps"]+=1
    for a,b in zip(ordered,ordered[1:]):
        pa,pb=a.get("period"),b.get("period")
        if isinstance(pa,(int,float)) and isinstance(pb,(int,float)):
            if pb<pa: c["candidate_period_regressions"]+=1
            elif pb==pa:
                ca,cb=_clock_seconds(a),_clock_seconds(b)
                if ca is not None and cb is not None and cb>ca: c["candidate_clock_increases_same_period"]+=1
    grouped:dict[str,list[dict[str,Any]]]=defaultdict(list)
    for p in ordered:
        if p.get("driveId") is not None: grouped[str(p["driveId"])].append(p)
    for did,dplays in grouped.items():
        offenses={p.get("offense") for p in dplays if p.get("offense") is not None}
        if len(offenses)>1: c["drives_with_multiple_play_offenses"]+=1
        row=drive_rows.get(did)
        if row:
            rp=[p.get("period") for p in dplays if isinstance(p.get("period"),(int,float))]
            if rp:
                sp,ep=row.get("startPeriod"),row.get("endPeriod")
                if isinstance(sp,(int,float)) and min(rp)<sp: c["drives_with_play_before_start_period"]+=1
                if isinstance(ep,(int,float)) and max(rp)>ep: c["drives_with_play_after_end_period"]+=1
    return c


def chronology_audit(root:Path,seasons:Iterable[int],examples:int=10)->dict[str,Any]:
    totals=Counter(); corpus_games=games_with_plays=0; missing=[]; conflicts=[]
    for season in seasons:
        for st,wk in discover_partitions(root,season):
            d=partition_dir(root,season,st,wk); games={str(g["id"]):g for g in _load(d/"games.json")}; corpus_games+=len(games)
            plays_by_game:dict[str,list[dict[str,Any]]]=defaultdict(list); drives_by_game:dict[str,list[dict[str,Any]]]=defaultdict(list)
            for p in _load(d/"plays.json"): plays_by_game[str(p.get("gameId"))].append(p)
            for dr in _load(d/"drives.json"): drives_by_game[str(dr.get("gameId"))].append(dr)
            for gid,g in games.items():
                plays=plays_by_game.get(gid,[])
                if not plays:
                    if len(missing)<examples: missing.append({"season":season,"season_type":st,"week":wk,"gameId":gid,"game":f"{g.get('awayTeam')} @ {g.get('homeTeam')}"})
                    continue
                games_with_plays+=1; c=_validate_candidate_game(plays,drives_by_game.get(gid,[])); totals.update(c)
                if sum(c.values()) and len(conflicts)<examples: conflicts.append({"season":season,"season_type":st,"week":wk,"gameId":gid,"game":f"{g.get('awayTeam')} @ {g.get('homeTeam')}","conflicts":dict(c)})
    return {"candidate_key":["gameId","driveNumber","playNumber"],"corpus_games":corpus_games,"games_with_plays":games_with_plays,"games_without_plays":corpus_games-games_with_plays,"totals":dict(totals),"games_without_plays_examples":missing,"conflict_examples":conflicts,"interpretation":"Candidate chronology is diagnostic only; raw data is unchanged."}


def concise_sequence(r:dict[str,Any])->str:
    t=r["totals"]
    return "\n".join(["RAW PLAY SEQUENCE AUDIT",f"Corpus games: {r['corpus_games']:,}",f"Games with plays: {r['games_scanned']:,}",f"Games without plays: {r['games_without_plays']:,}","","Source-order disagreements:",f"  drive-number regressions .............. {t.get('source_drive_number_regression',0):,}",f"  play-number regressions (same drive) .. {t.get('source_play_number_regression_same_drive',0):,}",f"  period regressions ..................... {t.get('source_period_regression',0):,}",f"  clock regressions (same period) ........ {t.get('source_clock_regression_same_period',0):,}",f"  wallclock regressions .................. {t.get('source_wallclock_regression',0):,}",f"  play-id regressions .................... {t.get('source_play_id_regression',0):,}","","Ordering ambiguity:",f"  duplicate play numbers within drives .. {t.get('duplicate_play_numbers_within_drive',0):,}",f"  drives with noncontiguous play numbers . {t.get('drives_with_noncontiguous_play_numbers',0):,}","","No ordering signal is promoted to canonical by this audit."])


def concise_chronology(r:dict[str,Any])->str:
    t=r["totals"]
    return "\n".join(["CANDIDATE CHRONOLOGY VALIDATION","Candidate: gameId -> driveNumber -> playNumber",f"Corpus games: {r['corpus_games']:,}",f"Games with plays: {r['games_with_plays']:,}",f"Games without plays: {r['games_without_plays']:,}","","After candidate sorting:",f"  period regressions ..................... {t.get('candidate_period_regressions',0):,}",f"  clock increases within period .......... {t.get('candidate_clock_increases_same_period',0):,}",f"  drive numbers mapped to >1 drive ID .... {t.get('drive_numbers_with_multiple_drive_ids',0):,}",f"  drive IDs mapped to >1 drive number .... {t.get('drive_ids_with_multiple_drive_numbers',0):,}",f"  games with drive-number gaps ........... {t.get('games_with_drive_number_gaps',0):,}",f"  drives with multiple play offenses ..... {t.get('drives_with_multiple_play_offenses',0):,}",f"  play before drive start period .......... {t.get('drives_with_play_before_start_period',0):,}",f"  play after drive end period ............. {t.get('drives_with_play_after_end_period',0):,}","","Candidate chronology remains diagnostic until exceptions are understood."])
