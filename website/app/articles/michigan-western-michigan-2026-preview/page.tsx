import type {CSSProperties} from "react";
import type {Metadata} from "next";
import Link from "next/link";
import {ArticleMobileToc} from "../../../components/ArticleMobileToc";
import {teamLogoUrl} from "../../../lib/team-assets";
import {teamColors} from "../../../lib/team-colors";
import {michiganWesternMichigan2026 as data} from "../../../lib/michigan/matchup-preview-data";
import type {ContinuitySide,CompareRow} from "../../../lib/michigan/matchup-preview-data";

// Michigan's bar uses the real brand maize (already the site's accent
// color). The opponent's bar uses a neutral silver rather than Western's
// literal brand brown -- WMU's brown is too low-contrast against this dark
// navy card to read at a glance, so this follows the same convention this
// codebase already uses for its other dark-background team comparison
// (see analytics-lab.css's .utah-bar). Real team color still shows up via
// the actual team logos next to each side.
const MICHIGAN_BAR="#ffcb05";
const OPPONENT_BAR="#ccced1";
const percentileFromRank=(rank:number)=>((137-rank)/136)*100;

const articleUrl="https://michiganfootballfocus.com/articles/michigan-western-michigan-2026-preview";
const articleImage="https://michiganfootballfocus.com/images/articles/michigan-western.png";
const socialDescription="Western brings Broc Lowry and its offensive backfield back almost intact. The defense that carried the Broncos in 2025 is rebuilding most of its front seven -- but not from scratch. The data-first Week 1 breakdown.";

export const metadata:Metadata={
  title:"Michigan vs. Western Michigan: What Actually Returns Decides This One",
  description:"Michigan opens 2026 against a Western Michigan team that returns its quarterback and backfield but is rebuilding its defensive front seven. Our opponent-adjusted model, plus our own roster-continuity audit for both teams.",
  openGraph:{type:"article",url:articleUrl,siteName:"Michigan Football Focus",title:"Michigan vs. Western Michigan: What Actually Returns Decides This One",description:socialDescription,images:[{url:articleImage,alt:"Michigan vs. Western Michigan, Week 1"}]},
  twitter:{card:"summary_large_image",title:"Michigan vs. Western Michigan: What Actually Returns Decides This One",description:socialDescription,images:[articleImage]}
};

const sections=[
  ["one-sentence","The game in one sentence"],
  ["2025-comparison","Michigan vs. Western: the 2025 numbers"],
  ["what-returns","What actually returns"],
  ["three-matchups","Three matchups that decide it"],
  ["how-western-competes","How Western makes this uncomfortable"],
  ["how-michigan-controls","How Michigan takes control"],
  ["numbers-that-matter","The numbers that matter"],
  ["methodology","Sources & methodology"],
] as const;

const michiganColors=teamColors(data.michiganTeamId);
const opponentColors=teamColors(data.opponentTeamId);

function kickoffLabel(iso:string){
  const d=new Date(iso);
  return d.toLocaleString("en-US",{timeZone:"America/New_York",month:"long",day:"numeric",year:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:"short"});
}

function Stat({value,label,detail}:{value:string;label:string;detail?:string}){
  return <div className="feature-stat"><strong>{value}</strong><span>{label}</span>{detail&&<small>{detail}</small>}</div>;
}

function ContinuityColumn({name,teamId,barColor,offense,defense}:{name:string;teamId:number;barColor:string;offense:ContinuitySide;defense:ContinuitySide}){
  return <div>
    <div className="continuity-col-head"><img src={teamLogoUrl(teamId,64)} alt=""/><span>{name.toUpperCase()}</span></div>
    <div className="continuity-side-label">Offense · {offense.overallPct.toFixed(1)}% roster continuity</div>
    {offense.positions.map(p=><div className="continuity-row" key={p.group}>
      <span>{p.group}</span>
      <div className="continuity-track"><div className="continuity-fill" style={{"--fill":barColor,"--pct":`${p.pct}%`} as CSSProperties}/></div>
      <b>{p.pct.toFixed(0)}%</b>
    </div>)}
    <div className="continuity-side-label">Defense · {defense.overallPct.toFixed(1)}% roster continuity</div>
    {defense.positions.map(p=><div className="continuity-row" key={p.group}>
      <span>{p.group}</span>
      <div className="continuity-track"><div className="continuity-fill" style={{"--fill":barColor,"--pct":`${p.pct}%`} as CSSProperties}/></div>
      <b>{p.pct.toFixed(0)}%</b>
    </div>)}
  </div>;
}

