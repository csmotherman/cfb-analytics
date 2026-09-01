// Orchestration: DATA (data-source.ts + this repo's existing schedule/
// prediction/market readers) -> ANALYSIS (analysis.ts) -> one
// MatchupGraphicData for the presentation layer. This is the only file
// that's allowed to call both the raw reader and the analysis functions;
// presentation.tsx never touches data-source.ts or does its own math.
import { readMatchupGraphicSource } from "./data-source";
import { buildPossessionPhase, buildPredictionDisplay, matchupBottomLine } from "./analysis";
import type { MatchupGraphicData } from "./types";
import { preseasonProjectionForGame } from "../preseason-power";
import { marketLineFor } from "../market-lines";

export function buildMatchupGraphicData(gameId: string | number): MatchupGraphicData | null {
  const source = readMatchupGraphicSource(gameId);
  if (!source) return null;

  // The site has two independent prediction pipelines: game-predictions.json
  // (margin only, probabilityStatus "NOT_CALIBRATED") and the calibrated
  // 50,000-run preseason simulation (preseason-2026-projection.json), which
  // is the one that actually carries a win probability. Use the calibrated
  // one -- it's what every other MFF model number on the site already is.
  const projection = preseasonProjectionForGame(gameId);
  const market = marketLineFor(gameId);

  const whenMichiganHasBall = buildPossessionPhase(source.michigan, source.opponent, true, source.opponent.name);
  const whenOpponentHasBall = buildPossessionPhase(source.opponent, source.michigan, false, source.opponent.name);

  return {
    gameId: source.gameId,
    season: source.season,
    week: source.week,
    kickoffISO: source.kickoffISO,
    venue: source.venue ?? "TBD",
    michigan: source.michigan,
    opponent: source.opponent,
    whenMichiganHasBall,
    whenOpponentHasBall,
    prediction: buildPredictionDisplay(
      projection && projection.dataAvailable ? { winProb: projection.winProb, predictedMargin: projection.predictedMargin, dataAvailable: true } : null,
      market ? { teamSpread: market.teamSpread, sportsbook: market.sportsbook } : null
    ),
    bottomLine: matchupBottomLine(whenMichiganHasBall.rows, whenOpponentHasBall.rows, source.michigan.name, source.opponent.name),
  };
}
