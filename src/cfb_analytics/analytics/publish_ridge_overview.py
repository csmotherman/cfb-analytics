"""Publish Michigan ridge offense/defense overview artifacts for the website."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from cfb_analytics.analytics.ridge_offense_composite import rankings as offense_rankings
from cfb_analytics.analytics.ridge_defense_composite import rankings as defense_rankings

OFF_FIELDS={"ppd":"adj_ppd","ypd":"adj_ypd","success":"adj_success","scoring":"adj_scoring"}
DEF_FIELDS={"ppd":"adj_ppd_allowed","ypd":"adj_ypd_allowed","success":"adj_success_allowed","scoring":"adj_scoring_allowed"}

def _load(path:Path):
 with path.open(encoding="utf-8") as h:return json.load(h)

def _metric_ranks(rows,fields,lower_better=False):
 out={}
 for name,field in fields.items():
  ordered=sorted(rows,key=lambda r:float(r[field]),reverse=not lower_better)
  out[name]={int(r["team_id"]):i for i,r in enumerate(ordered,1)}
 return out

def build_overview(rows,season:int,team:str="Michigan",lam:float=20.0):
 offense,_=offense_rankings(rows,season,lam);defense,_=defense_rankings(rows,season,lam)
 off=next((r for r in offense if str(r["team"]).casefold()==team.casefold()),None);deff=next((r for r in defense if str(r["team"]).casefold()==team.casefold()),None)
 if off is None or deff is None:raise ValueError(f"{team} not found for {season}")
 off_ranks=_metric_ranks(offense,OFF_FIELDS,False);def_ranks=_metric_ranks(defense,DEF_FIELDS,True)
 def block(row,fields,ranks):
  return {"rank":int(row["rank"]),"rating":float(row["rating"]),"field_size":len(offense),"metrics":{name:{"value":float(row[field]),"rank":int(ranks[name][int(row["team_id"])]),"field_size":len(offense)} for name,field in fields.items()}}
 return {"season":season,"team":team,"lambda":lam,"method":"weighted ridge least squares","weights":{"ppd":.25,"ypd":.25,"success":.25,"scoring":.25},"offense":block(off,OFF_FIELDS,off_ranks),"defense":block(deff,DEF_FIELDS,def_ranks)}

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument("--seasons",nargs="+",type=int);p.add_argument("--root",type=Path,default=Path("data/canonical"));p.add_argument("--published",type=Path,default=Path("data/published"));p.add_argument("--team",default="Michigan");p.add_argument("--lambda",dest="lam",type=float,default=20.0);a=p.parse_args(argv)
 if a.seasons:seasons=sorted(set(a.seasons))
 else:
  seasons=[]
  for d in a.root.glob("season=*"):
   try:s=int(d.name.split("=",1)[1])
   except ValueError:continue
   if (d/"team_games.json").exists():seasons.append(s)
  seasons.sort()
 for season in seasons:
  source=a.root/f"season={season}"/"team_games.json";artifact=build_overview(_load(source),season,a.team,a.lam);out=a.published/str(season)/"analytics"/"ridge-overview.json";out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(artifact,indent=2)+"\n",encoding="utf-8");print(f"{season} PUBLISHED — {out}")
 return 0
if __name__=="__main__":raise SystemExit(main())