function CompareBoard({rows}:{rows:CompareRow[]}){
  return <div className="stat-compare">
    <div className="stat-compare-key">
      <span><i style={{"--dot":MICHIGAN_BAR} as CSSProperties}/>MICHIGAN</span>
      <span><i style={{"--dot":OPPONENT_BAR} as CSSProperties}/>WESTERN MICHIGAN</span>
    </div>
    {rows.map(r=><div className="stat-compare-row" key={r.metric}>
      <div className="stat-compare-label">{r.metric}</div>
      <div className="stat-compare-bar-wrap">
        <div className="stat-compare-track-bg"><div className="stat-compare-fill" style={{"--fill":MICHIGAN_BAR,"--pct":`${percentileFromRank(r.michigan.rank)}%`} as CSSProperties}/></div>
        <b>{r.michigan.value} <small>#{r.michigan.rank}</small></b>
      </div>
      <div className="stat-compare-bar-wrap">
        <div className="stat-compare-track-bg"><div className="stat-compare-fill" style={{"--fill":OPPONENT_BAR,"--pct":`${percentileFromRank(r.opponent.rank)}%`} as CSSProperties}/></div>
        <b>{r.opponent.value} <small>#{r.opponent.rank}</small></b>
      </div>
    </div>)}
  </div>;
}

