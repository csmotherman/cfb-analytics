"""CLI for raw CFBD acquisition, auditing, census, anomalies, and sequencing."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from cfb_analytics.raw.acquire import acquire_season, acquire_week, calendar_partitions, get_calendar
from cfb_analytics.raw.audit import audit_partition, audit_season, audit_corpus
from cfb_analytics.raw.census import raw_census, concise_census
from cfb_analytics.raw.anomalies import anomaly_report, concise_anomalies, RULES
from cfb_analytics.raw.sequence import sequence_audit, concise_sequence, chronology_audit, concise_chronology
from cfb_analytics.sources.cfbd.client import CfbdClient

DEFAULT_ROOT=Path("data/raw")
SEASONS=(2014,2015,2016,2017,2018,2019,2021,2022,2023,2024,2025)

def parser():
    p=argparse.ArgumentParser(prog="cfb-raw"); p.add_argument("--root",type=Path,default=DEFAULT_ROOT); sub=p.add_subparsers(dest="command",required=True)
    cal=sub.add_parser("calendar"); cal.add_argument("--season",type=int,required=True)
    week=sub.add_parser("week"); week.add_argument("--season",type=int,required=True); week.add_argument("--season-type",required=True); week.add_argument("--week",type=int,required=True); week.add_argument("--refresh",action="store_true")
    audit=sub.add_parser("audit"); audit.add_argument("--season",type=int,required=True); audit.add_argument("--season-type",required=True); audit.add_argument("--week",type=int,required=True)
    sa=sub.add_parser("audit-season"); sa.add_argument("--season",type=int,required=True); sa.add_argument("--json",action="store_true",dest="as_json")
    ca=sub.add_parser("audit-corpus"); ca.add_argument("--json",action="store_true",dest="as_json")
    census=sub.add_parser("census"); census.add_argument("--season",type=int); census.add_argument("--json",action="store_true",dest="as_json"); census.add_argument("--top",type=int,default=25)
    anomalies=sub.add_parser("anomalies"); anomalies.add_argument("--season",type=int); anomalies.add_argument("--rule",choices=RULES); anomalies.add_argument("--examples",type=int,default=5); anomalies.add_argument("--json",action="store_true",dest="as_json")
    seq=sub.add_parser("sequence-audit"); seq.add_argument("--season",type=int); seq.add_argument("--examples",type=int,default=10); seq.add_argument("--json",action="store_true",dest="as_json")
    chrono=sub.add_parser("chronology-audit"); chrono.add_argument("--season",type=int); chrono.add_argument("--examples",type=int,default=10); chrono.add_argument("--json",action="store_true",dest="as_json")
    season=sub.add_parser("season"); season.add_argument("--season",type=int,required=True); season.add_argument("--refresh",action="store_true")
    backfill=sub.add_parser("backfill"); backfill.add_argument("--refresh",action="store_true")
    return p

def _print_season(r):
    print(f"{r['season']} RAW SEASON AUDIT: {r['status']}"); print(f"Partitions: {r['partition_count']}"); print(f"Games: {r['totals'].get('games',0):,} | Drives: {r['totals'].get('drives',0):,} | Plays: {r['totals'].get('plays',0):,}")
    for k,v in r['checks'].items(): print(f"{'PASS' if v else 'FAIL'}  {k}")
    print("Cross-partition duplicates:",r['cross_partition_duplicates']); print("Schema variants:",r['schema_variant_counts'])
    problems=[p for p in r['partitions'] if p['status']!='PASS']; print(f"Partition problems: {len(problems)}")
    for p in problems: print(f"  {p['season_type']} W{p['week']:02d}: {', '.join(p['failed_checks'])}")

def _print_corpus(r):
    print(f"RAW CORPUS AUDIT: {r['status']}")
    for s in r['seasons']:
        t=s['totals']; print(f"{s['season']}  {s['status']:<7} partitions={s['partition_count']:>2}  games={t.get('games',0):>5,}  drives={t.get('drives',0):>6,}  plays={t.get('plays',0):>7,}")
    print(f"TOTAL   games={r['totals'].get('games',0):,} drives={r['totals'].get('drives',0):,} plays={r['totals'].get('plays',0):,}")
    print("Cross-season duplicates:",r['cross_season_duplicates'])
    for k,v in r['checks'].items(): print(f"{'PASS' if v else 'FAIL'}  {k}")

def main():
    args=parser().parse_args()
    if args.command=="audit": print(json.dumps(audit_partition(args.root,args.season,args.season_type,args.week),indent=2)); return
    if args.command=="audit-season":
        r=audit_season(args.root,args.season); print(json.dumps(r,indent=2) if args.as_json else "",end="" if args.as_json else ""); _print_season(r) if not args.as_json else None; return
    if args.command=="audit-corpus":
        r=audit_corpus(args.root); print(json.dumps(r,indent=2) if args.as_json else "",end="" if args.as_json else ""); _print_corpus(r) if not args.as_json else None; return
    if args.command=="census":
        seasons=(args.season,) if args.season else SEASONS; r=raw_census(args.root,seasons=seasons); print(json.dumps(r,indent=2) if args.as_json else concise_census(r,args.top)); return
    if args.command=="anomalies":
        seasons=(args.season,) if args.season else SEASONS; r=anomaly_report(args.root,seasons,args.rule,args.examples)
        print(json.dumps(r,indent=2) if args.as_json or args.rule else concise_anomalies(r)); return
    if args.command=="sequence-audit":
        seasons=(args.season,) if args.season else SEASONS; r=sequence_audit(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_sequence(r)); return
    if args.command=="chronology-audit":
        seasons=(args.season,) if args.season else SEASONS; r=chronology_audit(args.root,seasons,args.examples); print(json.dumps(r,indent=2) if args.as_json else concise_chronology(r)); return
    with CfbdClient() as client:
        if args.command=="calendar": print(json.dumps({"season":args.season,"partitions":calendar_partitions(get_calendar(client,args.season))},indent=2)); return
        if args.command=="week": manifests=acquire_week(client,args.root,args.season,args.season_type,args.week,refresh=args.refresh)
        elif args.command=="season": manifests=acquire_season(client,args.root,args.season,refresh=args.refresh)
        else:
            manifests=[]
            for season in SEASONS: manifests.extend(acquire_season(client,args.root,season,refresh=args.refresh))
        for m in manifests: print(f"{m['season']} {m['season_type']} W{m['week']:02d} {m['entity']}: {m['record_count']}")

if __name__=="__main__": main()
