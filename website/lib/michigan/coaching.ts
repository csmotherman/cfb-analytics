import { readConfigJson } from "../server-data";
import type { ValueType } from "./types";
type StaffRow = { season: number; head_coach: string; offensive_coordinator?: string; defensive_coordinator?: string; value_type: ValueType; notes?: string };
type StaffFile = { seasons: StaffRow[] };
export function coachingForSeason(season: number): StaffRow | null {
  return readConfigJson<StaffFile>("michigan_staff.json")?.seasons.find((row) => row.season === season) ?? null;
}
