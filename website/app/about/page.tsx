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
          <div><h2>Build the Official 15</h2><p>The strongest, closest-ranked FBS matchups become the weekly card. Prediction confidence is not allowed to influence which games are selected.</p></div>
        </article>
        <article className="fan-how-card">
          <span>03</span>
          <div><h2>You pick before The Model</h2><p>Choose one winner per game. Only after your choice do we reveal The Model’s frozen pregame call for that matchup.</p></div>
        </article>
        <article className="fan-how-card">
          <span>04</span>
          <div><h2>Saturday keeps score</h2><p>Correct winner equals one point. The original weekly card and model calls stay attached to the final results in the archive.</p></div>
        </article>
      </section>

      <section className="fan-principles">
        <article className="fan-principle primary">
          <span className="fan-kicker">THE FAIRNESS CONTRACT</span>
          <h2>The Model never chooses its opponents.</h2>
          <p>The rankings select the card first. The frozen prediction model is attached second. Once picks open, the selected matchups and pregame calls are part of the permanent record.</p>
        </article>
        <article className="fan-principle">
          <span className="fan-kicker">THE SCORING RULE</span>
          <h2>Winner or loser. That’s it.</h2>
          <p>No spreads, odds, bankrolls, confidence points, or multipliers in the core game. One correct winner is one point.</p>
        </article>
      </section>

      <section className="fan-section">
        <div className="fan-section-heading">
          <div><span className="fan-kicker">THE WEEKLY RHYTHM</span><h2>A reason to come back all week.</h2></div>
        </div>
        <div className="fan-value-grid">
          <article><span className="fan-value-number">M</span><h3>Monday: new board</h3><p>Fresh rankings and a new Official 15 create the week’s arguments.</p></article>
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
