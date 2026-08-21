import math
from cfb_analytics.analytics.ridge_offense_backtest import _solve_ppd_ridge,backtest
from tests.test_chronological_offense_backtest import _multiweek

def test_ridge_shrinks_effects_vs_unregularized():
 rows=_multiweek()[:24]
 ls=_solve_ppd_ridge(rows,0.0);ridge=_solve_ppd_ridge(rows,20.0)
 assert sum(abs(v) for v in ridge['offense_effect'].values()) < sum(abs(v) for v in ls['offense_effect'].values())
 assert sum(abs(v) for v in ridge['defense_effect'].values()) < sum(abs(v) for v in ls['defense_effect'].values())

def test_ridge_backtest_returns_static_dynamic_and_buckets():
 r=backtest(_multiweek(),2025,min_games=2,static_lambdas=(0.0,1.0,10.0),dynamic_cs=(5.0,))
 assert r['observations']>0
 for m in ('raw','ridge_0','ridge_1','ridge_10','dyn_5'):
  assert m in r['errors'];assert math.isfinite(r['errors'][m]['rmse'])
 assert set(r['buckets'])=={'4-5','6-7','8-9','10+'}

def test_high_ridge_moves_predictions_toward_baseline():
 rows=_multiweek()[:24]
 low=_solve_ppd_ridge(rows,0.0);high=_solve_ppd_ridge(rows,1000.0)
 low_mag=max(abs(v) for v in low['offense_effect'].values());high_mag=max(abs(v) for v in high['offense_effect'].values())
 assert high_mag < low_mag
