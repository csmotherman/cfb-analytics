// Reusable Michigan-vs-opponent matchup graphic: shared types.
//
// DATA -> ANALYSIS -> PRESENTATION, kept in three separate files on
// purpose (data-source.ts / analysis.ts / presentation.tsx) so the edge
// math and the JSX can each change independently:
//   data-source.ts   reads the published per-game JSON (raw ranked values)
//   analysis.ts       pure functions: percentiles, edge scores, verdicts,
//                      per-phase breakdowns, prediction fallback
//   build-matchup.ts  orchestrates the two into one MatchupGraphicData
//   presentation.tsx  the JSX -- takes MatchupGraphicData, has ZERO
//                      opponent-specific logic or hardcoded team names

export type RankedValue = { rank: number; fieldSize: number };
export type RankedScore = RankedValue & { score: number };

export type MetricTier = "validated" | "research-only";

/** One metric's value for both units of one team, e.g. successRate. */
export type TeamMetric = {
  offense: RankedValue & { value: number };
  defense: RankedValue & { value: number };
  tier: MetricTier;
};

export const GRAPHIC_METRIC_IDS = ["successRate", "rushSuccessRate", "passSuccessRate", "explosivePlayRate", "thirdDownConversionRate"] as const;
export type GraphicMetricId = (typeof GRAPHIC_METRIC_IDS)[number];

export type TeamQuality = { overall: RankedScore; offense: RankedScore; defense: RankedScore };

export type FieldPosition = { ownYardLine: number; games: number } | null;

/** Raw, as-published team profile -- exactly what data-source.ts returns. No analysis yet. */
export type TeamMatchupData = {
  teamId: number;
  name: string;
  record: string;
  quality: TeamQuality;
  tendencies: { rushDecisionRate: number; dropbackRate: number; possessionsPerGame: number };
  metrics: Record<GraphicMetricId, TeamMetric>;
  fieldPosition: FieldPosition;
};

/** As-published root JSON: data/published/2026/michigan/matchup-graphics/<gameId>.json */
export type MatchupGraphicSource = {
  definitionVersion: string;
  gameId: string;
  season: number;
  week: number;
  kickoffISO: string;
  venue: string | null;
  analysisSeason: number;
  analysisModel: string;
  michigan: TeamMatchupData;
  opponent: TeamMatchupData;
};

// ---- Analysis-layer output types ----

/** "strong"/"moderate"/"slight" pair with a direction ("even"/"insufficient" have no direction). Formatted into
 * a display string (e.g. "STRONG OKLAHOMA EDGE") by analysis.ts's formatEdgeVerdict, which is
 * where the real opponent name gets substituted in -- never a hardcoded team name in a type. */
export type EdgeTier = "strong" | "moderate" | "slight" | "even" | "insufficient";
export type EdgeDirection = "michigan" | "opponent" | "even";

export type EdgeCategoryId = "efficiency" | "run" | "pass" | "explosiveness" | "situational";

/**
 * One category row inside a possession phase: the acting team's offense
 * in this metric against the facing team's defense in this metric --
 * never offense-vs-offense or defense-vs-defense. `score`/`tier`/`direction`
 * are Michigan-centric (positive score = Michigan favored) so the same
 * verdict vocabulary and color rule apply in both phases, even when
 * Michigan is the one on defense. `offenseScore` is offense-centric
 * (positive = the acting/offense team favored) and exists only to pick
 * the offense's own best/worst category -- see analysis.ts.
 */
export type PhaseEdgeRow = {
  id: EdgeCategoryId;
  label: string;
  offense: RankedValue & { value: number };
  defense: RankedValue & { value: number };
  score: number | null;
  offenseScore: number | null;
  tier: EdgeTier;
  direction: EdgeDirection;
  verdictLabel: string;
};

export type PlayCallSplit = { runPct: number; passPct: number };

/** "When [offenseTeamName] has the ball": offense's 5 metrics vs the facing defense's same 5, plus one deterministic summary sentence. */
export type PossessionPhase = {
  offenseTeamName: string;
  defenseTeamName: string;
  playCalling: PlayCallSplit;
  rows: PhaseEdgeRow[];
  whatItMeans: string;
};

export type PredictionDisplay =
  | { type: "model"; label: "MFF PROJECTION"; marginLabel: string; winProbabilityPct: number | null; marketNote: string | null }
  | { type: "market"; label: "MARKET LINE"; spreadLabel: string; book: string }
  | { type: "unavailable" };

/** Fully analyzed data the presentation layer consumes. Built by build-matchup.ts. */
export type MatchupGraphicData = {
  gameId: string;
  season: number;
  week: number;
  kickoffISO: string;
  venue: string;
  michigan: TeamMatchupData;
  opponent: TeamMatchupData;
  whenMichiganHasBall: PossessionPhase;
  whenOpponentHasBall: PossessionPhase;
  prediction: PredictionDisplay;
  bottomLine: string;
};
