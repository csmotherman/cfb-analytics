"""Deterministic Dropback v1 production-candidate classifier.

Evidence classes:
- PASS_COMPLETION
- PASS_INCOMPLETE
- PASS_TD
- SACK
- exactly one explicit INTERCEPTION attempt per validated interception possession

The interception rule is possession-adjudicated because standalone explicit
INTERCEPTION source records are not reliably marked offensive/scrimmage and may
also exist outside validated interception possessions. They therefore must not
be counted globally as ordinary canonical play records.

No-play and two-point contexts are excluded. PASS_UNSPECIFIED is not promoted.
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
    # State-transition-modified interception records are valid evidence just as
    # modified completions/incompletions/sacks are retained in the candidate.
    # Only true no-play/nullified and two-point contexts are excluded.
    if p.get("hasNoPlayContext") or p.get("isNoPlay") or _two_point(p): return False
    s=str(p.get("eventSubtype") or "").upper();src=str(p.get("sourcePlayType") or p.get("playType") or "").upper()
    return s=="INTERCEPTION" or src=="INTERCEPTION"

def classify_standard_dropback(p):
    cls=evidence_class(p)
    # INTERCEPTION is intentionally excluded from global play-record counting.
    # It is counted once per validated interception possession below.
    return cls if cls in ("PASS_COMPLETION","PASS_INCOMPLETE","PASS_TD","SACK") else None

def audit_candidate(plays,drives):
    c=Counter();by_drive=defaultdict(list)
    for p in plays:
        by_drive[(str(p.get("gameId")),str(p.get("driveId")))].append(p)
        cls=classify_standard_dropback(p)
        if cls:
            c["standard_dropbacks"]+=1;c[cls.lower()]+=1
    turn_ids,outcomes,unresolved,collisions=turnover_play_ids(drives,plays)
    recovered_ids=set()
    for d in drives:
        if not (d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS"):continue
        rows=by_drive[(str(d.get("gameId")),str(d.get("driveId")))]
        if not any(id(p) in turn_ids and outcomes.get(id(p))=="INTERCEPTION" for p in rows):continue
        c["validated_interception_possessions"]+=1
        explicit=[p for p in rows if _explicit_interception_record(p)]
        if explicit:
            # Exactly one interception attempt per validated interception possession.
            # Chronology is not needed for the count; duplicates are surfaced.
            chosen=explicit[-1];recovered_ids.add(id(chosen));c["interception_attempts"]+=1
            if len(explicit)>1:c["duplicate_interception_record_possessions"]+=1
        else:
            c["validated_int_without_explicit_record"]+=1
    c["candidate_dropbacks"]=c["standard_dropbacks"]+c["interception_attempts"]
    c["turnover_anchor_unresolved"]=unresolved;c["turnover_anchor_collisions"]=collisions
    return {"counts":dict(c),"recovered_ids":recovered_ids}

def merge(results):
    c=Counter();ids=set()
    for r in results:c.update(r["counts"]);ids.update(r["recovered_ids"])
    c["candidate_dropbacks"]=c["standard_dropbacks"]+c["interception_attempts"]
    return {"counts":dict(c),"recovered_ids":ids}

def concise(r):
    c=r["counts"];db=c.get("candidate_dropbacks",0)
    checks={
      "validated_interceptions_all_have_explicit_evidence":c.get("validated_int_without_explicit_record",0)==0,
      "interception_attempts_match_validated_possessions":c.get("interception_attempts",0)==c.get("validated_interception_possessions",0),
      "sacks_match_locked_havoc_corpus":c.get("sack",0)==33368,
      "dropback_components_reconcile":db==c.get("pass_completion",0)+c.get("pass_incomplete",0)+c.get("pass_td",0)+c.get("sack",0)+c.get("interception_attempts",0),
    }
    lines=[
      f"DROPBACK v1 PRODUCTION-CANDIDATE AUDIT: {'PASS' if all(checks.values()) else 'REVIEW'}",
      f"Candidate dropbacks: {db:,}",
      f"  PASS_COMPLETION: {c.get('pass_completion',0):,}",
      f"  PASS_INCOMPLETE: {c.get('pass_incomplete',0):,}",
      f"  PASS_TD: {c.get('pass_td',0):,}",
      f"  INTERCEPTION attempts (validated possessions): {c.get('interception_attempts',0):,}",
      f"  SACK: {c.get('sack',0):,}",
      f"Validated interception possessions: {c.get('validated_interception_possessions',0):,}",
      f"Duplicate-INT-record possessions deduplicated: {c.get('duplicate_interception_record_possessions',0):,}",
      f"Validated INT possessions still without explicit INT record: {c.get('validated_int_without_explicit_record',0):,}",
      f"Candidate sack rate: {c.get('sack',0)/db:.2%}" if db else "Candidate sack rate: n/a",
      "",
      "Checks:",
    ]
    lines.extend(f"{'PASS' if ok else 'FAIL'} {name}" for name,ok in checks.items())
    lines += ["","PASS_UNSPECIFIED remains excluded. Candidate only; no propagation yet."]
    return "\n".join(lines)
