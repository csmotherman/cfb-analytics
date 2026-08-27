import { readJson } from "./server-data";

export type UnitDetailMetric = {
  key: string;
  label: string;
  group: string;
  value: number | null;
  unit: string;
  rank: number | null;
  fieldSize: number;
  percentile: number | null;
  higherIsBetter: boolean;
};

export type UnitDetailProfile = {
  version: string;
  season: number;
  team: string;
  side: "offense" | "defense";
  fieldSize: number;
  groups: string[];
  sampleSizeCaveat: string | null;
  metrics: UnitDetailMetric[];
};

export function unitDetail(season: number, side: "offense" | "defense"): UnitDetailProfile | null {
  return readJson<UnitDetailProfile>("data", "published", String(season), "analytics", `${side}-detail.json`);
}
