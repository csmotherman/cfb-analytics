"""Deterministic Dropback v1 production-candidate classifier.

Evidence classes:
- PASS_COMPLETION
- PASS_INCOMPLETE
- PASS_TD
- SACK
- explicit INTERCEPTION event records, including the source pattern where the
  interception record is not marked offensive/scrimmage.

No-play and two-point contexts are excluded. PASS_UNSPECIFIED is not promoted.
Explicit interception records are deduplicated per validated interception
possession so duplicate source records cannot create multiple attempts.

Candidate only; no propagation here.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from cfb_analytics.analytics.dropback_taxonomy_forensics import _text,evidence_class
from cfb_analytics.analytics.havoc import turnover_play_ids

DROPBACK_VERSION="dropback-v1-candidate"

def _two_point(p):
    t=_text(p)
    return "TWO_POINT" in t or "TWO POINT" in t or "2PT" in t

def _explicit_interception_record(p):
    if p.get("hasNoPlayContext") or p.get("isNoPlay") or p.get("isModifiedContext") or _two_point(p): return False
    s=str(p.get("eventSubtype") or "").upper();src=str(p.get("sourcePlayType") or p.get("playType") or "").upper()
    return s=="INTERCEPTION" or src=="INTERCEPTION"

def classify_standard_dropback(p):
    cls=evidence_class(p)
    return cls if cls in ("PASS_COMPLETION","PASS_INCOMPLETE","PASS_TD","SACK","INTERCEPTION") else None

def audit_candidate(plays,drives):
    c=Counter();by_drive=defaultdict(list)
    for p in plays:
        by_drive[(str(p.get("gameId")),str(p.get("driveId")))].append(p)
        cls=classify_standard_dropback(p)
        if cls:
            c["standard_dropbacks"]+=1;c[cls.lower()]+=1
    turn_ids,outcomes,unresolved,collisions=turnover_play_ids(drives,plays)
    # Recover only validated interception possessions that have explicit source
    # interception records not already counted by the standard taxonomy.
    recovered_ids=set()
    for d in drives:
        if not (d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS"):continue
        rows=by_drive[(str(d.get("gameId")),str(d.get("driveId")))]
        if not any(id(p) in turn_ids and outcomes.get(id(p))=="INTERCEPTION" for p in rows):continue
        already=[p for p in rows if classify_standard_dropback(p)=="INTERCEPTION"]
        if already:continue
        explicit=[p for p in rows if _explicit_interception_record(p)]
        if explicit:
            # one recovered interception attempt per validated interception possession
            chosen=explicit[-1];recovered_ids.add(id(chosen));c["recovered_interception_attempts"]+=1
            if len(explicit)>1:c["duplicate_interception_record_possessions"]+=1
        else:c["validated_int_without_explicit_record"]+=1
    c["candidate_dropbacks"]=c["standard_dropbacks"]+c["recovered_interception_attempts"]
    c["candidate_interceptions"]=c["interception"]+c["recovered_interception_attempts"]
    c["turnover_anchor_unresolved"]=unresolved;c["turnover_anchor_collisions"]=collisions
    return {"counts":dict(c),"recovered_ids":recovered_ids}

def merge(results):
    c=Counter();ids=set()
    for r in results:c.update(r["counts"]);ids.update(r["recovered_ids"])
    c["candidate_dropbacks"]=c["standard_dropbacks"]+c["recovered_interception_attempts"]
    c["candidate_interceptions"]=c["interception"]+c["recovered_interception_attempts"]
    return {"counts":dict(c),"recovered_ids":ids}

def concise(r):
    c=r["counts"];db=c.get("candidate_dropbacks",0)
    return "\n".join([
      "DROPBACK v1 PRODUCTION-CANDIDATE AUDIT",
      f"Candidate dropbacks: {db:,}",
      f"  PASS_COMPLETION: {c.get('pass_completion',0):,}",
      f"  PASS_INCOMPLETE: {c.get('pass_incomplete',0):,}",
      f"  PASS_TD: {c.get('pass_td',0):,}",
      f"  SACK: {c.get('sack',0):,}",
      f"  explicit INTERCEPTION already canonical: {c.get('interception',0):,}",
      f"  recovered INT attempts from non-offensive source records: {c.get('recovered_interception_attempts',0):,}",
      f"  total interception attempts: {c.get('candidate_interceptions',0):,}",
      f"Duplicate-INT-record possessions deduplicated: {c.get('duplicate_interception_record_possessions',0):,}",
      f"Validated INT possessions still without explicit INT record: {c.get('validated_int_without_explicit_record',0):,}",
      f"Candidate sack rate: {c.get('sack',0)/db:.2%}" if db else "Candidate sack rate: n/a",
      "",
      "PASS_UNSPECIFIED remains excluded. Candidate only; no propagation yet."
    ])
