import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { ArticleMobileToc } from "../../../components/ArticleMobileToc";
import { teamLogoUrl } from "../../../lib/team-assets";
import { wmu2026Recap as data, type DriveRow } from "../../../lib/michigan/wmu-2026-recap-data";
import "./article.css";

const articleUrl = "https://michiganfootballfocus.com/articles/michigan-western-michigan-2026-recap";
const socialDescription = "Success rate liked Michigan's offense. Full-value EPA doesn't — two turnovers were worth more than every other snap combined. And the defense that \"couldn't get off the field\" actually allowed −0.34 EPA/play and zero touchdowns; it just gave 5.6 expected points back on one series with two penalties, including a flag that erased a real interception.";

export const metadata: Metadata = {
  title: "Michigan vs. Western Michigan by EPA: What the Turnovers and Penalties Actually Cost",
  description: socialDescription,
  openGraph: { type: "article", url: articleUrl, siteName: "Michigan Football Focus", title: "Michigan vs. Western Michigan by EPA: What the Turnovers and Penalties Actually Cost", description: socialDescription, images: ["/images/articles/michigan-western.png"] },
  twitter: { card: "summary_large_image", title: "Michigan vs. Western Michigan by EPA: What the Turnovers and Penalties Actually Cost", description: socialDescription, images: ["/images/articles/michigan-western.png"] },
};

const sections = [
  ["gap", "Two games, one box score"],
  ["drives", "The dead middle"],
  ["field-position", "Starting in the shadow of the goal line"],
  ["penalties", "The two plays that got erased"],
  ["turnovers", "Six free points"],
  ["third-down", "Third down: 2 for 9"],
  ["epa", "EPA/play and EPA/drive"],
  ["defense", "Why didn't the defense get them off the field?"],
  ["outlook", "Is the season over?"],
] as const;

const sources = [
  ["Michigan vs. Western Michigan game hub", "/games/401858428"],
  ["College Football Data — play-by-play, gameId 401858428", "https://collegefootballdata.com"],
] as const;

function pct(v: number, digits = 1) {
  return `${(v * 100).toFixed(digits)}%`;
}

function resultLabel(result: DriveRow["result"]) {
  if (result === "TD") return "TOUCHDOWN";
  if (result === "PUNT") return "PUNT";
  if (result === "INT") return "INTERCEPTION";
  return "FUMBLE";
}

function fieldSpot(yardsToGoal: number) {
  if (yardsToGoal <= 50) return `WMU ${yardsToGoal}`;
  return `own ${100 - yardsToGoal}`;
}

function epaLabel(v: number) {
  return `${v >= 0 ? "+" : "−"}${Math.abs(v).toFixed(2)} EPA`;
}

function DriveCard({ drive }: { drive: DriveRow }) {
  const scored = drive.result === "TD";
  const turnover = drive.result === "INT" || drive.result === "FUMBLE";
  return (
    <div className={`wr-drive${scored ? " wr-drive-td" : ""}${turnover ? " wr-drive-to" : ""}`}>
      <div className="wr-drive-seq">
        <span>DRIVE</span>
        <strong>{drive.seq}</strong>
        <small>Q{drive.quarter}</small>
      </div>
      <div className="wr-drive-body">
        <div className="wr-drive-top">
          <b className="wr-drive-result">{resultLabel(drive.result)}</b>
          <span className="wr-drive-plays">{drive.plays} plays</span>
          <span className={`wr-drive-epa${drive.epa >= 0 ? " wr-drive-epa-pos" : ""}`}>{epaLabel(drive.epa)}</span>
          <span className="wr-drive-track">{fieldSpot(drive.startYardsToGoal)} → {fieldSpot(drive.deepestYardsToGoal)}</span>
        </div>
        <p>{drive.note}</p>
      </div>
    </div>
  );
}

