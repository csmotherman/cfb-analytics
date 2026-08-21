import math
import pytest
from cfb_analytics.analytics.ridge_defense_composite import METRICS,_obs,rankings
from tests.test_opponent_adjusted_offense import _sample_rows

def test_defense_metric_mapping_and_denominators():
 r=_sample_rows()[0]
 assert _obs(r,'ppd')==(pytest.approx(1.4),10.0)
 assert _obs(r,'ypd')==(pytest.approx(14.0),10.0)
 assert _obs(r,'success')==(pytest.approx(20/60),60.0)
 assert _obs(r,'scoring')==(pytest.approx(.2),10.0)

def test_defense_rankings_have_all_metrics_and_normalized_weights():
 ranked,w=rankings(_sample_rows(),2025,lam=20)
 assert ranked and sum(w.values())==pytest.approx(1.0) and set(w)==set(METRICS)
 for r in ranked:
  for k in ('rating','adj_ppd_allowed','adj_ypd_allowed','adj_success_allowed','adj_scoring_allowed','rank'):
   assert k in r and math.isfinite(float(r[k]))

def test_better_defensive_allowances_produce_higher_rating():
 ranked,_=rankings(_sample_rows(),2025,lam=20)
 assert [r['rating'] for r in ranked]==sorted((r['rating'] for r in ranked),reverse=True)
 assert [r['rank'] for r in ranked]==list(range(1,len(ranked)+1))
