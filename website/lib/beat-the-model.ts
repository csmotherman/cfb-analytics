import fs from "node:fs";
import path from "node:path";

export type TeamPregameStats = {
  version: string;
  season: number;
  throughWeek: number;
  games: number;
  wins: number;
  losses: number;
  ties: number;
  pointsPerGame?: number | null;
  pointsAllowedPerGame?: number | null;
  offenseSuccessRate?: number | null;
  defenseSuccessRateAllowed?: number | null;
  offensePPA?: number | null;
  defensePPAAllowed?: number | null;
  offenseExplosiveness?: number | null;
  defenseExplosivenessAllowed?: number | null;
  pointsPerOpportunity?: number | null;
  pointsPerOpportunityAllowed?: number | null;
  advancedPlays?: number | null;
  advancedDrives?: number | null;
  excludeGarbageTime?: boolean;
};

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
  homeTeamId?: number | string | null;
  awayTeamId?: number | string | null;
  homeAbbreviation?: string | null;
  awayAbbreviation?: string | null;
  homeConference?: string | null;
  awayConference?: string | null;
  homeColor?: string | null;
  awayColor?: string | null;
  homeAlternateColor?: string | null;
  awayAlternateColor?: string | null;
  homeLogo?: string | null;
  awayLogo?: string | null;
  homePowerRating?: number | null;
  awayPowerRating?: number | null;
  homePregameStats?: TeamPregameStats | null;
  awayPregameStats?: TeamPregameStats | null;
  matchupScore?: number | null;
  selectionTier?: number | null;
  selectionScore?: number | null;
  marketSource?: string | null;
  marketProviderCount?: number | null;
  marketSpread?: number | null;
  marketFavorite?: string | null;
  marketLine?: string | null;
  marketHomeMoneyline?: number | null;
  marketAwayMoneyline?: number | null;
  marketHomeWinProbability?: number | null;
  marketAwayWinProbability?: number | null;
  marketSnapshotAt?: string | null;
  modelWinner?: string | null;
  modelMargin?: number | null;
  modelHomeWinProbability?: number | null;
  modelProjectedHomeScore?: number | null;
  modelProjectedAwayScore?: number | null;
  status: "upcoming" | "live" | "final";
  actualHomeScore?: number | null;
  actualAwayScore?: number | null;
};

export type BeatTheModelDataset = {
  season: number;
  week: number;
  updatedAt: string | null;
  status: "awaiting-slate" | "awaiting-model" | "open" | "locked" | "final";
  slateSize: number;
  rankingVersion: string;
  selectionVersion: string;
  modelVersion: string;
  modelReady?: boolean;
  selectionFrozen?: boolean;
  marketSource?: string | null;
  marketSnapshotAt?: string | null;
  marketFetchStatus?: string | null;
  marketAvailableGames?: number | null;
  marketSelectedGames?: number | null;
  games: BeatTheModelGame[];
};

export type BeatTheModelRanking = {
  rank: number;
  team: string;
  rating: number;
  teamId?: number | string | null;
  abbreviation?: string | null;
  conference?: string | null;
  color?: string | null;
  alternateColor?: string | null;
  logo?: string | null;
  sourceSeason?: number | null;
  gamesBefore?: number | null;
  pregameStats?: TeamPregameStats | null;
};

export type BeatTheModelRankings = {
  season: number;
  week: number;
  sourceSeason: number | null;
  rankingVersion: string;
  method?: string;
  teamMetadataSource?: string | null;
  teamMetadataStatus?: string | null;
  teamStatsVersion?: string | null;
  teamStatsStatus?: string | null;
  teamStatsThroughWeek?: number | null;
  teamStatsExcludeGarbageTime?: boolean | null;
  teams: BeatTheModelRanking[];
};

const EMPTY_DATASET: BeatTheModelDataset = {
  season: 2026,
  week: 1,
  updatedAt: null,
  status: "awaiting-slate",
  slateSize: 15,
  rankingVersion: "btm-site-aware-srs-four-game-carryover-v1",
  selectionVersion: "btm-close-ranked-market-matchups-v3",
  modelVersion: "prediction-v2-2026-prospective-freeze-v1",
  modelReady: false,
  selectionFrozen: false,
  marketSource: null,
  marketSnapshotAt: null,
  marketFetchStatus: null,
  marketAvailableGames: 0,
  marketSelectedGames: 0,
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
      modelReady: typeof parsed.modelReady === "boolean" ? parsed.modelReady : undefined,
      selectionFrozen: typeof parsed.selectionFrozen === "boolean" ? parsed.selectionFrozen : undefined,
      marketSource: typeof parsed.marketSource === "string" ? parsed.marketSource : null,
      marketSnapshotAt: typeof parsed.marketSnapshotAt === "string" ? parsed.marketSnapshotAt : null,
      marketFetchStatus: typeof parsed.marketFetchStatus === "string" ? parsed.marketFetchStatus : null,
      marketAvailableGames: typeof parsed.marketAvailableGames === "number" ? parsed.marketAvailableGames : null,
      marketSelectedGames: typeof parsed.marketSelectedGames === "number" ? parsed.marketSelectedGames : null,
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
      teamMetadataSource: null,
      teamMetadataStatus: null,
      teamStatsVersion: null,
      teamStatsStatus: null,
      teamStatsThroughWeek: null,
      teamStatsExcludeGarbageTime: null,
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
      teamMetadataSource: typeof parsed.teamMetadataSource === "string" ? parsed.teamMetadataSource : null,
      teamMetadataStatus: typeof parsed.teamMetadataStatus === "string" ? parsed.teamMetadataStatus : null,
      teamStatsVersion: typeof parsed.teamStatsVersion === "string" ? parsed.teamStatsVersion : null,
      teamStatsStatus: typeof parsed.teamStatsStatus === "string" ? parsed.teamStatsStatus : null,
      teamStatsThroughWeek: typeof parsed.teamStatsThroughWeek === "number" ? parsed.teamStatsThroughWeek : null,
      teamStatsExcludeGarbageTime: typeof parsed.teamStatsExcludeGarbageTime === "boolean" ? parsed.teamStatsExcludeGarbageTime : null,
      teams: Array.isArray(parsed.teams) ? parsed.teams : [],
    };
  } catch {
    return {
      season,
      week,
      sourceSeason: null,
      rankingVersion: EMPTY_DATASET.rankingVersion,
      teamMetadataSource: null,
      teamMetadataStatus: null,
      teamStatsVersion: null,
      teamStatsStatus: null,
      teamStatsThroughWeek: null,
      teamStatsExcludeGarbageTime: null,
      teams: [],
    };
  }
}

export function modelRecord(games: BeatTheModelGame[]) {
  const finals = games.filter(
    (game) => game.status === "final"
      && Boolean(game.modelWinner)
      && typeof game.actualHomeScore === "number"
      && typeof game.actualAwayScore === "number",
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
