"""Residual audit for clean 1-2-3 possessions lacking punt/score/turnover evidence.

Diagnostic only. Examines the 3-and-out residual family using drive/source
records, terminal snap state, period/clock, fourth-down continuation, and next
possession ownership. No production classification is changed.
"""
from __future__ import annotations
from collections import Counter,defaultdict

def _offensive_scrimmage(rows,off):
 return [p for p in rows if p.get("offense")==off and p.get("isOffensivePlay") is True and p.get("isScrimmagePlay") is True and not p.get("isNoPlay")]
def audit_partition(drives,plays):
 by_drive=defaultdict(list);by_game=defaultdict(list);c=Counter();examples=[]
 for p in plays:
  by_drive[(str(p.get("gameId")),str(p.get("driveId")))].append(p);by_game[str(p.get("gameId"))].append(p)
 for d in drives:
  if not (d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS" and d.get("offense")):continue
  gid=str(d.get("gameId"));did=str(d.get("driveId"));rows=by_drive[(gid,did)];off=d.get("offense");snaps=_offensive_scrimmage(rows,off)
  if len(snaps)!=3 or [p.get("down") for p in snaps] != [1,2,3]:continue
  source=[str(p.get("sourcePlayType") or "").upper() for p in rows];cats=[str(p.get("eventCategory") or "").upper() for p in rows];subs=[str(p.get("eventSubtype") or "").upper() for p in rows]
  punt=any("PUNT" in x for x in source+subs);turnover=any(x=="TURNOVER" for x in cats);score=any(x=="SCORING" for x in cats) or any("TOUCHDOWN" in x for x in subs)
  if punt or turnover or score:continue
  c["residual"]+=1;last=snaps[-1]
  if last.get("down")==3:c["terminal_third_down"]+=1
  dist=last.get("distance");yards=last.get("analyticsYardsGained")
  if isinstance(dist,(int,float)) and isinstance(yards,(int,float)):
   if yards>=dist:c["terminal_structural_conversion"]+=1
   else:c["terminal_failed_to_convert"]+=1
  # Any fourth-down offensive snap/source record in the same source drive means this was not a conventional 3-and-out.
  if any(p.get("down")==4 and p.get("offense")==off for p in rows):c["fourth_down_record_same_drive"]+=1
  period=last.get("period") or last.get("quarter");clock=last.get("clock") or last.get("clockDisplayValue") or last.get("clockText")
  if period in (2,4):c["terminal_q2_q4"]+=1
  # Detect obvious terminal clock strings without assuming a single schema.
  cs=str(clock or "")
  if cs.startswith("0:") or cs.startswith("00:") or cs in {"0","0.0","00:00"}:c["near_zero_clock_text"]+=1
  # Look at canonical records after the final snap in game order when source ordering is available.
  game=by_game[gid];idxs=[i for i,p in enumerate(game) if str(p.get("driveId"))==did]
  nxt=None
  if idxs:
   for p in game[max(idxs)+1:max(idxs)+6]:
    if p.get("offense") and p.get("offense")!=off:nxt=p;break
  if nxt:c["next_opponent_possession_signal"]+=1
  else:c["no_next_opponent_signal"]+=1
  if len(examples)<60:examples.append({"season":d.get("season"),"gameId":d.get("gameId"),"driveId":d.get("driveId"),"offense":off,"defense":d.get("defense"),"terminalDistance":dist,"terminalYards":yards,"period":period,"clock":clock,"driveResult":d.get("driveResult") or d.get("result"),"sourceTypes":sorted(set(source)),"subtypes":sorted(set(subs)),"nextOpponentSignal":bool(nxt)})
 return c,examples
def merge(results):
 c=Counter();examples=[]
 for x,e in results:c.update(x);examples.extend(e[:max(0,60-len(examples))])
 return {"counts":dict(c),"examples":examples}
def concise(r):
 c=r["counts"];return "\n".join(["THREE-AND-OUT RESIDUAL FORENSICS",f"Clean 1-2-3 no-punt/score/turnover residuals: {c.get('residual',0):,}","",f"Terminal failed-to-convert by yards/distance: {c.get('terminal_failed_to_convert',0):,}",f"Terminal structural conversion: {c.get('terminal_structural_conversion',0):,}",f"Fourth-down record in same drive: {c.get('fourth_down_record_same_drive',0):,}",f"Terminal in Q2/Q4: {c.get('terminal_q2_q4',0):,}",f"Near-zero clock text: {c.get('near_zero_clock_text',0):,}",f"Next-opponent-possession signal: {c.get('next_opponent_possession_signal',0):,}",f"No next-opponent signal: {c.get('no_next_opponent_signal',0):,}","","Diagnostic only. Residuals are not promoted to three-and-outs unless possession-exit evidence is strong enough.","Use --json for representative residual possessions."])
