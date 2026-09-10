import type {Metadata} from "next";
import Link from "next/link";
import {ArticleMobileToc} from "../../../components/ArticleMobileToc";
import {teamLogoUrl} from "../../../lib/team-assets";
import {michiganOklahoma2026 as data} from "../../../lib/michigan/oklahoma-2026-preview-data";
import type {CompareRow, StatPoint} from "../../../lib/michigan/oklahoma-2026-preview-data";
import "../michigan-western-michigan-2026-preview/preview-story.css";

const articleUrl="https://michiganfootballfocus.com/articles/michigan-oklahoma-2026-preview";
const socialDescription="Oklahoma brings the #2 defense from MFF's validated 2025 FBS sample into Michigan Stadium. Michigan brings a defense that allowed no touchdowns in Week 1 and an offense that turned it over three times. Here is the fact-checked matchup, current personnel picture and market read.";

export const metadata:Metadata={
  title:"Michigan vs. Oklahoma 2026 Preview: Matchups, Analytics & Prediction",
  description:"A fact-checked Michigan vs. Oklahoma Week 2 preview using validated 2025 opponent-adjusted efficiency, official 2026 Week 1 box scores, current personnel reporting and market context.",
  openGraph:{type:"article",url:articleUrl,siteName:"Michigan Football Focus",title:"Michigan vs. Oklahoma 2026 Preview: Matchups, Analytics & Prediction",description:socialDescription,images:["/og.png"]},
  twitter:{card:"summary_large_image",title:"Michigan vs. Oklahoma 2026 Preview: Matchups, Analytics & Prediction",description:socialDescription,images:["/og.png"]}
};

const sections=[
  ["identity","The matchup in 30 seconds"],
  ["baseline","2025 opponent-adjusted baseline"],
  ["week1","What Week 1 actually said"],
  ["matchups","Four matchups that decide it"],
  ["paths","How each team gets its game"],
  ["short-list","Numbers worth remembering"],
  ["methodology","Sources & methodology"],
] as const;

function kickoffLabel(iso:string){
  const d=new Date(iso);
  return d.toLocaleString("en-US",{timeZone:"America/New_York",month:"short",day:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:"short"});
}

