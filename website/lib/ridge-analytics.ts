import {readJson} from "./server-data";

export type RidgeMetric = {value:number;rank:number;field_size:number};
export type RidgeSide = {rank:number;rating:number;field_size:number;metrics:Record<"ppd"|"ypd"|"success"|"scoring",RidgeMetric>};
export type RidgeOverview = {season:number;team:string;lambda:number;method:string;weights:Record<string,number>;offense:RidgeSide;defense:RidgeSide};

export function ridgeOverview(season:number):RidgeOverview|null{
  return readJson<RidgeOverview>("data","published",String(season),"analytics","ridge-overview.json");
}

export function metricDisplay(metric:keyof RidgeSide["metrics"],value:number){
  if(metric==="ppd")return value.toFixed(2);
  if(metric==="ypd")return value.toFixed(1);
  return `${(value*100).toFixed(1)}%`;
}

export function rankDisplay(rank:number,fieldSize:number){return `#${rank} of ${fieldSize}`;}

export function overviewTraits(data:RidgeOverview){
  const labels={ppd:"Points per drive",ypd:"Yards per drive",success:"Success rate",scoring:"Scoring drive rate"} as const;
  const entries=(Object.keys(labels) as Array<keyof typeof labels>).flatMap(metric=>[
    {side:"Offense" as const,metric,label:`${labels[metric]} offense`,...data.offense.metrics[metric],quality:1-(data.offense.metrics[metric].rank-1)/Math.max(1,data.offense.metrics[metric].field_size-1)},
    {side:"Defense" as const,metric,label:`${labels[metric]} defense`,...data.defense.metrics[metric],quality:1-(data.defense.metrics[metric].rank-1)/Math.max(1,data.defense.metrics[metric].field_size-1)},
  ]);
  const sorted=[...entries].sort((a,b)=>b.quality-a.quality);
  return {strengths:sorted.slice(0,3),concerns:[...sorted].reverse().slice(0,3)};
}
