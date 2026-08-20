const evidence = [
  ["ACTUAL", "Observed game, drive, play, or player production from a completed season."],
  ["PROJECTED", "A published preseason role or lineup estimate. It is not an official Michigan depth chart."],
  ["PRESEASON", "A current roster, schedule, staff, or status fact published before games begin."],
  ["BENCHMARK", "External context such as recruiting consensus or a sourced market price—not game performance."],
];

const metrics = [
  ["Success rate", "The share of plays that gained enough yards for the down and distance. Higher is better."],
  ["Rush success rate", "Success rate on designed rushing attempts. Quarterback scrambles are not silently treated as called runs."],
  ["Explosive run rate", "The share of rushing attempts gaining at least 10 yards. Higher means more breakaway production."],
  ["Points per opportunity", "Points scored per possession that reaches the opponent's 40-yard line. It measures whether promising field position becomes points."],
  ["Points per resolved possession", "Points per possession with a known competitive result. It is broader than scoring-opportunity efficiency."],
  ["Position percentile", "A player's standing among the published national FBS comparison cohort at the same position and above the required usage threshold."],
  ["Production grade", "A display grade derived from measured 2025 usage and production within a positional cohort. It describes the season; it does not forecast the next one."],
  ["Prospect tier", "A display translation of recruiting consensus. It describes incoming pedigree, not college performance."],
  ["Market win chance", "A historical calibration from a sourced point spread. It is market context, not a game prediction."],
];

export default function Methodology() {
  return <div className="methodology-page">
    <section className="page-banner"><div className="wrap page-banner-inner"><div><span className="kicker">HOW THE ANALYSIS WORKS</span><h1>READ THE EVIDENCE</h1><p>Advanced football analysis in fan language—with every number labeled by what it knows and what it does not.</p></div><div className="banner-mark">4</div></div><div className="wrap summary-rail"><span><small>CURRENT TEAM DATA</small><b>2026 PRESEASON</b></span><span><small>PERFORMANCE BASELINE</small><b>2025 ACTUAL</b></span><span><small>MISSING DATA</small><b>NEVER INVENTED</b></span></div></section>
    <div className="wrap methodology-stack">
      <section><header className="methodology-heading"><span className="kicker navy">EVIDENCE TYPES</span><h2>Four labels. Four different claims.</h2><p>The label travels with the number so recruiting reputation, observed production, projections, and market context do not collapse into one grade.</p></header><div className="evidence-grid">{evidence.map(([label, description]) => <article key={label} className={`evidence-${label.toLowerCase()}`}><strong>{label}</strong><p>{description}</p></article>)}</div></section>
      <section><header className="methodology-heading"><span className="kicker navy">FAN GLOSSARY</span><h2>What the numbers mean.</h2><p>These are public-language definitions. The Python analytics system and metric registry remain the calculation source of truth.</p></header><div className="metric-glossary">{metrics.map(([name, definition]) => <article key={name}><h3>{name}</h3><p>{definition}</p></article>)}</div></section>
      <section className="methodology-split"><div><span className="kicker maize">CURRENT DATA STATUS</span><h2>What the site knows today.</h2></div><div><p><b>2026 roster, staff, schedule and roles:</b> preseason evidence.</p><p><b>Michigan and Utah team performance:</b> completed 2025 actuals.</p><p><b>Recruiting:</b> consensus benchmarks, not college proof.</p><p><b>Markets:</b> sourced prices and historical spread calibration.</p><p><b>2026 in-season analytics:</b> begin only after observed games are published.</p></div></section>
      <section className="methodology-split light"><div><span className="kicker navy">TRUST CONTRACT</span><h2>What we will not do.</h2></div><div><p>We do not invent rankings, grades, player roles, probabilities, or historical comparisons when an artifact is missing.</p><p>Utah's 2025 performance describes recent staff context; it does not guarantee Michigan will reproduce Utah's tendencies or results.</p><p>Public language may simplify a calculation, but it does not change its denominator, direction, or underlying definition.</p></div></section>
    </div>
  </div>;
}
