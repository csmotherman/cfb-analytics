import type {Metadata} from "next";
import Link from "next/link";
import {ArticleMobileToc} from "../../../components/ArticleMobileToc";
import {PlaycallingMatrix} from "../../../components/articles/PlaycallingMatrix";
import {PlaycallingTrendChart} from "../../../components/articles/PlaycallingTrendChart";
import {teamLogoUrl} from "../../../lib/team-assets";
import {beckAuditData} from "../../../lib/michigan/beck-audit-data";

const articleUrl="https://michiganfootballfocus.com/articles/michigan-offense-2025-playcalling-audit";
const articleImage="https://michiganfootballfocus.com/images/articles/jason-beck.png";
const socialDescription="A play-by-play audit of Michigan's 2025 offense against Jason Beck's Utah — what worked, what didn't, and what should transfer when Beck installs his own system in 2026.";

export const metadata:Metadata={
  title:"Michigan's 2025 Offense, Down by Down — Then the Offense Replacing It",
  description:socialDescription,
  openGraph:{type:"article",url:articleUrl,siteName:"Michigan Football Focus",title:"Michigan's 2025 Offense, Down by Down — Then the Offense Replacing It",description:socialDescription,images:[{url:articleImage,alt:"Jason Beck"}]},
  twitter:{card:"summary_large_image",title:"Michigan's 2025 Offense, Down by Down — Then the Offense Replacing It",description:socialDescription,images:[articleImage]}
};

const sections=[
  ["worked","What worked, what didn't"],
  ["trend","Better or worse?"],
  ["beck","What Beck brings"],
  ["watch","What to watch"]
] as const;

const sources=[
  ["Detroit News: Chip Lindsey headed to Missouri","https://www.detroitnews.com/story/sports/college/university-michigan/2025/12/21/michigan-football-offensive-coordinator-chip-lindsey-headed-to-missouri/87872359007/"],
  ["ESPN: Lindsey leaves Michigan for Missouri OC job","https://www.espn.com/college-football/story/_/id/47379892/chip-lindsey-leaves-michigan-missouri-offensive-coordinator-job"],
  ["mgoblue: Jason Beck named Michigan OC","https://mgoblue.com/news/2026/1/2/football-jason-beck-named-michigans-sanford-robertson-offensive-coordinator"],
  ["Deseret News: Beck on Utah's offense and QB uncertainty","https://www.deseret.com/sports/2025/10/28/jason-beck-thoughts-on-utahs-offense-devon-dampier-byrd-ficklin/"],
  ["KSL: Beck's positionless offensive scheme","https://www.ksl.com/article/51375990/jason-becks-positionless-offensive-scheme-and-how-it-can-pickle-the-defense"],
  ["SI: Comparing Devon Dampier to Bryce Underwood","https://www.si.com/college/michigan/football/comparing-devon-dampier-bryce-underwood-will-michigan-actually-run-its-qb"],
  ["SI: Beck plans to use Underwood's legs as a weapon","https://www.si.com/college/michigan/football/michigan-jason-beck-use-bryce-underwood-legs-weapon-2026"],
  ["CBS Sports: Underwood named Michigan's Week 1 starter","https://www.cbssports.com/college-football/news/bryce-underwood-named-michigan-qb-prized-recruit-is-fourth-true-freshman-to-start-for-wolverines-in-week-1/"],
  ["ClickOnDetroit: Koy Detmer Jr. on Underwood's growth","https://www.clickondetroit.com/all-about-ann-arbor/2026/08/26/michigan-football-qb-coach-koy-detmer-jr-praises-bryce-underwoods-growth-ahead-of-2026-season/"]
] as const;

function pct(v:number,digits=1):string{return `${(v*100).toFixed(digits)}%`;}
function ppa(v:number):string{return `${v>=0?"+":""}${v.toFixed(2)}`;}

function Stat({value,label,detail}:{value:string;label:string;detail:string}){
  return <div className="feature-stat"><strong>{value}</strong><span>{label}</span><small>{detail}</small></div>;
}

