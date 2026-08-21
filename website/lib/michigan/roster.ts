import { readJson } from "../server-data";
import type { MichiganPlayer, PlayerInsight } from "./types";

type RecruitingRatingRow={
  playerId:string;
  rating?:number|null;
  stars?:number|null;
  nationalRank?:number|null;
  recruitClass?:number|null;
  committedTo?:string|null;
  matchMethod?:string|null;
};

export function currentRoster(): MichiganPlayer[] {
  const roster = readJson<MichiganPlayer[]>("data", "published", "2026", "michigan", "roster.json") ?? [];
  const grades = readJson<Array<{playerId:string;grade?:MichiganPlayer["prospectGrade"];compositeRating?:number|null;stars?:number|null;nationalRecruitRank?:number|null;basis?:string|null}>>("data", "published", "2026", "michigan", "player-grades.json") ?? [];
  const recruitingRatings = readJson<RecruitingRatingRow[]>("data","published","2026","michigan","player-recruiting-ratings.json") ?? [];
  const productionGrades = readJson<Array<{playerId:string;grade?:MichiganPlayer["performanceGrade"];season:number;basis:string;productionPercentile?:number|null;usagePercentile?:number|null;nationalPositionPercentile?:number|null;productionScore?:number|null;usageValue?:number|null;cohortSize?:number|null;positionFamily?:string|null}>>("data", "published", "2026", "michigan", "player-production-grades.json") ?? [];
  const rosterStatuses = readJson<Array<{playerId:string;rosterStatus:MichiganPlayer["rosterStatus"];previousTeam?:string|null}>>("data", "published", "2026", "michigan", "player-roster-status.json") ?? [];
  const playerImages = readJson<Array<{playerId:string;imageUrl:string;source:string;sourceProfileUrl:string;acquiredAt:string}>>("data", "published", "2026", "michigan", "player-images.json") ?? [];
  const playerInsights = readJson<Array<PlayerInsight & {playerId:string}>>("data", "published", "2026", "michigan", "player-profile-insights.json") ?? [];
  const importance = readJson<{players:Array<{playerId:string;rank:number;role:string;tier:string;reason:string}>}>("data", "published", "2026", "michigan", "player-importance.json")?.players ?? [];
  const enriched = readJson<Array<{playerId:string;timeline?:MichiganPlayer["careerTimeline"];recruiting?:{grade?:MichiganPlayer["prospectGrade"];rating?:number|null;stars?:number|null;ranking?:number|null;year?:number|null;committedTo?:string|null}|null}>>("data","published","directory_history","players","current-by-team","michigan.json") ?? [];
  const byId = new Map(grades.map((grade) => [grade.playerId, grade]));
  const recruitingById = new Map(recruitingRatings.map((row) => [row.playerId,row]));
  const productionById = new Map(productionGrades.map((grade) => [grade.playerId, grade]));
  const statusById = new Map(rosterStatuses.map((status) => [status.playerId, status]));
  const enrichedById = new Map(enriched.map((row) => [row.playerId,row]));
  const imageById = new Map(playerImages.map((image) => [image.playerId,image]));
  const insightById = new Map(playerInsights.map((insight) => [insight.playerId,insight]));
  const importanceById = new Map(importance.map((row) => [row.playerId,row]));
  return roster.map((player) => {
    const grade = byId.get(player.id); const recruitingRating=recruitingById.get(player.id); const production = productionById.get(player.id); const status = statusById.get(player.id);
    const history=enrichedById.get(player.id);const recruit=history?.recruiting;const image=imageById.get(player.id);const importanceRow=importanceById.get(player.id);
    const rating=recruitingRating?.rating??recruit?.rating??grade?.compositeRating??null;
    const stars=recruitingRating?.stars??recruit?.stars??grade?.stars??null;
    const nationalRank=recruitingRating?.nationalRank??recruit?.ranking??grade?.nationalRecruitRank??null;
    const recruitClass=recruitingRating?.recruitClass??recruit?.year??null;
    const commitment=recruitingRating?.committedTo??recruit?.committedTo??null;
    const gradeBasis=recruitingRating?.rating!=null?`CFBD recruiting composite · ${recruitingRating.matchMethod??"canonical roster match"}`:recruit?"CFBD recruiting composite · longitudinal exact-ID join":grade?.basis??null;
    return {...player, importanceRank:importanceRow?.rank??null,importanceRole:importanceRow?.role??null,importanceTier:importanceRow?.tier??null,importanceReason:importanceRow?.reason??null,insight:insightById.get(player.id)??null,playerImageUrl:image?.imageUrl??null,playerImageSource:image?.source??null,playerImageSourceUrl:image?.sourceProfileUrl??null,playerImageUpdatedAt:image?.acquiredAt??null,rosterStatus: status?.rosterStatus ?? null, previousTeam: status?.previousTeam ?? null, performanceGrade: production?.grade ?? null, performanceGradeBasis: production?.basis ?? null, performanceGradeSeason: production?.season ?? null,productionPercentile:production?.productionPercentile??null,usagePercentile:production?.usagePercentile??null,nationalPositionPercentile:production?.nationalPositionPercentile??null,productionScore:production?.productionScore??null,usageValue:production?.usageValue??null,productionCohortSize:production?.cohortSize??null,positionFamily:production?.positionFamily??null, prospectGrade: recruit?.grade ?? grade?.grade ?? null, compositeRating: rating, stars, nationalRecruitRank:nationalRank, recruitClass,originalCommitment:commitment,careerTimeline:history?.timeline??[],gradeBasis};
  });
}

export function playerById(id: string): MichiganPlayer | null {
  return currentRoster().find((player) => player.id === id) ?? null;
}

export function playersByPosition(position: string): MichiganPlayer[] {
  const wanted = decodeURIComponent(position).toUpperCase();
  return currentRoster().filter((player) => player.position?.toUpperCase() === wanted);
}
