import { readJson } from "../server-data";
import { currentRoster } from "./roster";
import type { MichiganPlayer, ValueType } from "./types";

export type DepthSlot = { label: string; players: MichiganPlayer[] };
export type ResearchedDepthChart = {
  version: string;
  season: number;
  team: string;
  valueType: ValueType;
  status: "UNOFFICIAL";
  asOf: string;
  basis: string;
  sources: Array<{ label: string; url: string }>;
  offense: Array<{ label: string; playerIds: string[] }>;
  defense: Array<{ label: string; playerIds: string[] }>;
  specialists: Array<{ label: string; playerIds: string[] }>;
};

export function researchedDepthChart(): { offense: DepthSlot[]; defense: DepthSlot[]; specialists: DepthSlot[]; basis: string; asOf: string; sources: ResearchedDepthChart["sources"] } | null {
  const artifact = readJson<ResearchedDepthChart>("data", "published", "2026", "michigan", "researched-depth-chart.json");
  if (!artifact || artifact.valueType !== "PROJECTED" || artifact.status !== "UNOFFICIAL") return null;
  const players = new Map(currentRoster().map((player) => [player.id, player]));
  const resolve = (slots: Array<{ label: string; playerIds: string[] }>): DepthSlot[] | null => {
    const resolved = slots.map((slot) => ({ label: slot.label, players: slot.playerIds.map((id) => players.get(id)).filter(Boolean) as MichiganPlayer[] }));
    return resolved.every((slot, index) => slot.players.length === slots[index].playerIds.length) ? resolved : null;
  };
  const offense = resolve(artifact.offense);
  const defense = resolve(artifact.defense);
  const specialists = resolve(artifact.specialists);
  return offense && defense && specialists ? { offense, defense, specialists, basis: artifact.basis, asOf: artifact.asOf, sources: artifact.sources } : null;
}
