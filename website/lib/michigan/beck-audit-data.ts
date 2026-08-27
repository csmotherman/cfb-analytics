import raw from "./beck-audit-data.json";

export type TrendGame = {
  order: number;
  opponent: string;
  seasonType: "regular" | "postseason";
  win: boolean;
  successRate: number;
  passingDownSuccessRate: number;
};

export type MatrixCell = {
  down: string;
  bucket: string;
  totalPlays: number;
  runRate: number | null;
  run: { plays: number; successRate: number | null };
  pass: { plays: number; successRate: number | null };
};

export type TeamSummary = {
  successRate: number;
  passingDownSuccessRate: number;
  explosivePlayRate: number;
  redZoneTouchdownRate: number;
  thirdDownConversionRate: number;
  sackRate: number;
  yardsPerPlay: number;
  runRate: number;
  pointsPerGame: number;
};

export type RedZoneSplit = {
  runRate: number;
  run: { successRate: number; avgPpa: number };
  pass: { successRate: number; avgPpa: number };
};

export type BeckAuditData = {
  michigan: {
    trend: TrendGame[];
    matrix: MatrixCell[];
    redZone: RedZoneSplit;
    seasonSummary: TeamSummary;
    firstHalfSummary: TeamSummary;
    secondHalfSummary: TeamSummary;
    moneyDownPassPpa: number;
  };
  utah: {
    matrix: MatrixCell[];
    redZone: RedZoneSplit;
    seasonSummary: TeamSummary;
    moneyDownPassPpa: number;
  };
};

export const beckAuditData = raw as BeckAuditData;
