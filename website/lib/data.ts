import fs from "node:fs";
import path from "node:path";

export type PowerRow = {
  season:number;
  team:string;
  allTimeSimRank?:number;
  allTimeRank?:number;
  fieldWinPct?:number;
  averageNeutralMargin?:number;
  top25WinPct?:number;
  [key:string]:unknown;
};

export type DynamicIdentityRow = {
  season:number;
  team:string;
  identityName?:string;
  identityTags?:string[];
  identitySummary?:string;
  identityStyle?:Record<string,unknown>;
  identityVersion?:string;
  consistency?:Record<string,unknown>;
  [key:string]:unknown;
};

export type SituationalRow = {
  version:string;
  season:number;
  team:string;
  side:"offense"|"defense";
  quarter:number|"OT";
  half:number|"OT";
  down:number;
  distance:number;
  fieldPositionBucket:string;
  redZone:boolean;
  goalToGo:boolean;
  scoreState:string;
  plays:number;
  successes:number;
  yards:number;
  firstDowns:number;
  rushPlays:number;
  passPlays:number;
  rushSuccesses:number;
  passSuccesses:number;
  rushYards:number;
  passYards:number;
  explosiveEligiblePlays:number;
  explosivePlays:number;
  conversionAttempts:number;
  conversions:number;
  [key:string]:unknown;
};

const PROJECT_ROOT = path.resolve(process.cwd(), "..");

function readJson(relative:string):any|null{
  const file = path.join(PROJECT_ROOT, relative);
  if(!fs.existsSync(file)) return null;
  try{return JSON.parse(fs.readFileSync(file,"utf8"));}catch{return null;}
}

function asRows(payload:any):any[]{
  if(Array.isArray(payload)) return payload;
  for(const key of ["rankings","rows","matches","teamSeasons","results","states"]){
    if(Array.isArray(payload?.[key])) return payload[key];
  }
  return [];
}

export function tournamentRows():PowerRow[]{
  const payload = readJson("data/processed/derived/profiles/historical_cross_era_tournament_2014_2025.json");
  return asRows(payload) as PowerRow[];
}

export function dynamicIdentityRows():DynamicIdentityRow[]{
  const payload = readJson("data/processed/derived/profiles/dynamic_team_identities.json");
  return asRows(payload) as DynamicIdentityRow[];
}

export function findDynamicIdentity(team:string,season:number):DynamicIdentityRow|null{
  return dynamicIdentityRows().find(r=>Number(r.season)===Number(season)&&String(r.team||"").toLowerCase()===team.toLowerCase())||null;
}

export function situationalRows(team:string,season:number):SituationalRow[]{
  const payload=readJson(`data/processed/derived/situational_splits/season=${season}/situational_splits.json`);
  return (asRows(payload) as SituationalRow[]).filter(r=>String(r.team||"").toLowerCase()===team.toLowerCase());
}

export function archetypeRows():any[]{
  const payload = readJson("data/processed/derived/profiles/historical_archetype_layers_2014_2024.json");
  return asRows(payload);
}

export function datasetStatus(){
  const files = [
    ["Cross-era rankings","data/processed/derived/profiles/historical_cross_era_tournament_2014_2025.json"],
    ["Simulator cache","data/processed/derived/profiles/historical_game_simulator_cache.json"],
    ["Dynamic team identities","data/processed/derived/profiles/dynamic_team_identities.json"],
  ] as const;
  return files.map(([label,relative])=>({label,relative,ready:fs.existsSync(path.join(PROJECT_ROOT,relative))}));
}

export function seasonsAndTeams(){
  const rows=tournamentRows();
  const seasons=[...new Set(rows.map(r=>Number(r.season)).filter(Number.isFinite))].sort((a,b)=>b-a);
  const teams=[...new Set(rows.map(r=>String(r.team||"")).filter(Boolean))].sort();
  return {seasons,teams};
}

export function findPowerRow(team:string,season:number){
  return tournamentRows().find(r=>Number(r.season)===Number(season)&&String(r.team).toLowerCase()===team.toLowerCase());
}

export function fieldWinPct(row:any):number|null{
  for(const key of ["fieldWinPct","fieldWinProbability","expectedWinPct","winPct","fieldWinRate"]){
    const v=Number(row?.[key]); if(Number.isFinite(v)) return v>1?v/100:v;
  }
  return null;
}

export function avgMargin(row:any):number|null{
  for(const key of ["averageNeutralMargin","avgNeutralMargin","averageMargin","avgMargin"]){
    const v=Number(row?.[key]); if(Number.isFinite(v)) return v;
  }
  return null;
}

export function rankOf(row:any):number|null{
  for(const key of ["allTimeSimRank","allTimeRank","rank","powerRank"]){const v=Number(row?.[key]);if(Number.isFinite(v))return v;}
  return null;
}

export function projectRoot(){return PROJECT_ROOT;}
