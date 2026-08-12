"""Efficient partition-level team Havoc v1 metrics.

Expensive kneel and turnover anchoring is computed once per partition, then all
team offense/defense rows are accumulated in a single play scan.
"""
from __future__ import annotations
from collections import defaultdict
from cfb_analytics.analytics.havoc import _eligible,_sack,turnover_play_ids,HAVOC_VERSION
from cfb_analytics.analytics.tfl import high_confidence_kneel_ids,classify_tfl

def _rate(n,d):return n/d if d else None

def partition_team_havoc_metrics(plays,drives):
    kneels=high_confidence_kneel_ids(plays)
    turn_ids,_,unresolved,collisions=turnover_play_ids(drives,plays)
    m=defaultdict(lambda:defaultdict(int))
    for p in plays:
        if not _eligible(p):continue
        offense=p.get("offense");defense=p.get("defense");pid=id(p)
        is_tfl=classify_tfl(p,kneels);is_sack=_sack(p);is_turn=pid in turn_ids;is_havoc=is_tfl or is_sack or is_turn
        if offense:
            x=m[offense];x["havocEligiblePlays"]+=1;x["havocPlaysAllowed"]+=int(is_havoc);x["havocTflsAllowed"]+=int(is_tfl);x["havocSacksAllowed"]+=int(is_sack);x["havocTurnoversCommitted"]+=int(is_turn)
        if defense:
            x=m[defense];x["havocEligiblePlaysFaced"]+=1;x["havocPlays"]+=int(is_havoc);x["havocTfls"]+=int(is_tfl);x["havocSacks"]+=int(is_sack);x["havocTakeaways"]+=int(is_turn)
    out={}
    for team,x in m.items():
        d=dict(x);d["havocRateAllowed"]=_rate(d.get("havocPlaysAllowed",0),d.get("havocEligiblePlays",0));d["havocRate"]=_rate(d.get("havocPlays",0),d.get("havocEligiblePlaysFaced",0));d["havocTurnoverAnchorUnresolved"]=unresolved;d["havocTurnoverAnchorCollisions"]=collisions;d["havocDefinitionVersion"]=HAVOC_VERSION;out[team]=d
    return out

def team_havoc_metrics(team,plays,drives):
    """Compatibility wrapper; callers processing many teams should use partition_team_havoc_metrics."""
    return partition_team_havoc_metrics(plays,drives).get(team,{"havocEligiblePlays":0,"havocPlaysAllowed":0,"havocRateAllowed":None,"havocEligiblePlaysFaced":0,"havocPlays":0,"havocRate":None,"havocTflsAllowed":0,"havocSacksAllowed":0,"havocTurnoversCommitted":0,"havocTfls":0,"havocSacks":0,"havocTakeaways":0,"havocTurnoverAnchorUnresolved":0,"havocTurnoverAnchorCollisions":0,"havocDefinitionVersion":HAVOC_VERSION})
