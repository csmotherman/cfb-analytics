import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Pools",
  description: "Compete against friends or the public field on the same Beat the Model weekly card.",
};

export default function PoolsPage() {
  return (
    <>
      <section className="page-hero compact-hero btm-page-hero">
        <span className="eyebrow">POOLS</span>
        <h1>Same 15 games. Your people.</h1>
        <p>Everyone plays the exact same Official 15 and The Model appears in every pool as another competitor. Private and public pools are the social layer built on top of the core picking game.</p>
      </section>

      <section className="btm-pool-grid">
        <article className="btm-pool-card">
          <span className="eyebrow">PRIVATE POOL</span>
          <h2>Friends & family</h2>
          <p>Create a room, share an invite code, and compete week by week. The Model sits in the standings beside everyone else.</p>
          <div className="btm-pool-example">
            <span>1</span><strong>You</strong><em>12</em>
            <span>2</span><strong>The Model</strong><em>11</em>
            <span>3</span><strong>Ethan</strong><em>10</em>
            <span>4</span><strong>Jake</strong><em>9</em>
          </div>
          <span className="btm-coming-pill">Pool accounts coming next</span>
        </article>

        <article className="btm-pool-card">
          <span className="eyebrow">PUBLIC POOL</span>
          <h2>Everyone vs. The Model</h2>
          <p>Join the weekly public field, see your percentile, and find out how many players actually knew more than The Model.</p>
          <div className="btm-public-example">
            <div><span>Your score</span><strong>13-2</strong></div>
            <div><span>The Model</span><strong>11-4</strong></div>
            <div><span>Your finish</span><strong>Top 8%</strong></div>
          </div>
          <span className="btm-coming-pill">Public leaderboard coming next</span>
        </article>
      </section>

      <section className="btm-pool-rule">
        <div>
          <span className="eyebrow">NO DIFFERENT RULES</span>
          <h2>Pools never change the game.</h2>
          <p>Correct winner = 1 point. No confidence points, multipliers, power-ups, or betting lines. A pool is simply another place to compare the same locked weekly card.</p>
        </div>
        <Link className="btm-primary-cta" href="/play">Play the core game</Link>
      </section>
    </>
  );
}
