import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "How it works",
  description: "How Beat the Model ranks teams, chooses the Official 15, locks predictions, and scores the weekly college football challenge.",
};

export default function AboutPage() {
  return (
    <>
      <section className="fan-page-intro">
        <div>
          <span className="fan-kicker">HOW IT WORKS</span>
          <h1>Easy to play. Hard to fake.</h1>
          <p>Beat the Model is one weekly college football argument: you pick the winners, The Model picks the winners, and both sides are judged on the exact same games.</p>
        </div>
      </section>

      <section className="fan-how-grid" aria-label="How Beat the Model works">
        <article className="fan-how-card">
          <span>01</span>
          <div><h2>Rank every FBS team</h2><p>Before the week, every team receives one opponent-adjusted power rating. That gives us a complete board instead of a Top 25-only poll.</p></div>
        </article>
        <article className="fan-how-card">
          <span>02</span>
          <div><h2>Build the Official 15</h2><p>We combine team quality, rank closeness, and the consensus market line to find the best competitive games. The Model’s pick and margin are never selection inputs.</p></div>
        </article>
        <article className="fan-how-card">
          <span>03</span>
          <div><h2>You pick before The Model</h2><p>Use the rankings and market context, then choose one winner. Your first choice locks immediately and only then reveals The Model’s frozen pregame call.</p></div>
        </article>
        <article className="fan-how-card">
          <span>04</span>
          <div><h2>Saturday keeps score</h2><p>Correct winner equals one point. The original weekly card, market snapshot, and model calls stay attached to the final results.</p></div>
        </article>
      </section>

      <section className="fan-principles">
        <article className="fan-principle primary">
          <span className="fan-kicker">THE FAIRNESS CONTRACT</span>
          <h2>The Model never chooses its opponents.</h2>
          <p>BTM rankings and market competitiveness choose the card first. The frozen prediction model is attached second. Once picks open, the selected matchups, market snapshot, and pregame model calls become part of the record.</p>
        </article>
        <article className="fan-principle">
          <span className="fan-kicker">THE SCORING RULE</span>
          <h2>Winner or loser. That’s it.</h2>
          <p>The market is context, not scoring. No spread points, bankrolls, confidence multipliers, or betting results change the core game. One correct winner is one point.</p>
        </article>
      </section>

      <section className="fan-section">
        <div className="fan-section-heading">
          <div><span className="fan-kicker">THE MARKET BAR</span><h2>See what the market thinks before you pick.</h2></div>
        </div>
        <div className="fan-value-grid">
          <article><span className="fan-value-number">R</span><h3>Rankings</h3><p>BTM rank tells you how strong each team entered the week.</p></article>
          <article><span className="fan-value-number">M</span><h3>Market consensus</h3><p>Available sportsbook lines are reduced to one consensus view. Paired moneylines are converted to no-vig win probability for the bar.</p></article>
          <article><span className="fan-value-number">P</span><h3>Your pick</h3><p>The market is visible, The Model is not. Once you choose, your pick locks and The Model is revealed.</p></article>
        </div>
      </section>

      <section className="fan-section">
        <div className="fan-section-heading">
          <div><span className="fan-kicker">THE WEEKLY RHYTHM</span><h2>A reason to come back all week.</h2></div>
        </div>
        <div className="fan-value-grid">
          <article><span className="fan-value-number">M</span><h3>Monday: new board</h3><p>Fresh rankings, market context, and a new Official 15 create the week’s arguments.</p></article>
          <article><span className="fan-value-number">P</span><h3>Before kickoff: pick</h3><p>Build your card, discover your disagreements, and share the calls you want to defend.</p></article>
          <article><span className="fan-value-number">S</span><h3>Saturday: settle it</h3><p>Follow your head-to-head as games go final, then keep the result in the archive.</p></article>
        </div>
      </section>

      <section className="fan-final-cta fan-section">
        <div>
          <span className="fan-kicker">READY?</span>
          <h2>The explanation is over. Make the picks.</h2>
          <p>You and The Model get the same card.</p>
        </div>
        <Link className="fan-button fan-button-primary" href="/play">Go to this week</Link>
      </section>
    </>
  );
}
