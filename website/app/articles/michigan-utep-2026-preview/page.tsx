import type {Metadata} from "next";
import Link from "next/link";
import {ArticleMobileToc} from "../../../components/ArticleMobileToc";
import {teamLogoUrl} from "../../../lib/team-assets";
import {michiganUtep2026 as data} from "../../../lib/michigan/utep-2026-preview-data";
import type {CompareRow, StatPoint} from "../../../lib/michigan/utep-2026-preview-data";
import "../michigan-western-michigan-2026-preview/preview-story.css";

const articleUrl="https://michiganfootballfocus.com/articles/michigan-utep-2026-preview";
const socialDescription="Michigan is a 36.5-point favorite over a 1-1 UTEP team playing its first Mountain West season. The real question: can an offense still ranked outside the national top 75 finally look explosive against the same defense Oklahoma just carved up for 7.3 yards a play?";

export const metadata:Metadata={
  title:"Michigan vs. UTEP 2026 Preview: Stats, Matchups & Prediction",
  description:"A stats-first Michigan vs. UTEP Week 3 preview built on real 2026 opponent-adjusted data, official box scores, the site's preseason model and the current betting market.",
  openGraph:{type:"article",url:articleUrl,siteName:"Michigan Football Focus",title:"Michigan vs. UTEP 2026 Preview: Stats, Matchups & Prediction",description:socialDescription,images:["/og.png"]},
  twitter:{card:"summary_large_image",title:"Michigan vs. UTEP 2026 Preview: Stats, Matchups & Prediction",description:socialDescription,images:["/og.png"]}
};

const sections=[
  ["identity","The matchup in 30 seconds"],
  ["baseline","2026 opponent-adjusted baseline"],
  ["utep","Who is UTEP in 2026"],
  ["matchups","Three matchups that actually matter"],
  ["paths","How each script plays out"],
  ["short-list","Numbers worth remembering"],
  ["methodology","Sources & methodology"],
] as const;

function kickoffLabel(iso:string){
  const d=new Date(iso);
  return d.toLocaleString("en-US",{timeZone:"America/New_York",month:"short",day:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:"short"});
}

function SignalRow({row}:{row:CompareRow}){
  return <div className="wm-signal-row">
    <span>{row.metric}</span>
    <div className="wm-signal-value"><strong>{row.michigan.value}</strong><small>MICHIGAN · #{row.michigan.rank} NATIONAL</small></div>
  </div>;
}

function StatList({rows}:{rows:StatPoint[]}){
  return <div className="wm-headcount-grid" style={{gridTemplateColumns:"1fr 1fr 1fr"}}>
    {rows.map(row=><div key={row.label}><strong>{row.value}</strong><small>{row.label.toUpperCase()}</small></div>)}
  </div>;
}

function SectionHead({number,kicker,title,summary}:{number:string;kicker:string;title:string;summary?:string}){
  return <div className="wm-section-head">
    <div className="wm-section-no">{number}</div>
    <div><div className="wm-section-label">{kicker}</div><h2>{title}</h2>{summary&&<p>{summary}</p>}</div>
  </div>;
}

