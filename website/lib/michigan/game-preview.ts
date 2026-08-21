import {readJson} from "../server-data";
import type {MichiganScheduleGame} from "./types";
import {opponent} from "./games";

const slug=(name:string)=>name.toLowerCase().replace(/&/g,"and").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");

type SeasonProfile={team:string;team_id:number;games:number;yardsPerGame:number;yardsAllowedPerGame:number;successRate:number;successRateAllowed:number;national_successRate_rank:number;national_successRateAllowed_rank:number;national_explosivePlayRate_rank:number;national_explosivePlayRateAllowed_rank:number};
type TimelineRow={playerId:string;team:string;recruiting?:{name?:string;position?:string;rating?:number|null;stars?:number|null;ranking?:number|null;grade?:string|null}|null;timeline:Array<{season:number;team:string;position?:string;jersey?:number|null;year?:number|null}>};

function seasonProfile(team:string){return (readJson<SeasonProfile[]>("data","published","2025","teams",slug(team),"season.json")??[])[0]??null}
function currentDirectory(team:string){return readJson<TimelineRow[]>("data","published","directory_history","players","current-by-team",`${slug(team)}.json`)??[]}

function rosterMovement(team:string){
  const rows=currentDirectory(team);
  const returning=rows.filter(r=>r.timeline.some(t=>t.season===2025&&t.team===team)&&r.timeline.some(t=>t.season===2026&&t.team===team));
  const transfers=rows.filter(r=>{const now=r.timeline.find(t=>t.season===2026&&t.team===team);const prev=r.timeline.find(t=>t.season===2025);return !!now&&!!prev&&prev.team!==team}).map(r=>{
    const prev=r.timeline.find(t=>t.season===2025)!;
    return {name:r.recruiting?.name??`Player ${r.playerId}`,position:r.timeline.find(t=>t.season===2026)?.position??r.recruiting?.position??"—",from:prev.team,rating:r.recruiting?.rating??null,stars:r.recruiting?.stars??null,rank:r.recruiting?.ranking??null,grade:r.recruiting?.grade??null};
  }).sort((a,b)=>(b.rating??0)-(a.rating??0));
  const continuity=rows.length?returning.length/rows.length:null;
  const rated=transfers.filter(t=>t.rating!=null);
  const avgRating=rated.length?rated.reduce((s,t)=>s+(t.rating??0),0)/rated.length:null;
  const transferValue=avgRating==null?"UNRATED":avgRating>=.90?"HIGH":avgRating>=.86?"SOLID":"DEPTH";
  return {rosterSize:rows.length,returningCount:returning.length,continuity,transfers,transferValue,avgRating};
}

export function gamePreview(game:MichiganScheduleGame){
  const opp=opponent(game);
  const michigan2025=seasonProfile("Michigan");
  const opponent2025=seasonProfile(opp.name);
  const michiganMovement=rosterMovement("Michigan");
  const opponentMovement=rosterMovement(opp.name);
  return {opp,michigan2025,opponent2025,michiganMovement,opponentMovement};
}

export function offenseRank(profile:SeasonProfile|null){
  if(!profile)return null;
  return Math.round((profile.national_successRate_rank+profile.national_explosivePlayRate_rank)/2);
}

export function defenseRank(profile:SeasonProfile|null){
  if(!profile)return null;
  return Math.round((profile.national_successRateAllowed_rank+profile.national_explosivePlayRateAllowed_rank)/2);
}

export function profileRank(profile:SeasonProfile|null){
  if(!profile)return null;
  return Math.round((profile.national_successRate_rank+profile.national_successRateAllowed_rank+profile.national_explosivePlayRate_rank+profile.national_explosivePlayRateAllowed_rank)/4);
}