export default function PlaycallingAuditArticle(){
  const mi=beckAuditData.michigan;
  const ut=beckAuditData.utah;

  return <article className="focus-article feature-article">
    <div className="article-reading-progress" aria-hidden="true"/>
    <div className="focus-article-shell feature-shell">
      <Link className="feature-back" href="/articles">← THE NOTEBOOK</Link>

      <header className="focus-article-hero matchup-hero">
        <img src="/images/articles/jason-beck.png" alt="Jason Beck"/>
        <div className="focus-article-hero-copy">
          <span className="focus-article-eyebrow">PLAY-BY-PLAY AUDIT · 2025 SEASON</span>
          <h1>Michigan's Offense, Down by Down</h1>
          <p className="feature-headline">The data says Michigan's passing-down and red-zone execution broke down under a true freshman quarterback. Beck's Utah tape says he's built to fix exactly that — if the scheme can adapt to a different kind of quarterback than the one it was built for.</p>
          <p className="feature-deck">Chip Lindsey called Michigan's offense for all 12 regular-season games in 2025 with true freshman Bryce Underwood at quarterback, then left for Missouri. Jason Beck called Utah's offense all season — then Michigan hired him, and Underwood is still QB1. A full play-by-play audit of what worked, what didn't, and what should actually transfer.</p>
          <div className="focus-article-meta"><span>August 27, 2026</span><span>12 MIN READ</span><span>DATA AUDIT</span></div>
        </div>
      </header>

      <section className="feature-quick-read" aria-label="Quick read">
        <div className="feature-quick-label"><span>60-SECOND READ</span><strong>The audit in four numbers.</strong></div>
        <div className="feature-stat-grid">
          <Stat value={pct(mi.redZone.pass.successRate,0)+" / "+pct(ut.redZone.pass.successRate,0)} label="RED-ZONE PASS SUCCESS" detail="Michigan / Utah"/>
          <Stat value={ppa(mi.moneyDownPassPpa)} label="MICH MONEY-DOWN PASS EPA" detail={`Utah: ${ppa(ut.moneyDownPassPpa)}`}/>
          <Stat value={pct(mi.seasonSummary.runRate,0)} label="RUN RATE, BOTH TEAMS" detail={`Utah: ${pct(ut.seasonSummary.runRate,0)} — nearly identical`}/>
          <Stat value="9-4" label="MICHIGAN 2025 RECORD" detail="9-3 under Lindsey, plus a bowl loss"/>
        </div>
      </section>

      <ArticleMobileToc sections={sections}/>

      <div className="feature-reading-layout">
        <aside className="feature-toc">
          <span>IN THIS AUDIT</span>
          <nav>{sections.map(([id,label],index)=><a href={`#${id}`} key={id}><b>{String(index+1).padStart(2,"0")}</b>{label}</a>)}</nav>
          <Link href="/analytics/offense?year=2025">2025 OFFENSE DATA →</Link>
        </aside>

        <div className="focus-article-body feature-body">
          <p className="focus-article-lede">Michigan's full-season 2025 offense averaged 27.5 points per game and finished 9-4. But that number blends two different play-callers: Chip Lindsey ran the offense for all 12 regular-season games before leaving for Missouri's coordinator job in late December, and Steve Casula, promoted from tight ends coach, called the one-off Citrus Bowl loss to Texas as interim OC. Jason Beck ran Utah's offense the entire 2025 season — 11 wins, 2 losses, 39.5 points a game — before Michigan hired him as its own 2026 offensive coordinator. Same quarterback, new play-caller. This is what the play-by-play actually says changes.</p>

          <div className="feature-thesis"><span>THE AUDIT IN ONE SENTENCE</span><strong>Michigan's offense wasn't broken by identity — run rate, standard-down execution, even overall success rate were within a few points of Beck's Utah. It broke down in exactly two situations, and Beck's own tape says he already knows how to fix them.</strong></div>

          <section id="worked" className="feature-story-section">
            <div className="feature-section-number">01</div><div className="feature-section-kicker">SUCCESS RATE V1</div>
            <h2>What worked, what didn't</h2>
            <p>Every offensive snap sorted by down and distance-to-go, split by what was actually called. <strong>Short = 1–3 yards to go, Medium = 4–7, Long = 8+.</strong> Faded cells have fewer than 15 plays — too thin a sample to read much into, since 1st down is almost always 1st-and-10.</p>

            <div className="pc-matrix-wrap">
              <PlaycallingMatrix title="Michigan · Lindsey (12 games)" accent="mi" cells={mi.matrix}/>
              <PlaycallingMatrix title="Utah · Beck (12 games)" accent="ut" cells={ut.matrix}/>
            </div>

            <p>Read down the 3rd/4th-down row on Michigan's side: the run game was excellent in short yardage (85% success) and next to nothing worked once the down got long — 7% on the ground, 19% through the air. That's a true freshman quarterback and a first-year staff running out of answers exactly when the offense fell behind schedule — the same "passing-down" window Utah's offense treated as a real strength (Section 03).</p>

            <div className="feature-versus-stat">
              <div><small>MICHIGAN RUN, 3RD/4TH &amp; MEDIUM</small><strong>66.7%</strong><span>success rate — called only 41% of the time</span></div>
              <b>VS</b>
              <div><small>MICHIGAN PASS, 3RD/4TH &amp; MEDIUM</small><strong>46.7%</strong><span>success rate — called 59% of the time anyway</span></div>
            </div>
            <p>That's the one clear case in this whole grid where the tendency ran against the evidence instead of with it — Utah, in the identical bucket, leaned the correct direction. It's one cell out of nine, not a pattern of bad decisions; most of Michigan's 2025 calls already matched what the data says worked. But it's exactly the kind of small, fixable inefficiency a new play-caller with a full off-season to install his own system should be able to clean up.</p>
          </section>

          <section id="trend" className="feature-story-section">
            <div className="feature-section-number">02</div><div className="feature-section-kicker">GAME BY GAME</div>
            <h2>Did the play-calling get better or worse?</h2>
            <p>All 13 Michigan games in order, success rate by game. The dashed line marks where Lindsey's tape ends and Casula's one interim start begins. The flat line is Utah's full-season average under Beck, for scale.</p>

            <div className="pc-trend-legend">
              <span><i style={{background:"#ffcb05"}}/>Overall success rate</span>
              <span><i style={{background:"var(--pc-pass)"}}/>Passing-down success rate</span>
              <span><i style={{background:"#62798c",opacity:.6}}/>Utah 2025 average (Beck)</span>
            </div>
            <div className="pc-trend-shell"><PlaycallingTrendChart games={mi.trend} utahAvg={ut.seasonSummary.successRate}/></div>

            <p>That third spike — Central Michigan, week 3, Michigan's best game of the season on nearly every measure here — is worth a second look. Per contemporaneous reporting, Michigan hadn't let Underwood run much before that game, and Central Michigan was the one game then-head coach Sherrone Moore missed due to suspension; Underwood carried it nine times for 114 yards and two touchdowns that day. One game, against a lighter opponent, isn't proof the previous staff was wrong to be cautious with a true freshman. But it's a real, sourced data point that Michigan had more offense available than it usually called.</p>

            <div className="feature-data-list">
              <span>1st half passing-down success <b>{pct(mi.firstHalfSummary.passingDownSuccessRate,1)}</b></span>
              <span>2nd half passing-down success <b>{pct(mi.secondHalfSummary.passingDownSuccessRate,1)}</b></span>
              <span>1st half red-zone TD rate <b>{pct(mi.firstHalfSummary.redZoneTouchdownRate,1)}</b></span>
              <span>2nd half red-zone TD rate <b>{pct(mi.secondHalfSummary.redZoneTouchdownRate,1)}</b></span>
              <span>1st half 3rd-down conversion <b>{pct(mi.firstHalfSummary.thirdDownConversionRate,1)}</b></span>
              <span>2nd half 3rd-down conversion <b>{pct(mi.secondHalfSummary.thirdDownConversionRate,1)}</b></span>
            </div>
            <p>There's no single verdict, and that's the honest read: passing-down success barely moved, third-down conversion actually jumped, and red-zone touchdown rate fell hard as the season went on and the schedule got tougher — the back half includes a trip through an Ohio State defense that was elite all year. What's consistent is that Michigan's passing-down and red-zone execution never reliably separated from the opponent in front of it. That's what a true freshman's season looks like game to game, more than it's a program finding its footing.</p>

            <div className="feature-pullquote">In the one game Casula called as interim — the Citrus Bowl vs. Texas — Michigan passed on 56% of its snaps, the most pass-heavy game of the season, and passing-down success cratered to 16.7%.</div>
          </section>

          <section id="beck" className="feature-story-section">
            <div className="feature-section-number">03</div><div className="feature-section-kicker">THE COMPARISON</div>
            <h2>What Beck brings</h2>
            <p>Same season, same classifiers, Utah's offense instead. Both teams ran the ball on almost exactly the same share of snaps — {pct(mi.seasonSummary.runRate,0)} Michigan, {pct(ut.seasonSummary.runRate,0)} Utah. That's the first thing worth knowing: this isn't a run-more-or-pass-more story. Beck's offense is built run-first and RPO-heavy by design, and Beck has described his approach as "positionless" — built around what a given roster's best players can actually do, not a fixed playbook.</p>

            <div className="feature-matchup-card">
              <div><img src={teamLogoUrl(130,64)} alt=""/><span>MICHIGAN</span><strong>{mi.seasonSummary.pointsPerGame.toFixed(1)}</strong><small>PPG UNDER LINDSEY</small></div>
              <div className="feature-matchup-center"><span>RED-ZONE TD RATE</span><b>−19pt</b><small>MICHIGAN'S GAP TO UTAH</small></div>
              <div><img src={teamLogoUrl(254,64)} alt=""/><span>UTAH</span><strong>{ut.seasonSummary.pointsPerGame.toFixed(1)}</strong><small>PPG UNDER BECK</small></div>
            </div>

            <p>Beck himself has said passing <em>volume</em> — not rushing — was Utah's biggest offensive shortfall in 2025: "passing yardage per game is the only major offensive stat that Utah doesn't rank at or near the top of the Big 12 in." That matters, because the gap below isn't "Utah is a great passing team and Michigan isn't." It's narrower and more useful: an offense that's below-average at throwing overall still found sharper answers than Michigan's in the two highest-leverage moments of a drive.</p>

            <h3 style={{font:"800 22px var(--display)",color:"#fff",margin:"36px 0 14px"}}>Finding the touchdown</h3>
            <p>Both offenses were essentially tied on red-zone <strong>success rate</strong> — gaining enough to stay on schedule once inside the 20. They were not tied on red-zone <strong>touchdown rate</strong>. The difference is what happened when each team chose to throw down there.</p>
            <div className="feature-two-downs">
              <div><small>MICHIGAN RED-ZONE PASS</small><strong>{pct(mi.redZone.pass.successRate,0)}</strong><span>success · {ppa(mi.redZone.pass.avgPpa)} EPA/play</span></div>
              <div><small>UTAH RED-ZONE PASS</small><strong>{pct(ut.redZone.pass.successRate,0)}</strong><span>success · {ppa(ut.redZone.pass.avgPpa)} EPA/play</span></div>
            </div>

            <h3 style={{font:"800 22px var(--display)",color:"#fff",margin:"36px 0 14px"}}>Money downs</h3>
            <p>On 2nd-and-8+ / 3rd-and-5+ / 4th-and-5+ — downs where the defense knows a pass is more likely — Utah did lean pass somewhat more than Michigan (64% of money downs vs. 58%). But the bigger gap isn't how often each team threw. It's how well it worked when they did.</p>
            <div className="feature-versus-stat">
              <div><small>MICHIGAN</small><strong>{ppa(mi.moneyDownPassPpa)}</strong><span>EPA / passing-down pass call</span></div>
              <b>VS</b>
              <div><small>UTAH</small><strong>{ppa(ut.moneyDownPassPpa)}</strong><span>EPA / passing-down pass call</span></div>
            </div>

            <p>Both of Beck's actual 2025 quarterbacks — starter Devon Dampier and backup Byrd Ficklin — are dual-threat runners, and reporting describes the offense as built to make a defense respect the quarterback run on every snap, which is exactly what opens up these throws. Bryce Underwood, by his own position coach's description, "would rather stay in the pocket" and is "more of a pocket passer than what Dampier is" — even though he rushed for 392 yards and 6 touchdowns and forced 22 missed tackles as a true freshman, largely underused by the previous staff. Beck has said publicly he isn't trying to turn Underwood into Dampier: he wants "the system to conform to Underwood," and the only things being changed are "the things that will help Underwood be more efficient in the pass game."</p>
          </section>

          <section id="watch" className="feature-story-section feature-final-section">
            <div className="feature-section-number">04</div><div className="feature-section-kicker">THE OPEN QUESTIONS</div>
            <h2>What Michigan should watch</h2>
            <p>None of this is a guarantee. Three specific, sourced reasons the fit between Beck's system and Michigan's actual roster is still an open question heading into the 2026 opener — not a settled upgrade.</p>

            <p><strong>1. The scheme was built around a different kind of runner.</strong> Utah's 2025 quarterback room — Dampier and Ficklin — are both described as running quarterbacks first. Underwood profiles differently: 6'4", 228 pounds, and by his coaches' own description someone who "would rather stay in the pocket." He has real juice as a runner when used, but that's a different starting point than a scheme optimized for a quarterback whose first instinct is to pull it down. Beck's stated plan is to adapt the system to Underwood, not the reverse — that's the single biggest variable standing between Utah's 2025 numbers and Michigan's 2026 ones.</p>

            <p><strong>2. Beck's best personnel wrinkles were Utah-specific discoveries, not a formula.</strong> Part of what made Beck's "positionless" scheme work at Utah wasn't a scheme diagram — it was finding unusual individual fits on that specific roster: a defensive tackle who graded as one of Utah's best offensive players lining up at fullback, a tight end used at receiver, running back, and in Wildcat formations. Michigan will need its own version of that discovery process on its own roster. There's no public reporting yet on which Michigan players might fill an equivalent role — which means this specific ingredient of Utah's success is unproven at Michigan, not disproven.</p>

            <p><strong>3. The early returns are genuinely mixed, not settled.</strong> Beck's own quarterbacks coach, Koy Detmer Jr., says Underwood has made "big strides" with improved footwork and decision-making heading into 2026. But Underwood's spring game — the most recent public look at the new system before the season — was a rough one: 3-of-9 passing for 22 yards, with the staff publicly challenging him to keep working through the summer. Both things are true at once, and neither settles the question this data raises.</p>

            <div className="feature-checklist">
              <span>BOTTOM LINE</span>
              <b>The data: Michigan's 2025 offense had a specific, narrow problem — not a broad one.</b>
              <b>The research: Beck has a specific, credible plan aimed at that exact problem.</b>
              <b>The catch: it's built around adapting his scheme to a new quarterback, not porting last year's Utah playbook wholesale.</b>
            </div>

            <div className="feature-verdict">
              <span>THE VERDICT</span>
              <strong>Michigan's 2025 offense wasn't broken by scheme identity. It broke down in passing downs and the red zone — and Beck's 2025 tape shows he already solved close to that exact problem, through a run-first identity leaning on dual-threat quarterback play that doesn't map onto Underwood one-for-one.</strong>
              <p>Whether the adaptation lands by kickoff is a 2026-season question, not a 2025-data one. This audit can tell you precisely what needs to get fixed and why Beck is a reasonable bet to fix it — not whether he will.</p>
            </div>
          </section>
        </div>
      </div>

      <section className="focus-article-explore feature-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>See the full data behind this audit.</h2></div>
        <div className="focus-article-link-grid">
          <Link href="/analytics/offense?year=2025"><strong>2025 Michigan offense</strong><p>The full opponent-adjusted efficiency breakdown behind this piece.</p><span>VIEW →</span></Link>
          <Link href="/players/5141741"><strong>Bryce Underwood profile</strong><p>Underwood's freshman production and 2026 roster profile.</p><span>VIEW →</span></Link>
          <Link href="/articles/what-to-expect-michigan-offense-2026"><strong>2026 offense preview</strong><p>The bigger-picture season preview this audit digs underneath.</p><span>READ →</span></Link>
        </div>
      </section>

      <section className="focus-article-sources">
        <strong>REPORTING &amp; DATA SOURCES</strong>
        <div>{sources.map(([label,url])=><a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div>
      </section>
      <p style={{maxWidth:850,margin:"14px auto 0",color:"#62798c",fontSize:11}}>Situational splits (red zone, money downs, down/distance) are computed directly from play-by-play using this site's Success Rate v1 / Explosiveness v1 / Red-Zone v1 definitions, and can differ modestly from official box-score stats cited elsewhere on this site due to differing conventions for what counts as a red-zone trip.</p>

      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}
