import type { Metadata } from "next";
import Link from "next/link";
import { ArticleMobileToc } from "../../../components/ArticleMobileToc";
import "../dont-jump-the-gun-michigan-football-2026/article.css";

const articleUrl = "https://michiganfootballfocus.com/articles/how-michigan-beats-oklahoma-2026";
const socialDescription = "Oklahoma's defense graded #2 in the country last season. Michigan needed a walk-off touchdown to beat a MAC team. Here's how each team actually wins Saturday, and the metrics underneath both storylines.";

export const metadata: Metadata = {
  title: "How Michigan Beats Oklahoma — and How Oklahoma Makes Sure It Doesn't",
  description: socialDescription,
  openGraph: {
    type: "article",
    url: articleUrl,
    siteName: "Michigan Football Focus",
    title: "How Michigan Beats Oklahoma — and How Oklahoma Makes Sure It Doesn't",
    description: socialDescription,
    images: ["/og.png"],
  },
  twitter: {
    card: "summary_large_image",
    title: "How Michigan Beats Oklahoma — and How Oklahoma Makes Sure It Doesn't",
    description: socialDescription,
    images: ["/og.png"],
  },
};

const sections = [
  ["baseline", "The baseline nobody's talking about"],
  ["week1", "Two openers, two different tapes"],
  ["michigan", "How Michigan can win"],
  ["oklahoma", "How Oklahoma wins"],
  ["metrics", "The underlying metrics"],
  ["bottom-line", "The bottom line"],
] as const;

const sources = [
  ["Michigan vs. Oklahoma game preview & data", "/articles/michigan-oklahoma-2026-preview"],
  ["Michigan vs. Oklahoma game hub", "/games/401856679"],
  ["4 players to watch: Oklahoma vs. Michigan (Yahoo Sports)", "https://sports.yahoo.com/articles/4-players-watch-oklahoma-takes-120215933.html"],
  ["Way Too Early Michigan Opponent Preview: Week 2 vs. Oklahoma (SI)", "https://www.si.com/college/michigan/football/way-too-early-michigan-football-opponent-preview-week-2-vs-oklahoma"],
  ["Oklahoma vs. Michigan: market overreaction in favor of the Sooners (NBC Sports)", "https://www.nbcsports.com/watch/college-football/oklahoma-vs-michigan-preview-market-overreaction-in-favor-of-sooners"],
  ["Oklahoma vs. Michigan odds tracker (Action Network)", "https://www.actionnetwork.com/ncaaf-game/oklahoma-michigan-score-odds-september-12-2026/287974"],
  ["Don't Jump the Gun: why Michigan is in a better spot than it looks", "/articles/dont-jump-the-gun-michigan-football-2026"],
] as const;

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

