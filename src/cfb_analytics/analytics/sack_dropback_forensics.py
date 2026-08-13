"""Diagnostic Sack / Dropback v1 denominator forensics.

The sack numerator is already validated by Havoc v1. This audit investigates a
production-safe pass-attempt/dropback denominator before any sack-rate fields
are created. No data is modified or propagated.
"""
from __future__ import annotations
from collections import Counter


def _clean(p):
    return (bool(p.get("isScrimmagePlay")) or p.get("eventCategory")=="SCRIMMAGE") and not bool(p.get("hasNoPlayContext") or p.get("isModifiedContext") or p.get("isNoPlay"))

def _text(p):
    return " ".join(str(p.get(k) or "") for k in ("eventCategory","eventSubtype","sourcePlayType","playType")).upper()

def is_sack(p):
    return _clean(p) and (p.get("eventSubtype")=="SACK" or str(p.get("sourcePlayType") or p.get("playType") or "").lower()=="sack")

def audit(plays):
    c=Counter()
    examples=[]
    for p in plays:
        if not _clean(p):continue
        c["clean_scrimmage"]+=1
        text=_text(p)
        sack=is_sack(p)
        if sack:c["sacks"]+=1
        # Existing canonical pass-family signals are inspected rather than assumed.
        pass_flag=p.get("playFamily")=="PASS" or p.get("isPassPlay") is True or p.get("isPass") is True
        pass_text=any(x in text for x in ("PASS","INTERCEPTION","SACK"))
        if pass_flag:c["canonical_pass_flag"]+=1
        if pass_text:c["text_pass_signal"]+=1
        if pass_flag or pass_text:c["broad_dropback_candidate"]+=1
        if sack and not pass_flag:c["sack_missing_canonical_pass_flag"]+=1
        if pass_flag and not pass_text:c["canonical_pass_without_text_signal"]+=1
        if pass_text and not pass_flag:c["text_signal_without_canonical_pass"]+=1
        if (sack and not pass_flag) or (pass_flag != pass_text):
            if len(examples)<40:
                examples.append({k:p.get(k) for k in ("season","gameId","driveId","id","playNumber","sourcePlayType","playType","eventCategory","eventSubtype","playFamily","isPassPlay","isPass","isOffensivePlay","analyticsYardsGained","down","distance")})
    return {"counts":dict(c),"examples":examples}

def merge(results):
    c=Counter();examples=[]
    for r in results:
        c.update(r["counts"]);examples.extend(r["examples"][:max(0,40-len(examples))])
    return {"counts":dict(c),"examples":examples}

def concise(r):
    c=r["counts"]
    broad=c.get("broad_dropback_candidate",0)
    return "\n".join([
        "SACK / DROPBACK DENOMINATOR FORENSICS (v1)",
        f"Clean scrimmage plays: {c.get('clean_scrimmage',0):,}",
        f"Validated sack candidates: {c.get('sacks',0):,}",
        f"Canonical pass-family flagged plays: {c.get('canonical_pass_flag',0):,}",
        f"Text-derived pass/sack/interception signal: {c.get('text_pass_signal',0):,}",
        f"Broad dropback candidate union: {broad:,}",
        f"Candidate sack rate: {c.get('sacks',0)/broad:.2%}" if broad else "Candidate sack rate: n/a",
        "",
        f"Sacks missing canonical pass flag: {c.get('sack_missing_canonical_pass_flag',0):,}",
        f"Canonical pass flag without text signal: {c.get('canonical_pass_without_text_signal',0):,}",
        f"Text signal without canonical pass flag: {c.get('text_signal_without_canonical_pass',0):,}",
        "",
        "Diagnostic only. The denominator is not locked until canonical pass-family semantics and disagreement populations are understood.",
        "Use --json for representative disagreement examples."
    ])
