import { formatMetricValue } from "../../../lib/creator-hub/format-metric";
import { Visual16x9Frame } from "./Visual16x9Frame";

type Bar = { label: string; value: number | null; color: string };

/**
 * Generic two-bar comparison ("season avg vs today", "what opponent
 * normally allows vs what Michigan did") -- the same visual shape covers
 * both the baseline and opponent-adjusted comparisons the product spec asks
 * for, parameterized by which two values are passed in.
 */
export function ComparisonBarChart({
  title,
  metric,
  bars,
  source,
}: {
  title: string;
  metric: string;
  bars: [Bar, Bar];
  source: string;
}) {
  const max = Math.max(...bars.map((b) => b.value ?? 0), 0.0001);
  return (
    <Visual16x9Frame title={title} source={source}>
      <div className="ch-viz-bars">
        {bars.map((bar) => (
          <div key={bar.label} className="ch-viz-bar-row">
            <span className="ch-viz-bar-label">{bar.label}</span>
            <div className="ch-viz-bar-track">
              <div className="ch-viz-bar-fill" style={{ width: `${Math.max(((bar.value ?? 0) / max) * 100, 2)}%`, background: bar.color }} />
            </div>
            <span className="ch-viz-bar-value">{formatMetricValue(metric, bar.value)}</span>
          </div>
        ))}
      </div>
    </Visual16x9Frame>
  );
}
