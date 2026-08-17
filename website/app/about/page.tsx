import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "How it works",
  description: "How CFB Model turns pregame football data into one prediction and three clear reasons.",
};

export default function AboutPage() {
  return (
    <>
      <section className="page-hero compact-hero">
        <span className="eyebrow">HOW IT WORKS</span>
        <h1>The numbers stay under the hood.</h1>
        <p>You get the part that matters: who the model likes, how strongly it likes them, and why.</p>
      </section>

      <section className="method-steps">
        <article>
          <span>01</span>
          <h2>Measure the matchup</h2>
          <p>The model evaluates opponent-adjusted efficiency, explosiveness, field position, finishing drives, strength, and other pregame football signals.</p>
        </article>
        <article>
          <span>02</span>
          <h2>Make one call</h2>
          <p>Those signals become a projected score and win probability. The site does not bury the answer behind a dashboard.</p>
        </article>
        <article>
          <span>03</span>
          <h2>Lock the receipt</h2>
          <p>The prediction is timestamped before kickoff. After the game, the original pick stays visible beside the result.</p>
        </article>
      </section>

      <section className="principle-card">
        <span className="eyebrow">THE PRODUCT RULE</span>
        <h2>Prediction first. Explanation second. Everything else is noise.</h2>
        <p>Advanced metrics can power the model without forcing fans to learn a new language just to understand a football game.</p>
      </section>
    </>
  );
}
