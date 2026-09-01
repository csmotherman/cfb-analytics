// ANALYSIS layer: pure functions only. Nothing here reads a file, fetches
// a URL, or renders JSX -- everything takes already-loaded data in and
// returns plain values out, so it's independently testable and reusable
// (a future non-image use of this data could call the exact same
// functions). This is where "rank -> football sentence" happens.
import type { EdgeCategoryId, EdgeDirection, EdgeTier, GraphicMetricId, PhaseEdgeRow, PlayCallSplit, PossessionPhase, RankedValue, TeamMatchupData } from "./types";

// National rank -> percentile, where 1.0 is the best team in the field
// and 0.0 is the worst. Uses the field's own reported size rather than a
// hardcoded 136, so this keeps working if the FBS field size changes.
export function percentileFromRank(rank: number, fieldSize: number): number {
  if (fieldSize <= 1) return 0.5;
  return (fieldSize - rank) / (fieldSize - 1);
}

export function edgeTier(score: number): EdgeTier {
  const abs = Math.abs(score);
  if (abs >= 35) return "strong";
  if (abs >= 15) return "moderate";
  if (abs >= 5) return "slight";
  return "even";
}

export function edgeDirection(score: number): EdgeDirection {
  if (score >= 5) return "michigan";
  if (score <= -5) return "opponent";
  return "even";
}

// The opponent's real name is substituted in here -- never a hardcoded
// team name baked into a type or a string-replace hack on a fixed enum.
export function formatEdgeVerdict(score: number, opponentName: string): string {
  const tier = edgeTier(score);
  const direction = edgeDirection(score);
  if (direction === "even") return "EVEN";
  const team = direction === "michigan" ? "MICHIGAN" : opponentName.toUpperCase();
  if (tier === "strong") return `STRONG ${team} EDGE`;
  if (tier === "moderate") return `${team} EDGE`;
  return `SLIGHT ${team} EDGE`;
}

export function playCallSplit(team: TeamMatchupData): PlayCallSplit {
  const runPct = Math.round(team.tendencies.rushDecisionRate * 100);
  return { runPct, passPct: 100 - runPct };
}

const CATEGORY_ORDER: EdgeCategoryId[] = ["efficiency", "run", "pass", "explosiveness", "situational"];
const EDGE_CATEGORY_LABELS: Record<EdgeCategoryId, string> = {
  efficiency: "OVERALL EFFICIENCY",
  run: "RUN GAME",
  pass: "PASS GAME",
  explosiveness: "EXPLOSIVENESS",
  situational: "3RD DOWN",
};
const EDGE_CATEGORY_METRIC: Record<EdgeCategoryId, GraphicMetricId> = {
  efficiency: "successRate",
  run: "rushSuccessRate",
  pass: "passSuccessRate",
  explosiveness: "explosivePlayRate",
  situational: "thirdDownConversionRate",
};

function emptyRanked(): RankedValue & { value: number } {
  return { value: 0, rank: 0, fieldSize: 0 };
}

/**
 * Every row compares the acting team's OFFENSE metric against the facing
 * team's DEFENSE metric in the same category -- never offense-vs-offense
 * or defense-vs-defense (see types.ts's PhaseEdgeRow doc). `score` is
 * always expressed Michigan-centric (positive = Michigan favored) so the
 * verdict vocabulary and the maize/opponent-accent color rule work
 * identically in both phases, even on the phase where Michigan is the
 * defense. `offenseScore` keeps the un-flipped, offense-centric version
 * (positive = the acting/offense team favored) so the offense's own
 * best/worst category can be picked regardless of who that offense is.
 */
export function buildPhaseRows(offenseTeam: TeamMatchupData, defenseTeam: TeamMatchupData, offenseIsMichigan: boolean, opponentName: string): PhaseEdgeRow[] {
  return CATEGORY_ORDER.map((id) => {
    const metricId = EDGE_CATEGORY_METRIC[id];
    const off = offenseTeam.metrics[metricId]?.offense;
    const def = defenseTeam.metrics[metricId]?.defense;
    if (!off || !def) {
      return { id, label: EDGE_CATEGORY_LABELS[id], offense: emptyRanked(), defense: emptyRanked(), score: null, offenseScore: null, tier: "insufficient" as const, direction: "even" as const, verdictLabel: "INSUFFICIENT DATA" };
    }
    const offenseScore = Math.round((percentileFromRank(off.rank, off.fieldSize) - percentileFromRank(def.rank, def.fieldSize)) * 100);
    const score = offenseIsMichigan ? offenseScore : -offenseScore;
    return {
      id,
      label: EDGE_CATEGORY_LABELS[id],
      offense: off,
      defense: def,
      score,
      offenseScore,
      tier: edgeTier(score),
      direction: edgeDirection(score),
      verdictLabel: formatEdgeVerdict(score, opponentName),
    };
  });
}

