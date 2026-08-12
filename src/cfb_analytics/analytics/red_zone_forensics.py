"""Forensic audit for red-zone and goal-to-go efficiency.

This deliberately starts from clean Success-v1 offensive scrimmage plays and
uses canonical yardsToGoal. Red zone = snap starts at opponent 20 or closer;
goal-to-go = distance >= yardsToGoal (with positive usable values). Diagnostic
only: no production metrics are written until field-state semantics reconcile.
"""
from __future__ import annotations
from collections import Counter
from cfb_analytics.analytics.success import classify_success

def _num(v):return isinstance(v,(int,float)) and not isinstance(v,bool)
def classify_red_zone(play):
 result=classify_success(play)
 if result is None:return None
 ytg=play.get("yardsToGoal")
 if not _num(ytg) or ytg<0 or ytg>100:return None
 return ytg<=20

def classify_goal_to_go(play):
 rz=classify_red_zone(play)
 if rz is None:return None
 ytg=play.get("yardsToGoal");dist=play.get("distance")
 if not _num(dist) or dist<=0:return None
 return bool(rz and ytg>0 and dist>=ytg)
def audit(plays):
 c=Counter()
 for p in plays:
  success=classify_success(p)
  if success is None:continue
  c["success_eligible"]+=1;rz=classify_red_zone(p)
  if rz is None:c["invalid_field_state"]+=1;continue
  if not rz:continue
  c["red_zone_plays"]+=1;c["red_zone_successes"]+=int(success)
  ytg=p.get("yardsToGoal")
  if ytg==0:c["red_zone_start_at_goal_line"]+=1
  gtg=classify_goal_to_go(p)
  if gtg is None:c["goal_to_go_unclassified"]+=1
  elif gtg:c["goal_to_go_plays"]+=1;c["goal_to_go_successes"]+=int(success)
  else:c["red_zone_non_goal_to_go"]+=1
 return dict(c)
def concise(r):
 rate=lambda n,d:n/d if d else 0
 return "\n".join(["RED-ZONE / GOAL-TO-GO FORENSICS",f"Locked Success-v1 eligible plays: {r.get('success_eligible',0):,}",f"Invalid/missing yardsToGoal: {r.get('invalid_field_state',0):,}","",f"Red-zone plays (yardsToGoal <= 20): {r.get('red_zone_plays',0):,}",f"Red-zone successes: {r.get('red_zone_successes',0):,}",f"Red-zone success rate: {rate(r.get('red_zone_successes',0),r.get('red_zone_plays',0)):.2%}","",f"Goal-to-go plays (distance >= yardsToGoal): {r.get('goal_to_go_plays',0):,}",f"Goal-to-go successes: {r.get('goal_to_go_successes',0):,}",f"Goal-to-go success rate: {rate(r.get('goal_to_go_successes',0),r.get('goal_to_go_plays',0)):.2%}",f"Red-zone non-goal-to-go plays: {r.get('red_zone_non_goal_to_go',0):,}","",f"Starts recorded exactly at goal line: {r.get('red_zone_start_at_goal_line',0):,}",f"Goal-to-go unclassified: {r.get('goal_to_go_unclassified',0):,}","","Candidate definitions: red zone = clean Success-v1 snap at opponent 20 or closer; goal-to-go = red-zone snap with distance >= yardsToGoal.","Diagnostic only. No team-game/season propagation yet."])
