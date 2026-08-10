"""Derive one analytics row per team and season from validated team-game rows."""
from __future__ import annotations
import hashlib, json, os
from collections import defaultdict
from pathlib import Path
from typing import Any
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.derived.games import derived_game_partition_dir

SEASON_SCHEMA_VERSION="team-season-v1"

def derived_season_dir(root:Path,season:int)->Path:
 return root/"derived"/"seasons"/f"season={season}"
def _atomic(path:Path,data:bytes):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_bytes(data); os.replace(tmp,path)
def _sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def _sum(rows,key): return sum((r.get(key) or 0) for r in rows)
def _rate(n,d): return n/d if d else None

def derive_team_seasons(team_games,season):
 grouped=defaultdict(list)
 for r in team_games:
  if r.get("season")==season: grouped[r["team"]].append(r)
 out=[]
 for team,rows in sorted(grouped.items()):
  rows=sorted(rows,key=lambda r:(str(r.get("seasonType")),r.get("week",0),str(r.get("gameId"))))
  games=len(rows); poss=_sum(rows,"validatedPossessions"); dposs=_sum(rows,"validatedDefensivePossessions")
  plays=_sum(rows,"offensivePlays"); dplays=_sum(rows,"defensivePlays"); yards=_sum(rows,"offensiveYards"); dyards=_sum(rows,"defensiveYardsAllowed")
  review=_sum(rows,"reviewPossessionGroups"); review_games=sum(r.get("gameValidationStatus")!="PASS" for r in rows)
  out.append({"season":season,"team":team,"games":games,"validatedPossessions":poss,"validatedDefensivePossessions":dposs,
   "offensivePlays":plays,"defensivePlays":dplays,"offensiveYards":yards,"defensiveYardsAllowed":dyards,
   "yardsPerGame":_rate(yards,games),"yardsAllowedPerGame":_rate(dyards,games),"yardsPerPlay":_rate(yards,plays),"yardsAllowedPerPlay":_rate(dyards,dplays),
   "yardsPerPossession":_rate(yards,poss),"yardsAllowedPerPossession":_rate(dyards,dposs),"possessionsPerGame":_rate(poss,games),"defensivePossessionsPerGame":_rate(dposs,games),
   "reviewPossessionGroups":review,"reviewGames":review_games,"seasonValidationStatus":"PASS" if review_games==0 else "REVIEW","seasonSchemaVersion":SEASON_SCHEMA_VERSION})
 return out

def _load_season_games(raw_root,processed_root,season):
 rows=[]; payloads=[]
 for st,w in discover_partitions(raw_root,season):
  p=derived_game_partition_dir(processed_root,season,st,w)/"team_games.json"
  if not p.exists(): raise FileNotFoundError(f"Derived team-game partition missing: {p}")
  b=p.read_bytes(); payloads.append(b); rows.extend(json.loads(b))
 return rows,b"".join(payloads)
def materialize_season(processed_root,raw_root,season,refresh=False):
 rows,source=_load_season_games(raw_root,processed_root,season); target=derived_season_dir(processed_root,season); path=target/"team_seasons.json"; manifest=target/"team_seasons.manifest.json"; sig=_sha(source)
 if not refresh and path.exists() and manifest.exists():
  m=json.loads(manifest.read_text())
  if m.get("input_sha256")==sig and m.get("season_schema_version")==SEASON_SCHEMA_VERSION:return {**m,"status":"REUSED"}
 out=derive_team_seasons(rows,season); payload=json.dumps(out,ensure_ascii=False,separators=(",",":")).encode(); m={"entity":"team_seasons","layer":"derived","season":season,"record_count":len(out),"team_game_count":len(rows),"review_record_count":sum(r['seasonValidationStatus']!='PASS' for r in out),"input_sha256":sig,"output_sha256":_sha(payload),"season_schema_version":SEASON_SCHEMA_VERSION}
 _atomic(path,payload); _atomic(manifest,json.dumps(m,indent=2,sort_keys=True).encode()); return {**m,"status":"WRITTEN"}
def materialize_season_corpus(raw_root,processed_root,seasons,refresh=False): return [materialize_season(processed_root,raw_root,s,refresh) for s in seasons]
def season_corpus_audit(raw_root,processed_root,seasons):
 records=[]; game_rows=[]
 for s in seasons:
  p=derived_season_dir(processed_root,s)/"team_seasons.json"; records.extend(json.loads(p.read_text())); gr,_=_load_season_games(raw_root,processed_root,s); game_rows.extend(gr)
 keys={(r['season'],r['team']) for r in records}; expected={(r['season'],r['team']) for r in game_rows}
 game_counts=defaultdict(int)
 for r in game_rows: game_counts[(r['season'],r['team'])]+=1
 checks={"unique_team_season_rows":len(keys)==len(records),"all_team_games_represented":keys==expected,"games_played_reconciles":all(r['games']==game_counts[(r['season'],r['team'])] for r in records),"offense_defense_possessions_reconcile":sum(r['validatedPossessions'] for r in records)==sum(r['validatedDefensivePossessions'] for r in records),"offense_defense_yards_reconcile":sum(r['offensiveYards'] for r in records)==sum(r['defensiveYardsAllowed'] for r in records)}
 return {"status":"PASS" if all(checks.values()) else "REVIEW","team_season_rows":len(records),"team_game_rows":len(game_rows),"seasons":len(seasons),"review_rows":sum(r['seasonValidationStatus']!='PASS' for r in records),"checks":checks}
def concise_season_audit(r):
 lines=[f"DERIVED TEAM-SEASON CORPUS AUDIT: {r['status']}",f"Seasons: {r['seasons']:,}",f"Team-game rows aggregated: {r['team_game_rows']:,}",f"Team-season rows: {r['team_season_rows']:,}",f"Review rows: {r['review_rows']:,}","","Checks:"]
 lines += [f"{'PASS' if v else 'FAIL'} {k}" for k,v in r['checks'].items()]
 return "\n".join(lines)
