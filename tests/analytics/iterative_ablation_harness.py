from pathlib import Path
import json,math
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES,SRS_FEATURES,eligible_iterative_row,materialize_iterative_model_dataset
from cfb_analytics.analytics.opponent_adjustment_ablation import evaluate
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
def ok(r,n,features=ALL):return eligible_iterative_row(r,n) and all(finite(r.get(k)) for k in features)
def load(rr,pr,s):
 materialize_iterative_model_dataset(rr,pr,s);return json.loads((pr/'derived'/'iterative_ratings'/f'season={s}'/'games.json').read_text())
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
 print('ITERATIVE + SRS ABLATION v3 VALIDATION\nCommon eligible sample across primary models within each threshold: YES')
 print(f'Features: raw={len(RAW)}, iterative={len(ITERATIVE_FEATURES)}, srs={len(SRS)}, all={len(ALL)}')
 for n in (3,4):
  e={s:[r for r in d[s] if ok(r,n)] for s in DEFAULT_SEASONS};print(f'\nMINIMUM PRIOR GAMES PER TEAM: {n}')
  for t in TEST_SEASONS:
   tr=[r for s in DEFAULT_SEASONS if s<t for r in e[s]];te=e[t];out={k:evaluate(tr,te,v) for k,v in mods.items()};raw=out['RAW'];best=out['ITERATIVE'];print(f'\nTEST {t}')
   print(f'HOME-ONLY WINNER BASELINE: n={len(te):,} Winner={home_only(te):.2%}')
   for k,x in out.items():print(f"{k}: n={x['test_games']:,} MAE={x['margin_mae']:.3f} RMSE={x['margin_rmse']:.3f} Winner={x['winner_accuracy']:.2%}")
   for k in ('SRS','RAW_PLUS_SRS','ITERATIVE','ITERATIVE_PLUS_SRS','RAW_PLUS_ITERATIVE','RAW_PLUS_ITERATIVE_PLUS_SRS'):
    x=out[k];print(f"{k} vs RAW: MAE {x['margin_mae']-raw['margin_mae']:+.3f}, RMSE {x['margin_rmse']-raw['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-raw['winner_accuracy'])*100:+.2f} pp")
   s=out['ITERATIVE_PLUS_SRS'];print(f"ITERATIVE_PLUS_SRS vs ITERATIVE: MAE {s['margin_mae']-best['margin_mae']:+.3f}, RMSE {s['margin_rmse']-best['margin_rmse']:+.3f}, Winner {(s['winner_accuracy']-best['winner_accuracy'])*100:+.2f} pp")
   print('ITERATIVE BY WEEK (n>=10):')
   weeks=sorted({(str(r.get('seasonType') or 'regular'),int(r.get('week') or 0)) for r in te})
   for st,w in weeks:
    wk=[r for r in te if str(r.get('seasonType') or 'regular')==st and int(r.get('week') or 0)==w]
    if len(wk)>=10:
     z=evaluate(tr,wk,ITERATIVE_FEATURES);print(f"  {st} {w}: n={len(wk):3d} MAE={z['margin_mae']:.2f} RMSE={z['margin_rmse']:.2f} Winner={z['winner_accuracy']:.2%}")
   print('LEAVE-ONE-ITERATIVE-FAMILY-OUT:')
   for fam,pair in FAMILIES.items():
    features=tuple(k for k in ITERATIVE_FEATURES if k not in pair)
    tr2=[r for s in DEFAULT_SEASONS if s<t for r in d[s] if ok(r,n,features)];te2=[r for r in d[t] if ok(r,n,features)]
    z=evaluate(tr2,te2,features);print(f"  minus {fam}: n={z['test_games']:,} MAE {z['margin_mae']-best['margin_mae']:+.3f}, RMSE {z['margin_rmse']-best['margin_rmse']:+.3f}, Winner {(z['winner_accuracy']-best['winner_accuracy'])*100:+.2f} pp")
if __name__=='__main__':main()
