import fs from "node:fs";
import path from "node:path";

import type { PredictionReason } from "./predictions";

export const ARCHIVE_SEASONS = [2025, 2024, 2023, 2022, 2021, 2019, 2018, 2017, 2016, 2015, 2014];

export type ArchiveGame = {
  id: string;
  season: number;
  week: number;
  seasonType?: string | null;
  kickoff?: string | null;
  homeTeam: string;
  awayTeam: string;
  predictedWinner?: string | null;
  homeWinProbability?: number | null;
  projectedHomeScore?: number | null;
  projectedAwayScore?: number | null;
  modelHomeMargin?: number | null;
  modelAbsoluteError?: number | null;
  marketHomeMargin?: number | null;
  marketProvider?: string | null;
  modelAtsSide?: "HOME" | "AWAY" | null;
  atsCorrect?: boolean | null;
  atsResult?: "WIN" | "LOSS" | "PUSH" | null;
  winnerCorrect?: boolean | null;
  actualHomeScore?: number | null;
  actualAwayScore?: number | null;
  actualHomeMargin?: number | null;
  correct?: boolean | null;
  recommendedBet?: boolean;
  recommendedBetSide?: "HOME" | "AWAY" | null;
  recommendedBetTeam?: string | null;
  recommendedBetConfidence?: number | null;
  recommendedBetResult?: "WIN" | "LOSS" | "PUSH" | null;
  reasons?: PredictionReason[];
  risk?: string | null;
  lockedAt?: string | null;
  evidenceStatus?: "official-oos" | "historical-slate" | "retrospective" | string;
};

export type ArchiveWeekSummary = {
  games: number;
  modelGames: number;
  marketGames: number;
  modelMae: number | null;
  winnerWins: number;
  winnerLosses: number;
  winnerAccuracy: number | null;
  atsWins: number;
  atsLosses: number;
  atsPushes: number;
  atsAccuracy: number | null;
  recommendedBetSourcePresent: boolean;
  recommendedBets: number;
  recommendedBetWins: number;
  recommendedBetLosses: number;
  recommendedBetPushes: number;
  recommendedBetUnits: number | null;
  unitsConvention?: string;
};

export type ArchiveWeek = {
  season: number;
  week: number;
  label?: string;
  summary?: ArchiveWeekSummary;
  games: ArchiveGame[];
};

export type ArchiveIndexEntry = {
  season: number;
  weeks: number[];
};

const PROJECT_ROOT = path.resolve(process.cwd(), "..");

function archiveCandidates(season: number, week: number): string[] {
  return [
    path.join(PROJECT_ROOT, "data", "processed", "website", "prediction_archive", `season=${season}`, `week=${week}.json`),
    path.join(process.cwd(), "data", "archive", `season=${season}`, `week=${week}.json`),
    path.join(process.cwd(), "data", "archive", String(season), `week-${week}.json`),
    path.join(process.cwd(), "website", "data", "archive", `season=${season}`, `week=${week}.json`),
    path.join(process.cwd(), "website", "data", "archive", String(season), `week-${week}.json`),
  ];
}

function normalizeWeek(payload: unknown, season: number, week: number): ArchiveWeek {
  if (Array.isArray(payload)) {
    return { season, week, games: payload as ArchiveGame[] };
  }
  const record = payload && typeof payload === "object" ? payload as Record<string, unknown> : {};
  return {
    season: Number(record.season ?? season),
    week: Number(record.week ?? week),
    label: typeof record.label === "string" ? record.label : undefined,
    summary: record.summary && typeof record.summary === "object" ? record.summary as ArchiveWeekSummary : undefined,
    games: Array.isArray(record.games) ? record.games as ArchiveGame[] : [],
  };
}

export function getArchiveWeek(season: number, week: number): ArchiveWeek {
  if (!ARCHIVE_SEASONS.includes(season) || !Number.isInteger(week) || week < 0 || week > 20) {
    return { season, week, games: [] };
  }
  const file = archiveCandidates(season, week).find((candidate) => fs.existsSync(candidate));
  if (!file) return { season, week, games: [] };
  try {
    return normalizeWeek(JSON.parse(fs.readFileSync(file, "utf8")), season, week);
  } catch {
    return { season, week, games: [] };
  }
}

export function getArchiveGame(season: number, week: number, id: string): ArchiveGame | null {
  return getArchiveWeek(season, week).games.find((game) => String(game.id) === id) ?? null;
}

function discoverWeeksInDirectory(directory: string): number[] {
  if (!fs.existsSync(directory)) return [];
  try {
    return fs.readdirSync(directory)
      .map((name) => {
        const match = name.match(/^week-(\d+)\.json$/) ?? name.match(/^week=(\d+)\.json$/);
        return match ? Number(match[1]) : NaN;
      })
      .filter((week) => Number.isInteger(week));
  } catch {
    return [];
  }
}

export function getArchiveIndex(): ArchiveIndexEntry[] {
  return ARCHIVE_SEASONS.map((season) => {
    const weeks = new Set<number>();
    for (const directory of [
      path.join(PROJECT_ROOT, "data", "processed", "website", "prediction_archive", `season=${season}`),
      path.join(process.cwd(), "data", "archive", `season=${season}`),
      path.join(process.cwd(), "data", "archive", String(season)),
      path.join(process.cwd(), "website", "data", "archive", `season=${season}`),
      path.join(process.cwd(), "website", "data", "archive", String(season)),
    ]) {
      for (const week of discoverWeeksInDirectory(directory)) weeks.add(week);
    }

    const discovered = [...weeks].sort((a, b) => a - b);
    return { season, weeks: discovered.length ? discovered : Array.from({ length: 21 }, (_, week) => week) };
  });
}

export function archiveWeekHref(season: number, week: number): string {
  return `/archive/${season}/${week}`;
}

export function archiveGameHref(game: ArchiveGame): string {
  return `/archive/${game.season}/${game.week}/${game.id}`;
}
