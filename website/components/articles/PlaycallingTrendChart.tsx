import type { TrendGame } from "../../lib/michigan/beck-audit-data";

const OPP_SHORT: Record<string, string> = {
  "New Mexico": "N.Mex", "Central Michigan": "C.Mich", "Michigan State": "Mich St",
  "Northwestern": "N'western", "Ohio State": "Ohio St", "Washington": "Wash", "Wisconsin": "Wisc",
};

const round = (v: number) => Math.round(v * 100) / 100;

export function PlaycallingTrendChart({ games, utahAvg }: { games: TrendGame[]; utahAvg: number }) {
  const W = 1080, H = 380, padL = 54, padR = 20, padT = 20, padB = 56;
  const chartW = W - padL - padR, chartH = H - padT - padB;
  const n = games.length;
  const x = (i: number) => round(padL + (i / (n - 1)) * chartW);
  const y = (v: number) => round(padT + (1 - v) * chartH);
  const sepX = round((x(n - 2) + x(n - 1)) / 2);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="pc-trend-svg" role="img" aria-label="Michigan offensive success rate by game, 2025 season">
      {[0, 0.25, 0.5, 0.75, 1].map(v => (
        <g key={v}>
          <line x1={padL} x2={W - padR} y1={y(v)} y2={y(v)} className="pc-trend-grid" />
          <text x={padL - 10} y={y(v) + 4} textAnchor="end" className="pc-trend-tip">{v * 100}%</text>
        </g>
      ))}

      <line x1={sepX} x2={sepX} y1={padT} y2={H - padB + 6} className="pc-trend-sep" />
      <text x={sepX} y={padT - 4} textAnchor="middle" className="pc-trend-tip pc-trend-sep-label">Casula (interim) →</text>

      <line x1={padL} x2={W - padR} y1={y(utahAvg)} y2={y(utahAvg)} className="pc-trend-bench" />
      <text x={W - padR} y={y(utahAvg) - 6} textAnchor="end" className="pc-trend-tip">Utah avg {(utahAvg * 100).toFixed(1)}%</text>

      <polyline
        points={games.map((g, i) => `${x(i)},${y(g.passingDownSuccessRate)}`).join(" ")}
        className="pc-trend-line-pass"
      />
      <polyline
        points={games.map((g, i) => `${x(i)},${y(g.successRate)}`).join(" ")}
        className="pc-trend-line-main"
      />

      {games.map((g, i) => {
        const cx = x(i), cy = y(g.successRate);
        const label = OPP_SHORT[g.opponent] ?? g.opponent;
        return (
          <g key={g.order}>
            <circle cx={cx} cy={cy} r={5} className={`pc-trend-point${g.win ? " pc-win" : ""}`}>
              <title>{`${g.opponent} (${g.win ? "W" : "L"}) — ${(g.successRate * 100).toFixed(1)}% success`}</title>
            </circle>
            <text x={cx} y={H - padB + 20} textAnchor="end" className="pc-trend-tip" transform={`rotate(-42 ${cx} ${H - padB + 20})`}>{label}</text>
          </g>
        );
      })}
    </svg>
  );
}
