"""Derive one analytics row per team per game from validated possession drives."""
from __future__ import annotations
import hashlib, json, os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.canonical.materialize import canonical_partition_dir
from cfb_analytics.derived.drives import derived_drive_partition_dir
from cfb_analytics.analytics.success import classify_success, SUCCESS_VERSION

GAME_SCHEMA_VERSION="team-game-v2-success"

def derived_game_partition_dir(root:Path,season:int,season_type:str,week:int)->Path:
 return root/"derived"/"games"/f"season={season}"/f"season_type={season_type}"/f"week={week:02d}"
def _atomic(path:Path,data:bytes):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_bytes(data); os.replace(tmp,path)
def _sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def _num(v:Any)->bool:return isinstance(v,(int,float)) and not isinstance(v,bool)
def _rate(n,d): return n/d if d else None

def _success_counts(plays):
 c=Counter()
 for p in plays:
  result=classify_success(p)
  if result is None: continue
  c["eligible"]+=1; c["successful"]+=int(result)
  subtype=str(p.get("eventSubtype") or "").lower()
  if "rush" in subtype:
   c["rushEligible"]+=1; c["rushSuccessful"]+=int(result)
  elif any(x in subtype for x in ("pass","sack")):
   c["passEligible"]+=1; c["passSuccessful"]+=int(result)
  d=p.get("down")
  if d in (1,2,3,4): c[f"down{d}Eligible"]+=1; c[f"down{d}Successful"]+=int(result)
 return c

def _success_fields(off,deff):
 oc=_success_counts(off); dc=_success_counts(deff)
 out={"successEligiblePlays":oc["eligible"],"successfulPlays":oc["successful"],"successRate":_rate(oc["successful"],oc["eligible"]),"successEligiblePlaysAllowed":dc["eligible"],"successfulPlaysAllowed":dc["successful"],"successRateAllowed":_rate(dc["successful"],dc["eligible"]),"successDefinitionVersion":SUCCESS_VERSION}
 for prefix in ("rush","pass"):
  title=prefix.title(); out[f"{prefix}SuccessEligiblePlays"]=oc[f"{prefix}Eligible"]; out[f"{prefix}SuccessfulPlays"]=oc[f"{prefix}Successful"]; out[f"{prefix}SuccessRate"]=_rate(oc[f"{prefix}Successful"],oc[f"{prefix}Eligible"])
  out[f"{prefix}SuccessEligiblePlaysAllowed"]=dc[f"{prefix}Eligible"]; out[f"{prefix}SuccessfulPlaysAllowed"]=dc[f"{prefix}Successful"]; out[f"{prefix}SuccessRateAllowed"]=_rate(dc[f"{prefix}Successful"],dc[f"{prefix}Eligible"])
 for d in (1,2,3,4):
  out[f"down{d}SuccessEligiblePlays"]=oc[f"down{d}Eligible"]; out[f"down{d}SuccessfulPlays"]=oc[f"down{d}Successful"]; out[f"down{d}SuccessRate"]=_rate(oc[f"down{d}Successful"],oc[f"down{d}Eligible"])
  out[f"down{d}SuccessEligiblePlaysAllowed"]=dc[f"down{d}Eligible"]; out[f"down{d}SuccessfulPlaysAllowed"]=dc[f"down{d}Successful"]; out[f"down{d}SuccessRateAllowed"]=_rate(dc[f"down{d}Successful"],dc[f"down{d}Eligible"])
 return out

