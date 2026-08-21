import Link from "next/link";
import {AnalyticsYearSwitch} from "../../components/AnalyticsYearSwitch";
import {metricDisplay,michiganFanSeason,overviewTraits,pct,perGame,rankDisplay,ridgeOverview} from "../../lib/ridge-analytics";

const years=Array.from({length:17},(_,i)=>2010+i);

function SectionHeader({title,href,label}:{title:string;href:string;label:string}){
  return <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:"1rem",marginBottom:"1rem"}}>
    <h2 style={{margin:0}}>{title}</h2>
    <Link href={href} style={{fontSize:".8rem",fontWeight:900,letterSpacing:".04em",textTransform:"uppercase",whiteSpace:"nowrap"}}>{label} →</Link>
  </div>;
}

function StatCards({cards}:{cards:Array<[string,string,string,string]>}){
  return <div className="analytics-identity-grid">
    {cards.map(([label,value,detail,copy])=><article key={label}>
      <i aria-hidden="true">◇</i>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
      <p>{copy}</p>
    </article>)}
  </div>;
}

export default async function AnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const requested=Number(params.year);
  const year=years.includes(requested)?requested:2025;
  const data=ridgeOverview(year);
  const season=michiganFanSeason(year);
  const traits=data?overviewTraits(data):null;
  const best=traits?.strengths[0]??null;
  const concern=traits?.concerns[0]??null;

  const identity=data&&season
    ? data.defense.rank<data.offense.rank
      ? `Michigan was built around its defense, while the offense leaned on a run game that produced a ${pct(season.rushSuccessRate)} success rate and ${season.rushYardsPerAttempt.toFixed(2)} yards per carry.`
      : `Michigan's offense set the pace, while the defense held opponents to ${season.pointsPerResolvedPossessionAllowed.toFixed(2)} points per possession.`
    :null;

  return <div className="analytics-overview">
    <AnalyticsYearSwitch year={year}/>

    <section className="analytics-overview-hero">
      <div className="analytics-overview-hero-copy">
        <h1>MICHIGAN<br/><b>ANALYTICS</b></h1>
        <span>{year} SEASON OVERVIEW</span>
        <p>{data
          ?"The quick read on Michigan: how good the Wolverines were, what defined the team, and where the offense and defense ranked nationally."
          :"Michigan analytics are not available for this season yet."}
        </p>
      </div>
      <div className="analytics-overview-hero-image" aria-hidden="true"><img src="images/analytics/overview-header.png" alt=""/></div>
    </section>

    {data&&season?<>
      <section className="analytics-overview-section">
        <h2>MICHIGAN AT A GLANCE</h2>
        <section className="analytics-summary-grid" aria-label="Michigan season at a glance">
          <article className="good"><i>O</i><span>OFFENSE</span><strong>#{data.offense.rank}</strong><small>NATIONALLY</small><b>{data.offense.rating.toFixed(1)} rating</b></article>
          <article className="good"><i>D</i><span>DEFENSE</span><strong>#{data.defense.rank}</strong><small>NATIONALLY</small><b>{data.defense.rating.toFixed(1)} rating</b></article>
          <article className="good"><i>↑</i><span>TOTAL OFFENSE</span><strong>{season.yardsPerGame.toFixed(0)}</strong><small>YARDS / GAME</small><b>{season.yardsPerPlay.toFixed(2)} yards / play</b></article>
          <article className="good"><i>↓</i><span>TOTAL DEFENSE</span><strong>{season.yardsAllowedPerGame.toFixed(0)}</strong><small>YARDS ALLOWED / GAME</small><b>{season.yardsPerPlayAllowed.toFixed(2)} yards / play</b></article>
        </section>
      </section>

      {identity&&<section className="analytics-overview-section">
        <div className="analytics-story-card strength">
          <h2>TEAM IDENTITY</h2>
          <p>{identity}</p>
        </div>
      </section>}

      <section className="analytics-overview-section">
        <SectionHeader title="OFFENSE OVERVIEW" href={`/analytics/offense?year=${year}`} label="View all offense"/>
        <StatCards cards={[
          ["MAKING DRIVES COUNT",metricDisplay("ppd",data.offense.metrics.ppd.value),`#${data.offense.metrics.ppd.rank} NATIONALLY`,`Opponent-adjusted points per drive — the clearest measure of how efficiently Michigan turns possessions into points.`],
          ["RUSHING",`${perGame(season.rushYards,season.games).toFixed(0)} YPG`,`${season.rushYardsPerAttempt.toFixed(2)} YARDS / CARRY`,`${pct(season.rushSuccessRate)} of Michigan runs produced a successful result for the situation.`],
          ["THIRD DOWN",pct(season.thirdDownConversionRate),"CONVERSION RATE","How often Michigan keeps drives alive when another set of downs has to be earned."],
          ["EXPLOSIVE PLAYS",pct(season.explosivePlayRate),`#${season.national_explosivePlayRate_rank} NATIONALLY`,"How often the offense produces the chunk plays that flip field position and create scoring chances."],
        ]}/>
      </section>

      <section className="analytics-overview-section">
        <SectionHeader title="DEFENSE OVERVIEW" href={`/analytics/defense?year=${year}`} label="View all defense"/>
        <StatCards cards={[
          ["POINTS ALLOWED / DRIVE",metricDisplay("ppd",data.defense.metrics.ppd.value),`#${data.defense.metrics.ppd.rank} NATIONALLY`,`Opponent-adjusted scoring allowed per drive — a simple read on how difficult Michigan is to score against.`],
          ["RUN DEFENSE",`${season.rushYardsPerAttemptAllowed.toFixed(2)} YPC`,`${pct(season.rushSuccessRateAllowed)} SUCCESS ALLOWED`,"How efficiently opponents are able to stay on schedule by running the football."],
          ["THIRD DOWN DEFENSE",pct(season.thirdDownConversionRateAllowed),"CONVERSION RATE ALLOWED","How often Michigan gets off the field once an opponent reaches third down."],
          ["EXPLOSIVES ALLOWED",pct(season.explosivePlayRateAllowed),`#${season.national_explosivePlayRateAllowed_rank} NATIONALLY`,"How often Michigan gives up the chunk plays that can change a game in one snap."],
        ]}/>
      </section>

      <section className="analytics-story-grid">
        <article className="analytics-story-card strength">
          <h2>BIGGEST STRENGTH</h2>
          {best&&<div><i>✓</i><span><b>{best.label.toUpperCase()}</b><small>{rankDisplay(best.rank,best.field_size)} · {metricDisplay(best.metric,best.value)}</small><p>This is Michigan&apos;s strongest opponent-adjusted trait relative to the rest of the FBS.</p></span></div>}
        </article>
        <article className="analytics-story-card concern">
          <h2>BIGGEST CONCERN</h2>
          {concern&&<div><i>!</i><span><b>{concern.label.toUpperCase()}</b><small>{rankDisplay(concern.rank,concern.field_size)} · {metricDisplay(concern.metric,concern.value)}</small><p>This is the clearest area where Michigan trails its other national metrics.</p></span></div>}
        </article>
      </section>

      <section className="analytics-overview-section analytics-explore">
        <h2>KEEP EXPLORING</h2>
        <div className="analytics-explore-grid" style={{gridTemplateColumns:"repeat(2,minmax(0,1fr))"}}>
          <Link href={`/analytics/offense?year=${year}`} className="analytics-explore-card">
            <div className="analytics-explore-image" style={{backgroundImage:"linear-gradient(180deg,transparent 30%,rgba(3,20,38,.95)),url('/images/analytics/overview-offense.png')"}}/>
            <div><h3>OFFENSE</h3><p>Run/pass splits, drive efficiency, explosives, downs and situational performance.</p><b>›</b></div>
          </Link>
          <Link href={`/analytics/defense?year=${year}`} className="analytics-explore-card">
            <div className="analytics-explore-image" style={{backgroundImage:"linear-gradient(180deg,transparent 30%,rgba(3,20,38,.95)),url('/images/analytics/overview-defense.png')"}}/>
            <div><h3>DEFENSE</h3><p>Run defense, pass defense, havoc, explosives, scoring prevention and more.</p><b>›</b></div>
          </Link>
        </div>
      </section>
    </>:<section className="analytics-overview-section"><div className="analytics-story-card"><h2>ANALYTICS NOT AVAILABLE YET</h2><p>This season does not have a published Michigan analytics profile. Choose an available season to continue.</p></div></section>}
  </div>;
}
