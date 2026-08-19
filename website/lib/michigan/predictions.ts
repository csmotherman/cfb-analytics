import { readJson } from "../server-data";

export type GamePrediction = {
  gameId: string;
  season: number;
  week: number;
  homeTeam: string;
  awayTeam: string;
  predictedWinner: string;
  predictedHomeMargin: number;
  teamPredictedMargin: number;
  asOf: string;
  valueType: "PROJECTED";
  modelVersion: string;
  winProbability: null;
};

type PredictionPublication = {
  version: string;
  probabilityStatus: "NOT_CALIBRATED";
  games: GamePrediction[];
};

export type MarketOutlook = {
  version: string;
  season: number;
  team: string;
  valueType: "BENCHMARK";
  cfp: {
    format: "12_TEAM_2026";
    makePlayoffYesAmerican: number;
    makePlayoffNoAmerican: number;
    noVigImpliedProbability: number;
    calculation: string;
  };
  asOf: string;
  source: { name: string; url: string };
  disclaimer: string;
};

export function gamePredictions(): GamePrediction[] {
  return readJson<PredictionPublication>("data", "published", "2026", "michigan", "game-predictions.json")?.games ?? [];
}

export function predictionForGame(gameId: string | number): GamePrediction | null {
  return gamePredictions().find((prediction) => prediction.gameId === String(gameId)) ?? null;
}

export function currentMarketOutlook(): MarketOutlook | null {
  return readJson<MarketOutlook>("data", "published", "2026", "michigan", "outlook.json");
}

export function describeTeamMargin(prediction: GamePrediction): string {
  const margin = Math.abs(prediction.teamPredictedMargin).toFixed(1);
  return prediction.teamPredictedMargin >= 0 ? `Michigan by ${margin}` : `${prediction.predictedWinner} by ${margin}`;
}
