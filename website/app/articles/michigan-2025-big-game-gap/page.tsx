import type { Metadata } from "next";
import Link from "next/link";
import { ArticleMobileToc } from "../../../components/ArticleMobileToc";
import { ResidualChart, type ResidualRow } from "../../../components/articles/ResidualChart";
import { FourthDownBoard } from "../../../components/articles/FourthDownBoard";
import { bigGameDecisionsData } from "../../../lib/michigan/big-game-decisions-data";
import "./article.css";

const articleUrl = "https://michiganfootballfocus.com/articles/michigan-2025-big-game-gap";
const socialDescription = "Michigan's 2025 offense, adjusted to full-season opponent strength, plus every fourth-down decision graded against historical expected value. The marquee-game gap is real — and it wasn't just about who was across from Bryce Underwood.";

export const metadata: Metadata = {
  title: "Michigan's Big-Game Gap, and the Fourth Downs That Made It Worse",
  description: socialDescription,
  openGraph: { type: "article", url: articleUrl, siteName: "Michigan Football Focus", title: "Michigan's Big-Game Gap", description: socialDescription },
  twitter: { card: "summary_large_image", title: "Michigan's Big-Game Gap", description: socialDescription },
};

const RANKED_OPPONENTS = new Set(["Oklahoma", "Ohio State", "Texas"]);

const sections = [
  ["gap", "The gap"],
  ["offense", "Overall offense"],
  ["qb", "The quarterback"],
  ["fourth", "Fourth-down calls"],
  ["epa", "Rush vs. pass"],
  ["stories", "Three storylines"],
] as const;

const sources = [
  ["CollegeFootballData.com", "https://collegefootballdata.com"],
  ["Michigan 2025 schedule and results", "https://mgoblue.com/sports/football/schedule/2025"],
] as const;

function mean(values: number[]): number {
  return values.reduce((a, b) => a + b, 0) / values.length;
}
function pp(v: number): string {
  return `${v >= 0 ? "+" : "−"}${Math.abs(v * 100).toFixed(1)}pp`;
}
function ppNum(v: number): string {
  return `${Math.abs(v * 100).toFixed(1)}`;
}
function yds(v: number): string {
  return `${v >= 0 ? "+" : "−"}${Math.abs(v).toFixed(2)} yds`;
}
function epaFmt(v: number): string {
  return `${v >= 0 ? "+" : "−"}${Math.abs(v).toFixed(3)}`;
}

