export type ResidualSeries = {
  tag: string;
  value: number | null;
  scaleMax: number;
  valueLabel: string;
};

export type ResidualRow = {
  key: string;
  opponent: string;
  site: "home" | "away";
  oppRank: number | null;
  series: ResidualSeries[];
};

function barWidthPct(value: number, scaleMax: number): number {
  return Math.min(Math.abs(value) / scaleMax, 1) * 50;
}

export function ResidualChart({ rows, seriesCount = 1 }: { rows: ResidualRow[]; seriesCount?: number }) {
  return (
    <div className={`rc-shell ${seriesCount > 1 ? "rc-multi" : "rc-single"}`}>
      {rows.map((row) => (
        <div className="rc-row" key={row.key}>
          <div className="rc-label">
            {row.site === "away" ? <span className="rc-site">@</span> : null}
            <span className="rc-opp">{row.opponent}</span>
            {row.oppRank ? <span className="rc-rank">#{row.oppRank}</span> : null}
          </div>
          <div className="rc-series-stack">
            {row.series.map((s, i) => (
              <div className="rc-series-line" key={i}>
                {seriesCount > 1 ? <span className="rc-tag">{s.tag}</span> : null}
                <div className="rc-track">
                  {s.value !== null ? (
                    <span
                      className={`rc-fill ${s.value >= 0 ? "rc-pos" : "rc-neg"}`}
                      style={{ width: `${barWidthPct(s.value, s.scaleMax)}%` }}
                    />
                  ) : null}
                </div>
                <span className={`rc-value ${s.value !== null ? (s.value >= 0 ? "rc-pos-text" : "rc-neg-text") : "rc-muted-text"}`}>
                  {s.valueLabel}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
