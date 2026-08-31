// ANALYSIS layer: pure functions only. Nothing here reads a file, fetches
// a URL, or renders JSX -- everything takes already-loaded data in and
// returns plain values out, so it's independently testable and reusable
// (a future non-image use of this data could call the exact same
// functions). This is where "rank -> football sentence" happens.
import type {
  BestEdge,
  EdgeCategoryId,
  EdgeDirection,
  EdgeTier,
  GraphicMetricId,
  MatchupEdge,
  PlayCallSplit,
  PossessionCard,
  PredictionDisplay,
  Resistance,
  TeamMatchupData,
} from "./types";

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

/**
 * A category's edge is a blended UNIT comparison -- "who's the better run
 * team overall" -- averaging each team's own offensive and defensive
 * percentile in that metric, then comparing the two teams. This is
 * intentionally different from (and complements) the possession-card
 * edges below, which compare one team's offense directly against the
 * other's defense for a specific direction of play.
 */
export function buildMatchupEdges(michigan: TeamMatchupData, opponent: TeamMatchupData): MatchupEdge[] {
  return (Object.keys(EDGE_CATEGORY_LABELS) as EdgeCategoryId[]).map((id) => {
    const metricId = EDGE_CATEGORY_METRIC[id];
    const michMetric = michigan.metrics[metricId];
    const oppMetric = opponent.metrics[metricId];
    if (!michMetric || !oppMetric) {
      return { id, label: EDGE_CATEGORY_LABELS[id], score: null, tier: "insufficient" as const, direction: "even" as const, verdictLabel: "INSUFFICIENT DATA", michigan: { value: 0, rank: 0, fieldSize: 0 }, opponent: { value: 0, rank: 0, fieldSize: 0 } };
    }
    const michStrength = (percentileFromRank(michMetric.offense.rank, michMetric.offense.fieldSize) + percentileFromRank(michMetric.defense.rank, michMetric.defense.fieldSize)) / 2;
    const oppStrength = (percentileFromRank(oppMetric.offense.rank, oppMetric.offense.fieldSize) + percentileFromRank(oppMetric.defense.rank, oppMetric.defense.fieldSize)) / 2;
    const score = Math.round((michStrength - oppStrength) * 100);
    return {
      id,
      label: EDGE_CATEGORY_LABELS[id],
      score,
      tier: edgeTier(score),
      direction: edgeDirection(score),
      verdictLabel: formatEdgeVerdict(score, opponent.name),
      // "michigan"/"opponent" here surface each team's OFFENSE number for the category rail --
      // the two teams' attacking numbers in this facet, side by side.
      michigan: { value: michMetric.offense.value, rank: michMetric.offense.rank, fieldSize: michMetric.offense.fieldSize },
      opponent: { value: oppMetric.offense.value, rank: oppMetric.offense.rank, fieldSize: oppMetric.offense.fieldSize },
    };
  });
}

export function playCallSplit(team: TeamMatchupData): PlayCallSplit {
  const runPct = Math.round(team.tendencies.rushDecisionRate * 100);
  return { runPct, passPct: 100 - runPct };
}

const DIRECTIONAL_METRICS: GraphicMetricId[] = ["rushSuccessRate", "passSuccessRate", "explosivePlayRate", "successRate"];
const BEST_EDGE_LABEL: Record<GraphicMetricId, string> = {
  successRate: "OVERALL EFFICIENCY",
  rushSuccessRate: "RUN GAME",
  passSuccessRate: "PASS GAME",
  explosivePlayRate: "EXPLOSIVENESS",
  thirdDownConversionRate: "3RD DOWN",
};
const BEST_EDGE_SENTENCE: Record<GraphicMetricId, (team: string) => string> = {
  successRate: (team) => `${team} wins more snaps outright than this defense is used to allowing.`,
  rushSuccessRate: (team) => `${team} should be able to stay ahead of schedule on the ground.`,
  passSuccessRate: (team) => `${team}'s best matchup is through the air.`,
  explosivePlayRate: (team) => `${team} has the stronger big-play profile in this matchup.`,
  thirdDownConversionRate: (team) => `${team} has the edge on the down that ends drives.`,
};
const RESISTANCE_LABEL: Record<GraphicMetricId, string> = {
  successRate: "OVERALL DEFENSE",
  rushSuccessRate: "RUN DEFENSE",
  passSuccessRate: "PASS DEFENSE",
  explosivePlayRate: "BIG-PLAY DEFENSE",
  thirdDownConversionRate: "3RD-DOWN DEFENSE",
};
const RESISTANCE_SENTENCE: Record<GraphicMetricId, (team: string) => string> = {
  successRate: (team) => `${team}'s defense is not to be taken lightly on early downs.`,
  rushSuccessRate: (team) => `${team} can still make you earn it on the ground.`,
  passSuccessRate: (team) => `${team}'s pass defense is a real problem to solve.`,
  explosivePlayRate: (team) => `${team} limits the big play better than its offense suggests.`,
  thirdDownConversionRate: (team) => `${team} gets off the field on 3rd down.`,
};

