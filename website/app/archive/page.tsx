import Link from "next/link";

import { ArchiveBrowser } from "../../components/ArchiveBrowser";
import { getArchiveAllTimeSummary, getArchiveIndex } from "../../lib/archive";

export const metadata = {
  title: "Model Results & Archive",
  description: "See Beat the Model's all-time straight-up results and browse every archived college football week since 2014.",
};

function percent(value: number | null): string {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}

export default function ArchivePage() {
  const index = getArchiveIndex();
  const summary = getArchiveAllTimeSummary(index);

  return (
    <>
      <section className="fan-archive-hero">
        <div>
          <span className="fan-kicker">THE MODEL'S RECEIPTS</span>
          <h1>Don’t take our word for it. Check every result.</h1>
          <p>The historical game archive starts in 2014. Every supported pregame model call stays attached to the actual final score so fans can judge the record themselves.</p>
        </div>
        <Link className="fan-button fan-button-primary" href="/play">Make this week’s picks</Link>
      </section>

      <section className="fan-all-time-record" aria-labelledby="all-time-heading">
        <div className="fan-all-time-copy">
          <span className="fan-kicker">ALL-TIME MODEL RESULTS</span>
          <h2 id="all-time-heading">{summary.modelCalls ? `${summary.wins}-${summary.losses}` : "Record building"}</h2>
          <p>
            Straight-up winner calls with a final result.
            {summary.earliestModelSeason ? ` Supported archived model calls begin in ${summary.earliestModelSeason}.` : ""}
          </p>
        </div>
        <div className="fan-all-time-stats">
          <div><span>Accuracy</span><strong>{percent(summary.accuracy)}</strong></div>
          <div><span>Graded calls</span><strong>{summary.modelCalls.toLocaleString()}</strong></div>
          <div><span>Weeks archived</span><strong>{summary.weeks}</strong></div>
          <div><span>Games in archive</span><strong>{summary.games.toLocaleString()}</strong></div>
        </div>
      </section>

      <div className="fan-archive-honesty-note">
        <strong>What “since 2014” means:</strong>
        <span>The site preserves game history beginning in 2014, but it does not invent old model calls where a supported pregame prediction does not exist. Those games are clearly labeled “No model call” and are excluded from accuracy. 2020 remains intentionally omitted.</span>
      </div>

      <ArchiveBrowser index={index} />

      <section className="fan-section" aria-labelledby="season-history-heading">
        <div className="fan-section-heading">
          <div><span className="fan-kicker">YEAR BY YEAR</span><h2 id="season-history-heading">Model record by season.</h2></div>
        </div>
        <div className="fan-season-record-grid">
          {summary.seasonRecords.map((record) => {
            const entry = index.find((item) => item.season === record.season);
            const firstWeek = entry?.weeks[0] ?? 1;
            return (
              <Link key={record.season} href={`/archive/${record.season}/${firstWeek}`} className="fan-season-record-card">
                <header><strong>{record.season}</strong><span>{record.weeks} weeks</span></header>
                {record.modelCalls ? (
                  <>
                    <div className="fan-season-record-main"><strong>{record.wins}-{record.losses}</strong><span>{percent(record.accuracy)}</span></div>
                    <footer>{record.modelCalls} graded model calls <span aria-hidden="true">→</span></footer>
                  </>
                ) : (
                  <>
                    <div className="fan-season-record-main"><strong>Game history</strong><span>—</span></div>
                    <footer>No supported model calls <span aria-hidden="true">→</span></footer>
                  </>
                )}
              </Link>
            );
          })}
        </div>
      </section>
    </>
  );
}
