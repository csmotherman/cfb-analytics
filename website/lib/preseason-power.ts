import { readJson } from "./server-data";

export type PreseasonPowerTeam = {
  rank: number;
  team: string;
  teamId: number | null;
  slug: string | null;
  conference: string | null;
  powerScore: number | null;
  offense2025: number | null;
  defense2025: number | null;
  recruiting3yrAvg: number | null;
  qbReturningFlag: number | null;
};

export type PreseasonPowerNational = {
  season: number;
  version: string;
  valueType: "RESEARCH";
  disclaimer: string;
  publishedAtUtc: string;
  teamCount: number;
  teams: PreseasonPowerTeam[];
};

export type PreseasonProjectionGame = {
  week: number;
  opponent: string;
  gameId: string | null;
  opponentTeamId: number | null;
  opponentSlug: string | null;
  opponentRank: number | null;
  site: "home" | "away" | "neutral";
  dataAvailable: boolean;
  predictedMargin: number | null;
  winProb: number | null;
  medianMargin: number | null;
  p10Margin: number | null;
  p90Margin: number | null;
};

export type PreseasonWinDistribution = {
  expectedWins: number;
  medianWins: number;
  probUndefeated: number;
  gamesWithData: number;
  distributionPct: Record<string, number>;
};

export type MichiganPreseasonProjection = {
  season: number;
  team: string;
  teamId: number;
  version: string;
  valueType: "RESEARCH";
  disclaimer: string;
  publishedAtUtc: string;
  games: PreseasonProjectionGame[];
  winDistribution: PreseasonWinDistribution;
};

export function preseasonPowerNational(): PreseasonPowerNational | null {
  return readJson<PreseasonPowerNational>("data", "published", "2026", "national", "preseason-power.json");
}

export function michiganPreseasonProjection(): MichiganPreseasonProjection | null {
  return readJson<MichiganPreseasonProjection>("data", "published", "2026", "michigan", "preseason-2026-projection.json");
}

export function preseasonProjectionForGame(gameId: string | number): PreseasonProjectionGame | null {
  return michiganPreseasonProjection()?.games.find((game) => game.gameId === String(gameId)) ?? null;
}