export default function HowMichiganBeatsOklahomaArticle() {
  return (
    <article className="focus-article dont-jump">
      <div className="focus-article-shell djg-shell">
        <Link className="djg-back" href="/articles">← THE NOTEBOOK</Link>

        <header className="djg-hero">
          <div className="djg-hero-shade" />
          <div className="djg-hero-copy">
            <span className="djg-eyebrow">WEEK 2 · GAME PREVIEW</span>
            <h1>HOW MICHIGAN BEATS<br /><em>OKLAHOMA.</em></h1>
            <p className="djg-headline">And how Oklahoma makes sure it doesn't.</p>
            <p className="djg-deck">Oklahoma's defense graded as the #2 opponent-adjusted unit in the country last season. Michigan needed a 47-yard touchdown as time expired just to beat a MAC team at home. Both facts are true. Only one of them is really about football quality — the other is about one bad Saturday. Here's how each team actually wins on Sept. 12, and the metrics that separate signal from noise.</p>
          </div>
        </header>

        <section className="djg-thesis-board" aria-label="Week 2 thesis">
          <div className="djg-thesis-kicker"><span>THE THESIS</span><b>This collapses to one question: can Michigan's offense find answers against the best defense it will see all year?</b></div>
          <h2>The 2025 baseline says a 3-point game. The market says Oklahoma by 5.5 to 6.5. Both are reacting to real evidence.</h2>
          <div className="djg-signal-grid">
            <EvidenceCard label="OKLAHOMA DEFENSE COMPOSITE" value="#2" detail="Opponent-adjusted, 2025 season — the standard Michigan's offense has to clear." />
            <EvidenceCard label="OKLAHOMA OFFENSE COMPOSITE" value="#76" detail="The unit that has to prove Week 1's 51-0 over UTEP wasn't just about the opponent." />
            <EvidenceCard label="WEEK 1 FINAL SCORES" value="51-0 / 13-12" detail="Oklahoma routed UTEP. Michigan needed a walk-off score to beat a MAC team by one." />
            <EvidenceCard label="MARKET SWING" value="8-9 pts" detail="From Michigan -2.5 preseason to Oklahoma -5.5/-6.5 now — almost entirely a Week 1 reaction." />
          </div>
        </section>

        <ArticleMobileToc sections={sections} />

        <div className="djg-reading-layout">
          <aside className="djg-toc">
            <span>IN THIS STORY</span>
            <nav>{sections.map(([id, label], index) => <a href={`#${id}`} key={id}><b>{String(index + 1).padStart(2, "0")}</b>{label}</a>)}</nav>
            <Link href="/articles/michigan-oklahoma-2026-preview">SEE THE FULL DATA PREVIEW →</Link>
          </aside>

          <div className="djg-body">
            <p className="djg-lede">This was supposed to be close entering the season. By the site's own validated model, it still is — a 3.2-point overall composite edge for Michigan, not a blowout in either direction. What's changed since is Week 1: Oklahoma looked like the team its composite ranking said it was, and Michigan didn't. That's a real signal. It is not the whole story.</p>

            <section id="baseline" className="djg-section">
              <SectionHead number="01" kicker="THE BASELINE NOBODY'S TALKING ABOUT" title="Oklahoma's calling card is defense. Michigan's is offense. They're about to collide directly." />
              <p>Strip away both Week 1 results and go back to the repository's schedule-adjusted 2025 model. Michigan's offense finished #19 nationally — 49.0% rush success (#4), 46.8% overall success rate (#19), 6.55 yards per play (#21). Oklahoma's defense finished #2 — 32.1% success rate allowed (#1), 32.0% rush success allowed (#1), 4.20 yards per play allowed (#3).</p>
              <p>Flip it around and the gap narrows. Oklahoma's offense was a middling #76 nationally in 2025 — 41.7% success rate, 40.9% rush success, neither one inside the top 50. Michigan's defense, while good, wasn't dominant by comparison: #58 in success rate allowed, #47 against the run.</p>
              <div className="djg-two-paths">
                <div><span>WHAT THE COMPOSITE SAYS</span><strong>Michigan's offense vs. Oklahoma's defense is the swing matchup of the whole game.</strong></div>
                <div><span>WHAT THAT MEANS PRACTICALLY</span><strong>Oklahoma's defense should have the tougher assignment's easier half; Michigan's defense has margin for error Oklahoma's offense doesn't.</strong></div>
              </div>
              <p>Oklahoma also won the actual game last year — 24-13 in Ann Arbor. That result and this year's composite gap both point the same direction: a competitive game that tilts toward whichever offense finds room against the tougher defense in front of it.</p>
            </section>

            <section id="week1" className="djg-section">
              <SectionHead number="02" kicker="TWO OPENERS, TWO DIFFERENT TAPES" title="One team looked like its preseason profile. One team didn't." />
              <p>Oklahoma beat UTEP 51-0. John Mateer went 14-for-19 for 247 yards and 3 touchdowns, Lloyd Avant ran 15 times for 79 yards and a score, and the defense didn't allow a single point on UTEP's four trips into scoring range. Oklahoma posted a 56.1% success rate and a 17.5% explosive-play rate — genuinely elite efficiency, even against a bad opponent.</p>
              <p>Michigan beat Western Michigan 13-12 — trailing into the fourth quarter before Bryce Underwood hit JJ Buchanan for a 47-yard touchdown as time expired. Jordan Marshall (44 yards) and Underwood's legs carried the ground game; Underwood was mostly shaky through the air (12-for-23, 128 yards passing before the walk-off), and Michigan finished the night at -1 on turnover margin.</p>
              <p>The one thing that complicates the "Michigan is in trouble" read: Michigan's defense was actually the stingier of the two units by Week 1's own numbers. Despite facing 65 defensive snaps to Oklahoma's 54 — because Michigan's own offense couldn't sustain drives — Michigan allowed a 31.3% success rate and a 3.1% explosive-play rate, both better than what Oklahoma's defense allowed UTEP (34.0% / 8.0%). Oklahoma's front also had to work for its 4 sacks against UTEP's line; Michigan's front got home twice against Western Michigan.</p>
              <div className="djg-rule"><span>UTEP AND WESTERN MICHIGAN ARE NOT THE SAME OPENER.</span><strong>UTEP is bottom-tier FBS. Western Michigan is the reigning MAC champion that took Michigan to the final play.</strong></div>
              <p>Michigan didn't lose Week 1 on defense. It nearly lost it on offense and the turnover margin — the exact two things that have to be different against a defense this much better than Western Michigan's.</p>
            </section>

            <section id="michigan" className="djg-section">
              <SectionHead number="03" kicker="THE WOLVERINE PATH" title="How Michigan can win." />
              <p>Michigan is down three projected offensive line starters (Maikkula, Fodje, Fasusi), which pushed true freshman Noah Best into his second career start at center — against a front that just produced 4 sacks on UTEP. Everything starts with surviving that matchup.</p>
              <div className="djg-worry-grid">
                <div><span>01</span><strong>Get the run game established early.</strong><p>Michigan's offense ran for the #4 adjusted rush-success rate in the country in 2025. Leaning on Jordan Marshall keeps Michigan out of the long-yardage, obvious-passing situations where Oklahoma's defense — #8 against the pass, too — is most dangerous.</p></div>
                <div><span>02</span><strong>Chip and help before asking Best to win alone.</strong><p>A true freshman center in his second start doesn't need to be perfect if Michigan's scheme accounts for where Oklahoma's pressure is coming from.</p></div>
                <div><span>03</span><strong>Cash the possessions it gets.</strong><p>By this site's own recap, Michigan's offense reached Western Michigan's territory only once all night. Against a defense this good, that number has to move — Michigan doesn't need many explosive plays, but the ones it gets have to count.</p></div>
                <div><span>04</span><strong>Make Oklahoma one-dimensional.</strong><p>Michigan's front already got home twice against Western Michigan. Testing whether Oklahoma's stated 2026 goal of a "more balanced" offense survives real pressure is the clearest lever Michigan's defense controls.</p></div>
                <div><span>05</span><strong>Win the turnover margin, not just avoid losing it.</strong><p>Michigan is -1 for the season, including two Underwood giveaways that directly set up Western Michigan points. Oklahoma is already +2. That gap has to close.</p></div>
              </div>
              <p>None of this requires Michigan to look like Beck's old Utah offense overnight. It requires the version of Michigan that showed up on defense in Week 1 — disciplined, low-explosive-plays-allowed — to also show up on offense, even in a reduced, situational form.</p>
            </section>

            <section id="oklahoma" className="djg-section">
              <SectionHead number="04" kicker="THE SOONER PATH" title="How Oklahoma wins." />
              <p>Oklahoma doesn't need to blow anyone out. It needs to win time of possession, lean on its best defense-in-the-country baseline, and let a defensive front that's largely intact from 2025 go to work on a rebuilt Michigan line.</p>
              <div className="djg-coach-card">
                <span>WHY THAT MATTERS</span>
                <h3>Oklahoma's identity was never about scoring points in bunches.</h3>
                <p>Oklahoma's offense ranked #76 nationally in 2025 — middling, not explosive. Its case for winning has always run through the #2 defense, not through outscoring anyone. Feeding Lloyd Avant (79 yards, 5.3 per carry in Week 1) and staying balanced keeps Oklahoma in that lane rather than forcing Mateer to be the hero.</p>
              </div>
              <p>The blueprint is straightforward: control the clock, protect a turnover margin that's already +2 on the season, and let the same front seven that produced 4 sacks against UTEP dictate obvious passing downs against a true freshman center. Oklahoma doesn't have to be better than Michigan everywhere. It has to be better in exactly the one matchup — its defense against Michigan's offensive line — where the 2025 data already says it should be.</p>
              <p>The danger for Oklahoma is the same one that shows up in every "the market overreacted" argument about this game: leaning too hard on one blowout win over a bad UTEP team as proof the offense has arrived, when the actual 2025 baseline says that unit still has to prove it against a real defense — the one wearing maize and blue this time.</p>
            </section>

            <section id="metrics" className="djg-section">
              <SectionHead number="05" kicker="UNDERLYING METRICS" title="The numbers that actually explain how this goes." />
              <p>Put the validated 2025 model and the Week 1, 2026 tape side by side and the tension in this game is obvious:</p>
              <div className="djg-beck-board">
                <div className="djg-beck-top"><span>MFF · VALIDATED 2025 MODEL</span><Link href="/articles/michigan-oklahoma-2026-preview">SEE THE FULL DATA PREVIEW →</Link></div>
                <div className="djg-beck-grid">
                  <div><span>OVERALL COMPOSITE</span><strong>75.5</strong><small>MICHIGAN</small><b>vs.</b><strong>72.3</strong><small>OKLAHOMA</small></div>
                  <div><span>OFFENSE COMPOSITE</span><strong>83.4</strong><small>MICHIGAN</small><b>vs.</b><strong>46.7</strong><small>OKLAHOMA</small></div>
                  <div><span>DEFENSE COMPOSITE</span><strong>67.6</strong><small>MICHIGAN</small><b>vs.</b><strong>97.9</strong><small>OKLAHOMA</small></div>
                  <div><span>WEEK 1 SUCCESS RATE</span><strong>47.6%</strong><small>MICHIGAN</small><b>vs.</b><strong>56.1%</strong><small>OKLAHOMA</small></div>
                </div>
                <p>Michigan's offense is the better unit on paper (83.4 vs. 46.7). Oklahoma's defense is the far better unit on paper (97.9 vs. 67.6) — the widest single gap on either side of the ball in this matchup. Week 1's success-rate gap runs the same direction as the composite gap, but the sample is one game against very different levels of competition.</p>
              </div>
              <p>Read across the full picture and the tension resolves into a single, testable question: if Michigan's offense performs at its 2025 baseline (#19 nationally) against Oklahoma's defense at its 2025 baseline (#2 nationally), does Michigan still generate enough offense to win? The composite gap (+3.2 overall, in Michigan's favor) says it's close. The market (Oklahoma -5.5 to -6.5) says the read has shifted toward Oklahoma since Week 1. Both numbers are honest; they're just built from different evidence.</p>
            </section>

            <section className="djg-final">
              <span>THE BOTTOM LINE</span>
              <h2 id="bottom-line">This is a game about whether one Week 1 tape means anything.</h2>
              <p>Oklahoma looked like its preseason billing in Week 1. Michigan didn't. That's a real, if small, sample of evidence, and it's exactly why the market has moved 8 to 9 points toward Oklahoma since the preseason line.</p>
              <p>But the validated 2025 baseline underneath both tapes still says this is close — a +3.2 overall composite edge for Michigan, built on an offense that graded out #19 nationally running into a defense that graded out #2. That's not a contradiction of Week 1. It's the larger sample Week 1 sits on top of.</p>
              <p>Michigan wins by protecting a true freshman center, staying on schedule on the ground, and turning its limited possessions against Oklahoma's defense into points instead of punts. Oklahoma wins by doing what it's built to do — lean on the country's best defense, stay balanced enough on offense not to need a shootout, and make Michigan's rebuilt line live up to its worst-case Week 1 look for four quarters instead of one bad series.</p>
              <p><strong>One tape said Oklahoma is exactly as good as advertised. One tape said Michigan might not be. Saturday is the next data point — and the last one before a much larger sample makes the preseason numbers irrelevant either way.</strong></p>
              <div className="djg-final-line">The baseline says close. The market says Oklahoma. <em>Find out which number was right.</em></div>
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

        <footer className="djg-footer"><Link href="/articles">← ALL ARTICLES</Link><Link href="/articles/michigan-oklahoma-2026-preview">FULL DATA PREVIEW →</Link></footer>
      </div>
    </article>
  );
}
