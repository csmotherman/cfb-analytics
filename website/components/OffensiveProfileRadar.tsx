"use client";

import { useState } from "react";
import type { OffensiveProfile, OffensiveProfileMetric } from "../lib/offensive-profile";

const SHORT_LABEL: Record<string, string> = {
  ppa_play: "PPA / Play",
  early_down_ppa_play: "Early Down PPA",
  late_down_success_rate: "Late Down SR",
  rush_ppa_play: "Rush PPA",
  stuff_rate: "Stuff Rate",
  line_yards: "Line Yards",
  opportunity_rate: "Opp. Rate",
  explosive_play_rate: "Explosive Rate",
  pass_ppa_dropback: "Pass PPA / DB",
  yards_per_dropback: "Yds / Dropback",
  pass_success_rate: "Pass Success",
  havoc_rate_allowed: "Havoc Allowed",
};

function formatValue(m: OffensiveProfileMetric): string {
  if (m.value == null) return "—";
  if (m.unit === "rate") return `${(m.value * 100).toFixed(1)}%`;
  if (m.unit === "ppa") return m.value.toFixed(3);
  return m.value.toFixed(2);
}

function ordinal(n: number): string {
  const mod100 = n % 100;
  if (mod100 >= 11 && mod100 <= 13) return `${n}th`;
  switch (n % 10) {
    case 1: return `${n}st`;
    case 2: return `${n}nd`;
    case 3: return `${n}rd`;
    default: return `${n}th`;
  }
}

function DetailPanel({ metric }: { metric: OffensiveProfileMetric }) {
  return <div className="radar-detail">
    <div className="radar-detail-head">
      <strong>{metric.label}</strong>
      {!metric.higherIsBetter && <span className="radar-detail-flag">LOWER IS BETTER</span>}
    </div>
    <div className="radar-detail-body">
      <span className="radar-detail-value">{formatValue(metric)}</span>
      <span className="radar-detail-rank">{metric.rank != null ? `#${metric.rank} of ${metric.fieldSize} FBS` : "—"}</span>
      <span className="radar-detail-pct">{metric.percentile != null ? `${ordinal(Math.round(metric.percentile))} percentile` : "—"}</span>
    </div>
  </div>;
}

