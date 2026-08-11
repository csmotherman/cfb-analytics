"""Turnover v1 forensics.

Diagnostic possession-level turnover study. Plays are indexed once by
(gameId, driveId), avoiding repeated full-corpus scans for every drive.
"""
from __future__ import annotations
from collections import Counter, defaultdict

VERSION="turnover-forensics-v1"
INT_SUBTYPES={"INTERCEPTION"}
FUMBLE_LOSS_SUBTYPES={"FUMBLE_RECOVERY_OPPONENT","FUMBLE_RETURN_TD"}
RETURN_SUBTYPES={"INTERCEPTION_RETURN","INTERCEPTION_RETURN_TD","FUMBLE_RECOVERY_OWN","FUMBLE_RECOVERY_OPPONENT","FUMBLE_RETURN_TD"}

def _valid_possession(d):
 return d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS" and d.get("offense") and d.get("defense")

def _key(game_id,drive_id):return (str(game_id),drive_id)

def build_play_index(plays):
 index=defaultdict(list)
 for p in plays:index[_key(p.get("gameId"),p.get("driveId"))].append(p)
 return index

def _drive_plays(drive,play_index):
 did=drive.get("sourceDriveId",drive.get("driveId"))
 return play_index.get(_key(drive.get("gameId"),did),())

def classify_drive_turnover_from_plays(ps):
 subs=[p.get("eventSubtype") for p in ps];no_play=any(p.get("hasNoPlayContext") for p in ps)
 ints=sum(s in INT_SUBTYPES for s in subs);flost=sum(s in FUMBLE_LOSS_SUBTYPES for s in subs);turn_records=sum(bool(p.get("isTurnover")) for p in ps)
 if no_play and (ints or flost):return "MODIFIED_CONTEXT_REVIEW"
 if ints and flost:return "MULTIPLE_TURNOVER_SIGNALS"
 if ints:return "INTERCEPTION"
 if flost:return "FUMBLE_LOST"
 if turn_records:return "TURNOVER_RECORD_WITHOUT_GIVEAWAY_SIGNAL"
 return "NO_EXPLICIT_TURNOVER"

def classify_drive_turnover(drive,plays_or_index):
 index=plays_or_index if isinstance(plays_or_index,dict) else build_play_index(plays_or_index)
 return classify_drive_turnover_from_plays(_drive_plays(drive,index))

def turnover_forensics(drives,plays):
 valid=[d for d in drives if _valid_possession(d)];play_index=build_play_index(plays);outcomes=Counter();raw=Counter();examples=[]
 for d in valid:
  ps=_drive_plays(d,play_index);out=classify_drive_turnover_from_plays(ps);outcomes[out]+=1
  for p in ps:
   if p.get("isTurnover"):raw[str(p.get("eventSubtype"))]+=1
  if out not in {"NO_EXPLICIT_TURNOVER","INTERCEPTION","FUMBLE_LOST"} and len(examples)<20:
   examples.append({"gameId":d.get("gameId"),"driveId":d.get("driveId"),"offense":d.get("offense"),"outcome":out,"plays":[{"playType":p.get("playType"),"eventSubtype":p.get("eventSubtype"),"playText":p.get("playText")} for p in ps if p.get("isTurnover") or p.get("hasFumbleContext") or p.get("hasInterceptionContext")]})
 giveaways=outcomes["INTERCEPTION"]+outcomes["FUMBLE_LOST"]
 return {"version":VERSION,"validated_possessions":len(valid),"classified_giveaways":giveaways,"giveaway_rate":giveaways/len(valid) if valid else None,"drive_outcomes":dict(outcomes),"turnover_records_by_subtype":dict(raw),"review_examples":examples}

def concise_turnover_forensics(r):
 lines=["TURNOVER POSSESSION FORENSICS (v1)",f"Validated possession drives: {r['validated_possessions']:,}",f"Explicit classified giveaways: {r['classified_giveaways']:,}",f"Giveaway rate: {r['giveaway_rate']:.2%}" if r['giveaway_rate'] is not None else "Giveaway rate: N/A","","Drive-level outcomes:"]
 for k,v in sorted(r['drive_outcomes'].items(),key=lambda x:-x[1]):lines.append(f"{k:.<42} {v:>8,}")
 lines.append("\nTurnover-category records (diagnostic; not giveaway counts):")
 for k,v in sorted(r['turnover_records_by_subtype'].items(),key=lambda x:-x[1]):lines.append(f"{k:.<42} {v:>8,}")
 lines += ["","Diagnostic only. No turnover metrics are propagated and no data is modified.","Use --json to inspect review examples."]
 return "\n".join(lines)
