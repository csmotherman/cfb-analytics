import Link from "next/link";
import { ArchiveBrowser } from "./ArchiveBrowser";
import { PredictionCard } from "./PredictionCard";
import { getArchiveIndex } from "../lib/archive";
import {
  formatUpdatedAt,
  getPredictionDataset,
  seasonRecord,
} from "../lib/predictions";

export function PredictionFeed() {
  const data = getPredictionDataset();
  const record = seasonRecord(data.results);
  const updated = formatUpdatedAt(data.updatedAt);
  const [featured, ...rest] = data.current;
  const archiveIndex = getArchiveIndex();

  return (
    <>
      <section className="prediction-hero">
        <div className="eyebrow">{data.season} COLLEGE FOOTBALL PREDICTIONS</div>
        <h1>Who wins this week?</h1>
        <p>One model. One answer. Three clear reasons why.</p>
        <div className="hero-proof">
          {record.games > 0 ? (
            <>
              <strong>{record.wins}-{record.losses}</strong>
              <span>season record</span>
              <span className="proof-divider">•</span>
              <strong>{Math.round((record.accuracy ?? 0) * 100)}%</strong>
              <span>correct</span>
            </>
          ) : (
            <span>Every prediction is locked before kickoff and stays public afterward.</span>
          )}
          {updated ? <><span className="proof-divider">•</span><span>Updated {updated}</span></> : null}
        </div>
      </section>

      {featured ? (
        <section className="prediction-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">FEATURED</span>
              <h2>Week {data.week}</h2>
            </div>
          </div>
          <PredictionCard game={featured} featured />
          {rest.length > 0 ? (
            <div className="prediction-list">
              {rest.map((game) => <PredictionCard key={game.id} game={game} />)}
            </div>
          ) : null}
        </section>
      ) : (
        <section className="launch-state">
          <span className="eyebrow">WEEK {data.week}</span>
          <h2>The prediction feed is ready.</h2>
          <p>As soon as the live {data.season} slate is scored, every model pick will publish here with a projected score, win probability, and exactly three reasons behind it.</p>
          <div className="launch-rules">
            <span>Locked before kickoff</span>
            <span>Results stay public</span>
            <span>No post-game edits</span>
          </div>
        </section>
      )}

      <ArchiveBrowser index={archiveIndex} />

      <section className="accountability-strip">
        <div>
          <span className="eyebrow">WHY COME BACK?</span>
          <h2>The model keeps receipts.</h2>
          <p>Every pick stays on the record. No disappearing losses, no rewritten predictions.</p>
        </div>
        <Link className="text-link" href="/results">See the results <span aria-hidden="true">→</span></Link>
      </section>
    </>
  );
}
