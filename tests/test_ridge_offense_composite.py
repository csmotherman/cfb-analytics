import pytest
from cfb_analytics.analytics.ridge_offense_composite import METRICS,_obs,rankings
from tests.test_opponent_adjusted_offense import _sample_rows

def test_metric_value_and_weight_mapping_is_correct():
 row=_sample_rows()[0]
 ppd,w=_obs(row,'ppd');assert ppd==pytest.approx(3.5);assert w==pytest.approx(10)
 ypd,w=_obs(row,'ypd');assert ypd==pytest.approx(35.0);assert w==pytest.approx(10)
 sr,w=_obs(row,'success');assert sr==pytest.approx(.5);assert w==pytest.approx(60)
 score,w=_obs(row,'scoring');assert score==pytest.approx(.5);assert w==pytest.approx(10)

def test_multi_metric_rankings_have_all_adjusted_metrics():
 ranked,w=rankings(_sample_rows(),2025,lam=20)
 assert ranked
 assert sum(w.values())==pytest.approx(1.0)
 assert set(w)==set(METRICS)
 for r in ranked:
  for k in ('rating','adj_ppd','adj_ypd','adj_success','adj_scoring','rank'):
   assert k in r

def test_weights_are_normalized():
 _,w=rankings(_sample_rows(),2025,lam=20,weights={'ppd':2,'ypd':1,'success':1,'scoring':0})
 assert w['ppd']==pytest.approx(.5)
 assert w['ypd']==pytest.approx(.25)
 assert w['success']==pytest.approx(.25)
 assert w['scoring']==pytest.approx(0)

def test_rank_order_matches_rating():
 ranked,_=rankings(_sample_rows(),2025,lam=20)
 assert [r['rating'] for r in ranked]==sorted((r['rating'] for r in ranked),reverse=True)
 assert [r['rank'] for r in ranked]==list(range(1,len(ranked)+1))
