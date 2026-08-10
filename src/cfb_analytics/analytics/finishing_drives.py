"""Finishing Drives v1: scoring-opportunity and possession-outcome audit.

A scoring opportunity is a validated offensive possession that reaches the
opponent 40-yard line or closer (yardsToGoal <= 40) on a play belonging to the
drive offense. v1 classifies the possession outcome from explicit canonical
TD/FG events. Touchdowns are counted as six possession points and made field
goals as three; PAT/two-point tries are intentionally NOT attached yet because
source grouping may place them outside the possession drive.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.canonical.materialize import canonical_partition_dir
from cfb_analytics.derived.drives import derived_drive_partition_dir

FINISHING_DRIVES_VERSION="finishing-drives-v1"

def scoring_opportunity(drive, plays):
 if not drive.get("isPossessionDrive") or drive.get("driveValidationStatus")!="PASS" or not drive.get("offense"): return False
 offense=drive["offense"]
 for p in plays:
  if p.get("offense")!=offense: continue
  ytg=p.get("yardsToGoal")
  if isinstance(ytg,(int,float)) and not isinstance(ytg,bool) and 0<=ytg<=40: return True
 return False

def possession_outcome(drive, plays):
 offense=drive.get("offense")
 if not offense: return {"outcome":"UNKNOWN","possessionPointsExcludingTry":0}
 offensive=[p for p in plays if p.get("offense")==offense]
 subtypes={str(p.get("eventSubtype") or "") for p in offensive}
 if "RUSH_TD" in subtypes or "PASS_TD" in subtypes:
  return {"outcome":"TOUCHDOWN","possessionPointsExcludingTry":6}
 # Field goal events may be tagged special teams but still carry the possessing offense.
 if "FIELD_GOAL_GOOD" in subtypes:
  return {"outcome":"FIELD_GOAL","possessionPointsExcludingTry":3}
 # A safety by the offense is sufficiently unusual/ambiguous that v1 does not force it.
 if "SAFETY" in subtypes:
  return {"outcome":"OTHER_SCORING","possessionPointsExcludingTry":0}
 return {"outcome":"EMPTY","possessionPointsExcludingTry":0}

def finishing_drives_audit(raw_root:Path,processed_root:Path,seasons):
 totals=Counter(); outcomes=Counter(); points=0; by_season=defaultdict(Counter); conversion_groups=0; opportunity_examples=[]
 for season in seasons:
  for st,w in discover_partitions(raw_root,season):
   cp=canonical_partition_dir(processed_root,season,st,w)/"plays.json"; dp=derived_drive_partition_dir(processed_root,season,st,w)/"drives.json"
   plays=json.loads(cp.read_text()); drives=json.loads(dp.read_text()); grouped=defaultdict(list)
   for p in plays: grouped[(str(p.get("gameId")),str(p.get("driveId")))].append(p)
   for d in drives:
    if not d.get("isPossessionDrive") or d.get("driveValidationStatus")!="PASS": continue
    totals["validated_possessions"]+=1; rows=grouped[(str(d.get("gameId")),str(d.get("driveId")))]
    if scoring_opportunity(d,rows):
     totals["opportunities"]+=1; by_season[season]["opportunities"]+=1; result=possession_outcome(d,rows); outcomes[result["outcome"]]+=1; by_season[season][result["outcome"]]+=1; points+=result["possessionPointsExcludingTry"]
     if len(opportunity_examples)<5: opportunity_examples.append({"season":season,"week":w,"gameId":d.get("gameId"),"driveId":d.get("driveId"),"offense":d.get("offense"),"outcome":result["outcome"],"points_excluding_try":result["possessionPointsExcludingTry"]})
   # Count conversion-only source groups to quantify why tries need separate attachment logic.
   for d in drives:
    if d.get("nonPossessionProfile")=="SCORING_OR_CONVERSION_ONLY":
     rows=grouped[(str(d.get("gameId")),str(d.get("driveId")))]
     if any(p.get("eventCategory")=="CONVERSION" for p in rows): conversion_groups+=1
 opp=totals["opportunities"]
 return {"validated_possessions":totals["validated_possessions"],"opportunities":opp,"opportunity_rate":opp/totals["validated_possessions"] if totals["validated_possessions"] else None,"outcomes":dict(outcomes),"touchdown_rate":outcomes["TOUCHDOWN"]/opp if opp else None,"field_goal_rate":outcomes["FIELD_GOAL"]/opp if opp else None,"empty_rate":outcomes["EMPTY"]/opp if opp else None,"possession_points_excluding_try":points,"points_per_opportunity_excluding_try":points/opp if opp else None,"conversion_only_source_groups":conversion_groups,"by_season":{str(k):dict(v) for k,v in sorted(by_season.items())},"examples":opportunity_examples,"version":FINISHING_DRIVES_VERSION,"note":"v1 does not attach PAT/two-point tries to touchdown possessions."}
def concise_finishing_drives_audit(r):
 o=r["outcomes"]
 lines=["FINISHING DRIVES AUDIT (v1)",f"Validated possession drives: {r['validated_possessions']:,}",f"Scoring opportunities (reach opponent 40): {r['opportunities']:,}",f"Opportunity rate: {r['opportunity_rate']:.2%}" if r['opportunity_rate'] is not None else "Opportunity rate: N/A","","Opportunity outcomes:",f"Touchdowns: {o.get('TOUCHDOWN',0):,} ({r['touchdown_rate']:.2%})" if r['touchdown_rate'] is not None else "Touchdowns: 0",f"Field goals: {o.get('FIELD_GOAL',0):,} ({r['field_goal_rate']:.2%})" if r['field_goal_rate'] is not None else "Field goals: 0",f"Empty: {o.get('EMPTY',0):,} ({r['empty_rate']:.2%})" if r['empty_rate'] is not None else "Empty: 0"]
 if o.get("OTHER_SCORING",0): lines.append(f"Other/ambiguous scoring: {o['OTHER_SCORING']:,}")
 lines += ["",f"Possession points excluding tries: {r['possession_points_excluding_try']:,}",f"Points/opportunity excluding tries: {r['points_per_opportunity_excluding_try']:.3f}" if r['points_per_opportunity_excluding_try'] is not None else "Points/opportunity excluding tries: N/A",f"Conversion-only source groups observed: {r['conversion_only_source_groups']:,}","","Definition: validated possession reaches yardsToGoal <= 40.","TD=6 and made FG=3 in v1; PAT/two-point tries are not attached yet.","No data is modified by this audit."]
 return "\n".join(lines)