export default function BigGameGapArticle() {
  const data = bigGameDecisionsData;
  const games = data.games;
  const ranked = games.filter((g) => RANKED_OPPONENTS.has(g.opponent));
  const unranked = games.filter((g) => !RANKED_OPPONENTS.has(g.opponent));

  const rawRankedSuccess = mean(ranked.map((g) => g.success.actual));
  const rawUnrankedSuccess = mean(unranked.map((g) => g.success.actual));
  const rawGap = rawUnrankedSuccess - rawRankedSuccess;

  const adjRankedSuccess = mean(ranked.map((g) => g.success.residual!));
  const adjUnrankedSuccess = mean(unranked.map((g) => g.success.residual!));
  const adjGap = adjUnrankedSuccess - adjRankedSuccess;

  const passRankedGap = mean(ranked.map((g) => g.passSuccess.residual!));
  const passUnrankedGap = mean(unranked.map((g) => g.passSuccess.residual!));
  const passGapTotal = passUnrankedGap - passRankedGap;

  const ypdRankedGap = mean(ranked.map((g) => g.passYPD.residual!));
  const ypdUnrankedGap = mean(unranked.map((g) => g.passYPD.residual!));
  const ypdGapTotal = ypdUnrankedGap - ypdRankedGap;

  const orderedGames = [...games].sort((a, b) => (a.seasonType !== b.seasonType ? (a.seasonType === "regular" ? -1 : 1) : a.week - b.week));

  const teamRows: ResidualRow[] = orderedGames.map((g) => ({
    key: `${g.seasonType}-${g.week}`,
    opponent: g.opponent,
    site: g.site,
    oppRank: g.oppRank,
    series: [{ tag: "SUCC", value: g.success.residual, scaleMax: 0.25, valueLabel: g.success.residual !== null ? pp(g.success.residual) : "n/a" }],
  }));

  const qbRows: ResidualRow[] = orderedGames.map((g) => ({
    key: `${g.seasonType}-${g.week}`,
    opponent: g.opponent,
    site: g.site,
    oppRank: g.oppRank,
    series: [
      { tag: "SUCC", value: g.passSuccess.residual, scaleMax: 0.25, valueLabel: g.passSuccess.residual !== null ? pp(g.passSuccess.residual) : "n/a" },
      { tag: "Y/DB", value: g.passYPD.residual, scaleMax: 6, valueLabel: g.passYPD.residual !== null ? yds(g.passYPD.residual) : "n/a" },
    ],
  }));

  const fd = data.fourthDownSummary;
  const worstFourth = [...data.fourthDowns].filter((d) => d.evLost !== null).sort((a, b) => (b.evLost ?? 0) - (a.evLost ?? 0))[0];
  const conservativeMisses = (fd.byActual.punt.count - fd.byActual.punt.correct) + (fd.byActual.fieldGoal.count - fd.byActual.fieldGoal.correct);
  const aggressiveMisses = fd.byActual.go.count - fd.byActual.go.correct;

  const es = data.epaSummary;

  return (
    <article className="focus-article feature-article big-game-audit">
      <div className="article-reading-progress" aria-hidden="true" />
      <div className="focus-article-shell">
        <div className="bga-hero">
          <div className="bga-hero-inner">
            <Link href="/articles" style={{ color: "#9badc0", fontSize: 12, fontWeight: 700, letterSpacing: "0.05em" }}>← THE NOTEBOOK</Link>
            <p className="bga-kicker">Opponent-adjusted audit · 2025 season · full-season ratings</p>
            <h1>Michigan's <em>Big-Game</em> Gap</h1>
            <p className="bga-deck">
              {data.qbName}'s freshman offense looked like two different units depending on the opponent. Michigan's own
              opponent-adjustment formula — fit on the complete 2025 season — says some of that was always going to happen.
              <b> Most of it wasn't supposed to. And a separate, independent model says the coaching staff left {Math.abs(fd.totalEvLost).toFixed(1)} expected points on the field with fourth-down calls alone.</b>
            </p>
            <div className="bga-meta"><span>2025 SEASON REVIEW</span><span>12 MIN READ</span><span>DATA AUDIT</span></div>
          </div>
        </div>

        <ArticleMobileToc sections={sections} />

        <div className="bga-body">
          <section id="gap" className="bga-section">
            <div className="bga-section-kicker">01 · The headline number</div>
            <h2 className="bga-h2">A gap that survives adjustment</h2>
            <p className="bga-sub">Success rate, all 13 FBS games · marquee = AP Top 25 opponent at kickoff (Oklahoma #18, Ohio State #1, Texas #12)</p>
            <div className="bga-stat-grid">
              <div className="bga-stat-cell">
                <div className="bga-stat-label">Raw gap</div>
                <div className="bga-stat-num bga-faint-num">{ppNum(rawGap)}<span className="bga-stat-unit">pp</span></div>
                <div className="bga-stat-detail">{(rawUnrankedSuccess * 100).toFixed(1)}% success rate vs. unranked opponents<br />{(rawRankedSuccess * 100).toFixed(1)}% vs. ranked opponents</div>
              </div>
              <div className="bga-stat-cell">
                <div className="bga-stat-label">Gap after opponent adjustment</div>
                <div className="bga-stat-num bga-bad-num">{ppNum(adjGap)}<span className="bga-stat-unit">pp</span></div>
                <div className="bga-stat-detail">{pp(adjUnrankedSuccess)} above expectation vs. unranked<br />{pp(adjRankedSuccess)} below expectation vs. ranked</div>
              </div>
            </div>
            <p className="bga-note">Facing better defenses accounts for a bit under <b>half</b> of the raw disparity. The other half is a real, opponent-adjusted shortfall in marquee games. Every game&apos;s &quot;expected&quot; value uses each opponent&apos;s full-season defensive rating, fit by this repo&apos;s independent opponent-adjustment formula — not a leakage-safe forecast, a retrospective grade. See Method at the bottom.</p>
          </section>

          <section id="offense" className="bga-section">
            <div className="bga-section-kicker">02 · Team offense</div>
            <h2 className="bga-h2">Overall offense, adjusted to opponent defense</h2>
            <p className="bga-sub">Success-rate residual = actual minus opponent-adjusted expectation, chronological by week.</p>
            <div className="bga-chart-shell">
              <div className="bga-legend">
                <span><i className="bga-swatch good" />Outperformed expectation</span>
                <span><i className="bga-swatch bad" />Underperformed expectation</span>
              </div>
              <ResidualChart rows={teamRows} />
            </div>
          </section>

          <section id="qb" className="bga-section">
            <div className="bga-section-kicker">03 · The quarterback</div>
            <h2 className="bga-h2">The quarterback, game by game</h2>
            <p className="bga-sub">Two views of {data.qbName}&apos;s passing, both run through the identical opponent-adjustment formula, restricted to dropbacks: success rate (stayed on schedule) and net yards per dropback (overall throughput, sacks included).</p>
            <div className="bga-stat-grid">
              <div className="bga-stat-cell">
                <div className="bga-stat-label">Pass success-rate gap (adjusted)</div>
                <div className="bga-stat-num bga-bad-num">{ppNum(passGapTotal)}<span className="bga-stat-unit">pp</span></div>
                <div className="bga-stat-detail">{pp(passUnrankedGap)} vs. unranked · {pp(passRankedGap)} vs. ranked</div>
              </div>
              <div className="bga-stat-cell">
                <div className="bga-stat-label">Yards/dropback gap (adjusted)</div>
                <div className="bga-stat-num bga-bad-num">{ypdGapTotal.toFixed(2)}<span className="bga-stat-unit">yds</span></div>
                <div className="bga-stat-detail">{yds(ypdUnrankedGap)} vs. unranked · {yds(ypdRankedGap)} vs. ranked</div>
              </div>
            </div>
            <p className="bga-note">Unlike a team-level gap that&apos;s partly explained by opponent quality, the pass-specific success gap is <b>larger</b>, not smaller — and yards/dropback stays clearly negative in marquee games too. For Michigan, the passing problem in big games wasn&apos;t hidden by the run game. It was the whole story.</p>
            <div className="bga-chart-shell" style={{ marginTop: 18 }}>
              <div className="bga-legend">
                <span><i className="bga-swatch good" />Outperformed expectation</span>
                <span><i className="bga-swatch bad" />Underperformed expectation</span>
                <span style={{ marginLeft: "auto" }}><b className="rc-tag" style={{ fontSize: 11 }}>SUCC</b> = pass success rate · <b className="rc-tag" style={{ fontSize: 11 }}>Y/DB</b> = net yards/dropback</span>
              </div>
              <ResidualChart rows={qbRows} seriesCount={2} />
            </div>
          </section>

          <section id="fourth" className="bga-section">
            <div className="bga-section-kicker">04 · Coaching decisions</div>
            <h2 className="bga-h2">Good calls, bad calls: fourth downs</h2>
            <p className="bga-sub">Every fourth down Michigan faced in 2025, graded against a from-scratch expected-points model trained on 1.5M+ plays across 11 seasons (2014&ndash;2025), and three historical rate curves fit the same way: go-for-it conversion rate by distance, field-goal make rate by kick distance, and punt outcome by field position. Not a win-probability guess &mdash; what has actually worked, at scale, in these exact spots.</p>

            <div className="fd-summary-grid">
              <div className="fd-summary-cell"><div className="fd-summary-num">{fd.totalDecisions}</div><div className="fd-summary-label">4th-down decisions</div></div>
              <div className="fd-summary-cell"><div className="fd-summary-num" style={{ color: "var(--good)" }}>{fd.correctDecisions}</div><div className="fd-summary-label">Matched optimal call</div></div>
              <div className="fd-summary-cell"><div className="fd-summary-num" style={{ color: "var(--bad)" }}>{fd.incorrectDecisions}</div><div className="fd-summary-label">Missed the optimal call</div></div>
              <div className="fd-summary-cell"><div className="fd-summary-num" style={{ color: "var(--bad)" }}>-{fd.totalEvLost.toFixed(1)}</div><div className="fd-summary-label">Expected points lost</div></div>
            </div>

            <div className="bga-callout">
              <p>The pattern isn&apos;t indecisive &mdash; it&apos;s consistently <b>conservative</b>. Of the 23 missed calls, {conservativeMisses} were punts or field goals that the model says should have been fourth-down attempts; only {aggressiveMisses} were the reverse (went for it when kicking or punting was better). Every single 4th-and-3-or-less from the opponent&apos;s 3-yard line was kicked as a field goal &mdash; three times &mdash; and the model says <b>go</b> every time.</p>
              {worstFourth ? (
                <p>The single most expensive decision of the season: a Week 1 punt on 4th &amp; 1 near midfield against New Mexico, costing <span className="bga-num">-{worstFourth.evLost?.toFixed(2)}</span> expected points on its own.</p>
              ) : null}
              <p>Decision quality didn&apos;t track opponent strength the way the offense did &mdash; average EV lost per decision was nearly identical against ranked ({(4.83 / 24).toFixed(2)}) and unranked ({(8.68 / 49).toFixed(2)}) opponents. The conservatism was a season-long pattern, not a big-game one.</p>
            </div>

            <FourthDownBoard decisions={data.fourthDowns} />
          </section>

          <section id="epa" className="bga-section">
            <div className="bga-section-kicker">05 · Independent validation</div>
            <h2 className="bga-h2">Rush vs. pass, confirmed a different way</h2>
            <p className="bga-sub">The same expected-points model used to grade fourth downs also grades every offensive snap. This is a fully independent build from the opponent-adjustment formula above &mdash; and it lands on the same story.</p>
            <div className="bga-stat-grid">
              <div className="bga-stat-cell">
                <div className="bga-stat-label">Rush EPA / play</div>
                <div className="bga-stat-num bga-good-num">{epaFmt(es.rushAvgEpa)}</div>
                <div className="bga-stat-detail">Ranked opponents: {epaFmt(es.rankedRushAvgEpa)} · Unranked: {epaFmt(es.unrankedRushAvgEpa)}</div>
              </div>
              <div className="bga-stat-cell">
                <div className="bga-stat-label">Pass EPA / play</div>
                <div className="bga-stat-num bga-bad-num">{epaFmt(es.passAvgEpa)}</div>
                <div className="bga-stat-detail">Ranked opponents: {epaFmt(es.rankedPassAvgEpa)} · Unranked: {epaFmt(es.unrankedPassAvgEpa)}</div>
              </div>
            </div>
            <p className="bga-note">Passing was worth less than half of what rushing was worth per play across the season ({epaFmt(es.passAvgEpa)} vs. {epaFmt(es.rushAvgEpa)} EPA/play) &mdash; and against the three marquee defenses, passing EPA went <b>negative</b> ({epaFmt(es.rankedPassAvgEpa)}), while rushing merely flattened ({epaFmt(es.rankedRushAvgEpa)}, essentially replacement level). Across {es.totalPlays.toLocaleString()} graded offensive snaps, this independently-built model confirms the same shape the opponent-adjusted passing numbers above show: Michigan&apos;s run-first identity traveled to big games. The pass game didn&apos;t.</p>
          </section>

          <section id="stories" className="bga-section">
            <div className="bga-section-kicker">06 · Three storylines</div>
            <h2 className="bga-h2">Three games, one problem, three mechanisms</h2>
            <p className="bga-sub">Michigan only had three marquee games in 2025, and all three were pass-game underperformances &mdash; but not in the same way.</p>
            <p className="bga-p"><b>Ohio State (L, 9&ndash;27)</b> is total collapse: pass success, team success, and yards/dropback were all clearly below what a #1-ranked defense should have allowed. Nothing offsets anything here.</p>
            <p className="bga-p"><b>Oklahoma (L, 13&ndash;24)</b> is a pure consistency failure: pass success and team success both cratered, but yards/dropback landed almost exactly at expectation. A boom-or-bust day &mdash; long stretches of failed dropbacks broken up by enough big gains to keep the yardage total normal.</p>
            <p className="bga-p"><b>Texas (L, 27&ndash;41, CFP)</b> is the one the box score hides: team-level success was barely dented &mdash; the run game and other phases picked up real slack &mdash; but the passing-specific numbers were still clearly poor, the worst throughput mark of the three. A team-only view of this game would miss the quarterback&apos;s day almost entirely.</p>
          </section>

          <section id="method" className="bga-section" style={{ borderBottom: "none" }}>
            <div className="bga-section-kicker">Method</div>
            <h2 className="bga-h2">How this was built</h2>
            <div className="bga-method-grid">
              <div className="bga-method-item">
                <h3>What &quot;expected&quot; means (offense)</h3>
                <p>Success rate, pass success rate, and yards/dropback are each fit nationwide, all FBS teams, as actual = league mean + offense(team) &minus; defense(opponent), solved by iterative block coordinate descent. Fit once on the complete 2025 season and reused for every game &mdash; a deliberate departure from this site&apos;s leakage-safe predictive ratings, appropriate for retrospective grading rather than forecasting.</p>
              </div>
              <div className="bga-method-item">
                <h3>The fourth-down model</h3>
                <p>An independent expected-points model (&quot;next score before halftime,&quot; the standard EPA-model methodology), trained on 1.5M+ plays across 11 seasons of this site&apos;s validated play-by-play corpus &mdash; never on any vendor&apos;s win-probability numbers. Go-for-it, field-goal, and punt outcomes are priced using real historical rates in the same corpus, binned by distance and field position.</p>
              </div>
              <div className="bga-method-item">
                <h3>&quot;Marquee&quot; = AP rank at kickoff</h3>
                <p>An opponent counts as ranked if it appeared in the AP Top 25 released that week, not a preseason or final-season ranking.</p>
              </div>
              <div className="bga-method-item">
                <h3>What this doesn&apos;t claim</h3>
                <p>The fourth-down grade prices decisions against historical base rates, not a live win-probability or game-theoretic model &mdash; it doesn&apos;t know about injuries, weather, personnel mismatches, or a specific defense&apos;s tendencies on that snap. Treat it as a season-long pattern detector, not a play-by-play referee.</p>
              </div>
            </div>
          </section>
        </div>

        <section className="focus-article-explore">
          <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>Go from the article to the underlying data.</h2></div>
          <div className="focus-article-link-grid">
            <Link href="/analytics/offense?year=2025"><strong>2025 Michigan offense</strong><p>Opponent-adjusted efficiency and national context.</p><span>VIEW →</span></Link>
            <Link href="/players/5141741"><strong>Bryce Underwood profile</strong><p>Freshman production and 2026 roster context.</p><span>VIEW →</span></Link>
            <Link href="/articles/michigan-offense-2025-playcalling-audit"><strong>The 13.5-point mystery</strong><p>The earlier down/distance audit this piece builds on.</p><span>READ →</span></Link>
          </div>
        </section>

        <section className="focus-article-sources">
          <strong>REPORTING &amp; DATA SOURCES</strong>
          <div>{sources.map(([label, url]) => <a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div>
        </section>

        <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
      </div>
    </article>
  );
}
