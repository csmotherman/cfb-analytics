from pathlib import Path
import json,math

from cfb_analytics.analytics.football_mechanisms import FAMILY_FEATURES,orient_matchup
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES,SRS_FEATURES,eligible_iterative_row
from cfb_analytics.analytics.model_feature_store import load_saved_feature_store
from cfb_analytics.analytics.walk_forward_baseline import DEFAULT_SEASONS,TEST_SEASONS,_solve

BASE=tuple(ITERATIVE_FEATURES)+tuple(SRS_FEATURES)
MWDR=("home_MWDR_OffenseEdge","home_MWDR_DefenseEdge")
FINISHING=tuple(FAMILY_FEATURES["FINISHING"])
LAB=(
 "mwdrXExpectedPossessions",
 "expectedScoringPpdEdge",
 "expectedScoringMarginProxy",
 "expectedTdDriveEdge",
 "successVolumeEdge",
 "explosiveVolumeEdge",
 "turnoverVolumeEdge",
 "driveConversionInteraction",
)
FULL=BASE+MWDR+FINISHING+LAB
INDEX={k:i for i,k in enumerate(FULL)}


def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))
def avg(a,b):return (float(a)+float(b))/2 if finite(a) and finite(b) else None
def home_only(rows):return sum(r.get("target_homeWin")==1 for r in rows)/len(rows) if rows else 0.0


def oriented_raw(m,home,away):
 if {home,away}!={m.get("team1"),m.get("team2")}:return None
 hp="team1" if home==m.get("team1") else "team2";ap="team2" if hp=="team1" else "team1"
 h=lambda f:m.get(f"{hp}_{f}");a=lambda f:m.get(f"{ap}_{f}")
 return h,a


def add_lab_features(r,m,x):
 z={**r,**x};raw=oriented_raw(m,r.get("homeTeam"),r.get("awayTeam"))
 if raw is None:return None
 h,a=raw;poss=z.get("expectedPossessionsPerTeam")
 mwdr=(float(z[MWDR[0]])+float(z[MWDR[1]])) if finite(z.get(MWDR[0])) and finite(z.get(MWDR[1])) else None
 z["mwdrXExpectedPossessions"]=mwdr*float(poss) if finite(mwdr) and finite(poss) else None

 home_opp=avg(h("OffScoringOpportunityRate"),a("DefScoringOpportunityRateAllowed"))
 away_opp=avg(a("OffScoringOpportunityRate"),h("DefScoringOpportunityRateAllowed"))
 home_ppo=avg(h("OffPointsPerOpportunity"),a("DefPointsPerOpportunityAllowed"))
 away_ppo=avg(a("OffPointsPerOpportunity"),h("DefPointsPerOpportunityAllowed"))
 home_td=avg(h("OffTouchdownOpportunityRate"),a("DefTouchdownOpportunityRateAllowed"))
 away_td=avg(a("OffTouchdownOpportunityRate"),h("DefTouchdownOpportunityRateAllowed"))
 home_ppd=float(home_opp)*float(home_ppo) if finite(home_opp) and finite(home_ppo) else None
 away_ppd=float(away_opp)*float(away_ppo) if finite(away_opp) and finite(away_ppo) else None
 z["expectedScoringPpdEdge"]=float(home_ppd)-float(away_ppd) if finite(home_ppd) and finite(away_ppd) else None
 z["expectedScoringMarginProxy"]=float(z["expectedScoringPpdEdge"])*float(poss) if finite(z.get("expectedScoringPpdEdge")) and finite(poss) else None
 home_td_drive=float(home_opp)*float(home_td) if finite(home_opp) and finite(home_td) else None
 away_td_drive=float(away_opp)*float(away_td) if finite(away_opp) and finite(away_td) else None
 z["expectedTdDriveEdge"]=float(home_td_drive)-float(away_td_drive) if finite(home_td_drive) and finite(away_td_drive) else None
 z["successVolumeEdge"]=float(z["netSuccessRateEdge"])*float(poss) if finite(z.get("netSuccessRateEdge")) and finite(poss) else None
 z["explosiveVolumeEdge"]=float(z["netExplosiveRateEdge"])*float(poss) if finite(z.get("netExplosiveRateEdge")) and finite(poss) else None
 z["turnoverVolumeEdge"]=float(z["netTurnoverPressureEdge"])*float(poss) if finite(z.get("netTurnoverPressureEdge")) and finite(poss) else None
 z["driveConversionInteraction"]=float(z["netScoringOpportunityRateEdge"])*float(z["netPointsPerOpportunityEdge"]) if finite(z.get("netScoringOpportunityRateEdge")) and finite(z.get("netPointsPerOpportunityEdge")) else None
 return z


