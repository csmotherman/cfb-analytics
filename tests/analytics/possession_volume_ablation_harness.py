from pathlib import Path
import json,math
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES,SRS_FEATURES,eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.possession_volume import MATCHUP_FEATURES,orient_matchup
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS,TEST_SEASONS,_solve

BASE=tuple(ITERATIVE_FEATURES)+tuple(SRS_FEATURES)
PV=tuple(MATCHUP_FEATURES)
MWDR=("home_MWDR_OffenseEdge","home_MWDR_DefenseEdge")
DERIVED=("srsXExpectedPossessions","mwdrXExpectedPossessions")
FULL=BASE+PV+MWDR+DERIVED
INDEX={k:i for i,k in enumerate(FULL)}


def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))
def home_only(rows):return sum(r.get("target_homeWin")==1 for r in rows)/len(rows) if rows else 0.0

def load_all():
 pr=Path("data/processed");data={};print("Loading saved feature stores only; no football metrics will be recomputed.")
 for season in DEFAULT_SEASONS:
  base=load_saved_feature_store(pr,season);p=pr/"derived"/"possession_volume"/f"season={season}"/"matchups.json"
  if not p.exists():raise FileNotFoundError(f"Missing possession-volume store for {season}. Run: python -m cfb_analytics.analytics.possession_volume --all")
  match={str(r.get("gameId")):r for r in json.loads(p.read_text())};rows=[]
  for r in base:
   m=match.get(str(r.get("gameId")))
   if not m:continue
   x=orient_matchup(m,r.get("homeTeam"),r.get("awayTeam"))
   if x is None:continue
   z={**r,**x};poss=z.get("expectedPossessionsPerTeam")
   z["srsXExpectedPossessions"]=float(z["srsEdge"])*float(poss) if finite(z.get("srsEdge")) and finite(poss) else None
   mwdr=(float(z[MWDR[0]])+float(z[MWDR[1]])) if finite(z.get(MWDR[0])) and finite(z.get(MWDR[1])) else None
   z["mwdrXExpectedPossessions"]=mwdr*float(poss) if finite(mwdr) and finite(poss) else None
   rows.append(z)
  data[season]=rows;print(f"LOAD {season}: base={len(base):,} possession={len(match):,} merged={len(rows):,}")
 return data

def eligible(r,min_games):return eligible_iterative_row(r,min_games) and all(finite(r.get(k)) for k in FULL)

def prepare(rows):
 means=[];scales=[]
 for k in FULL:
  vals=[float(r[k]) for r in rows];m=sum(vals)/len(vals);v=sum((x-m)**2 for x in vals)/len(vals);means.append(m);scales.append(math.sqrt(v) or 1.0)
 p=len(FULL)+1;xtx=[[0.0]*p for _ in range(p)];xty=[0.0]*p
 for r in rows:
  x=[1.0]+[(float(r[k])-means[i])/scales[i] for i,k in enumerate(FULL)];y=float(r["target_margin"])
  for i,xi in enumerate(x):
   xty[i]+=xi*y
   for j in range(i,p):xtx[i][j]+=xi*x[j]
 for i in range(p):
  for j in range(i):xtx[i][j]=xtx[j][i]
 return {"means":means,"scales":scales,"xtx":xtx,"xty":xty,"n":len(rows)}

def fit(stats,features,ridge=1e-6):
 idx=[0]+[INDEX[k]+1 for k in features];a=[[stats["xtx"][i][j] for j in idx] for i in idx];b=[stats["xty"][i] for i in idx]
 for i in range(1,len(a)):a[i][i]+=ridge
 w=_solve(a,b)
 if w is None:raise ValueError("singular model")
 return {"features":tuple(features),"weights":w,"means":stats["means"],"scales":stats["scales"],"n":stats["n"]}

def score(model,rows):
 ae=[];se=[];correct=0
 for r in rows:
  pred=model["weights"][0]
  for j,k in enumerate(model["features"],1):
   i=INDEX[k];pred+=model["weights"][j]*(float(r[k])-model["means"][i])/model["scales"][i]
  y=float(r["target_margin"]);ae.append(abs(pred-y));se.append((pred-y)**2);correct+=int((pred>0)==bool(r["target_homeWin"]))
 n=len(rows);return {"mae":sum(ae)/n,"rmse":math.sqrt(sum(se)/n),"winner":correct/n,"n":n}

def main():
 data=load_all();models={
  "BASE_ITERATIVE_SRS":BASE,
  "BASE_PLUS_EXPECTED_POSSESSIONS":BASE+("expectedPossessionsPerTeam",),
  "BASE_PLUS_EXPECTED_TOTAL_PLAYS":BASE+("expectedTotalPlays",),
  "BASE_PLUS_PLAYS_PER_POSSESSION":BASE+("homePlaysPerPossessionEdge","awayPlaysPerPossessionEdge"),
  "BASE_PLUS_ALL_POSSESSION":BASE+PV,
  "BASE_PLUS_SRS_X_POSSESSIONS":BASE+("srsXExpectedPossessions",),
  "BASE_PLUS_MWDR":BASE+MWDR,
  "BASE_PLUS_MWDR_AND_POSSESSION":BASE+MWDR+PV,
  "BASE_PLUS_MWDR_POSSESSION_INTERACTION":BASE+MWDR+PV+("mwdrXExpectedPossessions",),
  "BASE_PLUS_ALL_INTERACTIONS":BASE+MWDR+PV+DERIVED,
 }
 print("POSSESSION & VOLUME v1 ABLATION")
 print("Winner metric: sign of predicted point margin")
 print("Common eligible sample across every model: YES")
 for min_games in (3,4):
  elig={s:[r for r in data[s] if eligible(r,min_games)] for s in DEFAULT_SEASONS};print(f"\nMINIMUM PRIOR GAMES PER TEAM: {min_games}")
  for test_season in TEST_SEASONS:
   train=[r for s in DEFAULT_SEASONS if s<test_season for r in elig[s]];test=elig[test_season];stats=prepare(train);base=None
   print(f"\nTEST {test_season}")
   print(f"COMMON SAMPLE: train={len(train):,} test={len(test):,}")
   print(f"HOME-ONLY WINNER BASELINE: {home_only(test):.2%}")
   scored={name:score(fit(stats,features),test) for name,features in models.items()};base=scored["BASE_ITERATIVE_SRS"]
   for name,x in scored.items():print(f"{name}: n={x['n']:,} MAE={x['mae']:.3f} RMSE={x['rmse']:.3f} WinnerFromMargin={x['winner']:.2%}")
   print("DELTAS VS BASE:")
   for name,x in scored.items():
    if name=="BASE_ITERATIVE_SRS":continue
    print(f"  {name}: MAE {x['mae']-base['mae']:+.3f}, RMSE {x['rmse']-base['rmse']:+.3f}, Winner {(x['winner']-base['winner'])*100:+.2f} pp")
if __name__=="__main__":main()
