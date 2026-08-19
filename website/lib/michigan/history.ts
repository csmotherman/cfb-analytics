import { coachingForSeason } from "./coaching";
import { supportedSeasons } from "./seasons";
import { michiganGames, michiganSeason } from "../michigan";
import { readJson } from "../server-data";

export type HistoricalRosterPlayer = {
  id: string;
  firstName: string;
  lastName: string;
  jersey?: number | null;
  position?: string | null;
  height?: number | null;
  weight?: number | null;
  year?: number | null;
  homeCity?: string | null;
  homeState?: string | null;
  team: string;
  season: number;
};

type HistoricalStatRow = { season: number; team: string; conference?: string; statName: string; statValue: number };
export type HistoricalGame = { id: number; season: number; week: number; seasonType: string; startDate?: string | null; completed: boolean; neutralSite: boolean; conferenceGame?: boolean; venue?: string | null; homeId: number; homeTeam: string; homePoints?: number | null; awayId: number; awayTeam: string; awayPoints?: number | null; notes?: string | null; playoff?: { competition?: string | null; round?: string | null; roundName?: string | null; bowlName?: string | null } | null };
export type HistoricalGrades = { season: number; overall: string; offense: string; defense: string; valueType: "ACTUAL" };
export type HistoricalCfpOutlook = {
  season: number;
  selectionChance: number;
  selectionRank: number;
  fieldSize: number;
  strengthOfSchedule: number;
  qualityWins: number;
  conferenceChampion: boolean;
  actualSelected: boolean;
  modelVersion: string;
  valueType: "RETROSPECTIVE";
};

export function historicalSeasonStats(season: number): Record<string, number> {
  const rows = readJson<HistoricalStatRow[]>("data", "published", "michigan_history", String(season), "stats.json") ?? [];
  return Object.fromEntries(rows.map((row) => [row.statName, Number(row.statValue)]).filter(([, value]) => Number.isFinite(value)));
}

export function historicalGames(season: number): HistoricalGame[] {
  return (readJson<HistoricalGame[]>("data", "published", "michigan_history", String(season), "games.json") ?? [])
    .filter((game) => game.completed)
    .sort((a, b) => (a.seasonType === "postseason" ? 1 : 0) - (b.seasonType === "postseason" ? 1 : 0) || a.week - b.week || String(a.startDate ?? "").localeCompare(String(b.startDate ?? "")) || a.id - b.id);
}

export function historicalGrades(season: number): HistoricalGrades | null {
  return readJson<HistoricalGrades>("data", "published", "michigan_history", String(season), "grades.json");
}

export function historicalCfpOutlook(season: number): HistoricalCfpOutlook | null {
  return readJson<HistoricalCfpOutlook>("data", "published", "michigan_history", String(season), "cfp-outlook.json");
}

export function historicalRoster(season: number): HistoricalRosterPlayer[] {
  const focused = readJson<HistoricalRosterPlayer[]>("data", "published", "michigan_history", String(season), "roster.json");
  const roster = focused ?? readJson<HistoricalRosterPlayer[]>("data", "published", "directory_history", "rosters", `${season}.json`) ?? [];
  return roster
    .filter((player) => player.team === "Michigan")
    .sort((a, b) => (a.position ?? "").localeCompare(b.position ?? "") || (a.jersey ?? 999) - (b.jersey ?? 999) || a.lastName.localeCompare(b.lastName));
}

export function historySeasons() {
  return supportedSeasons.filter((season) => season < 2026).map((season) => {
    const games = michiganGames(season); const sourceGames = historicalGames(season); const team = michiganSeason(season);
    const wins = games.length ? games.filter((g) => g.win === 1).length : sourceGames.filter((game) => game.homeTeam === "Michigan" ? Number(game.homePoints) > Number(game.awayPoints) : Number(game.awayPoints) > Number(game.homePoints)).length;
    const losses = (games.length || sourceGames.length) - wins;
    return { season, coach: coachingForSeason(season)?.head_coach ?? "Coach unavailable", available: Boolean(team) || Object.keys(historicalSeasonStats(season)).length > 0, rosterAvailable: historicalRoster(season).length > 0, wins, losses };
  });
}