function RadarSvg({ metrics, onSelect, selectedKey }: { metrics: OffensiveProfileMetric[]; onSelect: (key: string) => void; selectedKey: string }) {
  // Width is generously larger than height: the left/right-most axis labels
  // ("YDS / DROPBACK", "HAVOC ALLOWED") are drawn anchored outward from the
  // ring and need real horizontal margin, or they run past the viewBox edge
  // and get clipped. Vertical labels are single short words and don't need
  // the same margin, so the box stays wide rather than growing the whole
  // chart taller than it needs to be.
  const width = 760;
  const height = 560;
  const cx = width / 2;
  const cy = height / 2;
  const R = 190;
  const labelR = R + 46;
  const n = metrics.length;

  // Rounded to a fixed precision so server- and client-rendered markup match
  // byte-for-byte -- raw trig output can differ in the last float digit
  // between Node's and the browser's Math implementations, which otherwise
  // triggers a (harmless but noisy) hydration mismatch on every load.
  const round = (v: number) => Math.round(v * 100) / 100;
  const angleFor = (i: number) => -Math.PI / 2 + (i * 2 * Math.PI) / n;
  const pointAt = (i: number, pct: number) => {
    const angle = angleFor(i);
    const r = R * (Math.max(0, Math.min(100, pct)) / 100);
    return [round(cx + r * Math.cos(angle)), round(cy + r * Math.sin(angle))] as const;
  };

  const ringLevels = [25, 50, 75, 100];
  const ringPolygon = (level: number) =>
    Array.from({ length: n }, (_, i) => {
      const angle = angleFor(i);
      const r = R * (level / 100);
      return `${round(cx + r * Math.cos(angle))},${round(cy + r * Math.sin(angle))}`;
    }).join(" ");

  const dataPolygon = metrics.map((m, i) => pointAt(i, m.percentile ?? 0).join(",")).join(" ");

  return <svg viewBox={`0 0 ${width} ${height}`} className="radar-svg" role="img" aria-label="Offensive profile radar chart">
    {ringLevels.map(level => <polygon key={level} points={ringPolygon(level)} className="radar-ring" />)}
    {metrics.map((_, i) => {
      const [x, y] = pointAt(i, 100);
      return <line key={i} x1={cx} y1={cy} x2={x} y2={y} className="radar-spoke" />;
    })}

    <polygon points={dataPolygon} className="radar-fill" />
    <polygon points={dataPolygon} className="radar-stroke" />

    {metrics.map((m, i) => {
      const [x, y] = pointAt(i, m.percentile ?? 0);
      const active = m.key === selectedKey;
      return <circle
        key={m.key} cx={x} cy={y} r={active ? 7 : 5.5}
        className={`radar-vertex${active ? " active" : ""}`}
        tabIndex={0} role="button" aria-label={`${m.label}: ${formatValue(m)}, ${m.percentile != null ? ordinal(Math.round(m.percentile)) : "unknown"} percentile`}
        onMouseEnter={() => onSelect(m.key)}
        onFocus={() => onSelect(m.key)}
        onClick={() => onSelect(m.key)}
        onKeyDown={e => { if (e.key === "Enter" || e.key === " ") onSelect(m.key); }}
      />;
    })}

    {metrics.map((m, i) => {
      const angle = angleFor(i);
      const x = round(cx + labelR * Math.cos(angle));
      const y = round(cy + labelR * Math.sin(angle));
      const cos = Math.cos(angle);
      const anchor = cos > 0.3 ? "start" : cos < -0.3 ? "end" : "middle";
      const active = m.key === selectedKey;
      return <text
        key={m.key} x={x} y={y} textAnchor={anchor} dominantBaseline="middle"
        className={`radar-label${active ? " active" : ""}`}
        tabIndex={0} role="button"
        onMouseEnter={() => onSelect(m.key)}
        onFocus={() => onSelect(m.key)}
        onClick={() => onSelect(m.key)}
      >{SHORT_LABEL[m.key] ?? m.label}</text>;
    })}

    {ringLevels.map(level => {
      const r = R * (level / 100);
      return <text key={level} x={cx + 6} y={round(cy - r)} className="radar-ring-label">{level}</text>;
    })}
  </svg>;
}

export function OffensiveProfileRadar({ season, data }: { season: number; data: OffensiveProfile | null }) {
  const metrics = data?.metrics ?? [];
  const [selectedKey, setSelectedKey] = useState<string>(metrics[0]?.key ?? "");
  const selected = metrics.find(m => m.key === selectedKey) ?? metrics[0];

  if (!data || metrics.length === 0) {
    return <section className="mock-section radar-card">
      <header><div><span className="mock-eyebrow maize">{season} OFFENSIVE PROFILE</span><h2>National percentile among FBS offenses</h2></div></header>
      <p className="radar-empty">No offensive profile is available for {season} yet.</p>
    </section>;
  }

  return <section className="mock-section radar-card">
    <header><div>
      <span className="mock-eyebrow maize">{season} OFFENSIVE PROFILE</span>
      <h2>National percentile among FBS offenses</h2>
      <p className="radar-subtitle">100 = best in FBS that season · 50 = FBS median · every axis points outward toward better offense.</p>
      {data.sampleSizeCaveat && <p className="radar-caveat">{data.sampleSizeCaveat}</p>}
    </div></header>

    <div className="radar-layout">
      <div className="radar-desktop">
        <RadarSvg metrics={metrics} onSelect={setSelectedKey} selectedKey={selectedKey} />
        {selected && <DetailPanel metric={selected} />}
      </div>

      <div className="radar-mobile">
        {metrics.map(m => {
          const pct = m.percentile ?? 0;
          return <div className="radar-bar-row" key={m.key}>
            <div className="radar-bar-label">
              <strong>{m.label}</strong>
              {!m.higherIsBetter && <small>LOWER IS BETTER</small>}
            </div>
            <div className="radar-bar-track"><div className="radar-bar-fill" style={{ width: `${Math.max(2, pct)}%` }} /></div>
            <div className="radar-bar-meta">
              <span>{formatValue(m)}</span>
              <span>{m.rank != null ? `#${m.rank}/${m.fieldSize}` : "—"}</span>
              <b>{m.percentile != null ? `${Math.round(m.percentile)}%ile` : "—"}</b>
            </div>
          </div>;
        })}
      </div>
    </div>
  </section>;
}
