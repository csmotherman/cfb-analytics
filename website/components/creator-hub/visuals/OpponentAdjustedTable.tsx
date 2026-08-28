import { formatMetricDelta, formatMetricValue } from "../../../lib/creator-hub/format-metric";
import type { GameStory } from "../../../lib/creator-hub/game-story";

const SIGNAL_LABEL: Record<string, string> = {
  STRONG_SIGNAL: "Strong",
  WATCH: "Watch",
  LIKELY_NOISY: "Noisy",
};

function metricLabel(metric: string): string {
  return metric
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/Allowed$/i, " allowed")
    .replace(/^./, (c) => c.toUpperCase());
}

export function OpponentAdjustedTable({
  stories,
  opponentName,
}: {
  stories: GameStory[];
  opponentName: string;
}) {
  if (stories.length === 0) return null;

  const ordered = [...stories].sort((a, b) => {
    const signalOrder = { STRONG_SIGNAL: 0, WATCH: 1, LIKELY_NOISY: 2 } as const;
    const signalDiff = signalOrder[a.signalClass] - signalOrder[b.signalClass];
    if (signalDiff !== 0) return signalDiff;
    const aExtreme = a.percentile.percentile == null ? 0 : Math.abs(a.percentile.percentile - 0.5);
    const bExtreme = b.percentile.percentile == null ? 0 : Math.abs(b.percentile.percentile - 0.5);
    return bExtreme - aExtreme;
  });

  return (
    <section className="ch-data-panel ch-data-panel-wide">
      <div className="ch-data-panel-head">
        <div>
          <h2>Opponent-adjusted performance</h2>
          <p>Michigan&apos;s game value compared with what {opponentName} normally allowed or produced.</p>
        </div>
      </div>
      <div className="ch-insight-table-wrap">
        <table className="ch-insight-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Michigan</th>
              <th>{opponentName} baseline</th>
              <th>vs expectation</th>
              <th>Rank vs {opponentName}</th>
              <th>Signal</th>
            </tr>
          </thead>
          <tbody>
            {ordered.map((story) => {
              const gameValue = story.context.gameValue as number | null | undefined;
              const baseline = story.context.opponentBaseline as number | null | undefined;
              const rank = story.percentile.rank;
              const sample = story.percentile.sampleSize;
              return (
                <tr key={story.id}>
                  <td>
                    <strong>{metricLabel(story.metric)}</strong>
                    <span className={`ch-table-polarity ${story.polarity}`}>{story.side}</span>
                  </td>
                  <td className="numeric">{formatMetricValue(story.metric, gameValue)}</td>
                  <td className="numeric">{formatMetricValue(story.metric, baseline)}</td>
                  <td className="numeric"><strong>{formatMetricDelta(story.metric, story.delta)}</strong></td>
                  <td className="numeric">{rank != null ? `#${rank} / ${sample}` : "n/a"}</td>
                  <td><span className={`ch-table-signal ${story.signalClass.toLowerCase()}`}>{SIGNAL_LABEL[story.signalClass]}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
