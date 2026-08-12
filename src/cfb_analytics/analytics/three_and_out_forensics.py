"""Forensics for a conservative three-and-out possession definition.

A production three-and-out should represent a normal failed first-down series,
not merely any possession with three plays. This audit profiles validated
possessions by clean scrimmage-snap count, down sequence, first-down resets,
punt evidence, scoring, turnovers, and period-ending context before locking a
definition. Diagnostic only; no derived rows are modified.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from cfb_analytics.analytics.finishing_drives import possession_outcome

def _punt(p):
 s=(str(p.get("eventSubtype") or "")+" "+str(p.get("sourcePlayType") or "")+" "+str(p.get("eventCategory") or "")).upper()
 return "PUNT" in s

def _turnover(rows):
 return any(str(p.get("eventCategory") or "").upper()=="TURNOVER" for p in rows)

def _clean_scrimmage(rows):
 return [p for p in rows if p.get("isScrimmagePlay") is True and p.get("isOffensivePlay") is True and not p.get("hasNoPlayContext",False)]

def audit_partition(drives,plays):
 by_drive=defaultdict(list);by_game=defaultdict(list);c=Counter();examples=[]
 for p in plays:
  by_drive[(str(p.get("gameId")),str(p.get("driveId")))].append(p);by_game[str(p.get("gameId"))].append(p)
 for d in drives:
  if not (d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS" and d.get("offense")):continue
  c["possessions"]+=1;gid=str(d.get("gameId"));rows=by_drive[(gid,str(d.get("driveId")))];snaps=_clean_scrimmage(rows);downs=[p.get("down") for p in snaps]
  if len(snaps)==3:c["three_snap_possessions"]+=1
  else:continue
  starts_first=bool(downs and downs[0]==1);seq123=downs==[1,2,3];first_reset=any(x==1 for x in downs[1:]);punt=any(_punt(p) for p in rows);turn=_turnover(rows);out=possession_outcome(d,rows,by_game[gid]);score=out.get("outcome") in {"TOUCHDOWN","FIELD_GOAL","OTHER_SCORING"}
  if starts_first:c["starts_first_down"]+=1
  if seq123:c["exact_1_2_3_sequence"]+=1
  if first_reset:c["first_down_reset_within_three"]+=1
  if punt:c["punt_evidence"]+=1
  if turn:c["turnover_context"]+=1
  if score:c["scoring_outcome"]+=1
  # Period-ending proxy: no punt/score/turnover and drive's final record is in a different period
  # than a following game record, or clock is 0:00-ish when represented numerically/string.
  clock=d.get("endClock");terminal_clock=str(clock).strip() in {"0:00","00:00","0","0.0"}
  if terminal_clock:c["terminal_clock"]+=1
  candidate=starts_first and seq123 and not first_reset and punt and not turn and not score
  if candidate:c["strict_candidates"]+=1
  # Near misses are intentionally surfaced rather than coerced.
  if starts_first and seq123 and not first_reset and not score and not turn and not punt:c["clean_123_without_punt"]+=1
  if len(examples)<50 and (candidate or (starts_first and seq123 and not punt)):
   examples.append({"season":d.get("season"),"gameId":d.get("gameId"),"driveId":d.get("driveId"),"offense":d.get("offense"),"downs":downs,"punt":punt,"turnover":turn,"outcome":out.get("outcome"),"endPeriod":d.get("endPeriod"),"endClock":clock,"playCount":d.get("playCount"),"offensivePlayCount":d.get("offensivePlayCount")})
 return c,examples

def merge(results):
 c=Counter();examples=[]
 for x,e in results:c.update(x);examples.extend(e[:max(0,50-len(examples))])
 return {"counts":dict(c),"examples":examples}

def concise(r):
 c=r["counts"]
 lines=["THREE-AND-OUT FORENSICS (v1)",f"Validated possessions: {c.get('possessions',0):,}",f"Exactly three clean offensive scrimmage snaps: {c.get('three_snap_possessions',0):,}","",f"Start on first down: {c.get('starts_first_down',0):,}",f"Exact down sequence 1-2-3: {c.get('exact_1_2_3_sequence',0):,}",f"First-down reset within three snaps: {c.get('first_down_reset_within_three',0):,}",f"Punt evidence in source group: {c.get('punt_evidence',0):,}",f"Turnover context: {c.get('turnover_context',0):,}",f"Scoring outcome: {c.get('scoring_outcome',0):,}",f"Terminal-clock signal: {c.get('terminal_clock',0):,}","",f"Strict 1-2-3 + punt + no score/turnover candidates: {c.get('strict_candidates',0):,}",f"Clean 1-2-3 with no punt/score/turnover: {c.get('clean_123_without_punt',0):,}","","Diagnostic only. We will not classify three-and-outs until the no-punt 1-2-3 residual is understood.","Use --json for representative strict candidates and no-punt residuals."]
 return "\n".join(lines)
