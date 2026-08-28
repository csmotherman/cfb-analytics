import { teamColors } from "../../../lib/team-colors";
import type { HalfSplitSide } from "../../../lib/creator-hub/game-story";

function pct(value: number | null): number {
  if (value == null) return 0;
  return Math.max(0, Math.min(100, value * 100));
}

function label(value: number | null): string {
  return value == null ? "n/a" : `${(value * 100).toFixed(1)}%`;
}

export function HalfSplitChart({
  michigan,
  opponent,
  michiganTeamId,
  opponentTeamId,
  opponentName,
}: {
  michigan: HalfSplitSide;
  opponent: HalfSplitSide;
  michiganTeamId: number | null;
  opponentTeamId: number | null;
  opponentName: string;
}) {
  const michiganColors = teamColors(michiganTeamId);
  const opponentColors = teamColors(opponentTeamId);
  const halves = [
    {
      label: "1st half",
      michiganRate: michigan.firstHalf.successRate,
      michiganPlays: michigan.firstHalf.eligiblePlays,
      opponentRate: opponent.firstHalf.successRate,
      opponentPlays: opponent.firstHalf.eligiblePlays,
    },
    {
      label: "2nd half",
      michiganRate: michigan.secondHalf.successRate,
      michiganPlays: michigan.secondHalf.eligiblePlays,
      opponentRate: opponent.secondHalf.successRate,
      opponentPlays: opponent.secondHalf.eligiblePlays,
    },
  ];

  return (
    <section className="ch-data-panel">
      <div className="ch-data-panel-head">
        <div>
          <h2>Success rate by half</h2>
          <p>Whether Michigan sustained its efficiency or changed after halftime.</p>
        </div>
      </div>

      <div className="ch-half-chart" role="img" aria-label={`Success rate by half for Michigan and ${opponentName}`}>
        <div className="ch-half-yaxis"><span>100%</span><span>50%</span><span>0%</span></div>
        <div className="ch-half-groups">
          {halves.map((half) => (
            <div className="ch-half-group" key={half.label}>
              <div className="ch-half-bars">
                <div className="ch-half-bar-wrap">
                  <span className="ch-half-value">{label(half.michiganRate)}</span>
                  <div className="ch-half-bar" style={{ height: `${Math.max(pct(half.michiganRate), 2)}%`, background: michiganColors.primary }} />
                </div>
                <div className="ch-half-bar-wrap">
                  <span className="ch-half-value">{label(half.opponentRate)}</span>
                  <div className="ch-half-bar" style={{ height: `${Math.max(pct(half.opponentRate), 2)}%`, background: opponentColors.primary }} />
                </div>
              </div>
              <strong>{half.label}</strong>
              <small>Michigan {half.michiganPlays} plays · {opponentName} {half.opponentPlays}</small>
            </div>
          ))}
        </div>
      </div>

      <div className="ch-funnel-legend">
        <span><i style={{ background: michiganColors.primary }} /> Michigan</span>
        <span><i style={{ background: opponentColors.primary }} /> {opponentName}</span>
      </div>
    </section>
  );
}