export default function MichiganUtepPreview(){
  return <article className="focus-article wm-preview">
    <div className="focus-article-shell wm-preview-shell">
      <Link className="wm-back" href="/articles">← THE NOTEBOOK</Link>

      <header className="wm-story-hero">
        <div className="wm-hero-topline"><b>MICHIGAN FOOTBALL FOCUS</b><span>WEEK 3 · 2026 GAME PREVIEW</span></div>
        <div className="wm-matchup-lockup">
          <div className="wm-team-mark"><img src={teamLogoUrl(data.michiganTeamId,256)} alt="Michigan Wolverines logo"/></div>
          <div className="wm-matchup-copy">
            <span>SEPTEMBER 19 · MICHIGAN STADIUM</span>
            <h1>Michigan<em>vs</em>UTEP</h1>
            <div className="wm-matchup-meta">{kickoffLabel(data.kickoffISO)} · Ann Arbor, Michigan</div>
          </div>
          <div className="wm-team-mark"><img src={teamLogoUrl(data.opponentTeamId,256)} alt="UTEP Miners logo"/></div>
        </div>
        <div className="wm-hero-thesis">{data.heroThesis}</div>
        <div className="wm-model-rail">
          <div className="wm-model-accent"><small>Site model, frozen preseason</small><strong>{data.model.projectedMargin}</strong><span>{data.model.asOf}</span></div>
          <div><small>Current market</small><strong>{data.market.spread}</strong><span>{data.market.book} · {data.market.asOf}</span></div>
          <div><small>Michigan defense, national rank</small><strong>#16 pts/opp · #22 SR</strong><span>through 2 games, 2026</span></div>
          <div><small>Michigan offense, national rank</small><strong>#78 pts/opp · #90 SR</strong><span>through 2 games, 2026</span></div>
        </div>
      </header>

      <section id="identity" className="wm-story-intro">
        <div><div className="wm-section-label">THE 30-SECOND READ</div><h2>This game is a Michigan-offense evaluation, not a competitive question.</h2></div>
        <p><strong>Michigan is favored by 36.5 points, and both the market and the site's own preseason model land in almost the same place.</strong> UTEP's only game against comparable competition this year was a 51-0 loss to Oklahoma in which its defense allowed 7.3 yards per play -- the same Oklahoma offense Michigan's defense held to 4.7 yards per play a week later. The real story is Michigan's own offense, which still ranks outside the national top 75 in scoring efficiency and success rate after two games carried almost entirely by the defense.</p>
      </section>

      <div className="wm-scouting-grid">
        {data.scoutCards.map(card=><div className="wm-scout-card" key={card.kicker}><span>{card.kicker}</span><strong><em>{card.value}</em></strong><h3>{card.title}</h3><p>{card.body}</p></div>)}
      </div>

      <ArticleMobileToc sections={sections}/>

      <div className="wm-reading-layout">
        <aside className="wm-toc">
          <span>IN THIS PREVIEW</span>
          <nav>{sections.map(([id,label],index)=><a href={`#${id}`} key={id}><b>{String(index+1).padStart(2,"0")}</b>{label}</a>)}</nav>
        </aside>

        <div className="wm-story-body">
          <section id="baseline" className="wm-story-section">
            <SectionHead number="01" kicker="2026 OPPONENT-ADJUSTED BASELINE" title="Two real games, and a clear split between the two sides of the ball." summary={data.baseline.intro}/>
            <div className="wm-matchup-board">
              <div className="wm-unit-card">
                <header><span>MICHIGAN, TWO GAMES</span><b>2026 NATIONAL RANKS</b></header>
                {data.baseline.michiganTwoGameRows.map(row=><SignalRow key={row.metric} row={row}/>)}
              </div>
            </div>
            <div className="wm-continuity-grid">
              {data.baseline.perGame.map(game=><div className="wm-continuity-card" key={game.opponent}>
                <span>{game.opponent.toUpperCase()}</span>
                <StatList rows={game.rows}/>
              </div>)}
            </div>
            <p><strong>{data.baseline.takeaway}</strong></p>
          </section>

          <section id="utep" className="wm-story-section">
            <SectionHead number="02" kicker="THE OPPONENT" title="A rebuild colliding with a level jump." summary={data.utep.intro}/>
            <p className="wm-method-note" style={{marginBottom:14}}>{data.utep.programNote}</p>
            <div className="wm-continuity-grid">
              {data.utep.games.map(game=><div className="wm-continuity-card" key={game.line}>
                <span>{game.line.toUpperCase()}</span>
                <StatList rows={game.rows}/>
                {game.note&&<p className="wm-method-note" style={{marginTop:14,marginBottom:0}}>{game.note}</p>}
              </div>)}
            </div>
            <p><strong>{data.utep.takeaway}</strong></p>
          </section>

          <section id="matchups" className="wm-story-section">
            <SectionHead number="03" kicker="THE REAL QUESTIONS" title="Three matchups that actually matter Saturday."/>
            <div className="wm-matchup-list">
              {data.matchups.map((matchup,index)=><article className="wm-decision-card" key={matchup.id}>
                <div className="wm-decision-top"><div className="wm-decision-index">{index+1}</div><div><span>{matchup.kicker}</span><h3>{matchup.title}</h3><div className="wm-decision-question">{matchup.question}</div></div></div>
                <div className="wm-decision-data">{matchup.numbers.map(number=><b key={number.label}><strong>{number.value}</strong> · {number.label}</b>)}</div>
                <div className="wm-decision-copy">{matchup.narrative.map((paragraph,i)=><p key={i}>{paragraph}</p>)}</div>
              </article>)}
            </div>
          </section>

          <section id="paths" className="wm-story-section">
            <SectionHead number="04" kicker="TWO DIFFERENT SCRIPTS" title="The likely outcome, and what would make it interesting."/>
            <div className="wm-path-grid">
              <div className="wm-path-card wm-michigan-path"><span>HOW MICHIGAN WINS COMFORTABLY</span><h3>Every path leads back to finishing drives.</h3>{data.howMichiganWins.map((line,i)=><b key={i}>{line}</b>)}</div>
              <div className="wm-path-card"><span>WHAT WOULD MAKE IT INTERESTING</span><h3>The letdown-spot scenarios, in order of plausibility.</h3>{data.whatWouldMakeItInteresting.map((line,i)=><b key={i}>{line}</b>)}</div>
            </div>
          </section>

          <section id="short-list" className="wm-story-section">
            <SectionHead number="05" kicker="THE SHORT LIST" title="Six numbers worth remembering after you close the tab."/>
            <div className="wm-number-grid">{data.numbersThatMatter.slice(0,6).map(number=><div className="wm-number-card" key={number.label}><strong>{number.value}</strong><span>{number.label}</span><p>{number.why}</p></div>)}</div>
            <div className="wm-verdict"><span>EDITORIAL READ</span><strong>{data.verdict}</strong></div>
          </section>

          <section id="methodology" className="wm-story-section wm-methodology">
            <SectionHead number="06" kicker="DON'T BLEND DIFFERENT NUMBERS" title="Sources & methodology" summary="The 2026 opponent-adjusted baseline, UTEP's limited sample, the frozen preseason model and the current betting market answer different questions. They stay labeled separately here on purpose."/>
            <details><summary>2026 opponent-adjusted baseline</summary><p>{data.methodology.baseline}</p></details>
            <details><summary>UTEP's 2026 sample</summary><p>{data.methodology.utep}</p></details>
            <details><summary>Site model projection</summary><p>{data.methodology.model}</p></details>
            <details><summary>Market context</summary><p>{data.methodology.market}</p></details>
          </section>
        </div>
      </div>

      <section className="wm-share-section">
        <div className="wm-share-head"><div><div className="wm-section-label">THE MATCHUP GRAPHIC</div><h2>Team quality, identity, edges and the verdict.</h2></div><p>Same MFF matchup-graphic template we run for every opponent: national rank for both teams, how each wants to play, offense-vs-defense edges for both directions of the ball, and the model/market verdict.</p></div>
        <Link href="/matchup-graphic/401858450" className="button">OPEN THE FULL MATCHUP GRAPHIC →</Link>
      </section>

      <section className="focus-article-explore feature-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>Go deeper than the preview.</h2></div>
        <div className="focus-article-link-grid">
          <Link href="/articles/michigan-oklahoma-2026-preview"><strong>Michigan vs. Oklahoma preview</strong><p>The matchup story behind Michigan's biggest win of the season so far.</p><span>READ THE STORY →</span></Link>
          <Link href="/games/401858450"><strong>Michigan vs. UTEP game hub</strong><p>Model projection, matchup details and market context.</p><span>OPEN GAME HUB →</span></Link>
          <Link href="/analytics"><strong>Michigan analytics</strong><p>Explore the opponent-adjusted ratings behind the preview.</p><span>EXPLORE DATA →</span></Link>
        </div>
      </section>

      <section className="focus-article-sources"><strong>REPORTING &amp; DATA SOURCES</strong><div>{data.sources.map(({label,url})=><a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div></section>
      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}
