import { readJson } from "./server-data";
export type Game={id:number;week:number;startDate:string;startTimeTBD:boolean;homeId:number;homeTeam:string;awayId:number;awayTeam:string;venue?:string|null;completed:boolean;conferenceGame:boolean};
export type Player={id:string;firstName:string;lastName:string;jersey?:number|null;position?:string|null;year?:number|null;height?:number|null;weight?:number|null;playerImageUrl?:string|null;playerImageSource?:string|null;playerImageSourceUrl?:string|null};
type PlayerImage={playerId:string;imageUrl:string;source:string;sourceProfileUrl:string;acquiredAt:string};
type Grade={playerId:string;grade?:string|null;compositeRating?:number|null;stars?:number|null;nationalRecruitRank?:number|null;basis?:string|null};
type ProductionGrade={playerId:string;grade:string;season:number;nationalPositionPercentile:number;positionFamily:string;basis:string;valueType:"ACTUAL"};
type RosterStatus={playerId:string;rosterStatus:"RETURNING"|"TRANSFER"|"FRESHMAN"|"UNCLASSIFIED";previousTeam:string|null;basisSeason:number};
type PlayerInsight={playerId:string;focus:{kind:"PRODUCTION"|"PROSPECT";grade?:string|null;stars?:number|null;rating?:number|null;percentile?:number|null};pastSeasons:{season:number;team:string;stats:{label:string;value:number}[]}[];expectation:string};
export type Recruit={id:string;name:string;position?:string|null;stars?:number|null;ranking?:number|null;grade?:string|null;city?:string|null;stateProvince?:string|null};
type Recruiting={ranking?:{rank?:number|null;points?:number|null};recruits:Recruit[]};
type Outlook={asOf:string;valueType:"BENCHMARK";cfp:{noVigImpliedProbability:number};disclaimer:string;source:{name:string;url:string}};

export function homeData(){
  const schedule=readJson<Game[]>("data","published","2026","michigan","schedule.json")??[];const roster=readJson<Player[]>("data","published","2026","michigan","roster.json")??[];const images=readJson<PlayerImage[]>("data","published","2026","michigan","player-images.json")??[];const grades=readJson<Grade[]>("data","published","2026","michigan","player-grades.json")??[];const production=readJson<ProductionGrade[]>("data","published","2026","michigan","player-production-grades.json")??[];const statuses=readJson<RosterStatus[]>("data","published","2026","michigan","player-roster-status.json")??[];const insights=readJson<PlayerInsight[]>("data","published","2026","michigan","player-profile-insights.json")??[];const recruiting=readJson<Recruiting>("data","published","2026","michigan","recruiting.json");const outlook=readJson<Outlook>("data","published","2026","michigan","outlook.json");
  const gradeMap=new Map(grades.map(g=>[g.playerId,g]));const productionMap=new Map(production.map(g=>[g.playerId,g]));const statusMap=new Map(statuses.map(s=>[s.playerId,s]));const imageMap=new Map(images.map(i=>[i.playerId,i]));const insightMap=new Map(insights.map(i=>[i.playerId,i]));
  const squad=roster.map(p=>{const recruit=gradeMap.get(p.id);const actual=productionMap.get(p.id);const status=statusMap.get(p.id);const image=imageMap.get(p.id);return{...p,...recruit,...status,insight:insightMap.get(p.id)??null,playerImageUrl:image?.imageUrl??null,playerImageSource:image?.source??null,playerImageSourceUrl:image?.sourceProfileUrl??null,grade:actual?.grade??recruit?.grade,gradeBasis:actual?.basis??recruit?.basis,gradeValueType:actual?"ACTUAL" as const:"BENCHMARK" as const,gradeSeason:actual?.season??null,nationalPositionPercentile:actual?.nationalPositionPercentile??null}});
  const players=squad.filter(p=>p.grade).sort((a,b)=>(b.nationalPositionPercentile??-1)-(a.nationalPositionPercentile??-1)||(b.compositeRating??0)-(a.compositeRating??0));
  const productionPlayers=players.filter(p=>p.gradeValueType==="ACTUAL");return{schedule:schedule.sort((a,b)=>a.week-b.week),next:schedule.find(g=>!g.completed)??null,roster,squad,players,productionPlayers,recruiting,outlook};
}
export const logoUrl=(id:number,size:64|128|256=128)=>`https://cdn.collegefootballdata.com/logos/${size}/${id}.png`;
export const opponentOf=(game:Game)=>game.homeId===130?{id:game.awayId,name:game.awayTeam,site:"HOME"}:{id:game.homeId,name:game.homeTeam,site:"AWAY"};
export const gameDate=(game:Game)=>new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",timeZone:"America/Detroit"}).format(new Date(game.startDate));
export const gameTime=(game:Game)=>game.startTimeTBD?"TBD":new Intl.DateTimeFormat("en-US",{hour:"numeric",minute:"2-digit",timeZone:"America/Detroit"}).format(new Date(game.startDate));
