import type { Metadata } from "next";
import Link from "next/link";
import { ArticleMobileToc } from "../../../components/ArticleMobileToc";
import { PlaycallingMatrix } from "../../../components/articles/PlaycallingMatrix";
import { PlaycallingTrendChart } from "../../../components/articles/PlaycallingTrendChart";
import { teamLogoUrl } from "../../../lib/team-assets";
import { beckAuditData } from "../../../lib/michigan/beck-audit-data";
import "./article.css";

const articleUrl = "https://michiganfootballfocus.com/articles/michigan-offense-2025-playcalling-audit";
const articleImage = "https://michiganfootballfocus.com/images/articles/jason-beck.png";
const socialDescription = "Michigan and Jason Beck's Utah had nearly the same run rate, success rate and yards per play in the 2025 regular season. Utah still scored 13.5 more points per game. Here's where the gap actually appeared.";

export const metadata: Metadata = {
  title: "Michigan's 13.5-Point Offensive Mystery — What Jason Beck Must Fix",
  description: socialDescription,
  openGraph: {
    type: "article",
    url: articleUrl,
    siteName: "Michigan Football Focus",
    title: "Michigan's 13.5-Point Offensive Mystery",
    description: socialDescription,
    images: [{ url: articleImage, alt: "Jason Beck" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Michigan's 13.5-Point Offensive Mystery",
    description: socialDescription,
    images: [articleImage],
  },
};

const sections = [
  ["mystery", "The 13.5-point mystery"],
  ["matrix", "Down and distance"],
  ["trend", "Game by game"],
  ["beck", "What Beck changes"],
  ["watch", "The catch"],
] as const;

const sources = [
  ["Michigan 2025 cumulative statistics", "https://mgoblue.com/sports/football/stats/2025"],
  ["Michigan 2025 schedule and results", "https://mgoblue.com/sports/football/schedule/2025"],
  ["Utah 2025 cumulative statistics", "https://utahutes.com/sports/football/stats/2025"],
  ["Utah 2025 schedule and results", "https://utahutes.com/sports/football/schedule/2025"],
  ["Detroit News: Chip Lindsey headed to Missouri", "https://www.detroitnews.com/story/sports/college/university-michigan/2025/12/21/michigan-football-offensive-coordinator-chip-lindsey-headed-to-missouri/87872359007/"],
  ["Michigan: Jason Beck named offensive coordinator", "https://mgoblue.com/news/2026/1/2/football-jason-beck-named-michigans-sanford-robertson-offensive-coordinator"],
  ["KSL: Beck's positionless offensive scheme", "https://www.ksl.com/article/51375990/jason-becks-positionless-offensive-scheme-and-how-it-can-pickle-the-defense"],
  ["SI: Beck plans to use Underwood's legs as a weapon", "https://www.si.com/college/michigan/football/michigan-jason-beck-use-bryce-underwood-legs-weapon-2026"],
  ["ClickOnDetroit: Koy Detmer Jr. on Underwood's growth", "https://www.clickondetroit.com/all-about-ann-arbor/2026/08/26/michigan-football-qb-coach-koy-detmer-jr-praises-bryce-underwoods-growth-ahead-of-2026-season/"],
] as const;

const officialRegularSeasonScoring = {
  michigan: 27.6,
  utah: 41.1,
  gap: 13.5,
} as const;

function pct(v: number, digits = 1): string {
  return `${(v * 100).toFixed(digits)}%`;
}

function ppa(v: number): string {
  return `${v >= 0 ? "+" : ""}${v.toFixed(2)}`;
}

function BaselineCard({ label, michigan, utah, gap }: { label: string; michigan: string; utah: string; gap: string }) {
  return (
    <div className="audit-baseline-card">
      <span>{label}</span>
      <div><strong>{michigan}</strong><b>MI</b><i>vs</i><strong>{utah}</strong><b>UTAH</b></div>
      <small>{gap}</small>
    </div>
  );
}

function GapRow({ label, michigan, utah, gap, detail }: { label: string; michigan: number; utah: number; gap: string; detail: string }) {
  return (
    <div className="audit-gap-row">
      <div className="audit-gap-heading"><strong>{label}</strong><span>{gap}</span></div>
      <div className="audit-gap-bars">
        <div><b>MI</b><i><span style={{ width: `${michigan * 100}%` }} /></i><strong>{pct(michigan, 1)}</strong></div>
        <div><b>UTAH</b><i><span style={{ width: `${utah * 100}%` }} /></i><strong>{pct(utah, 1)}</strong></div>
      </div>
      <small>{detail}</small>
    </div>
  );
}

function RiskCard({ number, title, body }: { number: string; title: string; body: string }) {
  return (
    <article className="audit-risk-card">
      <span>{number}</span>
      <h3>{title}</h3>
      <p>{body}</p>
    </article>
  );
}

export default function PlaycallingAuditArticle() {
  const mi = beckAuditData.michigan;
  const ut = beckAuditData.utah;

  return (
    <article className="focus-article feature-article playcalling-audit">
      <div className="article-reading-progress" aria-hidden="true" />
      <div className="focus-article-shell feature-shell">
        <Link className="feature-back" href="/articles">← THE NOTEBOOK</Link>

        <header className="focus-article-hero matchup-hero audit-hero">
          <img src="/images/articles/jason-beck.png" alt="Jason Beck" />
          <div className="focus-article-hero-copy">
            <span className="focus-article-eyebrow">ACTUAL · 2025 REGULAR-SEASON AUDIT</span>
            <h1>Michigan's <em>13.5-Point</em> Mystery</h1>
            <p className="feature-headline">Michigan and Jason Beck's Utah were almost identical in run share, overall success rate and yards per play. Utah still scored 13.5 more points per game.</p>
            <p className="feature-deck">That is the question worth solving. Not whether Michigan needed to “run more.” Not whether one coordinator had a magic playbook. Where did two offenses with similar snap-to-snap foundations separate when the field got harder?</p>
            <div className="focus-article-meta"><span>AUGUST 27, 2026</span><span>10 MIN READ</span><span>DATA AUDIT</span></div>
          </div>
        </header>

        <section className="audit-mystery" aria-labelledby="mystery-board-title">
          <div className="audit-mystery-kicker"><span>THE MYSTERY</span><b>12 games vs. 12 games. Same season. Very different scoreboard.</b></div>
          <h2 id="mystery-board-title">They looked almost the same — until the points showed up.</h2>
          <div className="audit-baseline-grid">
            <BaselineCard label="SUCCESS RATE V1" michigan={pct(mi.seasonSummary.successRate, 1)} utah={pct(ut.seasonSummary.successRate, 1)} gap="Utah +1.1 pts" />
            <BaselineCard label="RUSH SHARE" michigan={pct(mi.seasonSummary.runRate, 1)} utah={pct(ut.seasonSummary.runRate, 1)} gap="Essentially identical" />
            <BaselineCard label="YARDS / PLAY" michigan={mi.seasonSummary.yardsPerPlay.toFixed(2)} utah={ut.seasonSummary.yardsPerPlay.toFixed(2)} gap="Utah +0.25 YPP" />
          </div>
          <div className="audit-score-reveal">
            <div className="audit-score-team">
              <img src={teamLogoUrl(130, 72)} alt="Michigan" />
              <span>MICHIGAN · LINDSEY</span>
              <strong>{officialRegularSeasonScoring.michigan.toFixed(1)}</strong>
              <small>OFFICIAL PPG · 12 REGULAR-SEASON GAMES</small>
            </div>
            <div className="audit-score-gap"><span>THE GAP</span><strong>+{officialRegularSeasonScoring.gap.toFixed(1)}</strong><b>PPG</b></div>
            <div className="audit-score-team">
              <img src={teamLogoUrl(254, 72)} alt="Utah" />
              <span>UTAH · BECK</span>
              <strong>{officialRegularSeasonScoring.utah.toFixed(1)}</strong>
              <small>OFFICIAL PPG · 12 REGULAR-SEASON GAMES</small>
            </div>
          </div>
          <p className="audit-source-note">Official scoring is calculated from each team's 12 regular-season results. Michigan's Citrus Bowl is excluded from the staff-to-staff comparison because Steve Casula, not Chip Lindsey, called that game.</p>
        </section>

        <ArticleMobileToc sections={sections} />

        <div className="feature-reading-layout">
          <aside className="feature-toc">
            <span>IN THIS AUDIT</span>
            <nav>{sections.map(([id, label], index) => <a href={`#${id}`} key={id}><b>{String(index + 1).padStart(2, "0")}</b>{label}</a>)}</nav>
            <Link href="/analytics/offense?year=2025">2025 OFFENSE DATA →</Link>
          </aside>

          <div className="focus-article-body feature-body">
            <p className="focus-article-lede">This is not a claim that Utah's roster, schedule or quarterback situation can be copied onto Michigan. It is a descriptive audit of two 2025 offenses using the same SOAR classifiers. The useful question is narrower: <strong>where did the raw efficiency gap expand, and are those areas relevant to what Jason Beck inherits in Ann Arbor?</strong></p>

            <div className="audit-scope">
              <span>READ THIS FIRST</span>
              <strong>Outcome data can identify where to investigate. It cannot prove what a coordinator “should have called.”</strong>
              <p>Rush/dropback families come from SOAR's locked play classifications, not film-charted intent. Scrambles, RPO decisions, exact distance, defensive front and game state can all affect the observed split. The matrix below is a review map, not a causal grade.</p>
            </div>

            <section id="mystery" className="feature-story-section audit-section">
              <div className="feature-section-number">01</div><div className="feature-section-kicker">WHERE THE GAP APPEARS</div>
              <h2>The offense wasn't bad everywhere.</h2>
              <p>Michigan's base efficiency was close to Utah's. The separation grew as the offense moved into situations where the defense had more information and the field compressed.</p>

              <div className="audit-wide audit-gap-chart">
                <GapRow label="OVERALL SUCCESS" michigan={mi.seasonSummary.successRate} utah={ut.seasonSummary.successRate} gap="UTAH +1.1 pts" detail="Nearly the same snap-to-snap floor." />
                <GapRow label="PASSING-DOWN SUCCESS" michigan={mi.seasonSummary.passingDownSuccessRate} utah={ut.seasonSummary.passingDownSuccessRate} gap="UTAH +6.1 pts" detail="2nd-and-8+ and 3rd/4th-and-5+ under SOAR's locked definition." />
                <GapRow label="RED-ZONE DROPBACK SUCCESS" michigan={mi.redZone.pass.successRate} utah={ut.redZone.pass.successRate} gap="UTAH +26.8 pts" detail="The largest raw separation in this audit. Descriptive, not opponent-adjusted." />
              </div>

              <div className="feature-thesis audit-thesis"><span>THE ACTUAL STORY</span><strong>Michigan did not need a completely different offensive identity. It needed better answers when the defense could narrow the menu.</strong></div>
              <p>That distinction matters for 2026. If Beck preserves Michigan's rushing floor and improves the offense when it falls behind schedule or reaches the red zone, the unit can change substantially without becoming pass-heavy.</p>
            </section>

            <section id="matrix" className="feature-story-section audit-section">
              <div className="feature-section-number">02</div><div className="feature-section-kicker">DOWN + DISTANCE</div>
              <h2>Use the matrix as a map, not a verdict.</h2>
              <p>Every regular-season offensive snap is bucketed by down and distance, then split into SOAR's rush and dropback families. <strong>Short = 1–3 yards, medium = 4–7, long = 8+.</strong> A cell only highlights an observed family edge when both sides have at least 15 plays and the success-rate difference is at least eight percentage points.</p>

              <div className="audit-wide pc-matrix-wrap">
                <PlaycallingMatrix title="Michigan · Lindsey (12 games)" accent="mi" cells={mi.matrix} />
                <PlaycallingMatrix title="Utah · Beck (12 games)" accent="ut" cells={ut.matrix} />
              </div>

              <div className="audit-review-window">
                <div><span>FILM-REVIEW WINDOW</span><strong>Michigan · late downs · medium</strong></div>
                <div className="audit-review-split">
                  <div><small>RUSH FAMILY</small><strong>66.7%</strong><span>21 plays · 41% share</span></div>
                  <b>vs</b>
                  <div><small>DROPBACK FAMILY</small><strong>46.7%</strong><span>30 plays · 59% share</span></div>
                </div>
                <p>The 20-point observed split is worth reviewing on film. It is <strong>not</strong> evidence that Michigan “should have run” every medium late down: 3rd and 4th down are grouped in the current artifact, and exact distance, scramble outcomes and defensive structure are not controlled here.</p>
              </div>
            </section>

            <section id="trend" className="feature-story-section audit-section">
              <div className="feature-section-number">03</div><div className="feature-section-kicker">GAME BY GAME</div>
              <h2>Did the offense actually improve?</h2>
              <p>The maize line is overall Success Rate v1. Blue dots are passing-down success. The Utah benchmark is context, not a target line: Michigan faced a different schedule, and single-game situational samples can swing hard.</p>

              <div className="pc-trend-legend">
                <span><i className="legend-overall" />Overall success</span>
                <span><i className="legend-pass" />Passing-down success</span>
                <span><i className="legend-utah" />Utah regular-season average</span>
              </div>
              <div className="audit-wide pc-trend-shell"><PlaycallingTrendChart games={mi.trend} utahAvg={ut.seasonSummary.successRate} /></div>

              <div className="audit-three-takeaways">
                <div><span>WEEK 3 · CMU</span><strong>64.5%</strong><p>Michigan's best overall success game. Underwood also produced his biggest rushing day.</p></div>
                <div><span>WEEK 12 · OHIO STATE</span><strong>25.6%</strong><p>The floor against an elite defense. Raw success fell almost 39 points from the CMU peak.</p></div>
                <div><span>BOWL · TEXAS</span><strong>39.5%</strong><p>Casula's interim game is visually separated because it is not Lindsey's playcalling sample.</p></div>
              </div>

              <div className="feature-pullquote audit-caution">This chart measures offensive performance by game. It does not isolate play-caller quality.</div>
            </section>

            <section id="beck" className="feature-story-section audit-section">
              <div className="feature-section-number">04</div><div className="feature-section-kicker">THE BECK TRANSLATION</div>
              <h2>Beck does not need Michigan to become pass-happy.</h2>
              <p>Michigan and Utah both finished the 2025 regular season at essentially a 58.5% rush share. The intriguing part of Beck's Utah offense was not raw pass volume. It was how much more productive the offense remained in leverage situations.</p>

              <div className="audit-wide audit-leverage-grid">
                <div className="audit-leverage-card">
                  <span>PASSING DOWNS</span>
                  <small>SUCCESS RATE</small>
                  <div><strong>{pct(mi.seasonSummary.passingDownSuccessRate, 1)}</strong><b>MI</b><i>→</i><strong>{pct(ut.seasonSummary.passingDownSuccessRate, 1)}</strong><b>UTAH</b></div>
                  <p>Utah +6.1 percentage points.</p>
                </div>
                <div className="audit-leverage-card audit-leverage-card-primary">
                  <span>RED ZONE</span>
                  <small>DROPBACK SUCCESS</small>
                  <div><strong>{pct(mi.redZone.pass.successRate, 0)}</strong><b>MI</b><i>→</i><strong>{pct(ut.redZone.pass.successRate, 0)}</strong><b>UTAH</b></div>
                  <p>PPA/play: {ppa(mi.redZone.pass.avgPpa)} Michigan · {ppa(ut.redZone.pass.avgPpa)} Utah.</p>
                </div>
                <div className="audit-leverage-card">
                  <span>MONEY DOWNS</span>
                  <small>DROPBACK PPA</small>
                  <div><strong>{ppa(mi.moneyDownPassPpa)}</strong><b>MI</b><i>→</i><strong>{ppa(ut.moneyDownPassPpa)}</strong><b>UTAH</b></div>
                  <p>Research split: 2nd-and-8+ / 3rd-and-5+ / 4th-and-5+.</p>
                </div>
              </div>

              <p>Beck's 2025 Utah quarterbacks were real run threats, which changed the arithmetic for the defense and helped create throws off the same run-first structure. Underwood is not Devon Dampier. Michigan's own quarterback coaches have described him as more naturally pocket-oriented, even though his freshman season showed legitimate rushing ability.</p>

              <div className="audit-translation">
                <span>THE 2026 BET</span>
                <strong>Do not copy Utah's playbook. Make Michigan's existing run-first identity harder to predict once the defense takes the obvious answer away.</strong>
                <p>Beck has publicly framed the install around conforming the system to Underwood. That is the right standard for judging the hire: adaptation, not imitation.</p>
              </div>
            </section>

            <section id="watch" className="feature-story-section feature-final-section audit-section">
              <div className="feature-section-number">05</div><div className="feature-section-kicker">WHAT COULD BREAK THE THEORY</div>
              <h2>Three reasons not to overfit Utah onto Michigan.</h2>

              <div className="audit-wide audit-risk-grid">
                <RiskCard number="01" title="Different quarterback geometry" body="Utah's system forced defenses to account for Dampier as a frequent designed-run threat. Underwood can run, but his default style is different. The same concepts may create different defensive reactions." />
                <RiskCard number="02" title="Different personnel answers" body="Beck's ‘positionless’ Utah offense found unusual roles for that specific roster. Michigan needs its own mismatches; those cannot be assumed from Utah's box score." />
                <RiskCard number="03" title="Different opponents, different game states" body="None of the Michigan-vs-Utah raw splits are opponent-adjusted here. They are diagnostic clues. They are not proof that the same calls would produce the same result in the Big Ten." />
              </div>

              <div className="audit-verdict-grid">
                <div><span>WHAT THE DATA CAN SAY</span><strong>Michigan's largest raw gaps to Beck's Utah showed up on passing downs and red-zone dropbacks.</strong></div>
                <div><span>WHAT IT CANNOT SAY</span><strong>That Lindsey chose the wrong play, or that Beck automatically imports Utah's 2025 production.</strong></div>
              </div>

              <div className="feature-verdict audit-verdict">
                <span>THE VERDICT</span>
                <strong>The 2026 bet is not that Jason Beck changes Michigan's identity. It is that he makes the same identity survive when defenses know what is coming.</strong>
                <p>Michigan already had the snap-to-snap foundation. Beck's Utah data is compelling because its biggest advantage appeared after the easy answers disappeared. That is exactly where Michigan has room to grow — and exactly where 2026 has to prove the comparison travels.</p>
              </div>
            </section>
          </div>
        </div>

        <section className="focus-article-explore feature-explore">
          <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>Go from the article to the underlying data.</h2></div>
          <div className="focus-article-link-grid">
            <Link href="/analytics/offense?year=2025"><strong>2025 Michigan offense</strong><p>Opponent-adjusted efficiency and national context.</p><span>VIEW →</span></Link>
            <Link href="/players/5141741"><strong>Bryce Underwood profile</strong><p>Freshman production and 2026 roster context.</p><span>VIEW →</span></Link>
            <Link href="/articles/what-to-expect-michigan-offense-2026"><strong>2026 offense preview</strong><p>The bigger-picture projection behind the coordinator change.</p><span>READ →</span></Link>
          </div>
        </section>

        <section className="focus-article-sources">
          <strong>REPORTING &amp; DATA SOURCES</strong>
          <div>{sources.map(([label, url]) => <a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div>
        </section>

        <div className="audit-method-note">
          <strong>METHOD NOTE</strong>
          <p>SOAR situational splits use the site's locked Success Rate v1, standard/passing-down, rush/dropback and red-zone definitions. The 12-game Michigan-vs-Utah comparison excludes Michigan's bowl to keep the play-caller sample consistent. The matrix is descriptive and does not film-chart intended play calls. PPA is shown only where the existing research artifact contains it; it is not relabeled as EPA.</p>
        </div>

        <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
      </div>
    </article>
  );
}
