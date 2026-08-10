"""CLI for raw acquisition, audits, and canonical play processing."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from cfb_analytics.raw.acquire import acquire_season, acquire_week, calendar_partitions, get_calendar
from cfb_analytics.raw.audit import audit_partition, audit_season, audit_corpus, discover_partitions
from cfb_analytics.raw.census import raw_census, concise_census
from cfb_analytics.raw.anomalies import anomaly_report, concise_anomalies, RULES
from cfb_analytics.raw.sequence import sequence_audit, concise_sequence, chronology_audit, concise_chronology, chronology_exceptions, concise_exceptions
from cfb_analytics.raw.transitions import transition_audit, concise_transitions
from cfb_analytics.canonical.audit import play_type_coverage, concise_play_type_coverage, canonical_play_audit, concise_canonical_play_audit
from cfb_analytics.canonical.materialize import materialize_corpus, verify_canonical_partition
from cfb_analytics.canonical.transitions import canonical_transition_audit, concise_canonical_transitions
from cfb_analytics.canonical.forensics import transition_forensics, concise_forensics
from cfb_analytics.canonical.failure_classification import failure_classification_audit, concise_failure_classification
from cfb_analytics.canonical.ambiguous import ambiguous_state_audit, concise_ambiguous_state
from cfb_analytics.canonical.counterfactual import counterfactual_repair_audit, concise_counterfactual
from cfb_analytics.canonical.play_text_census import play_text_census, concise_play_text_census
from cfb_analytics.canonical.play_text_forensics import play_text_forensics, concise_play_text_forensics
from cfb_analytics.canonical.play_text_normalization_audit import play_text_normalization_audit, concise_play_text_normalization_audit
from cfb_analytics.sources.cfbd.client import CfbdClient
DEFAULT_ROOT=Path("data/raw"); DEFAULT_PROCESSED_ROOT=Path("data/processed")
SEASONS=(2014,2015,2016,2017,2018,2019,2021,2022,2023,2024,2025)

def parser():
 p=argparse.ArgumentParser(prog="cfb-raw"); p.add_argument("--root",type=Path,default=DEFAULT_ROOT); p.add_argument("--processed-root",type=Path,default=DEFAULT_PROCESSED_ROOT); sub=p.add_subparsers(dest="command",required=True)
 cal=sub.add_parser("calendar"); cal.add_argument("--season",type=int,required=True)
 week=sub.add_parser("week"); week.add_argument("--season",type=int,required=True); week.add_argument("--season-type",required=True); week.add_argument("--week",type=int,required=True); week.add_argument("--refresh",action="store_true")
 audit=sub.add_parser("audit"); audit.add_argument("--season",type=int,required=True); audit.add_argument("--season-type",required=True); audit.add_argument("--week",type=int,required=True)
 sa=sub.add_parser("audit-season"); sa.add_argument("--season",type=int,required=True); sa.add_argument("--json",action="store_true",dest="as_json")
 ca=sub.add_parser("audit-corpus"); ca.add_argument("--json",action="store_true",dest="as_json")
 census=sub.add_parser("census"); census.add_argument("--season",type=int); census.add_argument("--json",action="store_true",dest="as_json"); census.add_argument("--top",type=int,default=25)
 anomalies=sub.add_parser("anomalies"); anomalies.add_argument("--season",type=int); anomalies.add_argument("--rule",choices=RULES); anomalies.add_argument("--examples",type=int,default=5); anomalies.add_argument("--json",action="store_true",dest="as_json")
 seq=sub.add_parser("sequence-audit"); seq.add_argument("--season",type=int); seq.add_argument("--examples",type=int,default=10); seq.add_argument("--json",action="store_true",dest="as_json")
 chrono=sub.add_parser("chronology-audit"); chrono.add_argument("--season",type=int); chrono.add_argument("--examples",type=int,default=10); chrono.add_argument("--json",action="store_true",dest="as_json")
 exc=sub.add_parser("chronology-exceptions"); exc.add_argument("--season",type=int); exc.add_argument("--examples",type=int,default=10); exc.add_argument("--json",action="store_true",dest="as_json")
 trans=sub.add_parser("transition-audit"); trans.add_argument("--season",type=int); trans.add_argument("--examples",type=int,default=10); trans.add_argument("--json",action="store_true",dest="as_json")
 cov=sub.add_parser("canonical-play-types"); cov.add_argument("--season",type=int); cov.add_argument("--json",action="store_true",dest="as_json")
 cpa=sub.add_parser("canonical-play-audit"); cpa.add_argument("--season",type=int); cpa.add_argument("--examples",type=int,default=5); cpa.add_argument("--json",action="store_true",dest="as_json")
 mat=sub.add_parser("canonical-plays"); mat.add_argument("--season",type=int); mat.add_argument("--refresh",action="store_true")
 ver=sub.add_parser("verify-canonical-plays"); ver.add_argument("--season",type=int)
 ct=sub.add_parser("canonical-transition-audit"); ct.add_argument("--season",type=int); ct.add_argument("--examples",type=int,default=10); ct.add_argument("--json",action="store_true",dest="as_json")
 cf=sub.add_parser("canonical-transition-forensics"); cf.add_argument("--season",type=int); cf.add_argument("--examples",type=int,default=12); cf.add_argument("--window",type=int,default=3); cf.add_argument("--json",action="store_true",dest="as_json")
 fc=sub.add_parser("canonical-failure-classification"); fc.add_argument("--season",type=int); fc.add_argument("--examples",type=int,default=3); fc.add_argument("--json",action="store_true",dest="as_json")
 amb=sub.add_parser("ambiguous-state-audit"); amb.add_argument("--season",type=int); amb.add_argument("--examples",type=int,default=3); amb.add_argument("--json",action="store_true",dest="as_json")
 ctr=sub.add_parser("counterfactual-repair-audit"); ctr.add_argument("--season",type=int); ctr.add_argument("--examples",type=int,default=3); ctr.add_argument("--json",action="store_true",dest="as_json")
 pt=sub.add_parser("play-text-census"); pt.add_argument("--season",type=int); pt.add_argument("--top",type=int,default=8); pt.add_argument("--examples",type=int,default=3); pt.add_argument("--json",action="store_true",dest="as_json")
 pf=sub.add_parser("play-text-forensics"); pf.add_argument("--season",type=int); pf.add_argument("--examples",type=int,default=3); pf.add_argument("--json",action="store_true",dest="as_json")
 pn=sub.add_parser("play-text-normalization-audit"); pn.add_argument("--season",type=int); pn.add_argument("--examples",type=int,default=3); pn.add_argument("--json",action="store_true",dest="as_json")
 season=sub.add_parser("season"); season.add_argument("--season",type=int,required=True); season.add_argument("--refresh",action="store_true")
 backfill=sub.add_parser("backfill"); backfill.add_argument("--refresh",action="store_true")
 return p

def main():
 args=parser().parse_args(); seasons=(getattr(args,"season",None),) if getattr(args,"season",None) else SEASONS
 if args.command=="audit": print(json.dumps(audit_partition(args.root,args.season,args.season_type,args.week),indent=2)); return
 if args.command=="audit-season":
  r=audit_season(args.root,args.season); print(json.dumps(r,indent=2) if args.as_json else f"{r['season']} RAW SEASON AUDIT: {r['status']}\nPartitions: {r['partition_count']}\nTotals: {r['totals']}\nChecks: {r['checks']}"); return
 if args.command=="audit-corpus":
  r=audit_corpus(args.root); print(json.dumps(r,indent=2) if args.as_json else "\n".join([f"RAW CORPUS AUDIT: {r['status']}"]+[f"{s['season']} {s['status']} {s['totals']}" for s in r['seasons']])); return
 if args.command=="census": r=raw_census(args.root,seasons=seasons); print(json.dumps(r,indent=2) if args.as_json else concise_census(r,args.top)); return
 if args.command=="anomalies": r=anomaly_report(args.root,seasons,args.rule,args.examples); print(json.dumps(r,indent=2) if args.as_json or args.rule else concise_anomalies(r)); return
 if args.command=="sequence-audit": r=sequence_audit(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_sequence(r)); return
 if args.command=="chronology-audit": r=chronology_audit(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_chronology(r)); return
 if args.command=="chronology-exceptions": r=chronology_exceptions(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_exceptions(r)); return
 if args.command=="transition-audit": r=transition_audit(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_transitions(r)); return
 if args.command=="canonical-play-types": r=play_type_coverage(args.root,seasons); print(json.dumps(r,indent=2) if args.as_json else concise_play_type_coverage(r)); return
 if args.command=="canonical-play-audit": r=canonical_play_audit(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_canonical_play_audit(r)); return
 if args.command=="canonical-plays":
  results=materialize_corpus(args.root,args.processed_root,seasons,refresh=args.refresh); written=sum(x['status']=='WRITTEN' for x in results); reused=sum(x['status']=='REUSED' for x in results); records=sum(x['record_count'] for x in results)
  print(f"CANONICAL PLAYS MATERIALIZATION: PASS\nPartitions: {len(results)}\nWritten: {written}\nReused: {reused}\nRecords: {records:,}\nOutput: {args.processed_root / 'canonical'}"); return
 if args.command=="verify-canonical-plays":
  results=[]
  for season in seasons:
   for st,wk in discover_partitions(args.root,season): results.append(verify_canonical_partition(args.root,args.processed_root,season,st,wk))
  failed=[r for r in results if r['status']!='PASS']; print(f"CANONICAL PLAYS VERIFICATION: {'PASS' if not failed else 'REVIEW'}\nPartitions: {len(results)}\nPassed: {len(results)-len(failed)}\nFailed: {len(failed)}")
  for r in failed[:20]: print(f"  {r['season']} {r['season_type']} W{r['week']:02d}: "+", ".join(k for k,v in r['checks'].items() if not v))
  return
 if args.command=="canonical-transition-audit": r=canonical_transition_audit(args.root,args.processed_root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_canonical_transitions(r)); return
 if args.command=="canonical-transition-forensics": r=transition_forensics(args.root,args.processed_root,seasons,args.examples,args.window); print(json.dumps(r,indent=2) if args.as_json else concise_forensics(r)); return
 if args.command=="canonical-failure-classification": r=failure_classification_audit(args.root,args.processed_root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_failure_classification(r)); return
 if args.command=="ambiguous-state-audit": r=ambiguous_state_audit(args.root,args.processed_root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_ambiguous_state(r)); return
 if args.command=="counterfactual-repair-audit": r=counterfactual_repair_audit(args.root,args.processed_root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_counterfactual(r)); return
 if args.command=="play-text-census": r=play_text_census(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_play_text_census(r,args.top)); return
 if args.command=="play-text-forensics": r=play_text_forensics(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_play_text_forensics(r)); return
 if args.command=="play-text-normalization-audit": r=play_text_normalization_audit(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_play_text_normalization_audit(r)); return
 with CfbdClient() as client:
  if args.command=="calendar": print(json.dumps({"season":args.season,"partitions":calendar_partitions(get_calendar(client,args.season))},indent=2)); return
  if args.command=="week": manifests=acquire_week(client,args.root,args.season,args.season_type,args.week,refresh=args.refresh)
  elif args.command=="season": manifests=acquire_season(client,args.root,args.season,refresh=args.refresh)
  else:
   manifests=[]
   for season in SEASONS: manifests.extend(acquire_season(client,args.root,season,refresh=args.refresh))
  for m in manifests: print(f"{m['season']} {m['season_type']} W{m['week']:02d} {m['entity']}: {m['record_count']}")
if __name__=="__main__": main()