def derive_team_games(plays,drives,season,season_type,week):
 by_game=defaultdict(list); play_games=defaultdict(list)
 for d in drives: by_game[str(d.get("gameId"))].append(d)
 for p in plays: play_games[str(p.get("gameId"))].append(p)
 out=[]
 for gid,ds in by_game.items():
  teams=set()
  for d in ds:
   if d.get("offense"): teams.add(d["offense"])
   if d.get("defense"): teams.add(d["defense"])
  for p in play_games.get(gid,[]):
   if p.get("offense"): teams.add(p["offense"])
   if p.get("defense"): teams.add(p["defense"])
  valid=[d for d in ds if d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS" and d.get("offense") and d.get("defense")]
  review=[d for d in ds if d.get("isPossessionDrive") is True and d.get("driveValidationStatus")!="PASS"]
  gp=play_games.get(gid,[])
  for team in sorted(teams):
   opps=[x for d in valid for x in (d.get("offense"),d.get("defense")) if x and x!=team]
   opponent=Counter(opps).most_common(1)[0][0] if opps else None
   off=[d for d in valid if d.get("offense")==team]; deff=[d for d in valid if d.get("defense")==team]
   off_yards=sum(d.get("analyticsYardsGained",0) for d in off if _num(d.get("analyticsYardsGained"))); def_yards=sum(d.get("analyticsYardsGained",0) for d in deff if _num(d.get("analyticsYardsGained")))
   off_plays=[p for p in gp if p.get("offense")==team]; def_plays=[p for p in gp if p.get("defense")==team]
   row={"season":season,"seasonType":season_type,"week":week,"gameId":gid,"team":team,"opponent":opponent,"validatedPossessions":len(off),"validatedDefensivePossessions":len(deff),"offensivePlays":sum(d.get("offensivePlayCount",0) for d in off),"defensivePlays":sum(d.get("offensivePlayCount",0) for d in deff),"offensiveYards":off_yards,"defensiveYardsAllowed":def_yards,"yardsPerPossession":off_yards/len(off) if off else None,"yardsAllowedPerPossession":def_yards/len(deff) if deff else None,"reviewPossessionGroups":sum(team in {d.get("offense"),d.get("defense")} for d in review),"gameValidationStatus":"PASS" if len(teams)==2 else "REVIEW","gameValidationIssues":[] if len(teams)==2 else ["TEAM_IDENTITY_COUNT_NOT_TWO"],"gameSchemaVersion":GAME_SCHEMA_VERSION}
   row.update(_success_fields(off_plays,def_plays)); out.append(row)
 return out

def materialize_game_partition(processed_root,season,season_type,week,refresh=False):
 cp=canonical_partition_dir(processed_root,season,season_type,week)/"plays.json"; dp=derived_drive_partition_dir(processed_root,season,season_type,week)/"drives.json"
 if not cp.exists() or not dp.exists(): raise FileNotFoundError("Canonical plays and derived drives must exist first")
 cb,db=cp.read_bytes(),dp.read_bytes(); target=derived_game_partition_dir(processed_root,season,season_type,week); path=target/"team_games.json"; manifest=target/"team_games.manifest.json"; sig=_sha(cb+db)
 if not refresh and path.exists() and manifest.exists():
  m=json.loads(manifest.read_text())
  if m.get("input_sha256")==sig and m.get("game_schema_version")==GAME_SCHEMA_VERSION:return {**m,"status":"REUSED"}
 rows=derive_team_games(json.loads(cb),json.loads(db),season,season_type,week); payload=json.dumps(rows,ensure_ascii=False,separators=(",",":")).encode(); m={"entity":"team_games","layer":"derived","season":season,"season_type":season_type,"week":week,"record_count":len(rows),"game_count":len({r['gameId'] for r in rows}),"review_record_count":sum(r['gameValidationStatus']!='PASS' for r in rows),"input_sha256":sig,"output_sha256":_sha(payload),"game_schema_version":GAME_SCHEMA_VERSION}
 _atomic(path,payload);_atomic(manifest,json.dumps(m,indent=2,sort_keys=True).encode());return {**m,"status":"WRITTEN"}
def materialize_game_corpus(raw_root,processed_root,seasons,refresh=False):return [materialize_game_partition(processed_root,s,st,w,refresh) for s in seasons for st,w in discover_partitions(raw_root,s)]
def game_corpus_audit(raw_root,processed_root,seasons):
 records=[]
 for s in seasons:
  for st,w in discover_partitions(raw_root,s): records.extend(json.loads((derived_game_partition_dir(processed_root,s,st,w)/"team_games.json").read_text()))
 by=Counter(r['gameId'] for r in records); issues=Counter(x for r in records for x in r.get('gameValidationIssues',[])); checks={"exactly_two_team_rows_per_game":all(n==2 for n in by.values()),"unique_team_game_rows":len({(r['gameId'],r['team']) for r in records})==len(records),"all_team_rows_have_opponent":all(r.get('opponent') for r in records),"success_offense_defense_eligible_reconciles":sum(r.get('successEligiblePlays',0) for r in records)==sum(r.get('successEligiblePlaysAllowed',0) for r in records),"success_offense_defense_successful_reconciles":sum(r.get('successfulPlays',0) for r in records)==sum(r.get('successfulPlaysAllowed',0) for r in records)}
 return {"status":"PASS" if all(checks.values()) else "REVIEW","team_game_rows":len(records),"games":len(by),"review_rows":sum(r['gameValidationStatus']!='PASS' for r in records),"success_eligible_plays":sum(r.get('successEligiblePlays',0) for r in records),"successful_plays":sum(r.get('successfulPlays',0) for r in records),"checks":checks,"issues":dict(issues)}
def concise_game_audit(r):
 lines=[f"DERIVED TEAM-GAME CORPUS AUDIT: {r['status']}",f"Games: {r['games']:,}",f"Team-game rows: {r['team_game_rows']:,}",f"Review rows: {r['review_rows']:,}",f"Success eligible plays: {r['success_eligible_plays']:,}",f"Successful plays: {r['successful_plays']:,}","","Checks:"]
 lines += [f"{'PASS' if v else 'FAIL'} {k}" for k,v in r['checks'].items()]
 if r['issues']: lines += ["","Issues:"]+[f"{k}: {v:,}" for k,v in r['issues'].items()]
 return "\n".join(lines)
