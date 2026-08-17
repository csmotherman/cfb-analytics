import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Pools",
  description: "Private and public Beat the Model pools are planned after the core weekly game is complete.",
};

export default function PoolsPage() {
  return (
    <>
      <section className="fan-page-intro">
        <div>
          <span className="fan-kicker">POOLS</span>
          <h1>Compete with friends—soon.</h1>
          <p>Pools will use the exact same Official 15, scoring rules, and locked weekly card as the core game. They are intentionally staying out of the main navigation until they are ready.</p>
        </div>
      </section>

      <section className="fan-empty-state">
        <span className="fan-status fan-status-amber">Coming later</span>
        <h2>The weekly picking game comes first.</h2>
        <p>Once the core mobile experience is solid, private friend pools and a public leaderboard can sit on top without changing how anyone makes or scores picks.</p>
        <div className="fan-hero-actions">
          <Link className="fan-button fan-button-primary" href="/play">Play this week</Link>
          <Link className="fan-button fan-button-secondary" href="/about">See how it works</Link>
        </div>
      </section>
    </>
  );
}
