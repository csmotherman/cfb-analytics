from pathlib import Path
import json,math
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES,SRS_FEATURES,eligible_iterative_row,materialize_iterative_model_dataset
from cfb_analytics.analytics.opponent_adjustment_ablation import fit_model,score_model
from cfb_analytics.analytics.walk_forward_baseline import FEATURES as RAW,DEFAULT_SEASONS,TEST_SEASONS

SRS=tuple(SRS_FEATURES)
COMBO=tuple(RAW)+tuple(ITERATIVE_FEATURES)
ALL=COMBO+SRS
FAMILIES={
 'Success':('home_iterativeSuccessEdge','away_iterativeSuccessEdge'),
 'Explosive':('home_iterativeExplosiveEdge','away_iterativeExplosiveEdge'),
 'YardsPerPlay':('home_iterativeYardsPerPlayEdge','away_iterativeYardsPerPlayEdge'),
 'YardsPerPossession':('home_iterativeYardsPerPossessionEdge','away_iterativeYardsPerPossessionEdge'),
 'Finishing':('home_iterativeFinishingEdge','away_iterativeFinishingEdge'),
 'FieldPosition':('home_iterativeFieldPositionEdge','away_iterativeFieldPositionEdge'),
}

def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))
def ok(r,n):return eligible_iterative_row(r,n) and all(finite(r.get(k)) for k in ALL)
def load(rr,pr,s):
 result=materialize_iterative_model_dataset(rr,pr,s)
 if result['status']!='PASS':raise RuntimeError(f"season {s} enriched audit failed: {result['checks']}")
 print(f"CACHE {s}: {result['cache_status']} rows={result['model_rows']:,} srs={result['srs_available_rows']:,}")
 return json.loads((pr/'derived'/'iterative_ratings'/f'season={s}'/'games.json').read_text())
def home_only(rows):return sum(r.get('target_homeWin')==1 for r in rows)/len(rows) if rows else 0.0

def main():
 rr=Path('data/raw');pr=Path('data/processed');d={s:load(rr,pr,s) for s in DEFAULT_SEASONS}
 mods={
  'RAW':tuple(RAW),
  'SRS':SRS,
  'RAW_PLUS_SRS':tuple(RAW)+SRS,
  'ITERATIVE':tuple(ITERATIVE_FEATURES),
  'ITERATIVE_PLUS_SRS':tuple(ITERATIVE_FEATURES)+SRS,
  'RAW_PLUS_ITERATIVE':COMBO,
  'RAW_PLUS_ITERATIVE_PLUS_SRS':ALL,
 }
 print('ITERATIVE + SRS ABLATION v4 CACHED VALIDATION')
 print('Common eligible sample across every model and family ablation: YES')
 print(f'Features: raw={len(RAW)}, iterative={len(ITERATIVE_FEATURES)}, srs={len(SRS)}, all={len(ALL)}')
 for n in (3,4):
  eligible={s:[r for r in d[s] if ok(r,n)] for s in DEFAULT_SEASONS}
  print(f'\nMINIMUM PRIOR GAMES PER TEAM: {n}')
  for test_season in TEST_SEASONS:
   train=[r for s in DEFAULT_SEASONS if s<test_season for r in eligible[s]]
   test=eligible[test_season]
   fitted={name:fit_model(train,features) for name,features in mods.items()}
   out={name:score_model(fitted[name],test) for name in mods}
   raw=out['RAW'];iterative=out['ITERATIVE']
   print(f'\nTEST {test_season}')
   print(f'HOME-ONLY WINNER BASELINE: n={len(test):,} Winner={home_only(test):.2%}')
   for name,x in out.items():
    print(f"{name}: n={x['test_games']:,} MAE={x['margin_mae']:.3f} RMSE={x['margin_rmse']:.3f} Winner={x['winner_accuracy']:.2%} LogitIters={x['logit_iterations']}")
   for name in ('SRS','RAW_PLUS_SRS','ITERATIVE','ITERATIVE_PLUS_SRS','RAW_PLUS_ITERATIVE','RAW_PLUS_ITERATIVE_PLUS_SRS'):
    x=out[name]
    print(f"{name} vs RAW: MAE {x['margin_mae']-raw['margin_mae']:+.3f}, RMSE {x['margin_rmse']-raw['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-raw['winner_accuracy'])*100:+.2f} pp")
   x=out['ITERATIVE_PLUS_SRS']
   print(f"ITERATIVE_PLUS_SRS vs ITERATIVE: MAE {x['margin_mae']-iterative['margin_mae']:+.3f}, RMSE {x['margin_rmse']-iterative['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-iterative['winner_accuracy'])*100:+.2f} pp")

   print('ITERATIVE BY WEEK (n>=10; one fitted model reused):')
   iterative_model=fitted['ITERATIVE']
   weeks=sorted({(str(r.get('seasonType') or 'regular'),int(r.get('week') or 0)) for r in test})
   for st,w in weeks:
    week_rows=[r for r in test if str(r.get('seasonType') or 'regular')==st and int(r.get('week') or 0)==w]
    if len(week_rows)>=10:
     z=score_model(iterative_model,week_rows)
     print(f"  {st} {w}: n={len(week_rows):3d} MAE={z['margin_mae']:.2f} RMSE={z['margin_rmse']:.2f} Winner={z['winner_accuracy']:.2%}")

   print('LEAVE-ONE-ITERATIVE-FAMILY-OUT (same common sample):')
   for family,pair in FAMILIES.items():
    features=tuple(k for k in ITERATIVE_FEATURES if k not in pair)
    z=score_model(fit_model(train,features),test)
    print(f"  minus {family}: n={z['test_games']:,} MAE {z['margin_mae']-iterative['margin_mae']:+.3f}, RMSE {z['margin_rmse']-iterative['margin_rmse']:+.3f}, Winner {(z['winner_accuracy']-iterative['winner_accuracy'])*100:+.2f} pp")

if __name__=='__main__':main()
