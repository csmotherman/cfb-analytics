from pathlib import Path
import math

from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES,SRS_FEATURES,eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS,TEST_SEASONS,_solve
from cfb_analytics.derived.sandbox_pregame import SYSTEMS

BASE=tuple(ITERATIVE_FEATURES)+tuple(SRS_FEATURES)
SYSTEM_FEATURES={s:(f"home_{s}_OffenseEdge",f"home_{s}_DefenseEdge") for s in SYSTEMS}
ALL_SYSTEMS=tuple(k for s in SYSTEMS for k in SYSTEM_FEATURES[s])
FULL=BASE+ALL_SYSTEMS
FULL_INDEX={k:i for i,k in enumerate(FULL)}


def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))
def eligible(row,min_games):return eligible_iterative_row(row,min_games) and all(finite(row.get(k)) for k in FULL)
def home_only(rows):return sum(r.get("target_homeWin")==1 for r in rows)/len(rows) if rows else 0.0


def load_all():
 pr=Path("data/processed");data={}
 print("Loading saved model feature store only; no football metrics will be recomputed.")
 for season in DEFAULT_SEASONS:
  rows=load_saved_feature_store(pr,season);data[season]=rows
  print(f"LOAD {season}: feature_store=REUSED rows={len(rows):,}")
 return data


def prepare_stats(rows):
 means=[];scales=[]
 for k in FULL:
  vals=[float(r[k]) for r in rows];m=sum(vals)/len(vals);v=sum((x-m)**2 for x in vals)/len(vals)
  means.append(m);scales.append(math.sqrt(v) or 1.0)
 p=len(FULL)+1;xtx=[[0.0]*p for _ in range(p)];xty=[0.0]*p
 for r in rows:
  x=[1.0]+[(float(r[k])-means[i])/scales[i] for i,k in enumerate(FULL)];y=float(r["target_margin"])
  for i,xi in enumerate(x):
   xty[i]+=xi*y
   for j in range(i,p):xtx[i][j]+=xi*x[j]
 for i in range(p):
  for j in range(i):xtx[i][j]=xtx[j][i]
 return {"means":means,"scales":scales,"xtx":xtx,"xty":xty,"train_games":len(rows)}


def fit_subset(stats,features,ridge=1e-6):
 idx=[0]+[FULL_INDEX[k]+1 for k in features]
 a=[[stats["xtx"][i][j] for j in idx] for i in idx];b=[stats["xty"][i] for i in idx]
 for i in range(1,len(a)):a[i][i]+=ridge
 w=_solve(a,b)
 if w is None:raise ValueError("OLS design matrix is singular")
 return {"features":tuple(features),"weights":w,"means":stats["means"],"scales":stats["scales"],"train_games":stats["train_games"]}


def score(model,rows):
 ae=[];se=[];correct=0
 for r in rows:
  pred=model["weights"][0]
  for j,k in enumerate(model["features"],start=1):
   i=FULL_INDEX[k];pred+=model["weights"][j]*(float(r[k])-model["means"][i])/model["scales"][i]
  y=float(r["target_margin"]);ae.append(abs(pred-y));se.append((pred-y)**2);correct+=int((pred>0)==bool(r["target_homeWin"]))
 n=len(rows)
 return {"train_games":model["train_games"],"test_games":n,"margin_mae":sum(ae)/n,"margin_rmse":math.sqrt(sum(se)/n),"winner_accuracy":correct/n}


def main():
 data=load_all();models={"BASE_ITERATIVE_SRS":BASE,"SYSTEMS_ONLY":ALL_SYSTEMS}
 for s in SYSTEMS:models[f"BASE_PLUS_{s}"]=BASE+SYSTEM_FEATURES[s]
 models["BASE_PLUS_ALL_SYSTEMS"]=FULL
 print("CFB SANDBOX SYSTEM ABLATION v2 FAST MARGIN")
 print("Baseline: ITERATIVE + SRS")
 print("Winner metric: sign of predicted point margin")
 print("Common eligible sample across every model: YES")
 print(f"Features: base={len(BASE)} systems={len(ALL_SYSTEMS)} full={len(FULL)}")
 for min_games in (3,4):
  elig={s:[r for r in data[s] if eligible(r,min_games)] for s in DEFAULT_SEASONS}
  print(f"\nMINIMUM PRIOR GAMES PER TEAM: {min_games}")
  for test_season in TEST_SEASONS:
   train=[r for s in DEFAULT_SEASONS if s<test_season for r in elig[s]];test=elig[test_season]
   print(f"\nTEST {test_season}")
   print(f"COMMON SAMPLE: train={len(train):,} test={len(test):,}")
   print(f"HOME-ONLY WINNER BASELINE: {home_only(test):.2%}")
   stats=prepare_stats(train)
   scored={name:score(fit_subset(stats,features),test) for name,features in models.items()};base=scored["BASE_ITERATIVE_SRS"]
   for name,x in scored.items():print(f"{name}: n={x['test_games']:,} MAE={x['margin_mae']:.3f} RMSE={x['margin_rmse']:.3f} WinnerFromMargin={x['winner_accuracy']:.2%}")
   print("ADDITIONS VS BASE:")
   for s in SYSTEMS:
    x=scored[f"BASE_PLUS_{s}"];print(f"  {s}: MAE {x['margin_mae']-base['margin_mae']:+.3f}, RMSE {x['margin_rmse']-base['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-base['winner_accuracy'])*100:+.2f} pp")
   full=scored["BASE_PLUS_ALL_SYSTEMS"];print(f"  ALL: MAE {full['margin_mae']-base['margin_mae']:+.3f}, RMSE {full['margin_rmse']-base['margin_rmse']:+.3f}, Winner {(full['winner_accuracy']-base['winner_accuracy'])*100:+.2f} pp")
   print("LEAVE-ONE-SYSTEM-OUT FROM FULL:")
   for s in SYSTEMS:
    features=tuple(k for k in FULL if k not in SYSTEM_FEATURES[s]);z=score(fit_subset(stats,features),test);print(f"  minus {s}: MAE {z['margin_mae']-full['margin_mae']:+.3f}, RMSE {z['margin_rmse']-full['margin_rmse']:+.3f}, Winner {(z['winner_accuracy']-full['winner_accuracy'])*100:+.2f} pp")


if __name__=="__main__":main()
