import type { Metadata } from "next";
import styles from "../../styles/methodology.module.css";

export const metadata: Metadata = {
  title: "Methodology | Michigan Football Focus",
  description: "How Michigan Football Focus labels evidence, defines public metrics, and separates observed production from projections, preseason context, and benchmarks.",
};

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

const currentStatus = [
  ["2026 roster, staff, schedule and roles", "Preseason evidence."],
  ["Michigan and Utah team performance", "Completed 2025 actuals."],
  ["Recruiting", "Consensus benchmarks, not college proof."],
  ["Markets", "Sourced prices and historical spread calibration."],
  ["2026 in-season analytics", "Begin only after observed games are published."],
];

const trustRules = [
  "We do not invent rankings, grades, player roles, probabilities, or historical comparisons when an artifact is missing.",
  "Utah's 2025 performance describes recent staff context; it does not guarantee Michigan will reproduce Utah's tendencies or results.",
  "Public language may simplify a calculation, but it does not change its denominator, direction, or underlying definition.",
];

export default function Methodology() {
  return <main className={styles.page}>
    <div className={styles.shell}>
      <section className={styles.hero}>
        <div className={styles.heroTop}>
          <div>
            <span className={styles.eyebrow}>HOW THE ANALYSIS WORKS</span>
            <h1>READ THE EVIDENCE.</h1>
            <p className={styles.heroLead}>Advanced football analysis in fan language, with every number labeled by what it knows, where it came from, and what it does not claim.</p>
          </div>

          <aside className={styles.heroNote}>
            <span>THE STANDARD</span>
            <strong>DATA FIRST.<br/>NO INVENTED CONFIDENCE.</strong>
            <p>The model can be complex. The public claim should always be clear.</p>
          </aside>
        </div>

        <div className={styles.statusRail}>
          <article><small>CURRENT TEAM DATA</small><b>2026 PRESEASON</b></article>
          <article><small>PERFORMANCE BASELINE</small><b>2025 ACTUAL</b></article>
          <article><small>MISSING DATA</small><b>NEVER INVENTED</b></article>
        </div>
      </section>

      <section className={styles.section}>
        <header className={styles.sectionHeader}>
          <div>
            <span className={styles.sectionKicker}>EVIDENCE TYPES</span>
            <h2>Four labels.<br/>Four different claims.</h2>
          </div>
          <p>The label travels with the number so recruiting reputation, observed production, projections, and market context never collapse into one misleading grade.</p>
        </header>

        <div className={styles.evidenceGrid}>
          {evidence.map(([label, description], index) => <article className={styles.evidenceCard} data-index={`0${index+1}`} key={label}>
            <div className={styles.evidenceAccent}/>
            <strong>{label}</strong>
            <p>{description}</p>
          </article>)}
        </div>
      </section>

      <section className={styles.section}>
        <header className={styles.sectionHeader}>
          <div>
            <span className={styles.sectionKicker}>FAN GLOSSARY</span>
            <h2>What the numbers mean.</h2>
          </div>
          <p>These are public-language definitions. The Python analytics system and metric registry remain the calculation source of truth.</p>
        </header>

        <div className={styles.glossary}>
          {metrics.map(([name, definition], index) => <article className={styles.metricRow} key={name}>
            <span className={styles.metricIndex}>{String(index+1).padStart(2,"0")}</span>
            <h3>{name}</h3>
            <p>{definition}</p>
          </article>)}
        </div>
      </section>

      <section className={styles.splitGrid}>
        <article className={styles.infoPanel}>
          <span className={styles.panelKicker}>CURRENT DATA STATUS</span>
          <h2>What the site knows today.</h2>
          <div className={styles.factList}>
            {currentStatus.map(([label, description], index) => <div className={styles.fact} key={label}>
              <span className={styles.factNumber}>{String(index+1).padStart(2,"0")}</span>
              <p><b>{label}:</b> {description}</p>
            </div>)}
          </div>
        </article>

        <article className={styles.trustPanel}>
          <span className={styles.panelKicker}>TRUST CONTRACT</span>
          <h2>What we will not do.</h2>
          <div className={styles.factList}>
            {trustRules.map((rule, index) => <div className={styles.fact} key={rule}>
              <span className={styles.factNumber}>{String(index+1).padStart(2,"0")}</span>
              <p>{rule}</p>
            </div>)}
          </div>
        </article>
      </section>

      <div className={styles.footerNote}>
        <strong>THE RULE IS SIMPLE.</strong>
        <p>If the underlying evidence changes, the label changes with it. If the evidence does not exist, the site should say so instead of pretending certainty.</p>
      </div>
    </div>
  </main>;
}