const ADVANTAGE_PHRASE: Record<EdgeCategoryId, string> = {
  efficiency: "in overall efficiency",
  run: "on the ground",
  pass: "through the air",
  explosiveness: "in explosive plays",
  situational: "on third down",
};
const BEST_PATH_NOUN: Record<EdgeCategoryId, string> = {
  efficiency: "overall efficiency",
  run: "the run game",
  pass: "the passing game",
  explosiveness: "explosive plays",
  situational: "third down",
};
const OWNS_NOUN: Record<EdgeCategoryId, string> = {
  efficiency: "efficiency",
  run: "running",
  pass: "passing",
  explosiveness: "explosive-play",
  situational: "third-down",
};

/**
 * A team's "best path" is whichever category it's least disadvantaged in
 * -- not necessarily one it actually wins. Only call it a genuine
 * "advantage" when the offense's own best category actually clears the
 * even threshold; otherwise phrase it as a best path for the offense
 * while naming what the defense actually owns, so a team can never be
 * described as having an "advantage" it doesn't have (see analysis
 * notes: possession-card copy must not conflate best option with edge).
 */
export function phaseWhatItMeans(rows: PhaseEdgeRow[], offenseTeamName: string, defenseTeamName: string): string {
  const scored = rows.filter((r): r is PhaseEdgeRow & { offenseScore: number } => r.offenseScore != null);
  if (scored.length === 0) return `${offenseTeamName} and ${defenseTeamName} don't have enough data here for a clear read.`;
  const best = scored.reduce((a, b) => (b.offenseScore > a.offenseScore ? b : a));
  const worst = scored.reduce((a, b) => (b.offenseScore < a.offenseScore ? b : a));
  if (best.offenseScore > 5) return `${offenseTeamName}'s clearest advantage is ${ADVANTAGE_PHRASE[best.id]}.`;
  if (worst.offenseScore < -5) return `${offenseTeamName}'s best path is ${BEST_PATH_NOUN[best.id]}, while ${defenseTeamName} owns the ${OWNS_NOUN[worst.id]} matchup.`;
  return `${offenseTeamName} and ${defenseTeamName} grade out closely across the board.`;
}

export function buildPossessionPhase(offenseTeam: TeamMatchupData, defenseTeam: TeamMatchupData, offenseIsMichigan: boolean, opponentName: string): PossessionPhase {
  const rows = buildPhaseRows(offenseTeam, defenseTeam, offenseIsMichigan, opponentName);
  return {
    offenseTeamName: offenseTeam.name,
    defenseTeamName: defenseTeam.name,
    playCalling: playCallSplit(offenseTeam),
    rows,
    whatItMeans: phaseWhatItMeans(rows, offenseTeam.name, defenseTeam.name),
  };
}

// ---- Prediction fallback (MFF model -> market -> unavailable) ----

export type RawPrediction = { winProb: number | null; predictedMargin: number | null; dataAvailable: boolean } | null;
export type RawMarket = { teamSpread: number; sportsbook: string } | null;

export function buildPredictionDisplay(model: RawPrediction, market: RawMarket) {
  if (model?.dataAvailable && model.predictedMargin != null) {
    const abs = Math.abs(model.predictedMargin).toFixed(1);
    const marginLabel = model.predictedMargin >= 0 ? `MICHIGAN BY ${abs}` : `OPPONENT BY ${abs}`;
    return {
      type: "model" as const,
      label: "MFF PROJECTION" as const,
      marginLabel,
      winProbabilityPct: model.winProb != null ? Math.round(model.winProb * 1000) / 10 : null,
      marketNote: market ? `Market: Michigan ${market.teamSpread >= 0 ? "+" : ""}${market.teamSpread}` : null,
    };
  }
  if (market) {
    const spreadLabel = `MICHIGAN ${market.teamSpread >= 0 ? "+" : ""}${market.teamSpread}`;
    return { type: "market" as const, label: "MARKET LINE" as const, spreadLabel, book: market.sportsbook };
  }
  return { type: "unavailable" as const };
}
