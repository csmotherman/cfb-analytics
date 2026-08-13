from pathlib import Path
import json,math
from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES,eligible_iterative_row,materialize_iterative_model_dataset
from cfb_analytics.analytics.opponent_adjustment_ablation import evaluate
from cfb_analytics.analytics.walk_forward_baseline import FEATURES as RAW,DEFAULT_SEASONS,TEST_SEASONS
COMBO=tuple(RAW)+tuple(ITERATIVE_FEATURES)
def ok(r,n):return eligible_iterative_row(r,n) and all(isinstance(r.get(k),(int,float)) and math.isfinite(float(r[k])) for k in RAW)
def load(rr,pr,s):
 materialize_iterative_model_dataset(rr,pr,s);return json.loads((pr/'derived'/'iterative_ratings'/f'season={s}'/'games.json').read_text())
def main():
 rr=Path('data/raw');pr=Path('data/processed');d={s:load(rr,pr,s) for s in DEFAULT_SEASONS};mods={'RAW':tuple(RAW),'ITERATIVE':tuple(ITERATIVE_FEATURES),'RAW_PLUS_ITERATIVE':COMBO}
 print('ITERATIVE RATINGS ABLATION v1\nCommon eligible sample across models within each threshold: YES\nFeatures: raw=14, iterative=12, combined=26')
 for n in (3,4):
  e={s:[r for r in d[s] if ok(r,n)] for s in DEFAULT_SEASONS};print(f'\nMINIMUM PRIOR GAMES PER TEAM: {n}')
  for t in TEST_SEASONS:
   tr=[r for s in DEFAULT_SEASONS if s<t for r in e[s]];te=e[t];out={k:evaluate(tr,te,v) for k,v in mods.items()};base=out['RAW'];print(f'\nTEST {t}')
   for k,x in out.items():print(f"{k}: n={x['test_games']:,} MAE={x['margin_mae']:.3f} RMSE={x['margin_rmse']:.3f} Winner={x['winner_accuracy']:.2%}")
   for k in ('ITERATIVE','RAW_PLUS_ITERATIVE'):
    x=out[k];print(f"{k} vs RAW: MAE {x['margin_mae']-base['margin_mae']:+.3f}, RMSE {x['margin_rmse']-base['margin_rmse']:+.3f}, Winner {(x['winner_accuracy']-base['winner_accuracy'])*100:+.2f} pp")
if __name__=='__main__':main()