def load_all():
 pr=Path("data/processed");data={};print("Loading saved feature stores only; football interaction lab.")
 for season in DEFAULT_SEASONS:
  base=load_saved_feature_store(pr,season);p=pr/"derived"/"football_mechanisms"/f"season={season}"/"matchups.json"
  if not p.exists():raise FileNotFoundError(f"Missing football mechanisms for {season}. Run: python -m cfb_analytics.analytics.football_mechanisms --all")
  match={str(q.get("gameId")):q for q in json.loads(p.read_text())};rows=[]
  for r in base:
   m=match.get(str(r.get("gameId")))
   if not m:continue
   x=orient_matchup(m,r.get("homeTeam"),r.get("awayTeam"))
   if x is None:continue
   z=add_lab_features(r,m,x)
   if z is not None:rows.append(z)
  data[season]=rows;print(f"LOAD {season}: base={len(base):,} mechanisms={len(match):,} merged={len(rows):,}")
 return data


def eligible(r,min_games):return eligible_iterative_row(r,min_games) and all(finite(r.get(k)) for k in FULL)


def prepare(rows):
 means=[];scales=[]
 for k in FULL:
  vals=[float(r[k]) for r in rows];m=sum(vals)/len(vals);v=sum((q-m)**2 for q in vals)/len(vals);means.append(m);scales.append(math.sqrt(v) or 1.0)
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
 data=load_all();stable=BASE+MWDR+("mwdrXExpectedPossessions",);current_full=stable+FINISHING
 models={
  "BASE":BASE,
  "CURRENT_STABLE":stable,
  "CURRENT_FULL":current_full,
  "BASE_PLUS_SCORING_PPD":BASE+("expectedScoringPpdEdge",),
  "BASE_PLUS_SCORING_MARGIN_PROXY":BASE+("expectedScoringMarginProxy",),
  "BASE_PLUS_TD_DRIVE_EDGE":BASE+("expectedTdDriveEdge",),
  "BASE_PLUS_SUCCESS_VOLUME":BASE+("successVolumeEdge",),
  "BASE_PLUS_EXPLOSIVE_VOLUME":BASE+("explosiveVolumeEdge",),
  "BASE_PLUS_TURNOVER_VOLUME":BASE+("turnoverVolumeEdge",),
  "BASE_PLUS_DRIVE_CONVERSION":BASE+("driveConversionInteraction",),
  "STABLE_PLUS_SCORING_PPD":stable+("expectedScoringPpdEdge",),
  "STABLE_PLUS_SCORING_MARGIN_PROXY":stable+("expectedScoringMarginProxy",),
  "STABLE_PLUS_TD_DRIVE_EDGE":stable+("expectedTdDriveEdge",),
  "STABLE_PLUS_SUCCESS_VOLUME":stable+("successVolumeEdge",),
  "STABLE_PLUS_EXPLOSIVE_VOLUME":stable+("explosiveVolumeEdge",),
  "STABLE_PLUS_TURNOVER_VOLUME":stable+("turnoverVolumeEdge",),
  "STABLE_PLUS_DRIVE_CONVERSION":stable+("driveConversionInteraction",),
  "STABLE_PLUS_SCORING_ENGINE":stable+("expectedScoringPpdEdge","expectedTdDriveEdge"),
  "STABLE_PLUS_VOLUME_ENGINE":stable+("successVolumeEdge","explosiveVolumeEdge","turnoverVolumeEdge"),
  "STABLE_PLUS_SCORING_AND_VOLUME":stable+("expectedScoringPpdEdge","expectedTdDriveEdge","successVolumeEdge","explosiveVolumeEdge","turnoverVolumeEdge"),
 }
 print("FOOTBALL INTERACTION LAB")
 print("Baseline: ITERATIVE + SRS")
 print("Current stable: BASE + MWDR + MWDR x EXPECTED POSSESSIONS")
 print("All features use prior-game information only; common sample across every model: YES")
 for min_games in (3,4):
  elig={s:[r for r in data[s] if eligible(r,min_games)] for s in DEFAULT_SEASONS};print(f"\nMINIMUM PRIOR GAMES PER TEAM: {min_games}")
  for test_season in TEST_SEASONS:
   train=[r for s in DEFAULT_SEASONS if s<test_season for r in elig[s]];test=elig[test_season];stats=prepare(train)
   print(f"\nTEST {test_season}")
   print(f"COMMON SAMPLE: train={len(train):,} test={len(test):,}")
   print(f"HOME-ONLY WINNER BASELINE: {home_only(test):.2%}")
   scored={name:score(fit(stats,features),test) for name,features in models.items()};base=scored["BASE"];st=scored["CURRENT_STABLE"]
   for name,q in scored.items():print(f"{name}: n={q['n']:,} MAE={q['mae']:.3f} RMSE={q['rmse']:.3f} WinnerFromMargin={q['winner']:.2%}")
   print("DELTAS VS BASE:")
   for name,q in scored.items():
    if name=="BASE":continue
    print(f"  {name}: MAE {q['mae']-base['mae']:+.3f}, RMSE {q['rmse']-base['rmse']:+.3f}, Winner {(q['winner']-base['winner'])*100:+.2f} pp")
   print("INCREMENTAL VS CURRENT_STABLE:")
   for name,q in scored.items():
    if not name.startswith("STABLE_PLUS_"):continue
    print(f"  {name}: MAE {q['mae']-st['mae']:+.3f}, RMSE {q['rmse']-st['rmse']:+.3f}, Winner {(q['winner']-st['winner'])*100:+.2f} pp")

if __name__=="__main__":main()
