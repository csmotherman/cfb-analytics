import { readJson } from "../server-data";
import type { MichiganPlayer } from "./types";

export function currentRoster(): MichiganPlayer[] {
  const roster = readJson<MichiganPlayer[]>("data", "published", "2026", "michigan", "roster.json") ?? [];
  const grades = readJson<Array<{playerId:string;grade?:MichiganPlayer["prospectGrade"];compositeRating?:number|null;stars?:number|null;nationalRecruitRank?:number|null;basis?:string|null}>>("data", "published", "2026", "michigan", "player-grades.json") ?? [];
  const enriched = readJson<Array<{playerId:string;timeline?:MichiganPlayer["careerTimeline"];recruiting?:{grade?:MichiganPlayer["prospectGrade"];rating?:number|null;stars?:number|null;ranking?:number|null;year?:number|null;committedTo?:string|null}|null}>>("data","published","directory_history","players","current-by-team","michigan.json") ?? [];
  const byId = new Map(grades.map((grade) => [grade.playerId, grade]));
  const enrichedById = new Map(enriched.map((row) => [row.playerId,row]));
  return roster.map((player) => {
    const grade = byId.get(player.id);
    const history=enrichedById.get(player.id);const recruit=history?.recruiting;
    return {...player, prospectGrade: recruit?.grade ?? grade?.grade ?? null, compositeRating: recruit?.rating ?? grade?.compositeRating ?? null, stars: recruit?.stars ?? grade?.stars ?? null, nationalRecruitRank: recruit?.ranking ?? grade?.nationalRecruitRank ?? null, recruitClass:recruit?.year??null,originalCommitment:recruit?.committedTo??null,careerTimeline:history?.timeline??[],gradeBasis: recruit ? "CFBD recruiting composite · longitudinal exact-ID join" : grade?.basis ?? null};
  });
}

export function playerById(id: string): MichiganPlayer | null {
  return currentRoster().find((player) => player.id === id) ?? null;
}

export function playersByPosition(position: string): MichiganPlayer[] {
  const wanted = decodeURIComponent(position).toUpperCase();
  return currentRoster().filter((player) => player.position?.toUpperCase() === wanted);
}
