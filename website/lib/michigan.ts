import {readJson} from "./server-data";

export type MichiganSeason = {
  season: number;
  team_id: number;
  team: string;
  slug: string;
  conference: string;
  games: number;
  season_state?: SeasonState;
  value_type?: ValueType;
  successRate?: number | null;
  successRateAllowed?: number | null;
  explosivePlayRate?: number | null;
  explosivePlayRateAllowed?: number | null;
  pointsPerResolvedPossession?: number | null;
  pointsPerResolvedPossessionAllowed?: number | null;
  yardsPerSuccessfulPlay?: number | null;
  yardsPerSuccessfulPlayAllowed?: number | null;
  havocRate?: number | null;
  havocRateAllowed?: number | null;
  [key: string]: unknown;
};

export type SeasonState = "HISTORICAL" | "PRESEASON" | "IN_SEASON" | "COMPLETE";
export type ValueType = "ACTUAL" | "PROJECTED" | "PRESEASON";
export const MICHIGAN_HISTORY_START = 2010;
export const CURRENT_MICHIGAN_SEASON = 2026;
export const LAST_COMPLETED_SEASON = 2025;

export type PublishedManifest = {
  season: number;
  season_state?: SeasonState;
  season_state_evidence?: string;
  value_type?: ValueType;
};

export type MichiganGame = {
  season: number;
  week: number;
  season_type: string;
  game_id: string;
  team_id: number;
  opponent: string;
  opponent_id: number;
  opponent_conference?: string | null;
  opponent_classification?: string | null;
  home_away: "home" | "away";
  neutral_site: boolean;
  points_for?: number | null;
  points_against?: number | null;
  win?: number | null;
  loss?: number | null;
  successRate?: number | null;
  successRateAllowed?: number | null;
};

export type ConferenceSummary = {
  season: number;
  conference: string;
  teams: number;
  games: number;
  successRate?: number | null;
  successRateAllowed?: number | null;
};

function readRows<T>(...segments: string[]): T[] {
  const parsed = readJson<unknown>(...segments);
  if (parsed == null) return [];
  if (!Array.isArray(parsed)) throw new TypeError(`Expected a published JSON array at ${segments.join("/")}`);
  return parsed as T[];
}

function readObject<T>(...segments: string[]): T | null {
  const parsed = readJson<unknown>(...segments);
  if (parsed == null) return null;
  if (Array.isArray(parsed) || typeof parsed !== "object") throw new TypeError(`Expected a published JSON object at ${segments.join("/")}`);
  return parsed as T;
}

export function supportedMichiganSeasons(): number[] {
  return Array.from({ length: CURRENT_MICHIGAN_SEASON - MICHIGAN_HISTORY_START + 1 }, (_, index) => CURRENT_MICHIGAN_SEASON - index);
}

export function publishedManifest(season: number): PublishedManifest | null {
  return readObject<PublishedManifest>("data", "published", String(season), "manifest.json");
}

export function seasonState(season: number): SeasonState {
  const manifest = publishedManifest(season);
  if (manifest?.season_state) return manifest.season_state;
  if (season === CURRENT_MICHIGAN_SEASON) return "PRESEASON";
  if (season <= LAST_COMPLETED_SEASON && season >= MICHIGAN_HISTORY_START) return "COMPLETE";
  return "HISTORICAL";
}

export function latestPublishedSeason(): number | null {
  for (const season of supportedMichiganSeasons()) {
    if (publishedManifest(season) || michiganSeason(season)) return season;
  }
  return null;
}

export function michiganSeason(season: number): MichiganSeason | null {
  return readRows<MichiganSeason>("data", "published", String(season), "teams", "michigan", "season.json")[0] ?? null;
}

export function michiganGames(season: number): MichiganGame[] {
  return readRows<MichiganGame>("data", "published", String(season), "teams", "michigan", "games.json")
    .sort((a, b) => a.week - b.week || a.game_id.localeCompare(b.game_id));
}

export function nationalTeams(season: number): MichiganSeason[] {
  return readRows<MichiganSeason>("data", "published", String(season), "national", "teams.json");
}

export function findPublishedTeam(season: number, identifier: string): MichiganSeason | null {
  const wanted = decodeURIComponent(identifier).toLowerCase();
  return nationalTeams(season).find((row) => row.slug === wanted || row.team.toLowerCase() === wanted) ?? null;
}

export function publishedTeamGames(season: number, slug: string): MichiganGame[] {
  return readRows<MichiganGame>("data", "published", String(season), "teams", slug, "games.json")
    .sort((a, b) => a.week - b.week || a.game_id.localeCompare(b.game_id));
}

export function conferenceSummaries(season: number): ConferenceSummary[] {
  return readRows<ConferenceSummary>("data", "published", String(season), "national", "conferences.json");
}

export function rank(row: MichiganSeason, metric: string, scope: "national" | "conference" = "national"): number | null {
  const value = Number(row[`${scope}_${metric}_rank`]);
  return Number.isFinite(value) ? value : null;
}

export function percentile(row: MichiganSeason, metric: string, scope: "national" | "conference" = "national"): number | null {
  const value = Number(row[`${scope}_${metric}_percentile`]);
  return Number.isFinite(value) ? value : null;
}

export function michiganAppData(season = CURRENT_MICHIGAN_SEASON) {
  if (season < MICHIGAN_HISTORY_START || season > CURRENT_MICHIGAN_SEASON) return null;
  const state = seasonState(season);
  const team = michiganSeason(season);
  const games = michiganGames(season);
  const national = nationalTeams(season);
  const conference = team ? national.filter((row) => row.conference === team.conference) : [];
  const conferenceSummary = team ? conferenceSummaries(season).find((row) => row.conference === team.conference) ?? null : null;
  return { season, state, valueType: team?.value_type ?? (state === "PRESEASON" ? "PRESEASON" : "ACTUAL"), team, games, national, conference, conferenceSummary };
}
