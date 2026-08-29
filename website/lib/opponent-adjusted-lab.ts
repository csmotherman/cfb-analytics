import {readJson} from "./server-data";

export type LabMetricMeta={k:string;l:string;u:"rate"|"yards"|string;f:"binomial"|"gaussian"|string};
export type LabMetricRating=[number|null,number|null,number|null,number|null];
export type LabTeam={
  id:string;
  n:string;
  s:string;
  c:string;
  os:number|null;
  ds:number|null;
  xs:number|null;
  or:number;
  dr:number;
  xr:number;
  m:LabMetricRating[];
};
export type LabGameMetric=[
  number|null,number|null,number|null,number|null,number,
  number|null,number|null,number|null,number|null,number
];
export type LabGame={
  id:string;
  w:number|null;
  p:number;
  st:string;
  t:string;
  o:string;
  on:string;
  ha:string;
  n:boolean;
  pf:number|null;
  pa:number|null;
  m:LabGameMetric[];
};
export type OpponentAdjustedLabData={
  v:string;
  season:number;
  ridge:number;
  homeRidge:number;
  metrics:LabMetricMeta[];
  teams:LabTeam[];
  games:LabGame[];
};

const CANDIDATE_SEASONS=Array.from({length:17},(_,index)=>2010+index);

export function opponentAdjustedLab(season:number):OpponentAdjustedLabData|null{
  return readJson<OpponentAdjustedLabData>(
    "data","published",String(season),"analytics","opponent-adjusted-lab.json"
  );
}

export function opponentAdjustedLabSeasons():number[]{
  return CANDIDATE_SEASONS.filter(season=>opponentAdjustedLab(season)!==null);
}
