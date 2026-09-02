import type {CSSProperties} from "react";
import type {Metadata} from "next";
import Link from "next/link";
import {ArticleMobileToc} from "../../../components/ArticleMobileToc";
import {teamLogoUrl} from "../../../lib/team-assets";
import {michiganWesternMichigan2026 as data} from "../../../lib/michigan/matchup-preview-data";
import type {CompareRow} from "../../../lib/michigan/matchup-preview-data";
import "./preview-story.css";

const articleUrl="https://michiganfootballfocus.com/articles/michigan-western-michigan-2026-preview";
const socialDescription="Western Michigan returns the pieces that make its run-first offense work. The defense was the better unit in 2025, but the front seven now carries the biggest continuity question. Here's the Week 1 matchup story.";

export const metadata:Metadata={
  title:"Michigan vs. Western Michigan: The Week 1 Matchup Story",
  description:"A story-first Michigan vs. Western Michigan Week 1 preview using 2025 opponent-adjusted efficiency, roster continuity, returning snaps research and the Michigan Football Focus model.",
  openGraph:{type:"article",url:articleUrl,siteName:"Michigan Football Focus",title:"Michigan vs. Western Michigan: The Week 1 Matchup Story",description:socialDescription,images:["/og.png"]},
  twitter:{card:"summary_large_image",title:"Michigan vs. Western Michigan: The Week 1 Matchup Story",description:socialDescription,images:["/og.png"]}
};

const sections=[
  ["identity","The matchup in 30 seconds"],
  ["numbers","What the 2025 data says"],
  ["continuity","Where the game changed"],
  ["matchups","Three matchups that decide it"],
  ["paths","How each team gets its game"],
  ["short-list","Numbers worth remembering"],
  ["methodology","Sources & methodology"],
] as const;

function kickoffLabel(iso:string){
  const d=new Date(iso);
  return d.toLocaleString("en-US",{timeZone:"America/New_York",month:"short",day:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:"short"});
}

function externalDefensePct(group:string){
  return data.continuity.opponentExternal.defensePositions.find(item=>item.group===group)?.pct??0;
}

function SignalRow({row,leftLabel,rightLabel}:{row:CompareRow;leftLabel:string;rightLabel:string}){
  return <div className="wm-signal-row">
    <span>{row.metric}</span>
    <div className="wm-signal-value"><strong>{row.michigan.value}</strong><small>{leftLabel} · #{row.michigan.rank}</small></div>
    <div className="wm-signal-value"><strong>{row.opponent.value}</strong><small>{rightLabel} · #{row.opponent.rank}</small></div>
  </div>;
}

function ContinuityBar({label,pct}:{label:string;pct:number}){
  return <div className="wm-continuity-row">
    <span>{label}</span>
    <div className="wm-continuity-track"><div className="wm-continuity-fill" style={{"--pct":`${pct}%`} as CSSProperties}/></div>
    <b>{pct}%</b>
  </div>;
}

function SectionHead({number,kicker,title,summary}:{number:string;kicker:string;title:string;summary?:string}){
  return <div className="wm-section-head">
    <div className="wm-section-no">{number}</div>
    <div><div className="wm-section-label">{kicker}</div><h2>{title}</h2>{summary&&<p>{summary}</p>}</div>
  </div>;
}

