import { readJson } from "../server-data";
import type { MichiganRecruit, RecruitingClass } from "./types";

export function currentRecruitingClass(): RecruitingClass | null {
  return readJson<RecruitingClass>("data", "published", "2026", "michigan", "recruiting.json");
}

export type TeamRecruitingRank = { year:number; team:string; rank?:number|null; points?:number|null };
export function nationalRecruits(): MichiganRecruit[] { return readJson<MichiganRecruit[]>("data","published","2026","recruiting","players.json") ?? []; }
export function nationalTeamRankings(): TeamRecruitingRank[] { return readJson<TeamRecruitingRank[]>("data","published","2026","recruiting","teams.json") ?? []; }
export function recruitById(id:string): MichiganRecruit|null { return nationalRecruits().find(recruit=>recruit.id===id) ?? null; }
export function recruitsForTeam(team:string): MichiganRecruit[] { const wanted=decodeURIComponent(team).toLowerCase(); return nationalRecruits().filter(recruit=>recruit.committedTo?.toLowerCase()===wanted); }

export const gradeScale = [
  ["S+", ".995+"], ["S", ".980+"], ["A", ".950+"], ["B", ".900+"],
  ["C", ".850+"], ["D", ".800+"], ["F", "below .800"],
] as const;
