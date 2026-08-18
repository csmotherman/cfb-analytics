import type { Metadata } from "next";

export const metadata: Metadata = { title: "Methodology", description: "How Michigan Football Analytics turns source plays into validated national comparisons." };

const metrics = [
  ["Staying on schedule", "Success Rate", "Did the offense gain enough yards for the down and distance? First down requires 50%, second down 70%, and third or fourth down 100%."],
  ["Creating big plays", "Explosive Play Rate", "A rush of at least 10 yards or a pass of at least 20. Successful-play yardage separately measures the size of productive snaps."],
  ["Turning drives into points", "Points per resolved possession", "Points scored divided by possessions whose point outcome can be confidently reconstructed."],
  ["Finishing chances", "Points per scoring opportunity", "How efficiently an offense cashes in after reaching scoring territory, using resolved opportunities only."],
  ["Disruption", "Havoc Rate", "Tackles for loss, sacks, and takeaways anchored to validated plays without double-counting the same event."],
  ["Opponent strength", "SOAR opponent adjustment", "Team performance is evaluated against what opponents had demonstrated before the game, protecting the calculation from future information."],
];

export default function MethodologyPage() { return <div className="michigan-home">
  <section className="michigan-page-hero"><span>TRACEABLE BY DESIGN</span><h1>Football answers, with receipts.</h1><p>CFBD supplies source facts. SOAR decides eligibility, reconstructs possessions, calculates each metric, and checks that every aggregate rebuilds from its evidence.</p></section>
  <section className="michigan-method-grid">{metrics.map(([plain, technical, explanation]) => <article key={plain}><span>{technical}</span><h2>{plain}</h2><p>{explanation}</p></article>)}</section>
  <section className="michigan-method"><span>THE NONNEGOTIABLE RULE</span><h2>Michigan never gets a special formula.</h2><p>Every FBS team follows the same cleaning, eligibility, aggregation, and ranking path. Michigan becomes the editorial focus only after the national calculation is complete.</p></section>
  </div>; }
