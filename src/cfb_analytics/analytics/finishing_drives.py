"""Finishing Drives v2: scoring opportunities and adjudicated possession points."""
from __future__ import annotations
import json
from collections import Counter,defaultdict
from pathlib import Path
from cfb_analytics.raw.audit import discover_partitions
from cfb_analytics.raw.sequence import _candidate_sort_key
from cfb_analytics.canonical.materialize import canonical_partition_dir
from cfb_analytics.derived.drives import derived_drive_partition_dir
from cfb_analytics.analytics.touchdown_points import adjudicate_touchdown_points

FINISHING_DRIVES_VERSION="finishing-drives-v2"

def scoring_opportunity(drive,plays):
 if not drive.get("isPossessionDrive") or drive.get("driveValidationStatus")!="PASS" or not drive.get("offense"):return False
 offense=drive["offense"]
 return any(p.get("offense")==offense and isinstance(p.get("yardsToGoal"),(int,float)) and not isinstance(p.get("yardsToGoal"),bool) and 0<=p.get("yardsToGoal")<=40 for p in plays)

def possession_outcome(drive,drive_plays,game_plays):
 offense=drive.get("offense")
 if not offense:return {"outcome":"UNKNOWN","points":0,"pointsResolved":False}
 offensive=[p for p in drive_plays if p.get("offense")==offense];subtypes={str(p.get("eventSubtype") or "") for p in offensive}
 if "RUSH_TD" in subtypes or "PASS_TD" in subtypes:
  ordered=sorted(game_plays,key=_candidate_sort_key);td_ids={str(p.get("id")) for p in offensive if p.get("eventSubtype") in {"RUSH_TD","PASS_TD"}}
  for i,p in enumerate(ordered):
   if str(p.get("id")) in td_ids:
    r=adjudicate_touchdown_points(ordered,i)
    if r["status"]=="RESOLVED":return {"outcome":"TOUCHDOWN","points":r["points"],"pointsResolved":True,"pointsSource":r["source"]}
  return {"outcome":"TOUCHDOWN","points":0,"pointsResolved":False,"pointsSource":"UNRESOLVED_TD_SCORE"}
 if "FIELD_GOAL_GOOD" in subtypes:return {"outcome":"FIELD_GOAL","points":3,"pointsResolved":True,"pointsSource":"FIELD_GOAL_GOOD"}
 if "SAFETY" in subtypes:return {"outcome":"OTHER_SCORING","points":0,"pointsResolved":False,"pointsSource":"AMBIGUOUS_SAFETY"}
 return {"outcome":"EMPTY","points":0,"pointsResolved":True,"pointsSource":"EMPTY"}

def team_finishing_metrics(team,drives,plays):
 by_drive=defaultdict(list)
 for p in plays:by_drive[(str(p.get("gameId")),str(p.get("driveId")))].append(p)
 off=[d for d in drives if d.get("offense")==team and d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS"]
 counts=Counter();points=0
 for d in off:
  rows=by_drive[(str(d.get("gameId")),str(d.get("driveId")))]
  if not scoring_opportunity(d,rows):continue
  counts["opportunities"]+=1;r=possession_outcome(d,rows,plays);counts[r["outcome"]]+=1
  if r["pointsResolved"]:counts["pointsResolvedOpportunities"]+=1;points+=r["points"]
  else:counts["unresolvedPointOpportunities"]+=1
 opp=counts["opportunities"]
 return {"scoringOpportunities":opp,"opportunityTouchdowns":counts["TOUCHDOWN"],"opportunityFieldGoals":counts["FIELD_GOAL"],"emptyOpportunities":counts["EMPTY"],"otherScoringOpportunities":counts["OTHER_SCORING"],"resolvedPointOpportunities":counts["pointsResolvedOpportunities"],"unresolvedPointOpportunities":counts["unresolvedPointOpportunities"],"opportunityPoints":points,"pointsPerOpportunity":points/counts["pointsResolvedOpportunities"] if counts["pointsResolvedOpportunities"] else None,"touchdownRatePerOpportunity":counts["TOUCHDOWN"]/opp if opp else None,"fieldGoalRatePerOpportunity":counts["FIELD_GOAL"]/opp if opp else None,"emptyRatePerOpportunity":counts["EMPTY"]/opp if opp else None,"finishingDrivesDefinitionVersion":FINISHING_DRIVES_VERSION}

def finishing_drives_audit(raw_root:Path,processed_root:Path,seasons):
 totals=Counter();points=0
 for season in seasons:
  for st,w in discover_partitions(raw_root,season):
   plays=json.loads((canonical_partition_dir(processed_root,season,st,w)/"plays.json").read_text());drives=json.loads((derived_drive_partition_dir(processed_root,season,st,w)/"drives.json").read_text());teams={d.get("offense") for d in drives if d.get("offense")}
   totals["validated_possessions"]+=sum(d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS" for d in drives)
   for team in teams:
    m=team_finishing_metrics(team,drives,plays);totals["opportunities"]+=m["scoringOpportunities"];totals["TOUCHDOWN"]+=m["opportunityTouchdowns"];totals["FIELD_GOAL"]+=m["opportunityFieldGoals"];totals["EMPTY"]+=m["emptyOpportunities"];totals["OTHER_SCORING"]+=m["otherScoringOpportunities"];totals["resolved"]+=m["resolvedPointOpportunities"];totals["unresolved"]+=m["unresolvedPointOpportunities"];points+=m["opportunityPoints"]
 opp=totals["opportunities"]
 return {"validated_possessions":totals["validated_possessions"],"opportunities":opp,"opportunity_rate":opp/totals["validated_possessions"] if totals["validated_possessions"] else None,"outcomes":{k:totals[k] for k in ("TOUCHDOWN","FIELD_GOAL","EMPTY","OTHER_SCORING")},"resolved_point_opportunities":totals["resolved"],"unresolved_point_opportunities":totals["unresolved"],"opportunity_points":points,"points_per_resolved_opportunity":points/totals["resolved"] if totals["resolved"] else None,"version":FINISHING_DRIVES_VERSION}
def concise_finishing_drives_audit(r):
 o=r["outcomes"];opp=r["opportunities"]
 lines=["FINISHING DRIVES AUDIT (v2)",f"Validated possession drives: {r['validated_possessions']:,}",f"Scoring opportunities: {opp:,}",f"Opportunity rate: {r['opportunity_rate']:.2%}" if r['opportunity_rate'] is not None else "Opportunity rate: N/A","",f"Touchdowns: {o.get('TOUCHDOWN',0):,}",f"Field goals: {o.get('FIELD_GOAL',0):,}",f"Empty: {o.get('EMPTY',0):,}",f"Other scoring: {o.get('OTHER_SCORING',0):,}","",f"Point-resolved opportunities: {r['resolved_point_opportunities']:,}",f"Unresolved point opportunities: {r['unresolved_point_opportunities']:,}",f"Adjudicated opportunity points: {r['opportunity_points']:,}",f"Points per resolved opportunity: {r['points_per_resolved_opportunity']:.3f}" if r['points_per_resolved_opportunity'] is not None else "Points per resolved opportunity: N/A","","TD points use only adjudicated +6/+7/+8 scoreboard evidence; unresolved TDs remain unresolved."]
 return "\n".join(lines)
