"""Field Position v1 from validated possession-drive starting state.

A drive is eligible when it is a validated possession and its starting
``yardsToGoal`` is numeric and between 0 and 100 inclusive. Lower yards-to-goal
means better offensive field position, so we also expose own-yard-line position
as ``100 - yardsToGoal`` for intuitive reporting.
"""
from __future__ import annotations
from typing import Any

FIELD_POSITION_VERSION="field-position-v1"

def _num(v:Any)->bool:return isinstance(v,(int,float)) and not isinstance(v,bool)

def valid_start_yards_to_goal(drive):
 if drive.get("isPossessionDrive") is not True or drive.get("driveValidationStatus")!="PASS":return None
 y=drive.get("startYardsToGoal")
 if not _num(y) or y<0 or y>100:return None
 return float(y)

def team_field_position_metrics(team,drives):
 off=[valid_start_yards_to_goal(d) for d in drives if d.get("offense")==team]
 deff=[valid_start_yards_to_goal(d) for d in drives if d.get("defense")==team]
 off=[y for y in off if y is not None];deff=[y for y in deff if y is not None]
 def fields(vals,prefix=""):
  n=len(vals);total=sum(vals);own=sum(100-y for y in vals)
  return {f"fieldPositionPossessions{prefix}":n,f"startYardsToGoalTotal{prefix}":total,f"averageStartYardsToGoal{prefix}":total/n if n else None,f"startOwnYardLineTotal{prefix}":own,f"averageStartOwnYardLine{prefix}":own/n if n else None}
 out=fields(off);out.update(fields(deff,"Allowed"));out["fieldPositionDefinitionVersion"]=FIELD_POSITION_VERSION;return out

def field_position_audit(drives):
 possessions=[d for d in drives if d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS"]
 vals=[valid_start_yards_to_goal(d) for d in possessions];eligible=[v for v in vals if v is not None]
 missing=len(possessions)-len(eligible);total=sum(eligible)
 buckets={"opponent_1_20":0,"opponent_21_40":0,"midfield_41_60":0,"own_21_40":0,"own_1_20":0}
 for y in eligible:
  if y<=20:buckets["opponent_1_20"]+=1
  elif y<=40:buckets["opponent_21_40"]+=1
  elif y<=60:buckets["midfield_41_60"]+=1
  elif y<=80:buckets["own_21_40"]+=1
  else:buckets["own_1_20"]+=1
 return {"validated_possessions":len(possessions),"eligible":len(eligible),"missing_or_invalid":missing,"coverage":len(eligible)/len(possessions) if possessions else None,"average_start_yards_to_goal":total/len(eligible) if eligible else None,"average_start_own_yard_line":100-total/len(eligible) if eligible else None,"buckets":buckets}

def concise_field_position_audit(r):
 lines=["FIELD POSITION AUDIT (v1)",f"Validated possession drives: {r['validated_possessions']:,}",f"Eligible starting field positions: {r['eligible']:,} ({r['coverage']:.2%})" if r['coverage'] is not None else "Eligible: 0",f"Missing/invalid starts: {r['missing_or_invalid']:,}",f"Average start yards to goal: {r['average_start_yards_to_goal']:.2f}" if r['average_start_yards_to_goal'] is not None else "Average start yards to goal: N/A",f"Average starting own-yard line: {r['average_start_own_yard_line']:.2f}" if r['average_start_own_yard_line'] is not None else "Average starting own-yard line: N/A","","Starting-field buckets:"]
 for k,v in r['buckets'].items():lines.append(f"{k:.<32} {v:>8,}")
 lines += ["","Definition: validated possession drive startYardsToGoal in [0,100].","No data is modified by this audit."]
 return "\n".join(lines)
