from pathlib import Path
import json,math
from concurrent.futures import ProcessPoolExecutor,as_completed

from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES,SRS_FEATURES,eligible_iterative_row,materialize_iterative_model_dataset
from cfb_analytics.analytics.opponent_adjustment_ablation import fit_model,score_model
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS,TEST_SEASONS
from cfb_analytics.derived.sandbox_pregame import SYSTEMS,materialize_sandbox_pregame

BASE=tuple(ITERATIVE_FEATURES)+tuple(SRS_FEATURES)
SYSTEM_FEATURES={s:(f"home_{s}_OffenseEdge",f"home_{s}_DefenseEdge") for s in SYSTEMS}
ALL_SYSTEMS=tuple(k for s in SYSTEMS for k in SYSTEM_FEATURES[s])
FULL=BASE+ALL_SYSTEMS
MAX_WORKERS=4

def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))

def orient_sandbox(row,m):
 home,away=row.get("homeTeam"),row.get("awayTeam")
 if {home,away}!={m.get("team1"),m.get("team2")}:return None
 p="team1" if home==m.get("team1") else "team2";out=dict(row)
 for s in SYSTEMS:
  out[f"home_{s}_OffenseEdge"]=m.get(f"{p}_{s}_OffenseEdge");out[f"home_{s}_DefenseEdge"]=m.get(f"{p}_{s}_DefenseEdge")
 return out

def load_one(season,raw_root="data/raw",processed_root="data/processed"):
 rr,pr=Path(raw_root),Path(processed_root)
 ir=materialize_iterative_model_dataset(rr,pr,season)
 if ir["status"]!="PASS":raise RuntimeError(f"season {season} iterative audit failed: {ir['checks']}")
 sb=materialize_sandbox_pregame(rr,pr,season)
 rows=json.loads((pr/"derived"/"iterative_ratings"/f"season={season}"/"games.json").read_text())
 matchups={str(r.get("gameId")):r for r in sb["matchups"]};merged=[]
 for row in rows:
  m=matchups.get(str(row.get("gameId")))
  if m:
   x=orient_sandbox(row,m)
   if x is not None:merged.append(x)
 return season,merged,ir["cache_status"],sb["cache_status"],len(rows),len(matchups)

def load_all():
 data={};workers=min(MAX_WORKERS,len(DEFAULT_SEASONS))
 print(f"Preparing {len(DEFAULT_SEASONS)} seasons with {workers} parallel workers...")
 with ProcessPoolExecutor(max_workers=workers) as pool:
  jobs={pool.submit(load_one,s):s for s in DEFAULT_SEASONS}
  for job in as_completed(jobs):
   s,rows,ic,sc,nm,ns=job.result();data[s]=rows
   print(f"LOAD {s}: iterative={ic} sandbox={sc} model={nm:,} sandbox_games={ns:,} merged={len(rows):,}",flush=True)
 return data

def eligible(row,min_games):return eligible_iterative_row(row,min_games) and all(finite(row.get(k)) for k in FULL)
def home_only(rows):return sum(r.get("target_homeWin")==1 for r in rows)/len(rows) if rows else 0.0

def main():
 data=load_all();models={"BASE_ITERATIVE_SRS":BASE,"SYSTEMS_ONLY":ALL_SYSTEMS}
 for s in SYSTEMS:models[f"BASE_PLUS_{s}"]=BASE+SYSTEM_FEATURES[s]
 models["BASE_PLUS_ALL_SYSTEMS"]=FULL
 print("CFB SANDBOX SYSTEM ABLATION v1")
 print("Baseline: ITERATIVE + SRS")
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
   fitted={name:fit_model(train,features) for name,features in models.items()};scored={name:score_model(fitted[name],test) for name in models};base=scored["BASE_ITERATIVE_SRS"]
   for name,x in scored.items():print(f"{name}: n={x['test_games']:,} MAE={x['margin_mae']:.3f} RMSE={x['margin_rmse']:.3f} Winner={x['winner_accuracy']:.2%} LogitIters={x['logit_iterations']}")
   print("ADDITIONS VS BASE:")
   for s in SYSTEMS:
    x=scored[f"BASE_PLUS_{s}"];print(f"  {s}: MAE {x['margin_mae']-base['margin_mae']:+.3f}, RMSE {x['margin_rmse']-base['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-base['winner_accuracy'])*100:+.2f} pp")
   x=scored["BASE_PLUS_ALL_SYSTEMS"];print(f"  ALL: MAE {x['margin_mae']-base['margin_mae']:+.3f}, RMSE {x['margin_rmse']-base['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-base['winner_accuracy'])*100:+.2f} pp")
   print("LEAVE-ONE-SYSTEM-OUT FROM FULL:")
   for s in SYSTEMS:
    features=tuple(k for k in FULL if k not in SYSTEM_FEATURES[s]);z=score_model(fit_model(train,features),test);print(f"  minus {s}: MAE {z['margin_mae']-x['margin_mae']:+.3f}, RMSE {z['margin_rmse']-x['margin_rmse']:+.3f}, Winner {(z['winner_accuracy']-x['winner_accuracy'])*100:+.2f} pp")

if __name__=="__main__":main()
