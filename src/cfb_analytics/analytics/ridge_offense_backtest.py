"""Chronological ridge backtest for opponent-adjusted offensive PPD.

Pure least squares can be unstable early in a season because the schedule graph is
sparse. This module adds L2 shrinkage to offense/defense effects and evaluates a
lambda sweep plus dynamic lambda = C / average prior games played.
"""
from __future__ import annotations
import argparse, json, math
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np
from cfb_analytics.analytics.chronological_offense_backtest import _ordered_games
from cfb_analytics.analytics.opponent_adjusted_offense import Totals,_eligible_rows,metrics,offensive_totals

STATIC_LAMBDAS=(0.0,0.1,0.25,0.5,1.0,2.0,5.0,10.0,20.0,50.0)
DYNAMIC_CS=(1.0,2.0,5.0,10.0,20.0,50.0)

def load(path:Path):
 with path.open(encoding='utf-8') as h:return json.load(h)

def _solve_ppd_ridge(rows:list[dict[str,Any]],lam:float)->dict[str,Any]:
 team_ids=sorted({int(r['team_id']) for r in rows}|{int(r['opponent_id']) for r in rows});idx={t:i for i,t in enumerate(team_ids)};n=len(team_ids)
 obs=[];wsum=ysum=0.0
 for r in rows:
  off=offensive_totals(r);value=metrics(off)[0];w=float(off.resolved_possessions)
  if value is None or w<=0:continue
  tid,oid=int(r['team_id']),int(r['opponent_id']);obs.append((tid,oid,float(value),w));wsum+=w;ysum+=float(value)*w
 if not obs:raise ValueError('No usable PPD observations')
 baseline=ysum/wsum
 # Weighted game rows + two sum-to-zero constraints + ridge rows.
 extra=2+(2*n if lam>0 else 0);X=np.zeros((len(obs)+extra,2*n));y=np.zeros(len(obs)+extra)
 for i,(tid,oid,value,w) in enumerate(obs):
  sw=math.sqrt(w);X[i,idx[tid]]=sw;X[i,n+idx[oid]]=-sw;y[i]=(value-baseline)*sw
 anchor=max(math.sqrt(wsum),1.0);cursor=len(obs);X[cursor,:n]=anchor;cursor+=1;X[cursor,n:]=anchor;cursor+=1
 if lam>0:
  sl=math.sqrt(lam)
  for j in range(2*n):X[cursor+j,j]=sl
 beta,*_=np.linalg.lstsq(X,y,rcond=None);offense={t:float(beta[idx[t]]) for t in team_ids};defense={t:float(beta[n+idx[t]]) for t in team_ids}
 return {'baseline':baseline,'offense_effect':offense,'defense_effect':defense}

def _raw_ppd(train):
 totals={}
 for r in train:
  tid=int(r['team_id']);totals[tid]=totals.get(tid,Totals())+offensive_totals(r)
 return {tid:metrics(t)[0] for tid,t in totals.items()}

def _error_block(obs,model):
 vals=[x for x in obs if model in x['pred']];wt=sum(x['weight'] for x in vals)
 if not wt:return {'observations':0,'mae':float('nan'),'rmse':float('nan'),'weight':0.0,'absolute_error':0.0,'squared_error':0.0}
 ae=sum(x['weight']*abs(x['pred'][model]-x['actual']) for x in vals);se=sum(x['weight']*(x['pred'][model]-x['actual'])**2 for x in vals)
 return {'observations':len(vals),'mae':ae/wt,'rmse':math.sqrt(se/wt),'weight':wt,'absolute_error':ae,'squared_error':se}

