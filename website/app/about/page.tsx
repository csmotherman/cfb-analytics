import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "How it works",
  description: "How Beat the Model ranks teams, selects the Official 15, and scores the weekly picking game.",
};

export default function AboutPage() {
  return (
    <>
      <section className="fan-page-intro">
        <div>
          <span className="fan-kicker">HOW IT WORKS</span>
          <h1>Simple for fans. Strict behind the scenes.</h1>
          <p>You pick winners. The Model picks winners. Both sides play the exact same 15 games, and every result stays public after the week ends.</p>
        </div>
      </section>

      <section className="fan-how-grid" aria-label="How Beat the Model works">
        <article className="fan-how-card">
          <span>01</span>
          <div><h2>Rank every team</h2><p>Every FBS team gets a weekly opponent-adjusted power rating. That board is built before the weekly contest card is chosen.</p></div>
        </article>
        <article className="fan-how-card">
          <span>02</span>
          <div><h2>Choose the Official 15</h2><p>The strongest ranked regular-season matchups become the weekly slate. Model confidence never decides which games make the card.</p></div>
        </article>
        <article className="fan-how-card">
          <span>03</span>
          <div><h2>You pick first</h2><p>Choose one winner in each game. The Model stays hidden until your choice is made, so you cannot simply copy it.</p></div>
        </article>
        <article className="fan-how-card">
          <span>04</span>
          <div><h2>Score the week</h2><p>A correct winner is one point. A wrong winner is zero. Your record and The Model's record are compared on the same card.</p></div>
        </article>
      </section>

      <section className="fan-principles">
        <article className="fan-principle primary">
          <span className="fan-kicker">THE FAIRNESS RULE</span>
          <h2>The Model never chooses its opponents.</h2>
          <p>The rankings select the slate first. Only after the games are set are The Model's pregame picks attached. Once those calls are frozen, the contest opens and the picks stay on the record.</p>
        </article>
        <article className="fan-principle">
          <span className="fan-kicker">THE FAN RULE</span>
          <h2>No extra scoring systems.</h2>
          <p>No spreads, confidence points, multipliers, or bankrolls in the core game. Pick the winner. Get one point. Move to the next matchup.</p>
        </article>
      </section>

      <section className="fan-explainer-card">
        <span className="fan-kicker">WHY THE ARCHIVE MATTERS</span>
        <h2>Good weeks and bad weeks stay visible.</h2>
        <p>After games finish, the original Official 15 and The Model's attached picks remain in the archive. That makes the game easy to understand and keeps the model accountable over time.</p>
      </section>
    </>
  );
}
