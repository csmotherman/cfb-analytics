import type { Metadata } from "next";
import Link from "next/link";
import { ArticleMobileToc } from "../../../components/ArticleMobileToc";
import { beckAuditData } from "../../../lib/michigan/beck-audit-data";
import "./article.css";

const articleUrl = "https://michiganfootballfocus.com/articles/dont-jump-the-gun-michigan-football-2026";
const articleImage = "https://michiganfootballfocus.com/images/articles/dont-jump-the-gun-twitter-card.jpg";
const socialDescription = "Michigan's 13-12 escape against Western Michigan was unacceptable. It was also one game. The evidence says downgrade the Wolverines after Week 1 — don't reclassify them.";

export const metadata: Metadata = {
  title: "Don't Jump the Gun: Why Michigan Football Is in a Better Spot Than It Looks",
  description: socialDescription,
  openGraph: {
    type: "article",
    url: articleUrl,
    siteName: "SOAR Analytics",
    title: "Don't Jump the Gun: Why Michigan Is in a Better Spot Than It Looks",
    description: socialDescription,
    images: [{ url: articleImage, alt: "Michigan football after the Western Michigan opener" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Don't Jump the Gun: Why Michigan Is in a Better Spot Than It Looks",
    description: socialDescription,
    images: [articleImage],
  },
};

const sections = [
  ["reality", "What actually happened"],
  ["defense", "The defense already translated"],
  ["western", "Western was not a generic opener"],
  ["beck", "Why Beck still matters"],
  ["bryce", "Don't erase Bryce's prior"],
  ["whittingham", "Twenty-one years vs. one game"],
  ["worry", "What would actually worry us"],
  ["oklahoma", "What Oklahoma can tell us"],
] as const;

const sources = [
  ["Michigan vs. Western Michigan official box score", "https://mgoblue.com/sports/football/stats/2026/western-michigan/boxscore/30374"],
  ["Michigan vs. Western Michigan game center", "https://mgoblue.com/game-center/30374"],
  ["Jason Beck coaching bio and 2025 Utah rankings", "https://mgoblue.com/sports/football/roster/coaches/jason-beck/6855"],
  ["Jay Hill coaching bio and 2024-25 BYU defensive rankings", "https://mgoblue.com/sports/football/roster/coaches/jay-hill/6865"],
  ["Kyle Whittingham Michigan coaching bio", "https://mgoblue.com/sports/football/roster/coaches/kyle-whittingham/6875"],
  ["Bryce Underwood 2025 season statistics", "https://www.espn.com/college-football/player/stats/_/id/5141741/bryce-underwood"],
  ["Western Michigan 2025 season statistics", "https://www.sports-reference.com/cfb/schools/western-michigan/2025.html"],
  ["Western Michigan 2025 MAC Championship", "https://wmubroncos.com/news/2025/12/7/football-broncos-win-2025-mac-championship.aspx"],
  ["SOAR: Michigan's 13.5-Point Offensive Mystery", "/articles/michigan-offense-2025-playcalling-audit"],
] as const;

const mi = beckAuditData.michigan.seasonSummary;
const ut = beckAuditData.utah.seasonSummary;
const rzMi = beckAuditData.michigan.redZone.pass.successRate;
const rzUt = beckAuditData.utah.redZone.pass.successRate;

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function SectionHead({ number, kicker, title }: { number: string; kicker: string; title: string }) {
  return (
    <div className="djg-section-head">
      <span>{number}</span>
      <div><b>{kicker}</b><h2>{title}</h2></div>
    </div>
  );
}

function EvidenceCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="djg-evidence-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </div>
  );
}

