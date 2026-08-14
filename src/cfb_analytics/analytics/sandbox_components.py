"""Compact game-level components for fast leakage-safe Sandbox ratings."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

from cfb_analytics.analytics.cfb_sandbox_systems import EXPLOSIVE_YARDS,_clean_play,_num,_points,_rate,_valid_drive
from cfb_analytics.analytics.cfb_sandbox_systems_aligned import SANDBOX_SYSTEMS_VERSION,_drive_key,red_zone_points_per_trip,true_three_and_out
from cfb_analytics.analytics.success import classify_success
from cfb_analytics.analytics.turnovers import build_play_index,team_turnover_metrics

COMPONENT_VERSION="cfb-sandbox-components-v1"


def _sum_success(rows):
 vals=[classify_success(p) for p in rows];vals=[v for v in vals if v is not None]
 return sum(bool(v) for v in vals),len(vals)

def build_game_components(plays,drives,season,season_type,week):
 by_game_p=defaultdict(list);by_game_d=defaultdict(list)
 for p in plays:by_game_p[str(p.get("gameId"))].append(p)
 for d in drives:by_game_d[str(d.get("gameId"))].append(d)
 out=[]
 for gid in sorted(set(by_game_p)|set(by_game_d)):
  gp=by_game_p[gid];gd=by_game_d[gid];vd=[d for d in gd if _valid_drive(d) and _points(d) is not None];cp=[p for p in gp if _clean_play(p)]
  teams=sorted({d.get("offense") for d in vd if d.get("offense")}|{d.get("defense") for d in vd if d.get("defense")})
  by_drive=defaultdict(list)
  for p in gp:by_drive[_drive_key(p)].append(p)
  game_plays={gid:gp};turn_idx=build_play_index(gp)
  for t in teams:
   od=[d for d in vd if d.get("offense")==t];dd=[d for d in vd if d.get("defense")==t];op=[p for p in cp if p.get("offense")==t];dp=[p for p in cp if p.get("defense")==t]
   row={"season":season,"seasonType":season_type,"week":week,"gameId":gid,"team":t,"sandboxSystemsVersion":SANDBOX_SYSTEMS_VERSION,"sandboxComponentVersion":COMPONENT_VERSION}
   row["offPoints"]=sum(float(_points(d)) for d in od);row["offPoss"]=len(od);row["defPoints"]=sum(float(_points(d)) for d in dd);row["defPoss"]=len(dd)
   row["offExplosive"]=sum(_num(p.get("analyticsYardsGained")) and float(p["analyticsYardsGained"])>=EXPLOSIVE_YARDS for p in op);row["offPlays"]=len(op)
   row["defExplosive"]=sum(_num(p.get("analyticsYardsGained")) and float(p["analyticsYardsGained"])>=EXPLOSIVE_YARDS for p in dp);row["defPlays"]=len(dp)
   row["offThreeOut"]=sum(true_three_and_out(d,by_drive.get(_drive_key(d),[]),turn_idx) for d in od);row["defThreeOut"]=sum(true_three_and_out(d,by_drive.get(_drive_key(d),[]),turn_idx) for d in dd)
   row["offThirdSuccess"],row["offThirdEligible"]=_sum_success([p for p in op if p.get("down")==3]);row["defThirdSuccess"],row["defThirdEligible"]=_sum_success([p for p in dp if p.get("down")==3])
   rz=red_zone_points_per_trip(od,by_drive,game_plays);rz_d=red_zone_points_per_trip(dd,by_drive,game_plays)
   row["offRzPoints"]=rz["points"];row["offRzResolved"]=rz["resolved"];row["offRzTrips"]=rz["trips"];row["defRzPoints"]=rz_d["points"];row["defRzResolved"]=rz_d["resolved"];row["defRzTrips"]=rz_d["trips"]
   tm=team_turnover_metrics(t,gd,gp);row["giveaways"]=tm["giveaways"];row["turnoverResolvedPossessions"]=tm["turnoverResolvedPossessions"];row["takeaways"]=tm["takeaways"];row["takeawayResolvedPossessions"]=tm["takeawayResolvedPossessions"]
   for label,periods in (("H1",{1,2}),("H2",{3,4})):
    ods=[d for d in od if d.get("startPeriod") in periods];dds=[d for d in dd if d.get("startPeriod") in periods]
    row[f"off{label}Points"]=sum(float(_points(d)) for d in ods);row[f"off{label}Poss"]=len(ods);row[f"def{label}Points"]=sum(float(_points(d)) for d in dds);row[f"def{label}Poss"]=len(dds)
    row[f"off{label}Success"],row[f"off{label}Eligible"]=_sum_success([p for p in op if p.get("period") in periods]);row[f"def{label}Success"],row[f"def{label}Eligible"]=_sum_success([p for p in dp if p.get("period") in periods])
   close=[d for d in vd if d.get("startPeriod") in {3,4} and _num(d.get("startOffenseScore")) and _num(d.get("startDefenseScore")) and abs(float(d["startOffenseScore"])-float(d["startDefenseScore"]))<=7];close_ids={str(d.get("driveId")) for d in close}
   cop=[p for p in op if str(p.get("driveId")) in close_ids];cdp=[p for p in dp if str(p.get("driveId")) in close_ids]
   co=[d for d in close if d.get("offense")==t];cd=[d for d in close if d.get("defense")==t]
   row["offClosePoints"]=sum(float(_points(d)) for d in co);row["offCloseDrives"]=len(co);row["defClosePoints"]=sum(float(_points(d)) for d in cd);row["defCloseDrives"]=len(cd)
   row["offCloseSuccess"],row["offCloseEligible"]=_sum_success(cop);row["defCloseSuccess"],row["defCloseEligible"]=_sum_success(cdp)
   out.append(row)
 return out

def write_components(processed_root:Path,season:int,rows):
 root=processed_root/"derived"/"sandbox_components"/f"season={season}";root.mkdir(parents=True,exist_ok=True);path=root/"team_games.json";path.write_text(json.dumps(rows,ensure_ascii=False,separators=(",",":")));return path
