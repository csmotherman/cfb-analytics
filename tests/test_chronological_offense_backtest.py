import math
from cfb_analytics.analytics.chronological_offense_backtest import _ordered_games,backtest
from tests.test_opponent_adjusted_offense import _sample_rows

def _multiweek():
 base=_sample_rows();out=[]
 # Repeat the six-game connected schedule across six chronological blocks with unique IDs.
 for week in range(1,7):
  for r in base:
   x=dict(r);x['gameId']=str(week*100+int(r['gameId']));x['startDate']=f'2025-09-{week:02d}T12:00:00Z';out.append(x)
 return out

def test_orders_by_date_not_input_order():
 rows=_multiweek();ordered=_ordered_games(list(reversed(rows)));dates=[]
 for _,rs in ordered:dates.append(rs[0]['startDate'])
 assert dates==sorted(dates)

def test_backtest_uses_only_prior_games_and_returns_all_models():
 r=backtest(_multiweek(),2025,min_games=2)
 assert r['test_games']>0 and r['observations']>0
 for model in ('raw','ls_ppd','current_composite','equal_composite'):
  e=r['errors'][model];assert e['observations']>0;assert math.isfinite(e['mae']);assert math.isfinite(e['rmse'])

def test_min_games_can_remove_all_test_observations():
 r=backtest(_multiweek(),2025,min_games=100)
 assert r['observations']==0
