import { readJson } from "./server-data";

export type OffensiveProfileMetric = {
  key: string;
  label: string;
  value: number | null;
  unit: string;
  rank: number | null;
  fieldSize: number;
  percentile: number | null;
  higherIsBetter: boolean;
};

export type OffensiveProfile = {
  version: string;
  season: number;
  team: string;
  fieldSize: number;
  sample: { offensivePlays: number; rushAttempts: number; dropbacks: number };
  sampleSizeCaveat: string | null;
  metrics: OffensiveProfileMetric[];
};

export function offensiveProfile(season: number): OffensiveProfile | null {
  return readJson<OffensiveProfile>("data", "published", String(season), "analytics", "offensive-profile.json");
}
