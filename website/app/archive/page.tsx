import Link from "next/link";

import { ArchiveBrowser } from "../../components/ArchiveBrowser";
import { getArchiveIndex } from "../../lib/archive";

export const metadata = {
  title: "Beat the Model Archive",
  description: "Browse the permanent weekly cards, model picks, and final results from Beat the Model.",
};

export default function ArchivePage() {
  const index = getArchiveIndex();
  const seasons = index.length;

  return (
    <>
      <section className="fan-page-intro">
        <div>
          <span className="fan-kicker">THE RECEIPTS</span>
          <h1>Every call stays on the record.</h1>
          <p>The archive is where Beat the Model earns trust. Revisit a published week to see the original ranked card, The Model’s pick in every game, and what actually happened.</p>
        </div>
      </section>

      <section className="fan-info-strip" aria-label="Archive details">
        <div><span>Seasons available</span><strong>{seasons || "—"}</strong></div>
        <div><span>Weekly record</span><strong>Permanent cards</strong></div>
        <div><span>Prediction edits</span><strong>None after lock</strong></div>
      </section>

      <ArchiveBrowser index={index} />

      <section className="fan-dashboard-grid fan-section">
        <article className="fan-feature-panel">
          <span className="fan-kicker">WHY THIS EXISTS</span>
          <h2>No disappearing bad picks.</h2>
          <p>A prediction game only matters if the misses are as visible as the hits. The archive keeps the weekly card and results together so The Model’s record can be checked instead of advertised.</p>
        </article>
        <article className="fan-feature-panel fan-model-panel">
          <span className="fan-kicker">THIS WEEK</span>
          <h2>The next receipt starts with your card.</h2>
          <p>Make your picks before kickoff, reveal The Model, and give Saturday something to settle.</p>
          <Link className="fan-text-link" href="/play">Go to the current week →</Link>
        </article>
      </section>
    </>
  );
}
