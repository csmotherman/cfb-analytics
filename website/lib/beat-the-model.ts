import fs from "node:fs";
import path from "node:path";

export type BeatTheModelGame = {
  id: string;
  season: number;
  week: number;
  slot: number;
  kickoff?: string | null;
  homeTeam: string;
  awayTeam: string;
  homeRank: number;
  awayRank: number;
  homePowerRating?: number | null;
  awayPowerRating?: number | null;
  matchupScore?: number | null;
  modelWinner: string;
  modelHomeWinProbability?: number | null;
  modelProjectedHomeScore?: number | null;
  modelProjectedAwayScore?: number | null;
  status: "upcoming" | "final";
  actualHomeScore?: number | null;
  actualAwayScore?: number | null;
};

export type BeatTheModelDataset = {
  season: number;
  week: number;
  updatedAt: string | null;
  status: "awaiting-slate" | "open" | "locked" | "final";
  slateSize: number;
  rankingVersion: string;
  selectionVersion: string;
  modelVersion: string;
  games: BeatTheModelGame[];
};

export type BeatTheModelRanking = {
  rank: number;
  team: string;
  rating: number;
  sourceSeason?: number | null;
};

export type BeatTheModelRankings = {
  season: number;
  week: number;
  sourceSeason: number | null;
  rankingVersion: string;
  method?: string;
  teams: BeatTheModelRanking[];
};

const EMPTY_DATASET: BeatTheModelDataset = {
  season: 2026,
  week: 1,
  updatedAt: null,
  status: "awaiting-slate",
  slateSize: 15,
  rankingVersion: "btm-site-aware-srs-four-game-carryover-v1",
  selectionVersion: "btm-top-15-power-matchups-v1",
  modelVersion: "prediction-v2-2026-prospective-freeze-v1",
  games: [],
};

function currentCandidates(): string[] {
  return [
    path.join(process.cwd(), "data", "beat-the-model", "current.json"),
    path.join(process.cwd(), "website", "data", "beat-the-model", "current.json"),
  ];
}

function rankingsCandidates(season: number, week: number): string[] {
  return [
    path.join(process.cwd(), "data", "beat-the-model", "rankings", `season=${season}`, `week=${week}.json`),
    path.join(process.cwd(), "website", "data", "beat-the-model", "rankings", `season=${season}`, `week=${week}.json`),
  ];
}

export function getBeatTheModelDataset(): BeatTheModelDataset {
  const file = currentCandidates().find((candidate) => fs.existsSync(candidate));
  if (!file) return EMPTY_DATASET;
  try {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8")) as Partial<BeatTheModelDataset>;
    return {
      season: Number(parsed.season ?? EMPTY_DATASET.season),
      week: Number(parsed.week ?? EMPTY_DATASET.week),
      updatedAt: typeof parsed.updatedAt === "string" ? parsed.updatedAt : null,
      status: parsed.status ?? EMPTY_DATASET.status,
      slateSize: Number(parsed.slateSize ?? EMPTY_DATASET.slateSize),
      rankingVersion: String(parsed.rankingVersion ?? EMPTY_DATASET.rankingVersion),
      selectionVersion: String(parsed.selectionVersion ?? EMPTY_DATASET.selectionVersion),
      modelVersion: String(parsed.modelVersion ?? EMPTY_DATASET.modelVersion),
      games: Array.isArray(parsed.games) ? parsed.games : [],
    };
  } catch {
    return EMPTY_DATASET;
  }
}

export function getBeatTheModelRankings(season: number, week: number): BeatTheModelRankings {
  const file = rankingsCandidates(season, week).find((candidate) => fs.existsSync(candidate));
  if (!file) {
    return {
      season,
      week,
      sourceSeason: week === 1 ? season - 1 : null,
      rankingVersion: EMPTY_DATASET.rankingVersion,
      teams: [],
    };
  }
  try {
    const parsed = JSON.parse(fs.readFileSync(file, "utf8")) as Partial<BeatTheModelRankings>;
    return {
      season: Number(parsed.season ?? season),
      week: Number(parsed.week ?? week),
      sourceSeason: typeof parsed.sourceSeason === "number" ? parsed.sourceSeason : null,
      rankingVersion: String(parsed.rankingVersion ?? EMPTY_DATASET.rankingVersion),
      method: typeof parsed.method === "string" ? parsed.method : undefined,
      teams: Array.isArray(parsed.teams) ? parsed.teams : [],
    };
  } catch {
    return {
      season,
      week,
      sourceSeason: null,
      rankingVersion: EMPTY_DATASET.rankingVersion,
      teams: [],
    };
  }
}

export function modelRecord(games: BeatTheModelGame[]) {
  const finals = games.filter(
    (game) => game.status === "final" && typeof game.actualHomeScore === "number" && typeof game.actualAwayScore === "number",
  );
  let wins = 0;
  for (const game of finals) {
    const actualWinner = (game.actualHomeScore ?? 0) > (game.actualAwayScore ?? 0) ? game.homeTeam : game.awayTeam;
    if (game.modelWinner === actualWinner) wins += 1;
  }
  return {
    wins,
    losses: finals.length - wins,
    games: finals.length,
    accuracy: finals.length ? wins / finals.length : null,
  };
}

export function formatKickoff(value: string | null | undefined): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}
