import {opponentAdjustedLab, type LabGame, type LabMetricMeta, type LabTeam} from "./opponent-adjusted-lab";

export type CreatorMetric={key:string;label:string;unit:string};
export type CreatorSplit={actual:number|null;expected:number|null;poe:number|null};
export type CreatorGameMetric={key:string;label:string;unit:string;offense:CreatorSplit;defense:CreatorSplit};
export type CreatorGame={
  id:string;
  week:number|null;
  opponent:string;
  pf:number|null;
  pa:number|null;
  result:string;
  opponentOffRank:number|null;
  opponentDefRank:number|null;
  opponentOverallRank:number|null;
  opponentOverallScore:number|null;
  metrics:CreatorGameMetric[];
};
export type CreatorProfileMetric={
  key:string;
  label:string;
  unit:string;
  offenseValue:number|null;
  offenseRank:number|null;
  offensePercentile:number|null;
  defenseValue:number|null;
  defenseRank:number|null;
  defensePercentile:number|null;
};
export type CreatorTeamProfile={
  name:string;
  conference:string;
  offenseScore:number|null;
  defenseScore:number|null;
  overallScore:number|null;
  offenseRank:number|null;
  defenseRank:number|null;
  overallRank:number|null;
  metrics:CreatorProfileMetric[];
};
export type CreatorBigTenTeam={
  name:string;
  offenseScore:number;
  defenseScore:number;
  overallScore:number;
  offenseRank:number;
  defenseRank:number;
  overallRank:number;
};
export type CreatorSpotlights={
  oklahoma:CreatorGame|null;
  washington:CreatorGame|null;
  ohioState:CreatorGame|null;
  usc:CreatorGame|null;
  wisconsin:CreatorGame|null;
};
export type CreatorChartPack={
  season:number;
  ridge:number;
  homeRidge:number;
  fieldSize:number;
  metrics:CreatorMetric[];
  michigan:CreatorTeamProfile;
  utah:CreatorTeamProfile;
  byu:CreatorTeamProfile;
  michiganGames:CreatorGame[];
  bigTen:CreatorBigTenTeam[];
  spotlights:CreatorSpotlights;
};

const finite=(value:unknown):value is number=>typeof value==="number"&&Number.isFinite(value);

function percentile(rank:number|null,field:number){
  if(rank==null||field<=1)return null;
  return 100*(field-rank)/(field-1);
}

function split(values:LabGame["m"][number]|undefined,offset:number):CreatorSplit{
  if(!values)return {actual:null,expected:null,poe:null};
  return {
    actual:finite(values[offset])?values[offset] as number:null,
    expected:finite(values[offset+1])?values[offset+1] as number:null,
    poe:finite(values[offset+2])?values[offset+2] as number:null,
  };
}

function teamProfile(team:LabTeam,metrics:LabMetricMeta[],field:number):CreatorTeamProfile{
  return {
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
      const offenseValue=rating&&finite(rating[0])?rating[0]:null;
      const offenseRank=rating&&finite(rating[1])?rating[1]:null;
      const defenseValue=rating&&finite(rating[2])?rating[2]:null;
      const defenseRank=rating&&finite(rating[3])?rating[3]:null;
      return {
        key:metric.k,
        label:metric.l,
        unit:metric.u,
        offenseValue,
        offenseRank,
        offensePercentile:percentile(offenseRank,field),
        defenseValue,
        defenseRank,
        defensePercentile:percentile(defenseRank,field),
      };
    }),
  };
}

function gameView(game:LabGame,metrics:LabMetricMeta[],teamById:Map<string,LabTeam>):CreatorGame{
  const opponent=teamById.get(game.o);
  const pf=finite(game.pf)?game.pf:null;
  const pa=finite(game.pa)?game.pa:null;
  const result=pf==null||pa==null?"—":pf>pa?"W":pf<pa?"L":"T";
  return {
    id:game.id,
    week:game.w,
    opponent:game.on,
    pf,
    pa,
    result,
    opponentOffRank:opponent&&finite(opponent.or)?opponent.or:null,
    opponentDefRank:opponent&&finite(opponent.dr)?opponent.dr:null,
    opponentOverallRank:opponent&&finite(opponent.xr)?opponent.xr:null,
    opponentOverallScore:opponent&&finite(opponent.xs)?opponent.xs:null,
    metrics:metrics.map((metric,index)=>({
      key:metric.k,
      label:metric.l,
      unit:metric.u,
      offense:split(game.m[index],0),
      defense:split(game.m[index],5),
    })),
  };
}

export function creatorChartPack(season=2025):CreatorChartPack|null{
  const data=opponentAdjustedLab(season);
  if(!data)return null;

  const teamById=new Map(data.teams.map(team=>[team.id,team]));
  const findTeam=(name:string)=>data.teams.find(team=>team.n.toLowerCase()===name.toLowerCase());
  const michigan=findTeam("Michigan");
  const utah=findTeam("Utah");
  const byu=findTeam("BYU");
  if(!michigan||!utah||!byu)return null;

  const regularGames=data.games
    .filter(game=>game.t===michigan.id&&String(game.st).toLowerCase().includes("regular"))
    .sort((a,b)=>a.p-b.p||a.id.localeCompare(b.id))
    .map(game=>gameView(game,data.metrics,teamById));

  const byOpponent=(name:string)=>regularGames.find(game=>game.opponent.toLowerCase()===name.toLowerCase())??null;

  const bigTen=data.teams
    .filter(team=>team.c==="Big Ten"&&finite(team.os)&&finite(team.ds)&&finite(team.xs)&&finite(team.or)&&finite(team.dr)&&finite(team.xr))
    .map(team=>({
      name:team.n,
      offenseScore:team.os as number,
      defenseScore:team.ds as number,
      overallScore:team.xs as number,
      offenseRank:team.or,
      defenseRank:team.dr,
      overallRank:team.xr,
    }))
    .sort((a,b)=>a.overallRank-b.overallRank||a.name.localeCompare(b.name));

  return {
    season:data.season,
    ridge:data.ridge,
    homeRidge:data.homeRidge,
    fieldSize:data.teams.length,
    metrics:data.metrics.map(metric=>({key:metric.k,label:metric.l,unit:metric.u})),
    michigan:teamProfile(michigan,data.metrics,data.teams.length),
    utah:teamProfile(utah,data.metrics,data.teams.length),
    byu:teamProfile(byu,data.metrics,data.teams.length),
    michiganGames:regularGames,
    bigTen,
    spotlights:{
      oklahoma:byOpponent("Oklahoma"),
      washington:byOpponent("Washington"),
      ohioState:byOpponent("Ohio State"),
      usc:byOpponent("USC"),
      wisconsin:byOpponent("Wisconsin"),
    },
  };
}
