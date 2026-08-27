import type { UnitDetailProfile, UnitDetailMetric } from "../lib/unit-detail";
import { GroupRadarChart } from "./GroupRadarChart";

const GROUP_LABEL: Record<string, { offense: string; defense: string; kicker: string }> = {
  "Efficiency": { offense: "OFFENSIVE EFFICIENCY", defense: "EFFICIENCY ALLOWED", kicker: "STAYING ON SCHEDULE" },
  "Explosiveness": { offense: "EXPLOSIVENESS", defense: "EXPLOSIVENESS ALLOWED", kicker: "CHUNK-PLAY ABILITY" },
  "Line Play": { offense: "OFFENSIVE LINE", defense: "DEFENSIVE LINE", kicker: "IN THE TRENCHES" },
  "Passing": { offense: "PASSING GAME", defense: "PASS DEFENSE", kicker: "THROUGH THE AIR" },
  "Situational": { offense: "SITUATIONAL & FINISHING", defense: "SITUATIONAL & FINISHING", kicker: "3RD DOWN, RED ZONE, POINTS" },
  "Havoc & Turnovers": { offense: "HAVOC & TURNOVERS", defense: "HAVOC & TAKEAWAYS", kicker: "DISRUPTION" },
};

function formatValue(m: UnitDetailMetric): string {
  if (m.value == null) return "—";
  if (m.unit === "rate") return `${(m.value * 100).toFixed(1)}%`;
  if (m.unit === "ppa") return m.value.toFixed(3);
  if (m.unit === "count") return m.value.toFixed(2);
  return m.value.toFixed(2);
}

function tierClass(percentile: number | null): string {
  if (percentile == null) return "";
  if (percentile >= 80) return "ud-elite";
  if (percentile >= 55) return "ud-good";
  if (percentile >= 30) return "ud-mid";
  return "ud-low";
}

function MetricTable({ metrics, side }: { metrics: UnitDetailMetric[]; side: "offense" | "defense" }) {
  return <div className="ud-table-shell">
    <div className="ud-swipe"><span>↔</span> SWIPE FOR RANK &amp; PERCENTILE</div>
    <div className="ud-table-wrap">
      <table className="ud-table">
        <thead><tr><th>METRIC</th><th>VALUE</th><th>RANK</th><th>PERCENTILE</th></tr></thead>
        <tbody>
          {metrics.map(m => <tr key={m.key}>
            <td className="ud-metric-label">
              {m.label}
              {!m.higherIsBetter && <small>LOWER IS BETTER</small>}
            </td>
            <td className="ud-value">{formatValue(m)}</td>
            <td className="ud-rank">{m.rank != null ? `#${m.rank}/${m.fieldSize}` : "—"}</td>
            <td className="ud-pct-cell">
              {m.percentile != null ? <div className="ud-pct-bar">
                <div className="ud-pct-track"><div className={`ud-pct-fill ${tierClass(m.percentile)}`} style={{ width: `${Math.max(2, m.percentile)}%` }} /></div>
                <b>{Math.round(m.percentile)}</b>
              </div> : "—"}
            </td>
          </tr>)}
        </tbody>
      </table>
    </div>
  </div>;
}

export function UnitDetailTables({ profile, side, season }: { profile: UnitDetailProfile | null; side: "offense" | "defense"; season: number }) {
  if (!profile || profile.metrics.length === 0) {
    const message = season >= 2026
      ? `The ${season} season hasn't been played yet — check back once games are in the books.`
      : season < 2014
      ? `This site's play-by-play analytics start in 2014. Pick a season from 2014 onward to see ${side} data.`
      : `No ${side} analytics are available for this season yet.`;
    return <section className="ud-empty"><p>{message}</p></section>;
  }

  const byGroup = new Map<string, UnitDetailMetric[]>();
  for (const m of profile.metrics) {
    if (!byGroup.has(m.group)) byGroup.set(m.group, []);
    byGroup.get(m.group)!.push(m);
  }

  return <>
    {profile.sampleSizeCaveat && <div className="ud-caveat">{profile.sampleSizeCaveat}</div>}
    {profile.groups.map(group => {
      const metrics = byGroup.get(group);
      if (!metrics || metrics.length === 0) return null;
      const meta = GROUP_LABEL[group] ?? { offense: group.toUpperCase(), defense: group.toUpperCase(), kicker: "" };
      // A radar with too few axes (a triangle, a line) doesn't read as a
      // shape -- it reads as a small, mostly-empty decoration. Only draw one
      // where there's enough data for the polygon to actually mean something.
      const chartable = metrics.filter(m => m.percentile != null).length >= 5;
      return <section className="ud-group" key={group}>
        <header><span className="ud-kicker">{meta.kicker}</span><h2>{side === "offense" ? meta.offense : meta.defense}</h2></header>
        <div className={chartable ? "ud-group-layout" : "ud-group-layout ud-no-radar"}>
          {chartable && <div className="ud-group-radar"><GroupRadarChart metrics={metrics}/></div>}
          <MetricTable metrics={metrics} side={side} />
        </div>
      </section>;
    })}
  </>;
}