export default function MichiganWesternMichiganPreview(){
  const b=data.blueprint;
  const michiganWithBall=b.michiganOffenseVsOpponentDefense.filter(row=>row.tier==="validated").filter(row=>["Rush success","Pass success","Yards per play"].includes(row.metric));
  const westernWithBall=b.opponentOffenseVsMichiganDefense.filter(row=>row.tier==="validated").filter(row=>["Rush success","Pass success","Yards per play"].includes(row.metric));
  const cbsDL=externalDefensePct("DL");
  const cbsLB=externalDefensePct("LB");
  const cbsDB=externalDefensePct("DB");

  return <article className="focus-article wm-preview">
    <div className="focus-article-shell wm-preview-shell">
      <Link className="wm-back" href="/articles">← THE NOTEBOOK</Link>

      <header className="wm-story-hero">
        <div className="wm-hero-topline"><b>MICHIGAN FOOTBALL FOCUS</b><span>WEEK 1 · 2026 GAME PREVIEW</span></div>
        <div className="wm-matchup-lockup">
          <div className="wm-team-mark"><img src={teamLogoUrl(data.michiganTeamId,256)} alt="Michigan Wolverines logo"/></div>
          <div className="wm-matchup-copy">
            <span>SEPTEMBER 5 · MICHIGAN STADIUM</span>
            <h1>Michigan<em>vs</em>Western Michigan</h1>
            <div className="wm-matchup-meta">{kickoffLabel(data.kickoffISO)} · Ann Arbor, Michigan</div>
          </div>
          <div className="wm-team-mark"><img src={teamLogoUrl(data.opponentTeamId,256)} alt="Western Michigan Broncos logo"/></div>
        </div>
        <div className="wm-hero-thesis">Western returns the pieces that make its offense work. <strong>The biggest question is whether the defense that carried 2025 still looks like the same defense up front.</strong></div>
        <div className="wm-model-rail">
          <div className="wm-model-accent"><small>MFF win probability</small><strong>{b.winProbMichiganPct}%</strong><span>Michigan</span></div>
          <div><small>MFF projected margin</small><strong>{b.projectedMargin.replace("Michigan by ","+")}</strong><span>Michigan perspective</span></div>
          <div><small>2025 overall</small><strong>#{b.michiganSeason.overall.rank} vs #{b.opponentSeason.overall.rank}</strong><span>validated composite</span></div>
          <div><small>market</small><strong>{data.market?.spread??"—"}</strong><span>{data.market?.book??"not published"}</span></div>
        </div>
      </header>

      <section id="identity" className="wm-story-intro">
        <div><div className="wm-section-label">THE 30-SECOND READ</div><h2>Understand the game before the data.</h2></div>
        <p><strong>Western's path is narrow, but it is coherent.</strong> Broc Lowry and a run-first offense want to stay on schedule, shorten the game and keep Michigan from turning the talent gap into extra possessions. Michigan's job is to break that script early: make Western throw, then make a reconstructed front seven defend the entire field.</p>
      </section>

      <div className="wm-scouting-grid">
        <div className="wm-scout-card"><span>WESTERN'S IDENTITY</span><strong><em>{data.opponentOffense.numbers[0].value}</em></strong><h3>Run first. Then run again.</h3><p>Western's 2025 rush decision rate tells you what it wants the game to become. The passing game was the less efficient option, not the foundation.</p></div>
        <div className="wm-scout-card"><span>THE REAL RESPECT POINT</span><strong>#{data.compositeComparison.opponent.defense.rank}</strong><h3>The defense was legitimately good.</h3><p>Western was much better on defense than offense in 2025, including a #{data.opponentDefense.numbers[1].detail?.match(/#\d+/)?.[0]?.replace("#","")??23} adjusted pass-success defense. This is not a unit to wave away.</p></div>
        <div className="wm-scout-card"><span>THE 2026 TENSION</span><strong><em>{cbsDL}% / {cbsLB}%</em></strong><h3>DL / LB returning snaps.</h3><p>CBS's snap-weighted research is the most important continuity clue: Western retained far less of the front-seven workload than the roster headcount alone suggests.</p></div>
      </div>

      <ArticleMobileToc sections={sections}/>

      <div className="wm-reading-layout">
        <aside className="wm-toc">
          <span>IN THIS PREVIEW</span>
          <nav>{sections.map(([id,label],index)=><a href={`#${id}`} key={id}><b>{String(index+1).padStart(2,"0")}</b>{label}</a>)}</nav>
        </aside>

        <div className="wm-story-body">
          <section id="numbers" className="wm-story-section">
            <SectionHead number="01" kicker="2025 OPPONENT-ADJUSTED BASELINE" title="The data doesn't say Western is bad. It says Western is uneven." summary="These are the validated 2025 matchup signals worth carrying into Week 1. The full table belongs in the analytics layer, not in the reader's face."/>
            <div className="wm-matchup-board">
              <div className="wm-unit-card">
                <header><span>WHEN MICHIGAN HAS THE BALL</span><b>MICH O · WMU D</b></header>
                {michiganWithBall.map(row=><SignalRow key={row.metric} row={row} leftLabel="MICH O" rightLabel="WMU D"/>)}
              </div>
              <div className="wm-unit-card">
                <header><span>WHEN WESTERN HAS THE BALL</span><b>MICH D · WMU O</b></header>
                {westernWithBall.map(row=><SignalRow key={row.metric} row={row} leftLabel="MICH D" rightLabel="WMU O"/>)}
              </div>
            </div>
            <p><strong>The matchup isn't "Michigan good, Western bad."</strong> Western's defense was the better half of its team. The offensive split is the sharper clue: adjusted rushing success ranked #{data.opponentOffense.numbers[1].detail?.match(/#\d+/)?.[0]?.replace("#","")??65}, while adjusted passing success ranked #{data.opponentOffense.numbers[2].detail?.match(/#\d+/)?.[0]?.replace("#","")??118}. If Michigan forces the game away from Western's preferred script, the statistical floor drops quickly.</p>
          </section>

          <section id="continuity" className="wm-story-section">
            <SectionHead number="02" kicker="WHAT ACTUALLY RETURNS" title="This is where the 2025 box score stops being enough." summary="Our roster audit measures returning bodies. CBS's research measures returning snaps. Those are different questions — and the difference is the story."/>
            <div className="wm-continuity-lead">Our headcount audit says <b>{data.continuity.opponent.defense.overallPct.toFixed(0)}%</b> of Western's defensive roster returns. CBS says only <b>{data.continuity.opponentExternal.defenseOverallPct}%</b> of its 2025 defensive snaps return. Up front, that falls to <b>{cbsDL}% DL</b> and <b>{cbsLB}% LB</b>.</div>
            <div className="wm-continuity-grid">
              <div className="wm-continuity-card">
                <span>OUR ROSTER HEADCOUNT AUDIT</span>
                <div className="wm-headcount-grid">
                  <div><strong>{data.continuity.michigan.offense.overallPct.toFixed(0)}%</strong><small>MICHIGAN OFFENSE</small></div>
                  <div><strong>{data.continuity.michigan.defense.overallPct.toFixed(0)}%</strong><small>MICHIGAN DEFENSE</small></div>
                  <div><strong>{data.continuity.opponent.offense.overallPct.toFixed(0)}%</strong><small>WESTERN OFFENSE</small></div>
                  <div><strong>{data.continuity.opponent.defense.overallPct.toFixed(0)}%</strong><small>WESTERN DEFENSE</small></div>
                </div>
                <p className="wm-method-note">Each returning roster player counts once. This is continuity of bodies, not continuity of playing time.</p>
              </div>
              <div className="wm-continuity-card">
                <span>CBS SPORTS · RETURNING 2025 SNAPS</span>
                <div className="wm-snap-overall">
                  <div><strong>{data.continuity.opponentExternal.offenseOverallPct}%</strong><small>WESTERN OFFENSE</small></div>
                  <div><strong>{data.continuity.opponentExternal.defenseOverallPct}%</strong><small>WESTERN DEFENSE</small></div>
                </div>
                <ContinuityBar label="DL" pct={cbsDL}/><ContinuityBar label="LB" pct={cbsLB}/><ContinuityBar label="DB" pct={cbsDB}/>
                <p className="wm-method-note">The front-seven drop is not the same as saying Western's defense will be bad. It says the unit Michigan sees in Week 1 is materially different from the one that produced the 2025 numbers.</p>
              </div>
            </div>
          </section>

          <section id="matchups" className="wm-story-section">
            <SectionHead number="03" kicker="THE GAME INSIDE THE GAME" title="Three matchups that decide whether this feels routine or uncomfortable."/>
            <div className="wm-matchup-list">
              {data.matchups.map((matchup,index)=><article className="wm-decision-card" key={matchup.id}>
                <div className="wm-decision-top"><div className="wm-decision-index">{index+1}</div><div><span>{matchup.kicker}</span><h3>{matchup.title}</h3><div className="wm-decision-question">{matchup.question}</div></div></div>
                <div className="wm-decision-data">{matchup.numbers.map(number=><b key={number.label}><strong>{number.value}</strong> · {number.label}</b>)}</div>
                <div className="wm-decision-copy">{matchup.narrative.map((paragraph,i)=><p key={i}>{paragraph}</p>)}</div>
              </article>)}
            </div>
          </section>

          <section id="paths" className="wm-story-section">
            <SectionHead number="04" kicker="TWO DIFFERENT GAMES" title="The team that gets its preferred script probably tells us the result early."/>
            <div className="wm-path-grid">
              <div className="wm-path-card"><span>WESTERN'S PATH</span><h3>Compress the game.</h3>{data.howOpponentCompetes.map((line,i)=><b key={i}>{line}</b>)}</div>
              <div className="wm-path-card wm-michigan-path"><span>MICHIGAN'S PATH</span><h3>Break the script.</h3>{data.howMichiganControls.map((line,i)=><b key={i}>{line}</b>)}</div>
            </div>
          </section>

          <section id="short-list" className="wm-story-section">
            <SectionHead number="05" kicker="THE SHORT LIST" title="Six numbers worth remembering after you close the tab."/>
            <div className="wm-number-grid">{data.numbersThatMatter.slice(0,6).map(number=><div className="wm-number-card" key={number.label}><strong>{number.value}</strong><span>{number.label}</span><p>{number.why}</p></div>)}</div>
            <div className="wm-verdict"><span>OUR READ</span><strong>{data.heroThesis}</strong><p>Western can make the opening stretch annoying if it stays ahead of the chains and lets its secondary keep the game compressed. Michigan takes control by forcing Western into the part of its offense that graded worst in 2025, then making a rebuilt front seven survive repeated pressure.</p></div>
          </section>

          <section id="methodology" className="wm-story-section wm-methodology">
            <SectionHead number="06" kicker="DON'T BLEND DIFFERENT NUMBERS" title="Sources & methodology" summary="The model, roster audit, returning-snaps research and betting market answer different questions. They stay labeled separately here on purpose."/>
            <details><summary>Validated opponent-adjusted efficiency</summary><p>{data.methodology.validated}</p></details>
            <details><summary>Michigan Football Focus roster continuity</summary><p>{data.methodology.internal}</p></details>
            <details><summary>External returning production / returning snaps</summary><p>{data.methodology.external}</p></details>
            <details><summary>Market context</summary><p>{data.methodology.market}</p></details>
          </section>
        </div>
      </div>

      <section className="wm-share-section">
        <div className="wm-share-head"><div><div className="wm-section-label">THE MATCHUP GRAPHIC</div><h2>Team quality, identity, edges and the verdict.</h2></div><p>Same MFF matchup-graphic template we run for every opponent: national rank for both teams, how each wants to play, offense-vs-defense edges for both directions of the ball, and the model/market verdict.</p></div>
        <Link href="/matchup-graphic/401858428" className="button">OPEN THE FULL MATCHUP GRAPHIC →</Link>
      </section>

      <section className="focus-article-explore feature-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>Go deeper than the preview.</h2></div>
        <div className="focus-article-link-grid">
          <Link href="/games/401858428"><strong>Michigan vs. Western Michigan game hub</strong><p>Model projection, matchup details and market context.</p><span>OPEN GAME HUB →</span></Link>
          <Link href="/analytics"><strong>Michigan analytics</strong><p>Explore the opponent-adjusted ratings behind the preview.</p><span>EXPLORE DATA →</span></Link>
          <Link href="/methodology"><strong>How we grade the evidence</strong><p>What validated, research-only, raw and adjusted mean.</p><span>READ METHODOLOGY →</span></Link>
        </div>
      </section>

      <section className="focus-article-sources"><strong>REPORTING &amp; DATA SOURCES</strong><div>{data.sources.map(({label,url})=><a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div></section>
      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}