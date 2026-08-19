import Link from "next/link";
import { analyticsStory } from "../../lib/michigan/analytics";

const pct = (value: number) => `${(value * 100).toFixed(1)}%`;
const dec = (value: number) => value.toFixed(2);

export default function AnalyticsPage() {
  const story = analyticsStory();

  if (!story) {
    return (
      <div className="wrap route-page">
        <span className="kicker navy">ANALYTICS</span>
        <h1>Review in progress</h1>
        <p>The verified comparison is not available yet.</p>
      </div>
    );
  }

  const michigan = story.teams.michigan;
  const utah = story.teams.utah;
  const comparisons = [
    { label: "Called runs", insight: "Both teams already preferred the ground game.", michiganDisplay: pct(michigan.designedBalanceRushShare), utahDisplay: pct(utah.designedBalanceRushShare), michiganValue: michigan.designedBalanceRushShare, utahValue: utah.designedBalanceRushShare },
    { label: "Created big runs", insight: "Utah found a few more breakaway chances.", michiganDisplay: pct(michigan.rushExplosivePlayRate), utahDisplay: pct(utah.rushExplosivePlayRate), michiganValue: michigan.rushExplosivePlayRate, utahValue: utah.rushExplosivePlayRate },
    { label: "Stayed on the field", insight: "Utah was better at moving the chains on third down.", michiganDisplay: pct(michigan.thirdDownConversionRate), utahDisplay: pct(utah.thirdDownConversionRate), michiganValue: michigan.thirdDownConversionRate, utahValue: utah.thirdDownConversionRate },
    { label: "Cashed in chances", insight: "Utah turned good field position into more points.", michiganDisplay: dec(michigan.pointsPerOpportunity), utahDisplay: dec(utah.pointsPerOpportunity), michiganValue: michigan.pointsPerOpportunity / 5, utahValue: utah.pointsPerOpportunity / 5 },
  ];

  return (
    <div className="editorial-page">
      <section className="page-banner">
        <div className="wrap page-banner-inner">
          <div>
            <span className="kicker">WHAT LAST SEASON TELLS US</span>
            <h1>THE HANDOFF</h1>
            <p>Michigan could already run the ball. The new staff’s opportunity is to make those drives count when the field gets shorter and the decisions get harder.</p>
          </div>
          <div className="banner-mark">25</div>
        </div>
        <div className="wrap summary-rail">
          <span><small>SUCCESS RATE RANK</small><b>#{michigan.successRateNationalRank}</b></span>
          <span><small>RUN PLAYS THAT WORKED</small><b>{pct(michigan.rushSuccessRate)}</b></span>
          <span><small>FINISHING RANK</small><b>#{michigan.pointsPerOpportunityNationalRank}</b></span>
        </div>
      </section>

      <div className="wrap editorial-stack">
        <section className="analytics-verdict" id="offense">
          <div className="verdict-copy">
            <span className="kicker navy">THE MICHIGAN READ</span>
            <h2>The run game gave Michigan enough. Drives still ended too quietly.</h2>
            <p>Michigan regularly gained useful yards and avoided falling behind the chains. But once the offense crossed the opponent’s 40-yard line, it averaged only {dec(michigan.pointsPerOpportunity)} points. That meant too many promising drives ended with a field goal—or nothing.</p>
          </div>
          <div className="signal-stack">
            <article className="positive"><small>BIG-PLAY THREAT</small><strong>{pct(michigan.rushExplosivePlayRate)}</strong><span>About one of every seven runs gained 10 or more yards.</span></article>
            <article><small>POINTS LEFT BEHIND</small><strong>{dec(michigan.pointsPerOpportunity)}</strong><span>Michigan ranked No. {michigan.pointsPerOpportunityNationalRank} at finishing scoring chances.</span></article>
            <article className="positive"><small>DEFENSE LIMITED DAMAGE</small><strong>#{story.michiganDefense.yardsPerSuccessfulPlayAllowedNationalRank}</strong><span>Even successful opponent plays rarely became huge gains.</span></article>
          </div>
        </section>

        <section className="utah-context" id="staff-context">
          <header className="section-header"><div><span className="kicker maize">UTAH · STAFF CONTEXT</span><h2>The lesson is not “run more.” It is “finish better.”</h2></div></header>
          <p className="context-deck">Utah is the comparison because Kyle Whittingham and offensive coordinator Jason Beck came to Michigan from that program. Michigan and Utah already called a similar kind of game. Utah separated itself by producing more explosive runs, surviving third down, and turning scoring chances into touchdowns.</p>
          <div className="team-key"><span><i className="michigan-dot" />MICHIGAN</span><span><i className="utah-dot" />UTAH</span></div>
          <div className="comparison-board">
            {comparisons.map((comparison) => (
              <article key={comparison.label}>
                <div><span>{comparison.label}<small>{comparison.insight}</small></span><b>{comparison.michiganDisplay}</b></div>
                <div className="comparison-track">
                  <i className="michigan-bar" style={{ width: `${Math.min(100, comparison.michiganValue * 100)}%` }} />
                  <i className="utah-bar" style={{ width: `${Math.min(100, comparison.utahValue * 100)}%` }} />
                </div>
                <div><b>{comparison.utahDisplay}</b></div>
              </article>
            ))}
          </div>
          <div className="staff-takeaway"><span>WHAT TO WATCH IN 2026</span><p>Look for better answers on third down and a more aggressive touchdown mindset after Michigan crosses midfield. If those improve, the offense does not need to become unrecognizable—it just needs to waste fewer good drives.</p></div>
          <small className="context-boundary"><b>POINTS PER OPPORTUNITY:</b> points scored per possession that reaches the opponent's 40-yard line. {story.interpretation.boundary}</small>
        </section>

        <section className="analytics-next">
          <div><span className="kicker navy">EXPLORE ONE LAYER DEEPER</span><h2>Choose the next question.</h2></div>
          <div className="dual-actions">
            <Link href="/analytics#offense"><small>2025 REVIEW</small><b>How Michigan moved the ball</b><em>→</em></Link>
            <Link href="/methodology"><small>DEFINITIONS</small><b>How these metrics work</b><em>→</em></Link>
          </div>
        </section>
      </div>
    </div>
  );
}
