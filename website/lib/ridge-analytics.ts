import {readJson} from "./server-data";

export type RidgeMetric = {value:number;rank:number;field_size:number};
export type RidgeSide = {rank:number;rating:number;field_size:number;metrics:Record<"ppd"|"ypd"|"success"|"scoring",RidgeMetric>};
export type RidgeOverview = {season:number;team:string;lambda:number;method:string;weights:Record<string,number>;offense:RidgeSide;defense:RidgeSide};

export type FanSeason = {
  games:number;
  yardsPerGame:number;
  yardsAllowedPerGame:number;
  yardsPerPlay:number;
  yardsAllowedPerPlay:number;
  rushYards:number;
  rushYardsAllowed:number;
  netPassYards:number;
  netPassYardsAllowed:number;
  rushYardsPerAttempt:number;
  rushYardsPerAttemptAllowed:number;
  netPassYardsPerDropback:number;
  netPassYardsPerDropbackAllowed:number;
  successRate:number;
  successRateAllowed:number;
  rushSuccessRate:number;
  rushSuccessRateAllowed:number;
  passSuccessRate:number;
  passSuccessRateAllowed:number;
  explosivePlayRate:number;
  explosivePlayRateAllowed:number;
  rushExplosivePlayRate:number;
  rushExplosivePlayRateAllowed:number;
  passExplosivePlayRate:number;
  passExplosivePlayRateAllowed:number;
  thirdDownConversionRate:number;
  thirdDownConversionRateAllowed:number;
  fourthDownConversionRate:number;
  fourthDownConversionRateAllowed:number;
  redZonePossessionScoringRate:number;
  redZonePossessionScoringRateAllowed:number;
  redZonePossessionTouchdownRate:number;
  redZonePossessionTouchdownRateAllowed:number;
  scoringRatePerPossession:number;
  scoringRatePerPossessionAllowed:number;
  pointsPerResolvedPossession:number;
  pointsPerResolvedPossessionAllowed:number;
  yardsPerPossession:number;
  yardsPerPossessionAllowed:number;
  sacks:number;
  sacksAllowed:number;
  tacklesForLoss:number;
  tacklesForLossAllowed:number;
  takeaways:number;
  giveaways:number;
  threeAndOuts:number;
  threeAndOutsForced:number;
  national_successRate_rank:number;
  national_successRateAllowed_rank:number;
  national_explosivePlayRate_rank:number;
  national_explosivePlayRateAllowed_rank:number;
  national_pointsPerOpportunity_rank:number;
  national_pointsPerOpportunityAllowed_rank:number;
  national_yardsPerSuccessfulPlay_rank:number;
  national_yardsPerSuccessfulPlayAllowed_rank:number;
};

export function ridgeOverview(season:number):RidgeOverview|null{
  return readJson<RidgeOverview>("data","published",String(season),"analytics","ridge-overview.json");
}

export function michiganFanSeason(season:number):FanSeason|null{
  const rows=readJson<FanSeason[]>("data","published",String(season),"teams","michigan","season.json");
  return rows?.[0]??null;
}

export function metricDisplay(metric:keyof RidgeSide["metrics"],value:number){
  if(metric==="ppd")return value.toFixed(2);
  if(metric==="ypd")return value.toFixed(1);
  return `${(value*100).toFixed(1)}%`;
}

export function rankDisplay(rank:number,fieldSize:number){return `#${rank} of ${fieldSize}`;}
export function pct(value:number){return `${(value*100).toFixed(1)}%`;}
export function perGame(total:number,games:number){return games?total/games:0;}

export function overviewTraits(data:RidgeOverview){
  const labels={ppd:"Points per drive",ypd:"Yards per drive",success:"Success rate",scoring:"Scoring drive rate"} as const;
  const entries=(Object.keys(labels) as Array<keyof typeof labels>).flatMap(metric=>[
    {side:"Offense" as const,metric,label:`${labels[metric]} offense`,...data.offense.metrics[metric],quality:1-(data.offense.metrics[metric].rank-1)/Math.max(1,data.offense.metrics[metric].field_size-1)},
    {side:"Defense" as const,metric,label:`${labels[metric]} defense`,...data.defense.metrics[metric],quality:1-(data.defense.metrics[metric].rank-1)/Math.max(1,data.defense.metrics[metric].field_size-1)},
  ]);
  const sorted=[...entries].sort((a,b)=>b.quality-a.quality);
  return {strengths:sorted.slice(0,3),concerns:[...sorted].reverse().slice(0,3)};
}
