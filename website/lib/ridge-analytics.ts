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

type FanGame = {
  win?:number|boolean;
  loss?:number|boolean;
  seasonType?:string;
  season_type?:string;
};

export type FanRecord = {
  wins:number;
  losses:number;
  record:string;
  regular:{wins:number;losses:number;record:string;games:number};
  postseason:{wins:number;losses:number;record:string;games:number};
};

export type FanTier = "elite"|"strong"|"average"|"concern";

export function ridgeOverview(season:number):RidgeOverview|null{
  return readJson<RidgeOverview>("data","published",String(season),"analytics","ridge-overview.json");
}

export function michiganFanSeason(season:number):FanSeason|null{
  const rows=readJson<FanSeason[]>("data","published",String(season),"teams","michigan","season.json");
  return rows?.[0]??null;
}

export function michiganRecord(season:number):FanRecord|null{
  const rows=readJson<FanGame[]>("data","published",String(season),"teams","michigan","games.json");
  if(!rows?.length)return null;
  const buckets={regular:{wins:0,losses:0,games:0},postseason:{wins:0,losses:0,games:0}};
  for(const game of rows){
    const type=String(game.seasonType??game.season_type??"regular").toLowerCase();
    const bucket=type.includes("regular")?buckets.regular:buckets.postseason;
    const won=game.win===true || Number(game.win)===1;
    const lost=game.loss===true || Number(game.loss)===1;
    if(!won&&!lost)continue;
    bucket.games+=1;
    if(won)bucket.wins+=1;
    if(lost)bucket.losses+=1;
  }
  const wins=buckets.regular.wins+buckets.postseason.wins;
  const losses=buckets.regular.losses+buckets.postseason.losses;
  return {
    wins,
    losses,
    record:`${wins}-${losses}`,
    regular:{...buckets.regular,record:`${buckets.regular.wins}-${buckets.regular.losses}`},
    postseason:{...buckets.postseason,record:`${buckets.postseason.wins}-${buckets.postseason.losses}`},
  };
}

export function metricDisplay(metric:keyof RidgeSide["metrics"],value:number){
  if(metric==="ppd")return value.toFixed(2);
  if(metric==="ypd")return value.toFixed(1);
  return `${(value*100).toFixed(1)}%`;
}

export function rankDisplay(rank:number,fieldSize:number){return `#${rank} of ${fieldSize}`;}
export function pct(value:number){return `${(value*100).toFixed(1)}%`;}
export function perGame(total:number,games:number){return games?total/games:0;}

export function fanTier(rank:number,fieldSize:number):FanTier{
  const pctRank=rank/Math.max(1,fieldSize);
  if(rank<=10 || pctRank<=.08)return "elite";
  if(rank<=30 || pctRank<=.25)return "strong";
  if(pctRank<=.58)return "average";
  return "concern";
}

export function fanTierLabel(rank:number,fieldSize:number){
  const tier=fanTier(rank,fieldSize);
  if(tier==="elite")return "ELITE";
  if(tier==="strong")return "SOLID";
  if(tier==="average")return "AVERAGE";
  return "CONCERN";
}

export function fanMetricName(side:"Offense"|"Defense",metric:keyof RidgeSide["metrics"]){
  const labels={
    Offense:{ppd:"Making Drives Count",ypd:"Moving the Ball",success:"Staying Ahead of the Chains",scoring:"Finishing Drives"},
    Defense:{ppd:"Keeping Teams Off the Board",ypd:"Limiting Long Drives",success:"Knocking Offenses Off Schedule",scoring:"Ending Drives Empty"},
  } as const;
  return labels[side][metric];
}

export function fanMetricExplanation(side:"Offense"|"Defense",metric:keyof RidgeSide["metrics"]){
  const copy={
    Offense:{
      ppd:"Michigan turns possessions into points efficiently, with opponent strength already accounted for.",
      ypd:"Michigan consistently moves the field and creates better scoring position over the course of a drive.",
      success:"Michigan wins enough plays to stay out of bad down-and-distance situations and keep the playbook open.",
      scoring:"Michigan finishes a high share of possessions with points instead of coming away empty.",
    },
    Defense:{
      ppd:"Michigan makes opponents work for points and limits scoring efficiency after opponent strength is accounted for.",
      ypd:"Michigan prevents opponents from stacking first downs and sustaining long drives.",
      success:"Michigan forces offenses behind schedule and into tougher second- and third-down situations.",
      scoring:"Michigan ends opponent possessions without points at a strong rate.",
    },
  } as const;
  return copy[side][metric];
}

export function overviewTraits(data:RidgeOverview){
  const entries=(Object.keys(data.offense.metrics) as Array<keyof RidgeSide["metrics"]>).flatMap(metric=>[
    {side:"Offense" as const,metric,label:fanMetricName("Offense",metric),explanation:fanMetricExplanation("Offense",metric),...data.offense.metrics[metric],quality:1-(data.offense.metrics[metric].rank-1)/Math.max(1,data.offense.metrics[metric].field_size-1)},
    {side:"Defense" as const,metric,label:fanMetricName("Defense",metric),explanation:fanMetricExplanation("Defense",metric),...data.defense.metrics[metric],quality:1-(data.defense.metrics[metric].rank-1)/Math.max(1,data.defense.metrics[metric].field_size-1)},
  ]);
  const sorted=[...entries].sort((a,b)=>b.quality-a.quality);
  return {strengths:sorted.slice(0,3),concerns:[...sorted].reverse().slice(0,3)};
}
