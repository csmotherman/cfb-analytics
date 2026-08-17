import fs from "node:fs";
import path from "node:path";

export type PredictionReason = {
  eyebrow: string;
  title: string;
  detail: string;
};

export type PredictionGame = {
  id: string;
  season: number;
  week: number;
  kickoff: string;
  homeTeam: string;
  awayTeam: string;
  predictedWinner: string;
  homeWinProbability: number;
  projectedHomeScore: number;
  projectedAwayScore: number;
  reasons: PredictionReason[];
  risk: string;
  lockedAt?: string | null;
  status: "upcoming" | "final";
  actualHomeScore?: number | null;
  actualAwayScore?: number | null;
  correct?: boolean | null;
};

export type PredictionDataset = {
  season: number;
  week: number;
  updatedAt: string | null;
  modelVersion: string;
  current: PredictionGame[];
  results: PredictionGame[];
};

const EMPTY: PredictionDataset = {
  season: 2026,
  week: 1,
  updatedAt: null,
  modelVersion: "prediction-v2-2026-prospective-freeze-v1",
  current: [],
  results: [],
};

function candidatePaths(): string[] {
  return [
    path.join(process.cwd(), "data", "predictions.json"),
    path.join(process.cwd(), "website", "data", "predictions.json"),
  ];
}

export function getPredictionDataset(): PredictionDataset {
  const file = candidatePaths().find((candidate) => fs.existsSync(candidate));
  if (!file) return EMPTY;
  try {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8")) as Partial<PredictionDataset>;
    return {
      season: Number(parsed.season ?? EMPTY.season),
      week: Number(parsed.week ?? EMPTY.week),
      updatedAt: parsed.updatedAt ?? null,
      modelVersion: String(parsed.modelVersion ?? EMPTY.modelVersion),
      current: Array.isArray(parsed.current) ? parsed.current : [],
      results: Array.isArray(parsed.results) ? parsed.results : [],
    };
  } catch {
    return EMPTY;
  }
}

export function getPredictionById(id: string): PredictionGame | null {
  const data = getPredictionDataset();
  return [...data.current, ...data.results].find((game) => game.id === id) ?? null;
}

export function predictedWinnerProbability(game: PredictionGame): number {
  return game.predictedWinner === game.homeTeam
    ? game.homeWinProbability
    : 1 - game.homeWinProbability;
}

export function seasonRecord(results: PredictionGame[]) {
  const graded = results.filter((game) => game.status === "final" && typeof game.correct === "boolean");
  const wins = graded.filter((game) => game.correct === true).length;
  const losses = graded.length - wins;
  return {
    wins,
    losses,
    games: graded.length,
    accuracy: graded.length ? wins / graded.length : null,
  };
}

export function formatKickoff(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(date);
}

export function formatUpdatedAt(value: string | null): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(date);
}