def backtest(rows:list[dict[str,Any]],season:int,min_games:int=4,static_lambdas=STATIC_LAMBDAS,dynamic_cs=DYNAMIC_CS):
 rows=_eligible_rows(rows,season);ordered=_ordered_games(rows);played=defaultdict(int);train=[];obs=[]
 models=['raw']+[f'ridge_{l:g}' for l in static_lambdas]+[f'dyn_{c:g}' for c in dynamic_cs]
 for gid,game_rows in ordered:
  eligible=[r for r in game_rows if played[int(r['team_id'])]>=min_games and played[int(r['opponent_id'])]>=min_games]
  if eligible and train:
   raw=_raw_ppd(train);static={l:_solve_ppd_ridge(train,l) for l in static_lambdas};avg_games=sum(played.values())/max(len(played),1);dynamic={c:_solve_ppd_ridge(train,c/max(avg_games,1.0)) for c in dynamic_cs}
   for r in eligible:
    tid,oid=int(r['team_id']),int(r['opponent_id']);actual=metrics(offensive_totals(r))[0];wt=offensive_totals(r).resolved_possessions
    if actual is None or wt<=0:continue
    pred={}
    if tid in raw and raw[tid] is not None:pred['raw']=float(raw[tid])
    for l,s in static.items():
     if tid in s['offense_effect'] and oid in s['defense_effect']:pred[f'ridge_{l:g}']=s['baseline']+s['offense_effect'][tid]-s['defense_effect'][oid]
    for c,s in dynamic.items():
     if tid in s['offense_effect'] and oid in s['defense_effect']:pred[f'dyn_{c:g}']=s['baseline']+s['offense_effect'][tid]-s['defense_effect'][oid]
    prior=min(played[tid],played[oid]);bucket='4-5' if prior<=5 else '6-7' if prior<=7 else '8-9' if prior<=9 else '10+'
    obs.append({'actual':float(actual),'weight':float(wt),'pred':pred,'bucket':bucket})
  train.extend(game_rows)
  for r in game_rows:played[int(r['team_id'])]+=1
 errors={m:_error_block(obs,m) for m in models};buckets={}
 for b in ('4-5','6-7','8-9','10+'):
  sub=[x for x in obs if x['bucket']==b];buckets[b]={m:_error_block(sub,m) for m in models}
 return {'season':season,'observations':len(obs),'errors':errors,'buckets':buckets}

def aggregate(results):
 models=list(results[0]['errors']);out={}
 for m in models:
  blocks=[r['errors'][m] for r in results];wt=sum(b['weight'] for b in blocks);ae=sum(b['absolute_error'] for b in blocks);se=sum(b['squared_error'] for b in blocks)
  out[m]={'mae':ae/wt,'rmse':math.sqrt(se/wt),'weight':wt}
 return out

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('--seasons',nargs='+',type=int,default=[2022,2023,2024,2025]);p.add_argument('--root',type=Path,default=Path('data/canonical'));p.add_argument('--min-games',type=int,default=4);a=p.parse_args(argv)
 results=[];print('\nRidge Opponent Adjustment Chronological Backtest');print('Prior games only | target: next-game PPD | lower RMSE is better\n')
 for s in a.seasons:
  r=backtest(load(a.root/f'season={s}'/'team_games.json'),s,a.min_games);results.append(r);best=min(r['errors'],key=lambda m:r['errors'][m]['rmse']);print(f"{s}: {r['observations']} team-games | best {best} RMSE {r['errors'][best]['rmse']:.5f} | raw {r['errors']['raw']['rmse']:.5f}")
 pooled=aggregate(results);print('\nPOOLED LAMBDA SWEEP')
 for m,e in sorted(pooled.items(),key=lambda kv:kv[1]['rmse']):print(f"  {m:<12} MAE {e['mae']:.5f}  RMSE {e['rmse']:.5f}")
 best=min(pooled,key=lambda m:pooled[m]['rmse']);raw=pooled['raw']['rmse'];print(f"\nBest pooled: {best} | RMSE improvement vs raw {(raw-pooled[best]['rmse'])/raw*100:+.2f}%")
 print('\nBEST MODEL BY PRIOR-GAMES BUCKET')
 for b in ('4-5','6-7','8-9','10+'):
  combined={}
  for m in pooled:
   blocks=[r['buckets'][b][m] for r in results];wt=sum(x['weight'] for x in blocks);se=sum(x['squared_error'] for x in blocks);combined[m]=math.sqrt(se/wt) if wt else float('nan')
  valid={m:v for m,v in combined.items() if math.isfinite(v)};winner=min(valid,key=valid.get);print(f"  {b:<4} {winner:<12} RMSE {valid[winner]:.5f} | raw {valid['raw']:.5f}")
 return 0
if __name__=='__main__':raise SystemExit(main())
