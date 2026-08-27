import type { TrendGame } from "../../lib/michigan/beck-audit-data";

const OPP_SHORT: Record<string, string> = {
  "New Mexico": "N.Mex", "Central Michigan": "CMU", "Michigan State": "MSU",
  "Northwestern": "NW", "Ohio State": "OSU", "Washington": "Wash", "Wisconsin": "Wisc",
};

const CALLOUTS: Record<string, { label: string; dx: number; dy: number; anchor: "start" | "middle" | "end" }> = {
  "Central Michigan": { label: "CMU · 64.5%", dx: 14, dy: -16, anchor: "start" },
  "Ohio State": { label: "OSU · 25.6%", dx: -10, dy: 34, anchor: "end" },
  "Texas": { label: "TEXAS · 39.5%", dx: -16, dy: -22, anchor: "end" },
};

const round = (v: number) => Math.round(v * 100) / 100;

export function PlaycallingTrendChart({ games, utahAvg }: { games: TrendGame[]; utahAvg: number }) {
  const W = 1080, H = 430, padL = 58, padR = 24, padT = 38, padB = 74;
  const chartW = W - padL - padR, chartH = H - padT - padB;
  const n = games.length;
  const x = (i: number) => round(padL + (i / Math.max(n - 1, 1)) * chartW);
  const y = (v: number) => round(padT + (1 - Math.min(Math.max(v, 0), 0.7) / 0.7) * chartH);
  const sepX = n > 1 ? round((x(n - 2) + x(n - 1)) / 2) : W - padR;
  const ticks = [0, 0.2, 0.4, 0.6];

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="pc-trend-svg" role="img" aria-label="Michigan offensive success rate by game in 2025, with passing-down success shown as dots and Utah's regular-season average as a benchmark">
      <rect x={sepX} y={padT} width={W - padR - sepX} height={chartH} className="pc-trend-postseason" />
      <text x={W - padR - 8} y={padT + 16} textAnchor="end" className="pc-trend-postseason-label">CASULA · BOWL</text>

      {ticks.map(v => (
        <g key={v}>
          <line x1={padL} x2={W - padR} y1={y(v)} y2={y(v)} className="pc-trend-grid" />
          <text x={padL - 12} y={y(v) + 4} textAnchor="end" className="pc-trend-tip">{v * 100}%</text>
        </g>
      ))}

      <line x1={sepX} x2={sepX} y1={padT} y2={H - padB} className="pc-trend-sep" />
      <text x={sepX - 8} y={padT - 12} textAnchor="end" className="pc-trend-sep-label">LINDSEY</text>

      <line x1={padL} x2={W - padR} y1={y(utahAvg)} y2={y(utahAvg)} className="pc-trend-bench" />
      <text x={W - padR} y={y(utahAvg) - 8} textAnchor="end" className="pc-trend-bench-label">UTAH AVG {(utahAvg * 100).toFixed(1)}%</text>

      <polyline
        points={games.map((game, i) => `${x(i)},${y(game.successRate)}`).join(" ")}
        className="pc-trend-line-main"
      />

      {games.map((game, i) => {
        const cx = x(i);
        const overallY = y(game.successRate);
        const passingY = y(game.passingDownSuccessRate);
        const label = OPP_SHORT[game.opponent] ?? game.opponent;
        const callout = CALLOUTS[game.opponent];
        const calloutX = callout ? cx + callout.dx : cx;
        const calloutY = callout ? overallY + callout.dy : overallY;

        return (
          <g key={game.order}>
            <circle cx={cx} cy={passingY} r={4} className="pc-trend-pass-point">
              <title>{`${game.opponent}: ${(game.passingDownSuccessRate * 100).toFixed(1)}% passing-down success`}</title>
            </circle>
            <circle cx={cx} cy={overallY} r={6} className={`pc-trend-point${game.win ? " pc-win" : ""}`}>
              <title>{`${game.opponent} (${game.win ? "W" : "L"}) — ${(game.successRate * 100).toFixed(1)}% overall success`}</title>
            </circle>
            {callout ? (
              <g className="pc-trend-callout">
                <line x1={cx} y1={overallY} x2={calloutX} y2={calloutY - 5} />
                <text x={calloutX} y={calloutY} textAnchor={callout.anchor}>{callout.label}</text>
              </g>
            ) : null}
            <text x={cx} y={H - padB + 24} textAnchor="end" className="pc-trend-opponent" transform={`rotate(-42 ${cx} ${H - padB + 24})`}>{label}</text>
          </g>
        );
      })}
    </svg>
  );
}
