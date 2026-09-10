import raw from "./big-game-decisions-data.json";

export type MetricSplit = { actual: number; expected: number | null; residual: number | null };

export type GameRow = {
  week: number;
  seasonType: "regular" | "postseason";
  opponent: string;
  oppRank: number | null;
  teamPoints: number;
  oppPoints: number;
  site: "home" | "away";
  success: MetricSplit;
  passSuccess: MetricSplit;
  passYPD: MetricSplit;
};

export type EpaByGame = {
  week: number;
  seasonType: "regular" | "postseason";
  opponent: string;
  plays: number;
  avgEpa: number | null;
};

export type EpaSummary = {
  rushAvgEpa: number;
  passAvgEpa: number;
  rankedAvgEpa: number;
  unrankedAvgEpa: number;
  rankedRushAvgEpa: number;
  unrankedRushAvgEpa: number;
  rankedPassAvgEpa: number;
  unrankedPassAvgEpa: number;
  totalPlays: number;
};

export type FourthDownDecision = {
  gameId: number;
  down: number;
  distance: number;
  yardsToGoal: number;
  actual: "go" | "fieldGoal" | "punt";
  actualEv: number | null;
  recommended: "go" | "fieldGoal" | "punt";
  recommendedEv: number;
  evLost: number | null;
  ev: Partial<Record<"go" | "fieldGoal" | "punt", number>>;
  goForItRate: number | null;
  fieldGoalMakeRate: number | null;
  definitionVersion: string;
  week: number;
  seasonType: "regular" | "postseason";
  opponent: string;
  period: number;
  clock: { minutes: number; seconds: number };
};

export type FourthDownSummary = {
  totalDecisions: number;
  correctDecisions: number;
  incorrectDecisions: number;
  totalEvLost: number;
  byActual: Record<"go" | "fieldGoal" | "punt", { count: number; correct: number; evLost: number }>;
};

export type BigGameDecisionsData = {
  team: string;
  season: number;
  qbName: string;
  games: GameRow[];
  epaByGame: EpaByGame[];
  epaSummary: EpaSummary;
  fourthDowns: FourthDownDecision[];
  fourthDownSummary: FourthDownSummary;
};

export const bigGameDecisionsData = raw as BigGameDecisionsData;
