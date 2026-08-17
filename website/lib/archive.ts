import fs from "node:fs";
import path from "node:path";

import type { PredictionGame } from "./predictions";

export const ARCHIVE_SEASONS = Array.from({ length: 12 }, (_, index) => 2025 - index);

export type ArchiveWeek = {
  season: number;
  week: number;
  label?: string;
  games: PredictionGame[];
};

export type ArchiveIndexEntry = {
  season: number;
  weeks: number[];
};

const PROJECT_ROOT = path.resolve(process.cwd(), "..");

function archiveCandidates(season: number, week: number): string[] {
  return [
    path.join(PROJECT_ROOT, "data", "processed", "website", "prediction_archive", `season=${season}`, `week=${week}.json`),
    path.join(process.cwd(), "data", "archive", String(season), `week-${week}.json`),
    path.join(process.cwd(), "website", "data", "archive", String(season), `week-${week}.json`),
  ];
}

function normalizeWeek(payload: unknown, season: number, week: number): ArchiveWeek {
  if (Array.isArray(payload)) {
    return { season, week, games: payload as PredictionGame[] };
  }
  const record = payload && typeof payload === "object" ? payload as Record<string, unknown> : {};
  return {
    season: Number(record.season ?? season),
    week: Number(record.week ?? week),
    label: typeof record.label === "string" ? record.label : undefined,
    games: Array.isArray(record.games) ? record.games as PredictionGame[] : [],
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
    const processedDir = path.join(PROJECT_ROOT, "data", "processed", "website", "prediction_archive", `season=${season}`);
    if (fs.existsSync(processedDir)) {
      try {
        for (const name of fs.readdirSync(processedDir)) {
          const match = name.match(/^week=(\d+)\.json$/) ?? name.match(/^week-(\d+)\.json$/) ?? name.match(/^week=(\d+)$/);
          if (match) weeks.add(Number(match[1]));
        }
      } catch {}
    }
    for (const directory of [
      path.join(process.cwd(), "data", "archive", String(season)),
      path.join(process.cwd(), "website", "data", "archive", String(season)),
    ]) {
      for (const week of discoverWeeksInDirectory(directory)) weeks.add(week);
    }

    // The UI must be navigable before generated archive files are present.
    // College-football regular/postseason week numbers are exposed as 0-20,
    // while unavailable weeks render a truthful empty state rather than fake picks.
    const discovered = [...weeks].sort((a, b) => a - b);
    return { season, weeks: discovered.length ? discovered : Array.from({ length: 21 }, (_, week) => week) };
  });
}

export function archiveWeekHref(season: number, week: number): string {
  return `/archive/${season}/${week}`;
}
