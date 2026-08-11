from __future__ import annotations
import argparse,json
from pathlib import Path
from cfb_analytics.raw.calendar import available_seasons
from cfb_analytics.analytics.touchdown_points import touchdown_points_audit,concise_touchdown_points_audit

def main():
 p=argparse.ArgumentParser();p.add_argument("command",choices=["audit"]);p.add_argument("--raw-root",type=Path,default=Path("data/raw/cfbd"));p.add_argument("--processed-root",type=Path,default=Path("data/processed"));p.add_argument("--json",action="store_true");p.add_argument("--examples",type=int,default=12);a=p.parse_args();seasons=available_seasons(a.raw_root);r=touchdown_points_audit(a.raw_root,a.processed_root,seasons,a.examples);print(json.dumps(r,indent=2) if a.json else concise_touchdown_points_audit(r))
if __name__=="__main__":main()
