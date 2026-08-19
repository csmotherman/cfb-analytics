import { readJson } from "../server-data";
import { currentRoster } from "./roster";
import type { MichiganPlayer, ValueType } from "./types";

export type DepthSlot = { label: string; player: MichiganPlayer };
export type ProjectedLineup = {
  version: string;
  season: number;
  team: string;
  valueType: ValueType;
  basis: string;
  offense: Array<{ label: string; playerId: string }>;
  defense: Array<{ label: string; playerId: string }>;
};

export function projectedLineups(): { offense: DepthSlot[]; defense: DepthSlot[]; basis: string } | null {
  const artifact = readJson<ProjectedLineup>("data", "published", "2026", "michigan", "projected-lineup.json");
  if (!artifact || artifact.valueType !== "PROJECTED" || !Array.isArray(artifact.offense) || !Array.isArray(artifact.defense)) return null;
  const players = new Map(currentRoster().map((player) => [player.id, player]));
  const resolve = (slots: Array<{ label: string; playerId: string }>): DepthSlot[] | null => {
    const resolved = slots.map((slot) => ({ label: slot.label, player: players.get(slot.playerId) }));
    return resolved.every((slot) => slot.player) ? resolved as DepthSlot[] : null;
  };
  const offense = resolve(artifact.offense);
  const defense = resolve(artifact.defense);
  return offense && defense ? { offense, defense, basis: artifact.basis } : null;
}