export default function DontJumpTheGunArticle() {
  return (
    <article className="focus-article dont-jump">
      <div className="focus-article-shell djg-shell">
        <Link className="djg-back" href="/articles">← THE NOTEBOOK</Link>

        <header className="djg-hero">
          <img src="/images/articles/dont-jump-the-gun-twitter-card.jpg" alt="Don't Jump the Gun — Michigan football Week 1 perspective" />
          <div className="djg-hero-shade" />
          <div className="djg-hero-copy">
            <span className="djg-eyebrow">WEEK 1 · PERSPECTIVE</span>
            <h1>DON'T JUMP<br /><em>THE GUN.</em></h1>
            <p className="djg-headline">Why Michigan football is in a better spot than it looked Saturday night.</p>
            <p className="djg-deck">The 13-12 escape was unacceptable. It was also one game. When 60 minutes of ugly football are weighed against the larger body of evidence surrounding Kyle Whittingham, Jason Beck, Jay Hill and Bryce Underwood, the rational response is to downgrade Michigan — not reclassify it.</p>
            <div className="djg-meta"><span>SEPTEMBER 8, 2026</span><span>14 MIN READ</span><span>SOAR ANALYTICS</span></div>
          </div>
        </header>

        <section className="djg-thesis-board" aria-label="Week 1 thesis">
          <div className="djg-thesis-kicker"><span>THE THESIS</span><b>One bad data point should move the forecast. It should not replace the forecast.</b></div>
          <h2>Michigan should be <em>downgraded</em> after Week 1. It should not be <em>reclassified</em> after Week 1.</h2>
          <div className="djg-signal-grid">
            <EvidenceCard label="MICHIGAN YARDS / PLAY" value="5.8" detail="Western Michigan averaged 3.3. The game was not a snap-for-snap physical domination." />
            <EvidenceCard label="TURNOVERS" value="3–0" detail="Michigan gave away three possessions. That is catastrophic in one game and highly volatile across a season." />
            <EvidenceCard label="POSSESSION" value="−20:16" detail="Western held the ball for 40:08. Michigan's offense got only 48 snaps." />
            <EvidenceCard label="TOUCHDOWNS ALLOWED" value="0" detail="Jay Hill's defense faced repeated stress and never allowed Western Michigan into the end zone." />
          </div>
        </section>

        <ArticleMobileToc sections={sections} />

        <div className="djg-reading-layout">
          <aside className="djg-toc">
            <span>IN THIS STORY</span>
            <nav>{sections.map(([id, label], index) => <a href={`#${id}`} key={id}><b>{String(index + 1).padStart(2, "0")}</b>{label}</a>)}</nav>
            <Link href="/analytics">EXPLORE SOAR DATA →</Link>
          </aside>

          <div className="djg-body">
            <p className="djg-lede">Michigan deserved the criticism. A program with Michigan's roster, resources and expectations should not need a 47-yard touchdown on the final play to survive Western Michigan at home. The Wolverines turned the ball over three times, committed nine penalties for 80 yards, converted three of 10 third downs and spent most of the night looking nothing like the team people expected to see.</p>
            <p>There is no need to soften that. But there is a difference between saying <strong>Michigan played a terrible game</strong> and saying <strong>Michigan is a terrible team, Jason Beck cannot coordinate this offense, Bryce Underwood has not developed or Kyle Whittingham was the wrong hire.</strong> The first claim is supported by evidence. The larger claims are attempts to infer an entire season — and in some cases an entire coaching tenure — from one observation.</p>
            <div className="djg-pullquote">We're not evaluating a failed season yet. We're reacting to one terrible Saturday.</div>

            <section id="reality" className="djg-section">
              <SectionHead number="01" kicker="THE REALITY CHECK" title="The final score looked worse than the underlying play-by-play." />
              <p>Start with the part nobody can argue with: Michigan was sloppy. But look at the game before assigning a diagnosis. Western Michigan ran 67 plays for 221 yards. Michigan ran only 48 plays and gained 276. That is <strong>5.8 yards per play for Michigan against 3.3 for Western.</strong></p>
              <p>Western rushed 46 times and averaged 2.9 yards per carry. Broc Lowry threw for 89 yards. The Broncos did not score a touchdown. Their 12 points came from four field goals.</p>
              <p>Michigan lost because almost every high-variance mistake landed on the same side of the ledger. The Wolverines lost two fumbles, threw an interception, committed nine penalties and allowed Western to possess the ball for 40:08. Michigan's offense had only 48 opportunities to run a play.</p>
              <div className="djg-two-paths">
                <div><span>WHAT THE SCORE SUGGESTS</span><strong>Michigan was physically outclassed by a MAC team.</strong></div>
                <div><span>WHAT THE BOX SCORE SUGGESTS</span><strong>Michigan created more yards per snap but destroyed its own possession value.</strong></div>
              </div>
              <p>Those are not the same problem. Turnovers, penalties, special-teams field position and third-down failures are absolutely real. They also tend to be more correctable than discovering that your roster simply cannot win blocks, cover receivers or generate efficient plays.</p>
              <p>The opener should lower confidence in Michigan's offensive floor. It does not provide enough evidence to erase the team's ceiling.</p>
            </section>

            <section id="defense" className="djg-section">
              <SectionHead number="02" kicker="THE PART THAT TRANSLATED" title="Jay Hill's defense already looked like a Jay Hill defense." />
              <p>If one game is going to be used as a referendum on Michigan's new staff, then the entire game has to count.</p>
              <p>Michigan's defense gave up <strong>221 yards, 3.3 yards per play and zero touchdowns.</strong> It did that while spending more than 40 minutes on the field and repeatedly being asked to survive after Michigan's offense or special teams created stress.</p>
              <p>Late in the second quarter, an Underwood interception gave Western the ball at the Michigan 26. Western gained negative one yard and kicked a field goal. Late in the fourth, an Underwood fumble gave Western the ball at the Michigan 31. Western gained 17 yards and kicked another field goal.</p>
              <p>The blemish was obvious: Western converted eight of 18 third downs and produced a 20-play, 71-yard drive that consumed 13:40. Against Oklahoma, that could become fatal. But the larger defensive signal was extremely difficult to miss.</p>
              <div className="djg-coach-card">
                <span>WHY THAT MATTERS</span>
                <h3>Hill arrived with a repeatable high-leverage profile.</h3>
                <p>His 2025 BYU defense ranked No. 5 nationally in red-zone defense, No. 7 in interceptions, No. 14 in turnovers gained, No. 19 on third down and No. 21 in scoring defense at 19.1 points per game. BYU had also ranked No. 18 in scoring defense the year before.</p>
              </div>
              <p>One game does not prove Michigan's defense will be elite. But the first Michigan sample under Hill aligned far more closely with his prior evidence than the offense did with Beck's. That is encouraging because defense was never supposed to be the rebuilding side of this team.</p>
            </section>

            <section id="western" className="djg-section">
              <SectionHead number="03" kicker="OPPONENT CONTEXT" title="Western Michigan was still better than the name on the jersey suggests." />
              <p>This cannot become an excuse. Michigan was a massive favorite and should have won comfortably.</p>
              <p>But analysis requires context. Western Michigan entered 2026 after a <strong>10-4 season, a MAC championship and a bowl win.</strong> The Broncos allowed 17.4 points per game in 2025, ninth nationally by Sports Reference's FBS table. Their defense, not their offense, was the strongest part of the team Michigan was facing.</p>
              <p>That matters because the useful conclusion is not “Michigan could barely move the ball against one of the worst teams in football.” Western was not one of the worst teams in football. It was a defending conference champion with an established defensive identity.</p>
              <p>The offensive performance remains bad. The opponent context simply tells us how much weight to put on it.</p>
              <div className="djg-rule"><span>CONTEXT IS NOT AN EXCUSE.</span><strong>It is how you stop a bad result from becoming a bad analysis.</strong></div>
            </section>

            <section id="beck" className="djg-section">
              <SectionHead number="04" kicker="THE LARGER OFFENSIVE SAMPLE" title="Forty-eight Michigan snaps do not erase two seasons of Jason Beck evidence." />
              <p>There is a reason Beck was one of the most interesting coordinator hires of the offseason. His 2025 Utah offense ranked <strong>No. 2 nationally in rushing offense, No. 4 in total offense, No. 5 in scoring offense and No. 3 in third-down conversion rate.</strong> Utah averaged 266.3 rushing yards, 482.9 total yards and 41.2 points per game.</p>
              <p>The year before, Beck coordinated a New Mexico offense that also finished top five nationally in rushing and total offense. That does not guarantee his system will translate to Michigan. It does establish a meaningful prior.</p>
              <p>And SOAR had already isolated why Beck was such a fascinating fit before this season started.</p>

              <div className="djg-beck-board">
                <div className="djg-beck-top"><span>SOAR · 2025 OFFENSIVE AUDIT</span><Link href="/articles/michigan-offense-2025-playcalling-audit">READ THE FULL AUDIT →</Link></div>
                <div className="djg-beck-grid">
                  <div><span>OVERALL SUCCESS</span><strong>{pct(mi.successRate)}</strong><small>MICHIGAN</small><b>vs.</b><strong>{pct(ut.successRate)}</strong><small>UTAH</small></div>
                  <div><span>RUSH SHARE</span><strong>{pct(mi.runRate)}</strong><small>MICHIGAN</small><b>vs.</b><strong>{pct(ut.runRate)}</strong><small>UTAH</small></div>
                  <div><span>PASSING-DOWN SUCCESS</span><strong>{pct(mi.passingDownSuccessRate)}</strong><small>MICHIGAN</small><b>vs.</b><strong>{pct(ut.passingDownSuccessRate)}</strong><small>UTAH</small></div>
                  <div><span>RED-ZONE DROPBACK SUCCESS</span><strong>{pct(rzMi)}</strong><small>MICHIGAN</small><b>vs.</b><strong>{pct(rzUt)}</strong><small>UTAH</small></div>
                </div>
                <p>Michigan and Utah had almost identical rushing shares and very similar overall success rates in the 2025 regular season. Utah still scored roughly <strong>13.5 more points per game.</strong> The separation expanded on passing downs and in the red zone — exactly the situations Michigan hired Beck to improve.</p>
              </div>

              <p>The correct Week 1 criticism is not that Beck's offense has been disproven. It is that <strong>Michigan did not yet look like the offense Beck's résumé told us to expect.</strong> Where were the consistent answers when Western crowded the run? Why did the quarterback-run element feel secondary? Why did the offense struggle to stay on schedule after the opening drive?</p>
              <p>Those are serious questions. They are also testable over the next several games.</p>
            </section>

            <section id="bryce" className="djg-section">
              <SectionHead number="05" kicker="BAYES, NOT AMNESIA" title="One ugly Bryce Underwood game should update the prior — not delete it." />
              <p>Underwood was 12-for-23 for 170 yards against Western Michigan. He threw an interception and lost a late fumble. He looked uncomfortable far too often. If that becomes normal, Michigan has a major problem.</p>
              <p>But the larger sample still exists.</p>
              <p>As an 18-year-old freshman in 2025, Underwood threw for <strong>2,428 yards</strong>, rushed for <strong>392</strong>, produced six rushing touchdowns and finished with a <strong>72.6 QBR, 29th nationally.</strong> He was inconsistent — exactly what an 18-year-old starting quarterback tends to be — but he was already productive enough to give Michigan a legitimate foundation.</p>
              <p>This is where football discussion often abandons basic probabilistic thinking. Before the Western game, we possessed an entire freshman season, an offseason of development, a new quarterback-friendly coordinator and Underwood's physical profile. Then one bad game arrived.</p>
              <div className="djg-equation"><span>THE CORRECT UPDATE</span><strong>Strong prior + one bad observation = lower confidence.</strong><b>Not: one bad observation = erase the prior.</b></div>
              <p>That is not blind optimism. It is simply refusing to overweight the newest information because it is the most emotionally vivid.</p>
            </section>

            <section id="whittingham" className="djg-section">
              <SectionHead number="06" kicker="THE HEAD COACH SAMPLE" title="Twenty-one seasons of Whittingham evidence still outweigh one Michigan Saturday." />
              <p>This is the strangest part of the postgame reaction. Michigan hired a head coach with more than two decades of evidence, then some observers attempted to decide whether he has a championship ceiling after one game in Ann Arbor.</p>
              <p>Whittingham went <strong>177-88 at Utah</strong>. He produced winning records in 18 of 21 seasons and won at least 10 games eight times. His 2008 team went 13-0 and beat Alabama in the Sugar Bowl. Utah later won consecutive Pac-12 championships in 2021 and 2022.</p>
              <p>That résumé does not prove Whittingham will win a national championship at Michigan. It does destroy the idea that his ceiling can reasonably be inferred from 60 minutes against Western Michigan.</p>
              <p>The “floor raiser, not ceiling raiser” label also skips the most interesting part of the experiment. Whittingham repeatedly pushed Utah beyond what its historical recruiting and resource profile would normally predict. Michigan is now giving that coach a different resource base.</p>
              <div className="djg-pullquote compact">The unanswered question is not whether Whittingham could maximize Utah. He already did. The unanswered question is what happens when he gets to maximize Michigan.</div>
              <p>We do not know the answer. That uncertainty cuts both ways. It is not evidence for optimism by itself, but it is certainly not evidence for declaring the hire a failure.</p>
            </section>

            <section id="worry" className="djg-section">
              <SectionHead number="07" kicker="THE STANDARD" title="Here is what would actually make us worry." />
              <p>None of this means Michigan is automatically fine. The purpose of rejecting panic is not to replace it with denial.</p>
              <div className="djg-worry-grid">
                <div><span>01</span><strong>The run game stays inefficient.</strong><p>If Michigan is still losing blocks and living behind schedule several weeks from now, that stops being first-game noise.</p></div>
                <div><span>02</span><strong>Underwood's legs remain secondary.</strong><p>Beck's system should make a defense account for the quarterback. If that threat never becomes central, the fit deserves scrutiny.</p></div>
                <div><span>03</span><strong>Turnover-worthy decisions persist.</strong><p>One interception and one fumble are a bad night. Repeated bad decisions become a quarterback-development problem.</p></div>
                <div><span>04</span><strong>The penalty problem becomes an identity.</strong><p>Nine penalties for 80 yards cannot be brushed aside if Michigan continues losing hidden possession value.</p></div>
                <div><span>05</span><strong>The defense cannot get off the field.</strong><p>Zero touchdowns allowed was excellent. Eight third-down conversions allowed was not. Hill has to win both parts.</p></div>
                <div><span>06</span><strong>The offense still has no answers by October.</strong><p>At that point the Beck résumé becomes less relevant because we would have a real Michigan sample to evaluate.</p></div>
              </div>
              <p>That is the difference between skepticism and panic. Skepticism asks Michigan to prove Western was an aberration. Panic assumes it wasn't.</p>
            </section>

            <section id="oklahoma" className="djg-section">
              <SectionHead number="08" kicker="THE NEXT DATA POINT" title="Oklahoma will tell us more — but it still will not tell us everything." />
              <p>Michigan could not ask for a more useful second test. No. 10 Oklahoma comes to Ann Arbor on September 12. The opponent is better, the athletes are better and the margin for self-inflicted errors is dramatically smaller.</p>
              <p>The result matters. The process may tell us even more.</p>
              <div className="djg-checklist">
                <span>WATCH FOR</span>
                <b>Does the offensive line communicate better?</b>
                <b>Does Beck make Underwood a true run-game constraint?</b>
                <b>Are there easier throws and cleaner early-down answers?</b>
                <b>Do the penalties and giveaway mistakes fall?</b>
                <b>Can Hill's defense get off the field without sacrificing its red-zone resistance?</b>
              </div>
              <p>If Michigan looks structurally better against Oklahoma, the Western game immediately begins to look more like a disastrous first rep than a season-defining truth. If the exact same problems repeat, then the concern gains another real piece of evidence.</p>
              <p>That is how evaluation is supposed to work: <strong>observe, update, observe again.</strong></p>
              <p><Link href="/articles/how-michigan-beats-oklahoma-2026">Read the full Oklahoma preview and how-each-team-wins breakdown →</Link></p>
            </section>

            <section className="djg-final">
              <span>THE BOTTOM LINE</span>
              <h2>Don't confuse ugly with doomed.</h2>
              <p>Michigan looked bad against Western Michigan. Really bad. The Wolverines deserved the national criticism, and the offense now carries a burden of proof into Oklahoma.</p>
              <p>But Michigan still has a sophomore quarterback who finished 29th nationally in QBR as an 18-year-old. It still has an offensive coordinator whose previous offense finished top five nationally in rushing, total offense and scoring. It still has a defensive coordinator whose units repeatedly excelled in high-leverage situations. And it still has a head coach with 177 Utah wins, an undefeated season and multiple power-conference championships.</p>
              <p>The one piece of 2026 evidence we possess also contains a major positive: Michigan's defense allowed 221 yards and zero touchdowns despite a game script designed to break it.</p>
              <p>Maybe the offense does not improve. Maybe Underwood does not make the expected leap. Maybe Beck's Utah success does not translate. Maybe Whittingham ultimately proves to be the wrong hire.</p>
              <p>Those outcomes are possible.</p>
              <p><strong>Possible is not proven.</strong></p>
              <p>After one game, we have learned enough to lower Michigan's floor. We have not learned enough to lower its ceiling nearly as far as the reaction suggests.</p>
              <div className="djg-final-line">Be concerned. Demand more. Make Michigan prove it. <em>But don't jump the gun.</em></div>
            </section>
          </div>
        </div>

        <section className="djg-sources">
          <div><span>REPORTING & DATA SOURCES</span><h2>Evidence used in this story</h2></div>
          <div className="djg-source-grid">
            {sources.map(([label, href]) => href.startsWith("/")
              ? <Link href={href} key={href}>{label}<span>→</span></Link>
              : <a href={href} rel="noreferrer" target="_blank" key={href}>{label}<span>↗</span></a>
            )}
          </div>
        </section>

        <footer className="djg-footer"><Link href="/articles">← ALL ARTICLES</Link><Link href="/analytics">EXPLORE ANALYTICS →</Link></footer>
      </div>
    </article>
  );
}
