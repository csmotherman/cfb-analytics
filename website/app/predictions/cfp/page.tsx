import { currentMarketOutlook } from "../../../lib/michigan/predictions";

export default function CfpPage() {
  const outlook = currentMarketOutlook();
  const chance = outlook ? outlook.cfp.noVigImpliedProbability * 100 : null;
  return <div className="page-stack page-pad">
    <section className="page-hero"><span className="eyebrow">2026 PLAYOFF ODDS</span><h1>MICHIGAN'S<br/>CFP PATH.</h1><p>Current chance to make the 12-team field.</p></section>
    {outlook ? <>
      <section className="metric-strip"><div className="metric-grade"><span>MAKE THE CFP</span><strong>{chance?.toFixed(1)}%</strong><small>MARKET ESTIMATE</small></div><div className="metric-grade"><span>CURRENT ODDS</span><strong>+{outlook.cfp.makePlayoffYesAmerican}</strong><small>{outlook.source.name.toUpperCase()}</small></div><div className="metric-grade"><span>UPDATED</span><strong>{new Date(outlook.asOf).toLocaleDateString("en-US",{month:"short",day:"numeric"}).toUpperCase()}</strong><small>2026</small></div></section>
      <section className="method-note"><strong>THE NUMBER</strong><p>The current Yes and No prices work out to a {chance?.toFixed(1)}% market chance. Odds move. Not betting advice.</p><p><a href={outlook.source.url} rel="noreferrer">See the current odds →</a></p></section>
    </> : <section className="empty-state"><strong>Playoff odds coming soon</strong><p>Check back for the latest Michigan outlook.</p></section>}
    <section><span className="eyebrow">HOW THE CFP WORKS</span><div className="pending-grid"><div><span>FIELD</span><strong>12 TEAMS</strong></div><div><span>CONFERENCE CHAMPS</span><strong>5 SPOTS</strong></div><div><span>AT-LARGE</span><strong>7 SPOTS</strong></div><div><span>FIRST-ROUND BYES</span><strong>TOP 4 SEEDS</strong></div></div></section>
  </div>;
}
