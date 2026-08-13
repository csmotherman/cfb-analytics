"""Final denominator forensics before Basic Yardage Efficiency v1 propagation.

The remaining issue is not missing yardage. It is metric semantics:
- 74 standalone FUMBLE scrimmage records should not silently enter rush/pass splits.
- 20 TWO_POINT_PASS and 3 PASS_UNSPECIFIED records are not Dropbacks v1.
- overall Y/P should be tested both on all clean scrimmage records and on the
  classified RUSH + locked Dropbacks-v1 population.

Diagnostic only.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from cfb_analytics.analytics.basic_yardage_forensics import _clean,_family,_yards
from cfb_analytics.analytics.dropback_v1_candidate import classify_standard_dropback,_explicit_interception_text,VALID_CLASSES
from cfb_analytics.analytics.havoc import turnover_play_ids

def audit(plays,drives):
 c=Counter();by_drive=defaultdict(list)
 for p in plays:
  by_drive[(str(p.get('gameId')),str(p.get('driveId')))].append(p)
  if not _clean(p):continue
  y=_yards(p) or 0;fam=_family(p);cls=classify_standard_dropback(p)
  c['all_clean_plays']+=1;c['all_clean_yards']+=y
  if fam=='RUSH':c['rush_attempts']+=1;c['rush_yards']+=y
  if fam is None:
   c['unclassified_plays']+=1;c['unclassified_yards']+=y
   if str(p.get('eventSubtype') or '').upper()=='FUMBLE':c['standalone_fumble_records']+=1;c['standalone_fumble_yards']+=y
  if cls:
   c['standard_dropbacks']+=1;c['standard_dropback_yards']+=y
 turn_ids,outcomes,_,_=turnover_play_ids(drives,plays)
 for d in drives:
  if not (d.get('isPossessionDrive') is True and d.get('driveValidationStatus')=='PASS'):continue
  rows=by_drive[(str(d.get('gameId')),str(d.get('driveId')))]
  if not any(id(p) in turn_ids and outcomes.get(id(p))=='INTERCEPTION' for p in rows):continue
  if any(classify_standard_dropback(p) in VALID_CLASSES for p in rows):continue
  explicit=[p for p in rows if _explicit_interception_text(p)]
  if explicit:
   c['recovered_int_attempts']+=1;c['recovered_int_yards']+=_yards(explicit[-1]) or 0
 c['dropbacks']=c['standard_dropbacks']+c['recovered_int_attempts'];c['dropback_yards']=c['standard_dropback_yards']+c['recovered_int_yards']
 c['classified_scrimmage_events']=c['rush_attempts']+c['dropbacks'];c['classified_scrimmage_yards']=c['rush_yards']+c['dropback_yards']
 return {'counts':dict(c)}
def merge(rs):
 c=Counter()
 for r in rs:c.update(r['counts'])
 # derived counters were included per partition, so recompute from primitives
 c['dropbacks']=c['standard_dropbacks']+c['recovered_int_attempts'];c['dropback_yards']=c['standard_dropback_yards']+c['recovered_int_yards'];c['classified_scrimmage_events']=c['rush_attempts']+c['dropbacks'];c['classified_scrimmage_yards']=c['rush_yards']+c['dropback_yards']
 return {'counts':dict(c)}
def concise(r):
 c=r['counts'];ap=c['all_clean_plays'];cp=c['classified_scrimmage_events'];lines=[
 'BASIC YARDAGE FINAL DENOMINATOR FORENSICS',
 f"All clean scrimmage records: {ap:,}",f"All clean scrimmage yards: {c['all_clean_yards']:,.0f}",f"Raw record yards/play: {c['all_clean_yards']/ap:.3f}",
 '',f"Rush attempts: {c['rush_attempts']:,}",f"Rush yards: {c['rush_yards']:,.0f}",f"Rush yards/attempt: {c['rush_yards']/c['rush_attempts']:.3f}",
 f"Locked Dropbacks v1: {c['dropbacks']:,}",f"Dropback yards: {c['dropback_yards']:,.0f}",f"Net pass yards/dropback: {c['dropback_yards']/c['dropbacks']:.3f}",
 '',f"Classified RUSH + Dropback events: {cp:,}",f"Classified RUSH + Dropback yards: {c['classified_scrimmage_yards']:,.0f}",f"Classified yards/play: {c['classified_scrimmage_yards']/cp:.3f}",
 '',f"Standalone unclassified records: {c['unclassified_plays']:,}",f"Standalone unclassified yards: {c['unclassified_yards']:,.0f}",f"  FUMBLE records: {c['standalone_fumble_records']:,}",f"  FUMBLE yards: {c['standalone_fumble_yards']:,.0f}",
 '',f"Raw-vs-classified play difference: {ap-cp:,}",f"Raw-vs-classified yard difference: {c['all_clean_yards']-c['classified_scrimmage_yards']:,.0f}",
 '',"Diagnostic only. If the difference is entirely source artifact/residual records, Basic Yardage v1 should use classified RUSH + locked Dropbacks for Y/P rather than raw canonical record count."
 ];return '\n'.join(lines)
