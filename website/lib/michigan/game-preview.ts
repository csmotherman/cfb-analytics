import {readJson} from "../server-data";
import type {MichiganScheduleGame} from "./types";
import {opponent} from "./games";

export type MatchupRidgeSide={rank:number;rating:number;field_size:number};
export type MatchupRidgeTeam={
  team_id:number;
  team:string;
  games:number;
  overall:{rank:number;rating:number;field_size:number};
  offense:MatchupRidgeSide;
  defense:MatchupRidgeSide;
};
type RidgeTeamPublication={season:number;lambda:number;method:string;overall_method:string;field_size:number;teams:MatchupRidgeTeam[]};

function ridgeTeams(season:number){
 return readJson<RidgeTeamPublication>("data","published",String(season),"analytics","ridge-team-ratings.json");
}

function ridgeTeam(season:number,teamId:number,teamName:string){
 const rows=ridgeTeams(season)?.teams??[];
 return rows.find(r=>r.team_id===teamId)??rows.find(r=>r.team.toLowerCase()===teamName.toLowerCase())??null;
}

export function gamePreview(game:MichiganScheduleGame,baselineSeason=2025){
 const opp=opponent(game);
 return {
  opp,
  baselineSeason,
  michigan:ridgeTeam(baselineSeason,130,"Michigan"),
  opponent:ridgeTeam(baselineSeason,opp.id,opp.name),
 };
}
