import { teamColors } from "../../../lib/team-colors";
import type { DriveFunnelSide } from "../../../lib/creator-hub/game-story";

function pct(value: number | null, total: number | null): number {
  if (value == null || total == null || total <= 0) return 0;
  return Math.max(0, Math.min(100, (value / total) * 100));
}

function valueLabel(value: number | null, total: number | null): string {
  if (value == null) return "n/a";
  if (total == null || total <= 0) return String(value);
  return `${value} (${Math.round((value / total) * 100)}%)`;
}

export function DriveFunnelChart({
  offense,
  defense,
  michiganTeamId,
  opponentTeamId,
  opponentName,
}: {
  offense: DriveFunnelSide;
  defense: DriveFunnelSide;
  michiganTeamId: number | null;
  opponentTeamId: number | null;
  opponentName: string;
}) {
  const michigan = teamColors(michiganTeamId);
  const opponent = teamColors(opponentTeamId);
  const rows = [
    { label: "Possessions", michigan: offense.possessions, opponent: defense.possessions },
    { label: "Scoring opportunities", michigan: offense.scoringOpportunities, opponent: defense.scoringOpportunities },
    { label: "Red-zone possessions", michigan: offense.redZonePossessions, opponent: defense.redZonePossessions },
    { label: "Touchdowns", michigan: offense.touchdowns, opponent: defense.touchdowns },
  ];

  return (
    <section className="ch-data-panel">
      <div className="ch-data-panel-head">
        <div>
          <h2>Drive conversion funnel</h2>
          <p>How often each offense turned possessions into real scoring chances and touchdowns.</p>
        </div>
      </div>

      <div className="ch-funnel-legend">
        <span><i style={{ background: michigan.primary }} /> Michigan</span>
        <span><i style={{ background: opponent.primary }} /> {opponentName}</span>
      </div>

      <div className="ch-funnel-chart">
        {rows.map((row, index) => {
          const michiganPct = index === 0 ? 100 : pct(row.michigan, offense.possessions);
          const opponentPct = index === 0 ? 100 : pct(row.opponent, defense.possessions);
          return (
            <div className="ch-funnel-stage" key={row.label}>
              <div className="ch-funnel-label">{row.label}</div>
              <div className="ch-funnel-series">
                <div className="ch-funnel-track">
                  <div className="ch-funnel-fill" style={{ width: `${michiganPct}%`, background: michigan.primary }} />
                </div>
                <strong>{valueLabel(row.michigan, offense.possessions)}</strong>
              </div>
              <div className="ch-funnel-series">
                <div className="ch-funnel-track">
                  <div className="ch-funnel-fill" style={{ width: `${opponentPct}%`, background: opponent.primary }} />
                </div>
                <strong>{valueLabel(row.opponent, defense.possessions)}</strong>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
