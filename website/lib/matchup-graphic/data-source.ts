// DATA layer: reads the published per-game JSON. No analysis, no
// football logic -- just I/O, using this repo's existing readJson
// convention (lib/server-data.ts) so this fits the same publish/read
// pattern as schedule.json, market-lines.json, etc.
import { readJson } from "../server-data";
import type { MatchupGraphicSource } from "./types";

export function readMatchupGraphicSource(gameId: string | number): MatchupGraphicSource | null {
  return readJson<MatchupGraphicSource>("data", "published", "2026", "michigan", "matchup-graphics", `${gameId}.json`);
}
