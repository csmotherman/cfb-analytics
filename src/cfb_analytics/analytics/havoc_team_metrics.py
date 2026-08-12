"""Team-level Havoc v1 metrics built from the locked play-level definition."""
from __future__ import annotations
from cfb_analytics.analytics.havoc import _eligible,_sack,turnover_play_ids,HAVOC_VERSION
from cfb_analytics.analytics.tfl import high_confidence_kneel_ids,classify_tfl

def _rate(n,d):return n/d if d else None

def team_havoc_metrics(team,plays,drives):
    kneels=high_confidence_kneel_ids(plays);turn_ids,outcomes,unresolved,collisions=turnover_play_ids(drives,plays)
    off_eligible=def_eligible=off_havoc=def_havoc=0
    off_tfl=def_tfl=off_sack=def_sack=off_turn=def_turn=0
    for p in plays:
        if not _eligible(p):continue
        offense=p.get("offense");defense=p.get("defense");pid=id(p)
        is_tfl=classify_tfl(p,kneels);is_sack=_sack(p);is_turn=pid in turn_ids;is_havoc=is_tfl or is_sack or is_turn
        if offense==team:
            off_eligible+=1;off_havoc+=int(is_havoc);off_tfl+=int(is_tfl);off_sack+=int(is_sack);off_turn+=int(is_turn)
        if defense==team:
            def_eligible+=1;def_havoc+=int(is_havoc);def_tfl+=int(is_tfl);def_sack+=int(is_sack);def_turn+=int(is_turn)
    return {"havocEligiblePlays":off_eligible,"havocPlaysAllowed":off_havoc,"havocRateAllowed":_rate(off_havoc,off_eligible),"havocEligiblePlaysFaced":def_eligible,"havocPlays":def_havoc,"havocRate":_rate(def_havoc,def_eligible),"havocTflsAllowed":off_tfl,"havocSacksAllowed":off_sack,"havocTurnoversCommitted":off_turn,"havocTfls":def_tfl,"havocSacks":def_sack,"havocTakeaways":def_turn,"havocTurnoverAnchorUnresolved":unresolved,"havocTurnoverAnchorCollisions":collisions,"havocDefinitionVersion":HAVOC_VERSION}
