import { readJson } from "../server-data";

export type GameStorySignal = "STRONG_SIGNAL" | "WATCH" | "LIKELY_NOISY";
export type GameStoryPolarity = "strength" | "concern" | "neutral";

export type GameStoryPercentile = {
  percentile: number | null;
  rank: number | null;
  sampleSize: number;
  sampleSizeCaveat: string | null;
};

export type GameStory = {
  id: string;
  topic: string;
  side: "offense" | "defense";
  metric: string;
  headline: string;
  evidence: string[];
  context: Record<string, unknown>;
  whyItMatters: string;
  videoAngle: string;
  signalClass: GameStorySignal;
  polarity: GameStoryPolarity;
  delta: number | null;
  percentile: GameStoryPercentile;
  metricStatus: string;
  definitionVersion: string;
};

export type DriveFunnelSide = {
  possessions: number | null;
  scoringOpportunities: number | null;
  redZonePossessions: number | null;
  touchdowns: number | null;
  otherScoringPossessions: number | null;
  resolvedPointPossessions: number | null;
  definitionVersion: string;
};

export type DriveResult = {
  driveNumber: number;
  offense: string;
  defense: string;
  startPeriod: number;
  startYardsToGoal: number | null;
  endYardsToGoal: number | null;
  playCount: number | null;
  yardsGained: number | null;
  result: string;
  points: number | null;
  scoredBy: string | null;
  definitionVersion: string;
};

export type HalfSplitHalf = { eligiblePlays: number; successfulPlays: number; successRate: number | null };
export type HalfSplitSide = { team: string; firstHalf: HalfSplitHalf; secondHalf: HalfSplitHalf; definitionVersion: string };

export type GameStoryPack = {
  gameId: string;
  season: number;
  week: number;
  opponent: string;
  opponentSlug: string;
  michiganTeamId: number | null;
  opponentTeamId: number | null;
  pointsFor: number | null;
  pointsAgainst: number | null;
  win: boolean;
  homeAway: string | null;
  stories: GameStory[];
  driveFunnel: { offense: DriveFunnelSide; defense: DriveFunnelSide };
  driveTimeline: DriveResult[];
  halfSplit: { michigan: HalfSplitSide; opponent: HalfSplitSide } | null;
  valueType: string;
};

// Seasons to search when a caller has only a gameId, not a season (e.g. a
// Postgres creator_attachments row, which stores game_id as a bare integer).
// Extend this as new seasons publish game-stories.json.
const KNOWN_SEASONS = [2026, 2025];

export function getAllGameStoryPacks(season: number): GameStoryPack[] {
  return readJson<GameStoryPack[]>("data", "published", String(season), "teams", "michigan", "game-stories.json") ?? [];
}

export function getGameStoryPack(season: number, gameId: string | number): GameStoryPack | null {
  return getAllGameStoryPacks(season).find((pack) => pack.gameId === String(gameId)) ?? null;
}

export function findGameStoryPackByGameId(gameId: string | number): GameStoryPack | null {
  for (const season of KNOWN_SEASONS) {
    const pack = getGameStoryPack(season, gameId);
    if (pack) return pack;
  }
  return null;
}

export function findStory(pack: GameStoryPack, storyId: string): GameStory | null {
  return pack.stories.find((story) => story.id === storyId) ?? null;
}

export function getAllKnownGameStoryPacks(): GameStoryPack[] {
  const packs = KNOWN_SEASONS.flatMap((season) => getAllGameStoryPacks(season));
  return packs.sort((a, b) => (b.season - a.season) || (b.week - a.week));
}

export function latestGameStoryPack(): GameStoryPack | null {
  return getAllKnownGameStoryPacks()[0] ?? null;
}
