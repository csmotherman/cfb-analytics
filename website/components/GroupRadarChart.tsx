import type { UnitDetailMetric } from "../lib/unit-detail";

const SHORT_LABEL: Record<string, string> = {
  success_rate: "Success", rush_success_rate: "Rush Success", pass_success_rate: "Pass Success",
  standard_down_success_rate: "Standard Down", passing_down_success_rate: "Passing Down",
  late_down_success_rate: "Late Down", third_down_distance: "3rd Dn Dist.",
  ppa_play: "PPA / Play", early_down_ppa_play: "Early Down PPA", rush_ppa_play: "Rush PPA",
  pass_ppa_dropback: "Pass PPA/DB", explosive_play_rate: "Explosive", rush_explosive_rate: "Rush Explosive",
  pass_explosive_rate: "Pass Explosive", yards_per_successful_play: "Yds/Success",
  line_yards: "Line Yards", opportunity_rate: "Opp. Rate", stuff_rate: "Stuff Rate",
  rush_yards_per_attempt: "Yds/Attempt", sack_rate: "Sack Rate", tfl_per_game: "TFL / Gm",
  yards_per_dropback: "Yds/Dropback", pass_yards_per_game: "Pass Yds/Gm", interceptions_per_game: "INT / Gm",
  third_down_conversion_rate: "3rd Dn Conv.", fourth_down_conversion_rate: "4th Dn Conv.",
  red_zone_scoring_rate: "RZ Scoring", red_zone_td_rate: "RZ TD", points_per_drive: "Pts / Drive",
  havoc_rate: "Havoc", turnovers_per_game: "Turnovers / Gm",
};

const round = (v: number) => Math.round(v * 100) / 100;

export function GroupRadarChart({ metrics }: { metrics: UnitDetailMetric[] }) {
  const usable = metrics.filter(m => m.percentile != null);
  if (usable.length < 5) return null;

  // Large and confident on purpose: a radar squeezed into a small box with a
  // tiny polygon and 9px labels reads as decoration, not data. This is sized
  // so the shape itself is the dominant element, with the percentile printed
  // right at each vertex -- readable at a glance, no cross-referencing the
  // table required. Width > height for label margin (see the main radar's
  // module for why: side-anchored labels need real horizontal room or they
  // clip against the viewBox edge).
  const n = usable.length;
  const width = 640;
  const height = 480;
  const cx = width / 2;
  const cy = height / 2;
  const R = 172;
  const labelR = R + 62;
  const valueR = R + 26;

  const angleFor = (i: number) => -Math.PI / 2 + (i * 2 * Math.PI) / n;
  const pointAt = (i: number, pct: number, radius = R) => {
    const angle = angleFor(i);
    const r = radius * (Math.max(0, Math.min(100, pct)) / 100);
    return [round(cx + r * Math.cos(angle)), round(cy + r * Math.sin(angle))] as const;
  };
  const ringLevels = [50, 100];
  const ringPolygon = (level: number) =>
    Array.from({ length: n }, (_, i) => {
      const angle = angleFor(i);
      const r = R * (level / 100);
      return `${round(cx + r * Math.cos(angle))},${round(cy + r * Math.sin(angle))}`;
    }).join(" ");
  const dataPolygon = usable.map((m, i) => pointAt(i, m.percentile ?? 0).join(",")).join(" ");

  return <svg viewBox={`0 0 ${width} ${height}`} className="group-radar-svg" role="img" aria-label="Group percentile radar">
    {ringLevels.map(level => <polygon key={level} points={ringPolygon(level)} className="group-radar-ring" />)}
    {usable.map((_, i) => {
      const [x, y] = pointAt(i, 100);
      return <line key={i} x1={cx} y1={cy} x2={x} y2={y} className="group-radar-spoke" />;
    })}
    <polygon points={dataPolygon} className="group-radar-fill" />
    <polygon points={dataPolygon} className="group-radar-stroke" />
    {usable.map((m, i) => {
      const [x, y] = pointAt(i, m.percentile ?? 0);
      return <circle key={m.key} cx={x} cy={y} r={6} className="group-radar-vertex" />;
    })}
    {usable.map((m, i) => {
      const angle = angleFor(i);
      const cos = Math.cos(angle);
      const anchor = cos > 0.3 ? "start" : cos < -0.3 ? "end" : "middle";
      const [lx, ly] = [round(cx + labelR * Math.cos(angle)), round(cy + labelR * Math.sin(angle))];
      // Percentile number sits between the vertex and the label, on the same
      // spoke, so it's unambiguous which axis it belongs to.
      const pct = Math.round(m.percentile ?? 0);
      const outward = pct >= 92 ? valueR - 14 : valueR;
      const [vx, vy] = [round(cx + outward * Math.cos(angle)), round(cy + outward * Math.sin(angle))];
      return <g key={m.key}>
        <text x={vx} y={vy} textAnchor="middle" dominantBaseline="middle" className="group-radar-value">{pct}</text>
        <text x={lx} y={ly} textAnchor={anchor} dominantBaseline="middle" className="group-radar-label">
          {SHORT_LABEL[m.key] ?? m.label}
        </text>
      </g>;
    })}
  </svg>;
}
