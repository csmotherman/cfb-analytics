import math
import numpy as np
from cfb_analytics.analytics.optimize_offense_composite import _fit_weights,_project_simplex,optimize
from tests.test_opponent_adjusted_offense import _sample_rows

def test_projection_stays_on_simplex():
 w=_project_simplex(np.array([1.2,-.2,.3,.7]));assert np.all(w>=0);assert w.sum()==pytest.approx(1.0)

def test_fit_weights_nonnegative_sum_to_one():
 samples=[(np.array([1.,0.,0.,0.]),1.,10.),(np.array([0.,1.,0.,0.]),0.,10.),(np.array([-1.,0.,0.,0.]),-1.,10.)]
 w=_fit_weights(samples,steps=1000,lr=.05);assert np.all(w>=0);assert math.isclose(float(w.sum()),1.0,abs_tol=1e-9);assert w[0]>w[1]

def test_leave_one_season_out_runs():
 rows={2022:[dict(r,season=2022) for r in _sample_rows()],2023:[dict(r,season=2023) for r in _sample_rows()],2024:[dict(r,season=2024) for r in _sample_rows()],2025:[dict(r,season=2025) for r in _sample_rows()]}
 out=optimize(rows,[2022,2023,2024,2025]);assert len(out['folds'])==4
 for f in out['folds']:
  assert abs(sum(f['weights'].values())-1)<1e-9;assert all(v>=0 for v in f['weights'].values());assert math.isfinite(f['learned']['rmse']);assert math.isfinite(f['current']['rmse'])
 assert abs(sum(out['final_weights'].values())-1)<1e-9
