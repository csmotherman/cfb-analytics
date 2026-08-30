import {opponentAdjustedLab, type LabGame, type LabMetricMeta, type LabTeam} from "./opponent-adjusted-lab";

export type GameMetricMeta={key:string;label:string;unit:string;explanation:string};
export type GameMetricSplit={actual:number|null;expected:number|null;poe:number|null};
export type GameMetricView={key:string;label:string;unit:string;explanation:string;offense:GameMetricSplit;defense:GameMetricSplit};
export type TeamMetricProfile={
  key:string;
  label:string;
  unit:string;
  offenseValue:number|null;
  offenseRank:number|null;
  defenseValue:number|null;
  defenseRank:number|null;
};
export type TeamProfile={
  id:string;
  name:string;
  conference:string;
  offenseScore:number|null;
  defenseScore:number|null;
  overallScore:number|null;
  offenseRank:number|null;
  defenseRank:number|null;
  overallRank:number|null;
  metrics:TeamMetricProfile[];
};
export type MichiganGameDossier={
  id:string;
  week:number|null;
  order:number;
  seasonType:string;
  homeAway:string;
  neutral:boolean;
  opponentName:string;
  pf:number|null;
  pa:number|null;
  result:string;
  opponent:TeamProfile;
  michiganMetrics:GameMetricView[];
  opponentMetrics:GameMetricView[];
};
export type CreatorGameLibrary={
  season:number;
  ridge:number;
  homeRidge:number;
  fieldSize:number;
  metrics:GameMetricMeta[];
  michigan:TeamProfile;
  games:MichiganGameDossier[];
};

const finite=(value:unknown):value is number=>typeof value==="number"&&Number.isFinite(value);

const EXPLANATIONS:Record<string,string>={
  successRate:"How often an offense gained enough yards to stay on schedule. Higher is better for the offense.",
  rushSuccessRate:"How often designed runs gained enough yards to keep the offense on schedule.",
  passSuccessRate:"How often dropbacks gained enough yards to keep the offense on schedule.",
  explosivePlayRate:"How often a play created an explosive gain. It captures big-play frequency, not just average yardage.",
  yardsPerPlay:"Average yards gained per offensive play. Useful for overall efficiency, but it can hide inconsistency if a few big plays carry the average.",
};

function split(values:LabGame["m"][number]|undefined,offset:number):GameMetricSplit{
  if(!values)return {actual:null,expected:null,poe:null};
  return {
    actual:finite(values[offset])?values[offset] as number:null,
    expected:finite(values[offset+1])?values[offset+1] as number:null,
    poe:finite(values[offset+2])?values[offset+2] as number:null,
  };
}

function teamProfile(team:LabTeam,metrics:LabMetricMeta[]):TeamProfile{
  return {
    id:team.id,
    name:team.n,
    conference:team.c,
    offenseScore:finite(team.os)?team.os:null,
    defenseScore:finite(team.ds)?team.ds:null,
    overallScore:finite(team.xs)?team.xs:null,
    offenseRank:finite(team.or)?team.or:null,
    defenseRank:finite(team.dr)?team.dr:null,
    overallRank:finite(team.xr)?team.xr:null,
    metrics:metrics.map((metric,index)=>{
      const rating=team.m[index];
      return {
        key:metric.k,
        label:metric.l,
        unit:metric.u,
        offenseValue:rating&&finite(rating[0])?rating[0]:null,
        offenseRank:rating&&finite(rating[1])?rating[1]:null,
        defenseValue:rating&&finite(rating[2])?rating[2]:null,
        defenseRank:rating&&finite(rating[3])?rating[3]:null,
      };
    }),
  };
}

function metricViews(game:LabGame,metrics:LabMetricMeta[]):GameMetricView[]{
  return metrics.map((metric,index)=>({
    key:metric.k,
    label:metric.l,
    unit:metric.u,
    explanation:EXPLANATIONS[metric.k]??metric.l,
    offense:split(game.m[index],0),
    defense:split(game.m[index],5),
  }));
}

export function creatorGameLibrary(season=2025):CreatorGameLibrary|null{
  const data=opponentAdjustedLab(season);
  if(!data)return null;

  const michigan=data.teams.find(team=>team.n.toLowerCase()==="michigan");
  if(!michigan)return null;

  const teamById=new Map(data.teams.map(team=>[team.id,team]));
  const gameByTeam=new Map(data.games.map(game=>[`${game.id}:${game.t}`,game]));
  const michiganProfile=teamProfile(michigan,data.metrics);

  const games=data.games
    .filter(game=>game.t===michigan.id)
    .sort((a,b)=>a.p-b.p||a.id.localeCompare(b.id))
    .flatMap(game=>{
      const opponentTeam=teamById.get(game.o);
      const opponentGame=gameByTeam.get(`${game.id}:${game.o}`);
      if(!opponentTeam||!opponentGame)return [];
      const pf=finite(game.pf)?game.pf:null;
      const pa=finite(game.pa)?game.pa:null;
      const result=pf==null||pa==null?"—":pf>pa?"W":pf<pa?"L":"T";
      return [{
        id:game.id,
        week:game.w,
        order:game.p,
        seasonType:game.st,
        homeAway:game.ha,
        neutral:game.n,
        opponentName:game.on,
        pf,
        pa,
        result,
        opponent:teamProfile(opponentTeam,data.metrics),
        michiganMetrics:metricViews(game,data.metrics),
        opponentMetrics:metricViews(opponentGame,data.metrics),
      } satisfies MichiganGameDossier];
    });

  return {
    season:data.season,
    ridge:data.ridge,
    homeRidge:data.homeRidge,
    fieldSize:data.teams.length,
    metrics:data.metrics.map(metric=>({
      key:metric.k,
      label:metric.l,
      unit:metric.u,
      explanation:EXPLANATIONS[metric.k]??metric.l,
    })),
    michigan:michiganProfile,
    games,
  };
}
