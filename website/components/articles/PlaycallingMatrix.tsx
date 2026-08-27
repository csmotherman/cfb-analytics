import { Fragment } from "react";
import type { MatrixCell } from "../../lib/michigan/beck-audit-data";

const DOWN_ORDER = ["1st Down", "2nd Down", "3rd/4th Down"];
const BUCKET_ORDER = ["Short (1-3)", "Medium (4-7)", "Long (8+)"];
const MIN_FAMILY_SAMPLE = 15;

function pct(v: number | null, digits = 0): string {
  return v == null ? "—" : `${(v * 100).toFixed(digits)}%`;
}

function observedEdgeLabel(runRate: number, passRate: number): string {
  const gap = Math.round(Math.abs(runRate - passRate) * 100);
  return `${runRate > passRate ? "RUSH" : "DROPBACK"} +${gap} pts observed`;
}

export function PlaycallingMatrix({ title, accent, cells }: { title: string; accent: "mi" | "ut"; cells: MatrixCell[] }) {
  return (
    <div className={`pc-matrix-panel pc-${accent}`}>
      <div className="pc-matrix-heading">
        <h4>{title}</h4>
        <span>ACTUAL · 2025 REGULAR SEASON</span>
      </div>
      <div className="pc-swipe"><span>&harr;</span> SWIPE FOR LONG YARDAGE</div>
      <div className="pc-matrix-scroll">
        <div className="pc-matrix-grid" role="table" aria-label={`${title} rush versus dropback outcomes by down and distance`}>
          <div className="pc-matrix-corner" />
          {BUCKET_ORDER.map(bucket => (
            <div className="pc-matrix-colhead" role="columnheader" key={bucket}>{bucket.replace(" (", "\n(")}</div>
          ))}
          {DOWN_ORDER.map(down => (
            <Fragment key={down}>
              <div className="pc-matrix-rowhead" role="rowheader">
                {down === "3rd/4th Down" ? "Late Downs\n(3rd/4th)" : down}
              </div>
              {BUCKET_ORDER.map(bucket => {
                const cell = cells.find(candidate => candidate.down === down && candidate.bucket === bucket);
                if (!cell || cell.totalPlays === 0) {
                  return <div className="pc-matrix-cell pc-thin" role="cell" key={bucket}><span className="pc-cell-n">NO PLAYS</span></div>;
                }

                const runSR = cell.run.successRate;
                const passSR = cell.pass.successRate;
                const runPct = cell.runRate != null ? Math.round(cell.runRate * 100) : 0;
                const passPct = 100 - runPct;
                const comparisonReady = cell.run.plays >= MIN_FAMILY_SAMPLE && cell.pass.plays >= MIN_FAMILY_SAMPLE && runSR != null && passSR != null;
                const meaningfulGap = comparisonReady && Math.abs(runSR - passSR) >= 0.08;
                const lowSample = !comparisonReady;

                return (
                  <div className={`pc-matrix-cell${lowSample ? " pc-thin" : ""}`} role="cell" key={bucket}>
                    <div className="pc-cell-topline">
                      <span className="pc-cell-n">n={cell.totalPlays}</span>
                      {lowSample ? <span className="pc-cell-caution">SAMPLE CAUTION</span> : null}
                    </div>
                    <div className="pc-cell-split" aria-label={`${runPct}% rush family, ${passPct}% dropback family`}>
                      <i style={{ width: `${runPct}%` }} />
                      <i style={{ width: `${passPct}%` }} />
                    </div>
                    <div className={`pc-cell-line${meaningfulGap && runSR! > passSR! ? " pc-observed-edge" : ""}`}>
                      <b>RUSH</b><strong>{pct(runSR)}</strong><small>{cell.run.plays} plays · {runPct}% share</small>
                    </div>
                    <div className={`pc-cell-line pc-pass${meaningfulGap && passSR! > runSR! ? " pc-observed-edge" : ""}`}>
                      <b>DROPBACK</b><strong>{pct(passSR)}</strong><small>{cell.pass.plays} plays · {passPct}% share</small>
                    </div>
                    {meaningfulGap ? <span className="pc-cell-edge-note">{observedEdgeLabel(runSR!, passSR!)}</span> : null}
                  </div>
                );
              })}
            </Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