/** offenseTeam's offense vs defenseTeam's defense, for every directional metric. Positive score favors offenseTeam. */
function directionalEdges(offenseTeam: TeamMatchupData, defenseTeam: TeamMatchupData): Array<{ metricId: GraphicMetricId; score: number; attacker: { value: number; rank: number; fieldSize: number }; defender: { value: number; rank: number; fieldSize: number } }> {
  return DIRECTIONAL_METRICS.map((metricId) => {
    const off = offenseTeam.metrics[metricId]?.offense;
    const def = defenseTeam.metrics[metricId]?.defense;
    if (!off || !def) return null;
    const score = Math.round((percentileFromRank(off.rank, off.fieldSize) - percentileFromRank(def.rank, def.fieldSize)) * 100);
    return { metricId, score, attacker: off, defender: def };
  }).filter((v): v is NonNullable<typeof v> => v !== null);
}

function bestOffensiveEdge(offenseTeam: TeamMatchupData, defenseTeam: TeamMatchupData, offenseTeamName: string): BestEdge {
  const edges = directionalEdges(offenseTeam, defenseTeam);
  if (edges.length === 0) return null;
  const best = edges.reduce((a, b) => (b.score > a.score ? b : a));
  return {
    metricId: best.metricId,
    label: BEST_EDGE_LABEL[best.metricId],
    attacker: best.attacker,
    defender: best.defender,
    score: best.score,
    sentence: BEST_EDGE_SENTENCE[best.metricId](offenseTeamName),
  };
}

/** The defending team's single best (lowest-rank) directional metric against this specific offense -- what to "watch out for." */
function strongestResistance(offenseTeam: TeamMatchupData, defenseTeam: TeamMatchupData, defenseTeamName: string): Resistance {
  const candidates = DIRECTIONAL_METRICS.map((metricId) => defenseTeam.metrics[metricId]?.defense && { metricId, def: defenseTeam.metrics[metricId].defense }).filter((v): v is { metricId: GraphicMetricId; def: { value: number; rank: number; fieldSize: number } } => Boolean(v));
  if (candidates.length === 0) return null;
  const best = candidates.reduce((a, b) => (b.def.rank < a.def.rank ? b : a));
  return {
    metricId: best.metricId,
    label: RESISTANCE_LABEL[best.metricId],
    value: best.def.value,
    rank: best.def.rank,
    sentence: RESISTANCE_SENTENCE[best.metricId](defenseTeamName),
  };
}

export function buildPossessionCard(offenseTeam: TeamMatchupData, defenseTeam: TeamMatchupData): PossessionCard {
  return {
    offenseTeamName: offenseTeam.name,
    defenseTeamName: defenseTeam.name,
    playCalling: playCallSplit(offenseTeam),
    bestEdge: bestOffensiveEdge(offenseTeam, defenseTeam, offenseTeam.name),
    resistance: strongestResistance(offenseTeam, defenseTeam, defenseTeam.name),
  };
}

// ---- Prediction fallback (MFF model -> market -> unavailable) ----

export type RawPrediction = { winProb: number | null; predictedMargin: number | null; dataAvailable: boolean } | null;
export type RawMarket = { teamSpread: number; sportsbook: string } | null;

export function buildPredictionDisplay(model: RawPrediction, market: RawMarket): PredictionDisplay {
  if (model?.dataAvailable && model.predictedMargin != null) {
    const abs = Math.abs(model.predictedMargin).toFixed(1);
    const marginLabel = model.predictedMargin >= 0 ? `MICHIGAN BY ${abs}` : `OPPONENT BY ${abs}`;
    return {
      type: "model",
      label: "MFF PROJECTION",
      marginLabel,
      winProbabilityPct: model.winProb != null ? Math.round(model.winProb * 1000) / 10 : null,
      marketNote: market ? `Market: Michigan ${market.teamSpread >= 0 ? "+" : ""}${market.teamSpread}` : null,
    };
  }
  if (market) {
    const spreadLabel = `MICHIGAN ${market.teamSpread >= 0 ? "+" : ""}${market.teamSpread}`;
    return { type: "market", label: "MARKET LINE", spreadLabel, book: market.sportsbook };
  }
  return { type: "unavailable" };
}