export default function MichiganWesternMichiganPreview(){
  return <article className="focus-article feature-article">
    <div className="article-reading-progress" aria-hidden="true"/>
    <div className="focus-article-shell feature-shell">
      <Link className="feature-back" href="/articles">← THE NOTEBOOK</Link>

      <header className="focus-article-hero matchup-hero feature-hero">
        <img src="/images/articles/michigan-western.png" alt="Michigan Wolverines vs. Western Michigan Broncos"/>
        <div className="focus-article-hero-copy">
          <span className="focus-article-eyebrow">WEEK 1 · SEPT. 5 · THE BIG HOUSE</span>
          <h1>Michigan vs. Western Michigan</h1>
          <p className="feature-headline">{data.oneSentence}</p>
          <div className="focus-article-meta"><span>{kickoffLabel(data.kickoffISO)}</span><span>{data.venue}</span><span>DATA PREVIEW</span></div>
        </div>
      </header>

      <div className="feature-matchup-card">
        <div><img src={teamLogoUrl(data.michiganTeamId,64)} alt=""/><span>MICHIGAN</span><strong>{`#${data.compositeComparison.michigan.overall.rank}`}</strong><small>{`${data.compositeComparison.michigan.overall.value} OVERALL`}</small></div>
        <div className="feature-matchup-center"><span>COMPOSITE</span><b>{data.compositeComparison.overallEdge}</b><small>MICHIGAN OVERALL EDGE</small></div>
        <div><img src={teamLogoUrl(data.opponentTeamId,64)} alt=""/><span>WESTERN</span><strong>{`#${data.compositeComparison.opponent.overall.rank}`}</strong><small>{`${data.compositeComparison.opponent.overall.value} OVERALL`}</small></div>
      </div>

      <section className="feature-quick-read" aria-label="Quick read">
        <div className="feature-quick-label"><span>30-SECOND READ</span><strong>What kind of game this actually is.</strong></div>
        <div className="feature-stat-grid">
          <Stat value={data.opponentOffense.numbers[0].value} label="WMU RUSH DECISION RATE" detail="run-first by design"/>
          <Stat value="#65 vs #118" label="WMU RUSH VS. PASS SUCCESS RANK" detail="the exploitable split"/>
          <Stat value="#19 vs #34" label="MICH VS. WMU DEFENSE RANK" detail="both units are real"/>
          <Stat value="20% / 12%" label="WMU DL / LB SNAP CONTINUITY" detail="CBS Sports"/>
        </div>
      </section>

      <ArticleMobileToc sections={sections}/>

      <div className="feature-reading-layout">
        <aside className="feature-toc">
          <span>IN THIS PREVIEW</span>
          <nav>{sections.map(([id,label],index)=><a href={`#${id}`} key={id}><b>{String(index+1).padStart(2,"0")}</b>{label}</a>)}</nav>
          <Link href="/games/401858428">GAME HUB →</Link>
        </aside>

        <div className="focus-article-body feature-body">
          <p className="focus-article-lede">Michigan opens the 2026 season against Western Michigan on Sept. 5 at Michigan Stadium -- the first game of the Kyle Whittingham era, with Jason Beck running the offense and Jay Hill running the defense. Western enters as the defending MAC champion, officially 10-4 after beating Kennesaw State in the Myrtle Beach Bowl.</p>

          <div className="feature-thesis" id="one-sentence"><span>THE PREVIEW IN ONE SENTENCE</span><strong>{data.heroThesis}</strong></div>

          <section id="2025-comparison" className="feature-story-section">
            <div className="feature-section-number">01</div><div className="feature-section-kicker">2025 BASELINE</div>
            <h2>Michigan vs. Western Michigan: the 2025 numbers</h2>
            <p>Every metric below comes from the same opponent-adjusted model, run for both teams at once and re-verified live for this preview. Bar length is each team's national percentile on that stat (out of 136 FBS teams) -- not the raw value -- so a rate stat and a yards-per-play stat land on one honestly comparable scale.</p>

            <div className="feature-section-kicker" style={{marginTop:28}}>OFFENSE</div>
            <CompareBoard rows={data.offenseCompareRows}/>
            <p><strong>{data.michiganOffenseTakeaway}</strong> {data.opponentOffense.takeaway}</p>

            <div className="feature-section-kicker" style={{marginTop:28}}>DEFENSE</div>
            <CompareBoard rows={data.defenseCompareRows}/>
            <p><strong>{data.michiganDefenseTakeaway}</strong> {data.opponentDefense.takeaway}</p>

            <div className="feature-versus-stat">
              <div><small>WMU ADJ. RUSH SUCCESS</small><strong>{data.opponentOffense.numbers[1].value}</strong><span>{data.opponentOffense.numbers[1].detail}</span></div>
              <b>VS</b>
              <div><small>WMU ADJ. PASS SUCCESS</small><strong>{data.opponentOffense.numbers[2].value}</strong><span>{data.opponentOffense.numbers[2].detail}</span></div>
            </div>
            <p>That split -- roughly average on the ground, bottom-quarter through the air -- is the widest internal gap on either team's offense, and it's the foundation for the first matchup below.</p>
          </section>

          <section id="what-returns" className="feature-story-section">
            <div className="feature-section-number">02</div><div className="feature-section-kicker">2026 CONTINUITY</div>
            <h2>What actually returns</h2>
            <p>This is where the story flips again. We built our own roster-continuity audit for <em>both</em> teams -- matching each team's 2025 and 2026 official rosters player by player, position by position -- so this comparison is apples-to-apples instead of borrowed from two different outside sources.</p>

            <div className="continuity-panel">
              <div className="continuity-overall">
                <div><strong style={{color:michiganColors.secondary}}>{data.continuity.michigan.offense.overallPct.toFixed(0)}%</strong><span>MICHIGAN OFFENSE</span></div>
                <div><strong style={{color:michiganColors.secondary}}>{data.continuity.michigan.defense.overallPct.toFixed(0)}%</strong><span>MICHIGAN DEFENSE</span></div>
                <div><strong>{data.continuity.opponent.offense.overallPct.toFixed(0)}%</strong><span>WESTERN OFFENSE</span></div>
                <div><strong>{data.continuity.opponent.defense.overallPct.toFixed(0)}%</strong><span>WESTERN DEFENSE</span></div>
              </div>
              <div className="continuity-grid">
                <ContinuityColumn name="Michigan" teamId={data.michiganTeamId} barColor={MICHIGAN_BAR} offense={data.continuity.michigan.offense} defense={data.continuity.michigan.defense}/>
                <ContinuityColumn name="Western Michigan" teamId={data.opponentTeamId} barColor={OPPONENT_BAR} offense={data.continuity.opponent.offense} defense={data.continuity.opponent.defense}/>
              </div>
              <div className="continuity-external">
                <strong style={{color:"#fff"}}>Externally researched, snap-weighted (for comparison):</strong> {data.continuity.opponentExternal.source} has Western Michigan returning {data.continuity.opponentExternal.offenseOverallPct}% of offensive snaps and {data.continuity.opponentExternal.defenseOverallPct}% of defensive snaps overall -- {data.continuity.opponentExternal.offensePositions.map(p=>`${p.group} ${p.pct}%`).join(", ")} on offense; {data.continuity.opponentExternal.defensePositions.map(p=>`${p.group} ${p.pct}%`).join(", ")} on defense.
              </div>
              <div className="continuity-note">{data.continuity.divergenceNote}</div>
            </div>
            <p>The headline: Michigan returns meaningfully more of both sides of the ball than Western does by this measure. And on Western's side specifically, the offensive backfield and receiving room return considerably more than the defensive front seven -- exactly the imbalance that shapes the matchups below.</p>
          </section>

          <section id="three-matchups" className="feature-story-section">
            <div className="feature-section-number">03</div><div className="feature-section-kicker">THE CORE OF THIS PREVIEW</div>
            <h2>Three matchups that decide the game</h2>
            {data.matchups.map((m,i)=><div key={m.id} style={i>0?{marginTop:44,paddingTop:36,borderTop:"1px solid #21394e"}:undefined}>
              <div className="feature-section-kicker">{m.kicker}</div>
              <h3 style={{font:"700 clamp(22px,2.6vw,30px)/1.15 var(--display)",margin:"8px 0 14px",color:"#fff"}}>{m.title}</h3>
              <div className="feature-pullquote" style={{fontSize:"clamp(16px,2vw,20px)",padding:"18px 22px",margin:"18px 0"}}>{m.question}</div>
              <div className="feature-data-list">
                {m.numbers.map(n=><span key={n.label}><b>{n.value}</b> {n.label}{n.detail?` — ${n.detail}`:""}</span>)}
              </div>
              {m.narrative.map((p,pi)=><p key={pi}>{p}</p>)}
            </div>)}
          </section>

          <section id="how-western-competes" className="feature-story-section">
            <div className="feature-section-number">04</div><div className="feature-section-kicker">STRESS-TESTING MICHIGAN</div>
            <h2>How Western makes this uncomfortable</h2>
            <p>This isn't a preview written from the assumption of a comfortable Michigan win. Here's Western's actual path to making it competitive, validated against the data above rather than generic keys to the game.</p>
            <div className="feature-checklist"><span>WESTERN'S SCRIPT</span>{data.howOpponentCompetes.map((line,i)=><b key={i}>{line}</b>)}</div>
          </section>

          <section id="how-michigan-controls" className="feature-story-section">
            <div className="feature-section-number">05</div><div className="feature-section-kicker">FLIP IT</div>
            <h2>How Michigan takes control</h2>
            <p>Now the other side of the same matchup data.</p>
            <div className="feature-checklist"><span>MICHIGAN'S SCRIPT</span>{data.howMichiganControls.map((line,i)=><b key={i}>{line}</b>)}</div>
          </section>

          <section id="numbers-that-matter" className="feature-story-section feature-final-section">
            <div className="feature-section-number">06</div><div className="feature-section-kicker">THE SHORT LIST</div>
            <h2>The numbers that matter</h2>
            <p>Everything above, distilled to the handful of numbers actually worth remembering.</p>
            <div className="feature-data-list" style={{gridTemplateColumns:"1fr"}}>
              {data.numbersThatMatter.map(n=><span key={n.label} style={{alignItems:"flex-start",flexDirection:"column",gap:2,padding:"13px 15px"}}>
                <span><b>{n.value}</b> {n.label}</span>
                <small style={{color:"#8298ab",fontSize:11,lineHeight:1.5}}>{n.why}</small>
              </span>)}
            </div>
            {data.market&&<p style={{marginTop:20,fontSize:13,color:"#8298ab"}}>Market context: {data.market.book} has {data.market.spread} ({data.market.winChance} implied win probability), as of {data.market.asOf}, via <a href={data.market.sourceUrl} target="_blank" rel="noreferrer" style={{color:"#ffcb05"}}>{data.market.source}</a>. That's the market's read, not our model's -- kept separate from every opponent-adjusted claim above.</p>}
            <div className="feature-verdict"><span>OUR READ</span><strong>{data.heroThesis}</strong><p>Michigan is the better team on paper by a wide margin. The version of this game that stays uncomfortable for Michigan the longest is the one where Western wins early downs, plays a low-possession game, and never lets its rebuilt front seven get exposed in obvious passing situations.</p></div>
          </section>

          <section id="methodology" className="feature-story-section">
            <div className="feature-section-number">07</div><div className="feature-section-kicker">HOW THIS WAS BUILT</div>
            <h2>Sources & methodology</h2>
            <p style={{fontSize:14,color:"#aebdca"}}><strong style={{color:"#fff"}}>Validated opponent-adjusted numbers: </strong>{data.methodology.validated}</p>
            <p style={{fontSize:14,color:"#aebdca"}}><strong style={{color:"#fff"}}>Our internal roster/continuity numbers: </strong>{data.methodology.internal}</p>
            <p style={{fontSize:14,color:"#aebdca"}}><strong style={{color:"#fff"}}>External research (ESPN / CBS): </strong>{data.methodology.external}</p>
            <p style={{fontSize:14,color:"#aebdca"}}><strong style={{color:"#fff"}}>Market line: </strong>{data.methodology.market}</p>
          </section>
        </div>
      </div>

      <section className="focus-article-explore feature-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>Don't stop at the final whistle.</h2></div>
        <div className="focus-article-link-grid">
          <Link href="/games/401858428"><strong>Michigan vs. Western Michigan game hub</strong><p>Sitewide Ridge ratings, matchup details and the current market spread.</p><span>OPEN GAME HUB →</span></Link>
          <Link href="/analytics"><strong>Michigan analytics</strong><p>Explore the opponent-adjusted ratings behind this preview.</p><span>EXPLORE DATA →</span></Link>
          <Link href="/methodology"><strong>How we grade the evidence</strong><p>What "validated," "research-only," "raw" and "adjusted" mean sitewide.</p><span>READ METHODOLOGY →</span></Link>
        </div>
      </section>

      <section className="focus-article-sources">
        <strong>REPORTING &amp; DATA SOURCES</strong>
        <div>{data.sources.map(({label,url})=><a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div>
      </section>

      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}