function SignalRow({row,leftLabel,rightLabel}:{row:CompareRow;leftLabel:string;rightLabel:string}){
  return <div className="wm-signal-row">
    <span>{row.metric}</span>
    <div className="wm-signal-value"><strong>{row.michigan.value}</strong><small>{leftLabel} · #{row.michigan.rank}</small></div>
    <div className="wm-signal-value"><strong>{row.opponent.value}</strong><small>{rightLabel} · #{row.opponent.rank}</small></div>
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

export default function MichiganOklahomaPreview(){
  return <article className="focus-article wm-preview">
    <div className="focus-article-shell wm-preview-shell">
      <Link className="wm-back" href="/articles">← THE NOTEBOOK</Link>

      <header className="wm-story-hero">
        <div className="wm-hero-topline"><b>MICHIGAN FOOTBALL FOCUS</b><span>WEEK 2 · 2026 GAME PREVIEW</span></div>
        <div className="wm-matchup-lockup">
          <div className="wm-team-mark"><img src={teamLogoUrl(data.michiganTeamId,256)} alt="Michigan Wolverines logo"/></div>
          <div className="wm-matchup-copy">
            <span>SEPTEMBER 12 · MICHIGAN STADIUM</span>
            <h1>Michigan<em>vs</em>Oklahoma</h1>
            <div className="wm-matchup-meta">{kickoffLabel(data.kickoffISO)} · Ann Arbor, Michigan</div>
          </div>
          <div className="wm-team-mark"><img src={teamLogoUrl(data.opponentTeamId,256)} alt="Oklahoma Sooners logo"/></div>
        </div>
        <div className="wm-hero-thesis">{data.heroThesis}</div>
        <div className="wm-model-rail">
          <div className="wm-model-accent"><small>Preseason win probability</small><strong>{data.preseasonModel.winProbMichiganPct}%</strong><span>Michigan · before Week 1</span></div>
          <div><small>Preseason projected margin</small><strong>{data.preseasonModel.projectedMargin.replace("Michigan by ","+")}</strong><span>not a current prediction</span></div>
          <div><small>2025 overall composite</small><strong>#{data.compositeComparison.michigan.overall.rank} vs #{data.compositeComparison.opponent.overall.rank}</strong><span>validated FBS sample</span></div>
          <div><small>current market</small><strong>{data.market.spread}</strong><span>{data.market.book} · {data.market.asOf}</span></div>
        </div>
      </header>

      <section id="identity" className="wm-story-intro">
        <div><div className="wm-section-label">THE 30-SECOND READ</div><h2>Start with the evidence that survives scrutiny.</h2></div>
        <p><strong>Oklahoma owns the best unit in this game: the #2 defense in MFF's validated 2025 FBS sample.</strong> Michigan's Week 1 offense turned the ball over three times and went 3-for-10 on third down. But Michigan's defense allowed Western Michigan only 221 yards and no touchdowns, and Oklahoma's 51-0 included an 88-yard punt-return touchdown. The market has flipped eight points from Oklahoma +2.5 at open to Oklahoma -5.5 now. That is a major repricing, not proof that the Week 1 scoreboards tell the whole story.</p>
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
            <SectionHead number="01" kicker="2025 OPPONENT-ADJUSTED BASELINE" title="The 2025 baseline is closer than the Week 1 scoreboard." summary={data.baseline.intro}/>
            <div className="wm-matchup-board">
              <div className="wm-unit-card">
                <header><span>WHEN MICHIGAN HAS THE BALL</span><b>MICH O · OU D</b></header>
                {data.baseline.michiganOffenseVsOpponentDefense.map(row=><SignalRow key={row.metric} row={row} leftLabel="MICH O" rightLabel="OU D"/>)}
              </div>
              <div className="wm-unit-card">
                <header><span>WHEN OKLAHOMA HAS THE BALL</span><b>MICH D · OU O</b></header>
                {data.baseline.opponentOffenseVsMichiganDefense.map(row=><SignalRow key={row.metric} row={row} leftLabel="MICH D" rightLabel="OU O"/>)}
              </div>
            </div>
            <p><strong>{data.baseline.takeaway}</strong></p>
          </section>

          <section id="week1" className="wm-story-section">
            <SectionHead number="02" kicker="WEEK 1, 2026" title="What the official box scores actually say." summary={data.week1.intro}/>
            <div className="wm-continuity-grid">
              <div className="wm-continuity-card">
                <span>{data.week1.oklahoma.line.toUpperCase()}</span>
                <p className="wm-method-note" style={{marginTop:0,marginBottom:14}}>{data.week1.oklahoma.qb}<br/>{data.week1.oklahoma.rb}</p>
                <StatList rows={data.week1.oklahoma.rows}/>
              </div>
              <div className="wm-continuity-card">
                <span>{data.week1.michigan.line.toUpperCase()}</span>
                <p className="wm-method-note" style={{marginTop:0,marginBottom:14}}>{data.week1.michigan.qb}<br/>{data.week1.michigan.rb}</p>
                <StatList rows={data.week1.michigan.rows}/>
              </div>
            </div>
            <p><strong>{data.week1.takeaway}</strong></p>
            <p className="wm-method-note">{data.week1.caveat}</p>
          </section>

          <section id="matchups" className="wm-story-section">
            <SectionHead number="03" kicker="THE GAME INSIDE THE GAME" title="Four matchup levers that will decide the game."/>
            <div className="wm-matchup-list">
              {data.matchups.map((matchup,index)=><article className="wm-decision-card" key={matchup.id}>
                <div className="wm-decision-top"><div className="wm-decision-index">{index+1}</div><div><span>{matchup.kicker}</span><h3>{matchup.title}</h3><div className="wm-decision-question">{matchup.question}</div></div></div>
                <div className="wm-decision-data">{matchup.numbers.map(number=><b key={number.label}><strong>{number.value}</strong> · {number.label}</b>)}</div>
                <div className="wm-decision-copy">{matchup.narrative.map((paragraph,i)=><p key={i}>{paragraph}</p>)}</div>
              </article>)}
            </div>
          </section>

          <section id="paths" className="wm-story-section">
            <SectionHead number="04" kicker="TWO DIFFERENT GAMES" title="The scripts are clear. The execution is not."/>
            <div className="wm-path-grid">
              <div className="wm-path-card"><span>OKLAHOMA'S PATH</span><h3>Let the defense create the game.</h3>{data.howOklahomaWins.map((line,i)=><b key={i}>{line}</b>)}</div>
              <div className="wm-path-card wm-michigan-path"><span>MICHIGAN'S PATH</span><h3>Win enough early downs to give Underwood a chance.</h3>{data.howMichiganWins.map((line,i)=><b key={i}>{line}</b>)}</div>
            </div>
          </section>

          <section id="short-list" className="wm-story-section">
            <SectionHead number="05" kicker="THE SHORT LIST" title="Six numbers worth remembering after you close the tab."/>
            <div className="wm-number-grid">{data.numbersThatMatter.slice(0,6).map(number=><div className="wm-number-card" key={number.label}><strong>{number.value}</strong><span>{number.label}</span><p>{number.why}</p></div>)}</div>
            <div className="wm-verdict"><span>EDITORIAL READ</span><strong>{data.verdict}</strong></div>
          </section>

          <section id="methodology" className="wm-story-section wm-methodology">
            <SectionHead number="06" kicker="DON'T BLEND DIFFERENT NUMBERS" title="Sources & methodology" summary="The validated 2025 model, official Week 1 box scores, preseason simulation and current betting market answer different questions. They stay labeled separately here on purpose."/>
            <details><summary>Validated 2025 opponent-adjusted efficiency</summary><p>{data.methodology.validated}</p></details>
            <details><summary>Week 1, 2026 official evidence</summary><p>{data.methodology.week1}</p></details>
            <details><summary>Preseason simulation</summary><p>{data.methodology.preseason}</p></details>
            <details><summary>Market context</summary><p>{data.methodology.market}</p></details>
          </section>
        </div>
      </div>

      <section className="wm-share-section">
        <div className="wm-share-head"><div><div className="wm-section-label">THE MATCHUP GRAPHIC</div><h2>Team quality, identity, edges and the verdict.</h2></div><p>Same MFF matchup-graphic template we run for every opponent: national rank for both teams, how each wants to play, offense-vs-defense edges for both directions of the ball, and the model/market verdict.</p></div>
        <Link href="/matchup-graphic/401856679" className="button">OPEN THE FULL MATCHUP GRAPHIC →</Link>
      </section>

      <section className="focus-article-explore feature-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>Go deeper than the preview.</h2></div>
        <div className="focus-article-link-grid">
          <Link href="/articles/dont-jump-the-gun-michigan-football-2026"><strong>Don't Jump the Gun on Michigan after Week 1</strong><p>Why one ugly opener matters without becoming the entire evaluation of the 2026 Wolverines.</p><span>READ THE STORY →</span></Link>
          <Link href="/games/401856679"><strong>Michigan vs. Oklahoma game hub</strong><p>Model projection, matchup details and market context.</p><span>OPEN GAME HUB →</span></Link>
          <Link href="/analytics"><strong>Michigan analytics</strong><p>Explore the opponent-adjusted ratings behind the preview.</p><span>EXPLORE DATA →</span></Link>
        </div>
      </section>

      <section className="focus-article-sources"><strong>REPORTING &amp; DATA SOURCES</strong><div>{data.sources.map(({label,url})=><a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div></section>
      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}
