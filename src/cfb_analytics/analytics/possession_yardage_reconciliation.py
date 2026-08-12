"""Corpus reconciliation for offensive play yards per validated possession.

This deliberately measures summed canonical offensive-play analytics yardage,
not physical start-to-end field advancement. It verifies that validated-drive
analyticsYardsGained equals the canonical offensive-play sum and that offense
and defense mirrors reconcile before production propagation.
"""
from __future__ import annotations
from collections import Counter,defaultdict

def audit_partition(drives,plays):
 by_drive=defaultdict(list);c=Counter();drive_yards=0.0;play_yards=0.0
 for p in plays:by_drive[(str(p.get("gameId")),str(p.get("driveId")))].append(p)
 for d in drives:
  if not (d.get("isPossessionDrive") is True and d.get("driveValidationStatus")=="PASS" and d.get("offense")):continue
  c["possessions"]+=1;dy=d.get("analyticsYardsGained")
  if not isinstance(dy,(int,float)) or isinstance(dy,bool):c["invalid_drive_yards"]+=1;continue
  rows=by_drive[(str(d.get("gameId")),str(d.get("driveId")))];off=d.get("offense");py=sum((p.get("analyticsYardsGained") or 0) for p in rows if p.get("offense")==off and isinstance(p.get("analyticsYardsGained"),(int,float)) and not isinstance(p.get("analyticsYardsGained"),bool))
  drive_yards+=dy;play_yards+=py
  if abs(dy-py)<=1e-9:c["drive_play_exact"]+=1
  else:c["drive_play_mismatch"]+=1
  if d.get("defense"):c["defense_mirror_possessions"]+=1
 return c,drive_yards,play_yards
def merge(results):
 c=Counter();dy=py=0.0
 for x,a,b in results:c.update(x);dy+=a;py+=b
 p=c["possessions"]
 return {"counts":dict(c),"drive_yards":dy,"canonical_play_yards":py,"yards_per_possession":dy/p if p else None,"yards_difference":dy-py}
def concise(r):
 c=r["counts"];checks={"all_possessions_have_drive_yards":c.get("invalid_drive_yards",0)==0,"every_drive_matches_canonical_play_sum":c.get("drive_play_mismatch",0)==0 and c.get("drive_play_exact",0)==c.get("possessions",0),"corpus_yards_reconcile":abs(r["yards_difference"])<=1e-9,"all_possessions_have_defense_mirror":c.get("defense_mirror_possessions",0)==c.get("possessions",0)}
 lines=[f"POSSESSION YARDAGE RECONCILIATION: {'PASS' if all(checks.values()) else 'REVIEW'}",f"Validated possessions: {c.get('possessions',0):,}",f"Drive-level summed offensive yards: {r['drive_yards']:,.0f}",f"Canonical offensive-play yards: {r['canonical_play_yards']:,.0f}",f"Difference: {r['yards_difference']:,.0f}",f"Yards per possession: {r['yards_per_possession']:.3f}" if r['yards_per_possession'] is not None else "Yards per possession: N/A",f"Exact drive-to-play reconciliations: {c.get('drive_play_exact',0):,}",f"Drive-to-play mismatches: {c.get('drive_play_mismatch',0):,}","","Checks:"]+[f"{'PASS' if v else 'FAIL'} {k}" for k,v in checks.items()]+["","Definition: summed canonical offensive-play analytics yardage per validated possession; NOT net physical field-position advancement."]
 return "\n".join(lines)
