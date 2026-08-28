// Presentation-only formatting (no calculation) mirroring the rate/points/
// yards distinction in src/cfb_analytics/analytics/game_story/stories.py's
// _RATE_METRICS set, so a value like averageStartYardsToGoal never renders
// as a nonsense percentage.
const RATE_METRICS = new Set([
  "successRate", "successRateAllowed", "rushSuccessRate", "rushSuccessRateAllowed",
  "passSuccessRate", "passSuccessRateAllowed", "explosivePlayRate", "explosivePlayRateAllowed",
  "havocRate", "havocRateAllowed", "standardDownSuccessRate", "standardDownSuccessRateAllowed",
  "passingDownSuccessRate", "passingDownSuccessRateAllowed", "thirdDownConversionRate",
  "thirdDownConversionRateAllowed", "redZonePossessionTouchdownRate", "redZonePossessionTouchdownRateAllowed",
]);

export function isRateMetric(metric: string): boolean {
  return RATE_METRICS.has(metric);
}

export function formatMetricValue(metric: string, value: number | null | undefined): string {
  if (value == null) return "n/a";
  return isRateMetric(metric) ? `${(value * 100).toFixed(1)}%` : value.toFixed(2);
}

export function formatMetricDelta(metric: string, delta: number | null | undefined): string {
  if (delta == null) return "n/a";
  return isRateMetric(metric) ? `${(delta * 100 >= 0 ? "+" : "")}${(delta * 100).toFixed(1)} pts` : `${delta >= 0 ? "+" : ""}${delta.toFixed(2)}`;
}
