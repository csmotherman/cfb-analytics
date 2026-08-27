import { Fragment } from "react";
import type { MatrixCell } from "../../lib/michigan/beck-audit-data";

const DOWN_ORDER = ["1st Down", "2nd Down", "3rd/4th Down"];
const BUCKET_ORDER = ["Short (1-3)", "Medium (4-7)", "Long (8+)"];

function pct(v: number | null, digits = 0): string {
  return v == null ? "—" : `${(v * 100).toFixed(digits)}%`;
}

export function PlaycallingMatrix({ title, accent, cells }: { title: string; accent: "mi" | "ut"; cells: MatrixCell[] }) {
  return (
    <div className={`pc-matrix-panel pc-${accent}`}>
      <h4>{title}</h4>
      <div className="pc-swipe"><span>&harr;</span> SWIPE FOR LONG YARDAGE</div>
      <div className="pc-matrix-scroll"><div className="pc-matrix-grid">
        <div className="pc-matrix-corner" />
        {BUCKET_ORDER.map(b => (
          <div className="pc-matrix-colhead" key={b}>{b.replace(" (", "\n(")}</div>
        ))}
        {DOWN_ORDER.map(d => (
          <Fragment key={d}>
            <div className="pc-matrix-rowhead">{d}</div>
            {BUCKET_ORDER.map(b => {
              const cell = cells.find(c => c.down === d && c.bucket === b);
              if (!cell || cell.totalPlays === 0) {
                return <div className="pc-matrix-cell pc-thin" key={b}><span className="pc-cell-n">n=0</span></div>;
              }
              const thin = cell.totalPlays < 15;
              const runSR = cell.run.successRate;
              const passSR = cell.pass.successRate;
              const runWins = runSR != null && (passSR == null || runSR >= passSR);
              const runPct = cell.runRate != null ? Math.round(cell.runRate * 100) : 0;
              return (
                <div className={`pc-matrix-cell${thin ? " pc-thin" : ""}`} key={b}>
                  <span className="pc-cell-n">n={cell.totalPlays}</span>
                  <div className="pc-cell-split">
                    <i style={{ width: `${runPct}%` }} />
                    <i style={{ width: `${100 - runPct}%`, background: "var(--pc-pass)" }} />
                  </div>
                  <div className={`pc-cell-line${runWins ? " pc-win" : ""}`}>
                    <b>RUN</b> {pct(runSR)} <small>{runPct}% called</small>
                  </div>
                  <div className={`pc-cell-line pc-pass${!runWins && passSR != null ? " pc-win" : ""}`}>
                    <b>PASS</b> {pct(passSR)} <small>{100 - runPct}% called</small>
                  </div>
                </div>
              );
            })}
          </Fragment>
        ))}
      </div></div>
    </div>
  );
}