export default function WesternMichiganRecapArticle() {
  const nonScoring = data.drives.filter((d) => d.result !== "TD");
  const neverCrossedMidfield = nonScoring.filter((d) => d.deepestYardsToGoal > 50).length;
  const compYards = (data.quarterback.completions / data.quarterback.attempts) * 100;

  return (
    <article className="focus-article feature-article wr-recap">
      <div className="article-reading-progress" aria-hidden="true" />
      <div className="focus-article-shell feature-shell">
        <Link className="feature-back" href="/articles">← THE NOTEBOOK</Link>

        <header className="focus-article-hero matchup-hero wr-hero">
          <img src="/images/articles/michigan-western.png" alt="" />
          <div className="focus-article-hero-copy">
            <span className="focus-article-eyebrow">WEEK 1 RECAP · EPA &amp; PENALTY AUDIT</span>
            <h1>What Actually Went Wrong — and Actually Didn't</h1>
            <p className="feature-headline">Forget the Hail Mary. Forget Clockgate. Run every snap through an independent EPA model and a very different, more precise story shows up on both sides of the ball.</p>
            <p className="feature-deck">Michigan's offense looked fine by success rate — until its two turnovers, priced in full value, outweigh every other snap it ran combined. Michigan's defense, the unit that "couldn't get Western off the field," actually allowed −0.34 expected points per play and zero touchdowns all game; it gave back 5.6 points on one series to two of its own penalties, one of which erased a real interception. Two units, one shared disease: elite process, undone by flags and turnovers worth 16 expected points combined.</p>
            <div className="focus-article-meta"><span>{data.kickoffLabel}</span><span>10 MIN READ</span><span>DATA AUDIT</span></div>
          </div>
        </header>

        <div className="wr-scoreboard">
          <div className="wr-scoreboard-team">
            <img src={teamLogoUrl(data.michiganTeamId, 128)} alt="Michigan" />
            <span>MICHIGAN</span>
            <strong>{data.finalScore.michigan}</strong>
          </div>
          <div className="wr-scoreboard-mid"><span>FINAL</span><b>1–0</b></div>
          <div className="wr-scoreboard-team">
            <img src={teamLogoUrl(data.opponentTeamId, 128)} alt="Western Michigan" />
            <span>WESTERN MICHIGAN</span>
            <strong>{data.finalScore.westernMichigan}</strong>
          </div>
        </div>

        <ArticleMobileToc sections={sections} />

        <div className="feature-reading-layout">
          <aside className="feature-toc">
            <span>IN THIS AUDIT</span>
            <nav>{sections.map(([id, label], index) => <a href={`#${id}`} key={id}><b>{String(index + 1).padStart(2, "0")}</b>{label}</a>)}</nav>
            <Link href="/games/401858428">GAME HUB →</Link>
          </aside>

          <div className="focus-article-body feature-body">
            <p className="focus-article-lede">A one-point win off a 47-yard touchdown as time expired is the kind of finish that swallows every other storyline. It shouldn't. Underneath the walk-off, Michigan's offense had a genuinely bad two-and-a-half quarters — and the play log says exactly why, without needing a single word about the final snap.</p>

            <section id="gap" className="feature-story-section wr-section">
              <div className="feature-section-number">01</div>
              <div className="feature-section-kicker">TWO GAMES, ONE BOX SCORE</div>
              <h2>The offense that opened the game and the offense that showed up for the next eight drives were not the same offense.</h2>
              <p>Michigan scored touchdowns on its <b>first</b> possession and its <b>last</b> possession. In between: six punts, an interception, and a fumble. That's the entire story of "Michigan couldn't do anything on offense" — it isn't a feeling, it's eight possessions in a row that produced zero points.</p>
              <div className="feature-thesis"><span>THE HEADLINE STAT</span><strong>{neverCrossedMidfield} of Michigan's {nonScoring.length} non-scoring possessions never crossed midfield.</strong></div>
              <p>Only one series — a seven-play drive in the third quarter — ever got the ball into Western Michigan territory, and it only reached the 44 before stalling. Everything else Michigan ran between the two touchdowns happened entirely on its own side of the field.</p>
            </section>

            <section id="drives" className="feature-story-section wr-section">
              <div className="feature-section-number">02</div>
              <div className="feature-section-kicker">EVERY POSSESSION</div>
              <h2>The dead middle, drive by drive.</h2>
              <p>Here is every Michigan offensive possession in order, with each drive's expected-points value (EPA) attached — the independent, from-scratch model explained in full in section 07. The pattern isn't one bad quarter — it's a bad half sandwiched between two scoring drives, with the same three problems (field position, penalties, turnovers) showing up over and over, and only three of ten drives grading positive.</p>
              <div className="wr-drive-list">
                {data.drives.map((drive) => <DriveCard drive={drive} key={drive.seq} />)}
              </div>
            </section>

            <section id="field-position" className="feature-story-section wr-section">
              <div className="feature-section-number">03</div>
              <div className="feature-section-kicker">THE HIDDEN OPPONENT</div>
              <h2>Michigan wasn't just playing Western Michigan. It was playing the field.</h2>
              <p>Michigan's average starting field position was its own <b>{data.fieldPosition.michiganAvgStart}-yard line</b>. Western Michigan's was its own <b>{data.fieldPosition.opponentAvgStart}</b> — a 16-yard swing on every single possession. Three different Michigan drives started inside the 10: the 8, the 7, and the 2. Every one of those is a possession that needs a nearly perfect series just to reach midfield, before the offense has to do anything difficult at all.</p>
              <div className="feature-versus-stat">
                <div><small>MICHIGAN AVG. START</small><strong>Own {data.fieldPosition.michiganAvgStart}</strong><span>10 possessions</span></div>
                <b>VS</b>
                <div><small>WESTERN MICHIGAN AVG. START</small><strong>Own {data.fieldPosition.opponentAvgStart}</strong><span>11 possessions</span></div>
              </div>
              <p>That gap isn't the offense's fault, but it is the offense's problem. Long fields amplify every other issue on this list: a penalty that costs 10 yards from your own 20 is a survivable inconvenience; the same penalty from your own 8 turns a manageable drive into a near-impossible one.</p>
            </section>

            <section id="penalties" className="feature-story-section wr-section">
              <div className="feature-section-number">04</div>
              <div className="feature-section-kicker">SELF-INFLICTED</div>
              <h2>Michigan's two biggest offensive plays of the day didn't count.</h2>
              <p>Michigan drew five offensive penalties. Most were the ordinary cost of doing business. Two of them erased the two most explosive plays the offense produced all game:</p>
              <div className="wr-callout-grid">
                <div className="wr-callout-card">
                  <span>DRIVE 2 · 3RD-AND-5 · −2.45 EPA</span>
                  <strong>16-yard completion, wiped</strong>
                  <p>Underwood hit JJ Buchanan for 16 yards — a clean third-down conversion. An Illegal Formation flag brought it back. Running the same model used for the EPA section below on both branches — the actual replayed 3rd-and-10 versus the first down that should have existed — this one flag cost Michigan <b>2.45 expected points</b>. The replayed down stalled two plays later and Michigan punted.</p>
                </div>
                <div className="wr-callout-card">
                  <span>DRIVE 7 · 1ST-AND-10 · −2.22 EPA</span>
                  <strong>20-yard run, wiped</strong>
                  <p>Broderick Kuzdzal broke a 20-yard run that would have reached the Western Michigan 30. A holding call on Underwood, of all people, brought it back. Same model, same accounting: <b>2.22 expected points</b> erased. The drive still ended in a punt.</p>
                </div>
              </div>
              <p>These aren't ordinary 5- and 10-yard setbacks — together they cost Michigan's offense <b>4.67 expected points</b>, essentially a touchdown's worth of value, from two flags alone. That's the difference between a third-down conversion that keeps a drive alive and a punt, and between a first-and-goal-in-range field position and another long field. Add in a penalty that turned a stuffed run into 2nd-and-15, and a substitution penalty on the drive that ended in a fumble, and Michigan's offense fought its own equipment manager as much as it fought Western Michigan's defense.</p>
            </section>

            <section id="turnovers" className="feature-story-section wr-section">
              <div className="feature-section-number">05</div>
              <div className="feature-section-kicker">GIVE AND NEVER TAKE</div>
              <h2>Both Michigan turnovers turned directly into Western Michigan points.</h2>
              <p>Michigan gave the ball away twice and got nothing back — Western Michigan lost two fumbles of its own but recovered both. A <b>−2 turnover margin</b> in a game decided by one point is about as costly as a stat line gets, and this one was direct: both giveaways set up short fields that Western Michigan converted immediately into points.</p>
              <div className="wr-callout-grid">
                {data.turnovers.map((t) => (
                  <div className="wr-callout-card wr-callout-danger" key={t.drive}>
                    <span>DRIVE {t.drive} · {t.type.toUpperCase()} · {epaLabel(t.epa)}</span>
                    <strong>{t.detail}</strong>
                    <p>{t.result}</p>
                  </div>
                ))}
              </div>
              <p>Priced by the same expected-points model as everything else on this page, the interception cost Michigan <b>3.37 points</b> and the fumble cost <b>2.35</b> — <b>5.72 combined</b>. That single number explains almost the entire gap between how good Michigan's offense looked on clean snaps and how bad it looked in the final tally: see section 07.</p>
              <div className="feature-pullquote">Half of Western Michigan's 12 points came directly off Michigan giveaways.</div>
            </section>

            <section id="third-down" className="feature-story-section wr-section">
              <div className="feature-section-number">06</div>
              <div className="feature-section-kicker">STAYING ON SCHEDULE</div>
              <h2>Michigan couldn't sustain a drive without a mistake bailing it out.</h2>
              <p>Strip out the game-winning final drive and the one first down Western Michigan handed Michigan with a pre-snap penalty, and Michigan converted <b>{data.thirdDown.realConversions} of {data.thirdDown.realAttempts}</b> real third downs — {pct(data.thirdDown.realConversions / data.thirdDown.realAttempts, 0)}. The box-score version, counting everything, still only reads {data.thirdDown.boxScoreConversions} of {data.thirdDown.boxScoreAttempts} ({pct(data.thirdDown.boxScoreConversions / data.thirdDown.boxScoreAttempts, 0)}). Six of Michigan's ten possessions ended in a punt. That's not an offense that got a couple of unlucky breaks — it's an offense that couldn't move the sticks on its own for most of the afternoon.</p>
            </section>

            <section id="epa" className="feature-story-section wr-section">
              <div className="feature-section-number">07</div>
              <div className="feature-section-kicker">THE NUMBER THAT ACTUALLY DECIDES GAMES</div>
              <h2>Success rate liked Michigan's offense. Full-value EPA doesn't.</h2>
              <p>Run this site's locked success-rate and explosive-play classifiers and Michigan's offense grades out ahead of Western Michigan's on a snap-to-snap basis — a better floor, more chunk plays, more yards per successful play:</p>
              <div className="stat-compare">
                <div className="stat-compare-key">
                  <span><i style={{ "--dot": "#ffcb05" } as CSSProperties} />Michigan</span>
                  <span><i style={{ "--dot": "#5b9bd8" } as CSSProperties} />Western Michigan</span>
                </div>
                {data.efficiency.map((row) => {
                  const max = Math.max(row.michigan, row.opponent) * 1.15;
                  const miPct = (row.michigan / max) * 100;
                  const wmuPct = (row.opponent / max) * 100;
                  const fmt = (v: number) => (row.unit === "pct" ? pct(v, 1) : v.toFixed(1));
                  return (
                    <div className="stat-compare-row" key={row.metric}>
                      <div className="stat-compare-label">{row.metric}</div>
                      <div className="stat-compare-bar-wrap">
                        <div className="stat-compare-track-bg"><div className="stat-compare-fill" style={{ "--pct": `${miPct}%`, "--fill": "#ffcb05" } as CSSProperties} /></div>
                        <b>{fmt(row.michigan)}</b>
                      </div>
                      <div className="stat-compare-bar-wrap">
                        <div className="stat-compare-track-bg"><div className="stat-compare-fill" style={{ "--pct": `${wmuPct}%`, "--fill": "#5b9bd8" } as CSSProperties} /></div>
                        <b>{fmt(row.opponent)}</b>
                      </div>
                    </div>
                  );
                })}
              </div>
              <p>Success rate is a floor metric — it rewards staying on schedule and doesn't care how a snap ends once it's "successful." It also doesn't know what a turnover is worth. That's exactly where this gets interesting. Built entirely on this site's independent EPA v2 model — trained from scratch on 1,544,257 plays across 11 seasons (2014–2025), never on CFBD's own ppa field, the same engine that grades every fourth-down decision elsewhere on Michigan Football Focus — and priced play by play, Michigan's offense flips sign the moment its two turnovers are included at full value:</p>
              <div className="feature-two-downs">
                <div>
                  <small>CLEAN SNAPS ONLY (46 PLAYS)</small>
                  <strong>+{data.epaSummary.michiganOffenseCleanSnapsOnly.epaPerPlay.toFixed(3)}</strong>
                  <span>EPA/play — this is the number that made success rate look good.</span>
                </div>
                <div>
                  <small>EVERY SNAP, INCL. BOTH TURNOVERS (48 PLAYS)</small>
                  <strong>{data.epaSummary.michiganOffense.epaPerPlay.toFixed(3)}</strong>
                  <span>EPA/play — {data.epaSummary.michiganOffense.epaPerDrive.toFixed(2)} EPA/drive across all 10 possessions.</span>
                </div>
              </div>
              <p>Two plays — one interception, one fumble — are worth more in expected points than all 46 other Michigan snaps combined were worth in the other direction. That's not a knock on the offensive process; it's exactly why the site grades fourth downs and fumbles on EPA instead of success rate in the first place. A metric that can't see a turnover coming isn't measuring the thing that actually decides one-score games.</p>
              <p>Only one sack allowed all game. Underwood finished {data.quarterback.completions} of {data.quarterback.attempts} ({compYards.toFixed(0)}%) for {data.quarterback.passYards} yards, one touchdown and the one interception — plus a team-leading {data.quarterback.carries} carries for {data.quarterback.rushYards} yards and a rushing score. The offensive line wasn't overwhelmed and the quarterback wasn't running for his life; the value problem was decision and ball security on a small number of snaps, not the other 46.</p>
            </section>

            <section id="defense" className="feature-story-section wr-section">
              <div className="feature-section-number">08</div>
              <div className="feature-section-kicker">THE OTHER SIDE OF THE BALL</div>
              <h2>The defense didn't get gashed. It got flagged.</h2>
              <p>Run the same EPA model on every Western Michigan snap — which is really Michigan's defense allowing or preventing value — and the per-play picture is not close to "the defense couldn't get them off the field." It's closer to the opposite:</p>
              <div className="feature-versus-stat">
                <div><small>MICHIGAN OFFENSE</small><strong>{data.epaSummary.michiganOffense.epaPerPlay.toFixed(2)}</strong><span>EPA/play, {data.epaSummary.michiganOffense.plays} snaps</span></div>
                <b>VS</b>
                <div><small>MICHIGAN DEFENSE ALLOWED</small><strong>{data.epaSummary.michiganDefenseAllowed.epaPerPlay.toFixed(2)}</strong><span>EPA/play, {data.epaSummary.michiganDefenseAllowed.plays} snaps</span></div>
              </div>
              <p>At <b>−{Math.abs(data.epaSummary.michiganDefenseAllowed.epaPerPlay).toFixed(2)} EPA allowed per play</b> and <b>−{Math.abs(data.epaSummary.michiganDefenseAllowed.epaPerDrive).toFixed(2)} EPA allowed per drive</b>, Michigan's defense had one of the more dominant per-snap performances you'll see in a single game — the average Western Michigan possession left them worse off, in expected-points terms, than when it started. Western Michigan ran <b>{data.epaSummary.michiganDefenseAllowed.plays} offensive snaps to Michigan's {data.epaSummary.michiganOffense.plays}</b> — 19 more, across just one extra possession. That volume gap, not a per-play breakdown, is the real source of the "the defense could never get off the field" feeling. It's a time-of-possession illusion sitting on top of a genuinely dominant per-snap number.</p>
              <p>The clearest proof: Western Michigan's longest drive of the day — <b>{data.longestWmuDrive.plays} plays, {data.longestWmuDrive.yards} yards</b>, third quarter, ending in a field goal — was still a <b>{epaLabel(data.longestWmuDrive.epa)}</b> possession. Nineteen snaps, three points, and Michigan's defense still won it by the numbers that matter. Bend, don't break: Western Michigan reached scoring range four times all game and left with four field goals — zero touchdowns allowed.</p>
              <p>Money downs back it up. Western Michigan converted just <b>{data.westernMichiganThirdDown.conversions} of {data.westernMichiganThirdDown.attempts}</b> third downs ({pct(data.westernMichiganThirdDown.conversions / data.westernMichiganThirdDown.attempts, 0)}) against Michigan — a losing number for the offense, ten stops out of seventeen tries for the defense.</p>
              <div className="feature-thesis"><span>WHERE IT ACTUALLY WENT WRONG</span><strong>One Western Michigan possession, two Michigan defensive penalties, {(data.defensivePenalties[0].epaNegated + data.defensivePenalties[1].epaNegated).toFixed(2)} expected points gifted away.</strong></div>
              <div className="wr-callout-grid">
                {data.defensivePenalties.map((p) => (
                  <div className="wr-callout-card wr-callout-danger" key={p.type}>
                    <span>{p.drive.toUpperCase()} · {epaLabel(p.epaNegated)} TO WMU</span>
                    <strong>{p.type}</strong>
                    <p>{p.detail}</p>
                  </div>
                ))}
              </div>
              <p>The first one is the whole story in miniature: Jyaire Hill actually intercepted the pass. Michigan's defense earned the exact takeaway this article's offense section spent so much time wishing for — and a pass-interference flag took it away and handed Western Michigan a fresh set of downs instead, worth roughly {data.defensivePenalties[0].epaNegated.toFixed(1)} expected points by itself. A personal foul on the very next snap piled on {data.defensivePenalties[1].epaNegated.toFixed(1)} more. And the defense <b>still forced a punt</b> on that possession anyway. That's not a unit getting outplayed. That's a genuinely elite defensive performance with two self-inflicted holes in it — the exact same disease as the offense, on the other side of the ball.</p>
            </section>

            <section id="outlook" className="feature-story-section wr-section feature-final-section">
              <div className="feature-section-number">09</div>
              <div className="feature-section-kicker">WHAT TO EXPECT GOING FORWARD</div>
              <h2>Is the season over? No. But this game is a warning, not a fluke.</h2>
              <p>Michigan is 1-0. One point separated a clean win from a season-opening loss to a MAC team, and by EPA, both units actually graded out well on the snaps that were just football — Michigan's offense was fine on 46 of 48 plays, and its defense was flatly dominant on a per-snap basis (−0.34 EPA/play allowed) while giving up zero touchdowns all game. The difference wasn't talent, scheme, or either line getting physically beaten. It was two Michigan offensive turnovers worth 5.72 expected points, two Michigan offensive penalties worth another 4.67, and two Michigan defensive penalties on one series worth 5.61 more — north of 16 expected points self-inflicted across both sides of the ball, in a game decided by one. Those are correctable problems. They are not the same as being outclassed.</p>
              <p>That's also exactly why this game can't be waved off as one weird night that ends the moment the highlight of Buchanan's touchdown stops trending. Western Michigan is a MAC opponent that punted the ball well and settled for four field goals instead of touchdowns. A Big Ten defense does not do Michigan the same favors. It converts a Michigan interception or fumble into seven points instead of three, and a Big Ten offense does not let a wiped-out interception and a free personal-foul first down turn into just a punt the way Western Michigan's drive did. Run this exact mistake profile — turnovers, backbreaking penalties on both sides of the ball, a rash of stalled third downs — against a real conference opponent, and 13-12 becomes a loss.</p>
              <div className="feature-checklist">
                <span>WHAT TO WATCH NEXT</span>
                <b>Pre-snap discipline in no-huddle sets on offense — three of Michigan's five offensive penalties came out of hurry-up shotgun looks.</b>
                <b>Ball security on Underwood's scrambles and designed runs, given he's already the team's leading rusher through one game.</b>
                <b>Discipline on the back end of the defense — the pass-interference call that wiped out a real interception is the kind of penalty that turns a takeaway into a touchdown drive against better competition.</b>
                <b>Whether the offense can sustain a drive without a penalty or a mistake bailing it out — 2-for-9 on real third downs has to improve fast.</b>
              </div>
              <div className="feature-verdict">
                <span>THE VERDICT</span>
                <strong>This wasn't a talent problem on either side of the ball. It was a discipline problem — and discipline problems either get fixed in practice or they get exposed by an opponent that doesn't hand back the free possessions and free stops Western Michigan did.</strong>
                <p>The underlying value says both of Michigan's units have real quality: a positive-EPA offense on clean snaps, and a defense allowing negative EPA on nearly every snap it played, with zero touchdowns surrendered. The scoreboard says a combined six self-inflicted plays were worth more than 16 expected points in the wrong direction. Both things are true, and the second one is the one that has to change before Big Ten play starts mattering.</p>
              </div>
            </section>
          </div>
        </div>

        <section className="focus-article-explore feature-explore">
          <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>Go from the recap to the underlying data.</h2></div>
          <div className="focus-article-link-grid">
            <Link href="/games/401858428"><strong>Michigan vs. Western Michigan game hub</strong><p>Full game data, model comparison and market context.</p><span>OPEN GAME HUB →</span></Link>
            <Link href="/articles/michigan-western-michigan-2026-preview"><strong>The Week 1 preview</strong><p>What the model and the roster-continuity research said before kickoff.</p><span>READ →</span></Link>
            <Link href="/articles/what-to-expect-michigan-offense-2026"><strong>2026 offense season preview</strong><p>The bigger-picture projection behind Jason Beck's offense.</p><span>READ →</span></Link>
          </div>
        </section>

        <section className="focus-article-sources">
          <strong>REPORTING &amp; DATA SOURCES</strong>
          <div>{sources.map(([label, url]) => <a href={url} rel={url.startsWith("http") ? "noreferrer" : undefined} target={url.startsWith("http") ? "_blank" : undefined} key={url}>{label} ↗</a>)}</div>
        </section>

        <div className="wr-method-note">
          <strong>METHOD NOTE</strong>
          <p>Drive results, penalty text, third-down outcomes and turnover detail are read from the canonical play log's own flags (isPenalty, isTurnover, hasNoPlayContext, eventSubtype) for gameId 401858428. Field position, success rate, explosive-play rate and points-per-opportunity use this site's locked field-position-v1, success-v1 and explosiveness-v1 definitions from the canonical 2026 team-game dataset. "Real" third downs exclude Michigan's final, game-winning drive and one first down awarded by a Western Michigan pre-snap penalty rather than a Michigan snap.</p>
          <p>EPA figures use this site's independent, from-scratch EPA v2 research model (epa-v2-research-next-score: realized next-score-before-halftime value, never trained on CFBD's ppa field) — the same model that grades every fourth-down decision elsewhere on Michigan Football Focus. Fit on 1,544,257 plays across 11 seasons (2014–2025, excluding 2020) and applied to every state-eligible snap of this game, including turnover rows, which the model prices directly rather than excluding. "EPA negated by a penalty" holds the pre-snap state fixed and compares the expected-points value of the actual down/distance/field position that resulted against the hypothetical one that would have resulted had the penalty not been called. This is retrospective research-grade grading, not a live win-probability model, and it is not part of this repo's locked production metric contract.</p>
        </div>

        <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
      </div>
    </article>
  );
}
