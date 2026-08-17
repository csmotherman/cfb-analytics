import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "How it works",
  description: "How Beat the Model ranks teams, selects the Official 15, and scores the weekly picking game.",
};

export default function AboutPage() {
  return (
    <>
      <section className="page-hero compact-hero btm-page-hero">
        <span className="eyebrow">HOW IT WORKS</span>
        <h1>Pick first. Then face The Model.</h1>
        <p>Beat the Model is a weekly college football picking game. No spreads, no odds, no betting bankroll—just winner picks and a public score.</p>
      </section>

      <section className="method-steps btm-method-steps">
        <article>
          <span>01</span>
          <h2>Rank every team</h2>
          <p>Every FBS team receives a weekly opponent-adjusted power rating. Week 1 starts from the previous season's final rating, then current-season evidence takes over over four games.</p>
        </article>
        <article>
          <span>02</span>
          <h2>Choose the Official 15</h2>
          <p>The 15 strongest eligible regular-season matchups are chosen from those rankings. The Model's prediction, confidence, and historical performance are never used to make the slate easier.</p>
        </article>
        <article>
          <span>03</span>
          <h2>Make your picks</h2>
          <p>You pick the winner of each game. The Model's answer stays hidden until you make your own choice, so you cannot simply copy it.</p>
        </article>
        <article>
          <span>04</span>
          <h2>Score it straight up</h2>
          <p>A correct winner is one point. A wrong winner is zero. You and The Model are scored on the exact same 15 games.</p>
        </article>
        <article>
          <span>05</span>
          <h2>Compete</h2>
          <p>The core game works one-on-one against The Model first. Private friend pools and public pools can use the same locked weekly card without changing the scoring rules.</p>
        </article>
        <article>
          <span>06</span>
          <h2>Keep the receipts</h2>
          <p>After the games finish, the original slate and model picks stay in the archive. The Model cannot remove a bad week or rewrite a loss.</p>
        </article>
      </section>

      <section className="principle-card btm-principle-card">
        <span className="eyebrow">THE FAIRNESS RULE</span>
        <h2>The Model never gets to choose the games it has to predict.</h2>
        <p>Rankings select the slate first. Prediction v2 then plays the same card as everyone else. That separation is part of the product contract.</p>
      </section>
    </>
  );
}
