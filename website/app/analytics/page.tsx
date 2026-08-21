import Link from "next/link";
import {AnalyticsYearSwitch} from "../../components/AnalyticsYearSwitch";
import {metricDisplay,overviewTraits,rankDisplay,ridgeOverview,type RidgeOverview} from "../../lib/ridge-analytics";

const years=Array.from({length:17},(_,i)=>2010+i);
const metricLabels={ppd:"POINTS / DRIVE",ypd:"YARDS / DRIVE",success:"SUCCESS RATE",scoring:"SCORING DRIVE %"} as const;
const metricCopy={
  ppd:{offense:"Estimated scoring efficiency against an average FBS defense.",defense:"Estimated points allowed per drive against an average FBS offense."},
  ypd:{offense:"How much field the offense creates on a typical possession.",defense:"How much field the defense concedes on a typical possession."},
  success:{offense:"Down-to-down efficiency after opponent and schedule adjustment.",defense:"How often opposing plays stay efficient after adjustment."},
  scoring:{offense:"Share of possessions that produce points after adjustment.",defense:"Share of opponent possessions that produce points after adjustment."},
} as const;

function Profile({title,side,data}:{title:string;side:"offense"|"defense";data:RidgeOverview}){
  const block=data[side];
  const cards=[
    {key:"rating",label:`${side.toUpperCase()} RATING`,value:block.rating.toFixed(1),rank:rankDisplay(block.rank,block.field_size),copy:"Balanced ridge rating across PPD, YPD, success rate and scoring-drive rate."},
    ...(Object.keys(metricLabels) as Array<keyof typeof metricLabels>).map(metric=>({key:metric,label:metricLabels[metric],value:metricDisplay(metric,block.metrics[metric].value),rank:rankDisplay(block.metrics[metric].rank,block.metrics[metric].field_size),copy:metricCopy[metric][side]})),
  ];
  return <section className="analytics-overview-section"><h2>{title}</h2><div className="analytics-identity-grid">
    {cards.map(card=><article key={card.key}><i aria-hidden="true">◇</i><span>{card.label}</span><strong>{card.value}</strong><small>NATIONAL</small><b>{card.rank}</b><p>{card.copy}</p></article>)}
  </div></section>;
}

export default async function AnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const requested=Number(params.year);
  const year=years.includes(requested)?requested:2025;
  const data=ridgeOverview(year);
  const traits=data?overviewTraits(data):null;
  const best=traits?.strengths[0]??null;
  const concern=traits?.concerns[0]??null;
  const explore=[
    ["/analytics/offense","OFFENSE","How Michigan moves the ball","/images/analytics/overview-offense.png"],
    ["/analytics/defense","DEFENSE","How Michigan stops opponents","/images/analytics/overview-defense.png"],
    ["/analytics/players","PLAYERS","Who drives Michigan's success","/images/analytics/overview-players.png"],
    ["/analytics/national","NATIONAL COMPARISON","Where Michigan ranks nationally","/images/analytics/overview-national.png"],
  ] as const;

  return <div className="analytics-overview">
    <AnalyticsYearSwitch year={year}/>
    <section className="analytics-overview-hero">
      <div className="analytics-overview-hero-copy">
        <h1>MICHIGAN<br/><b>ANALYTICS</b></h1>
        <span>{year} REVIEW</span>
        <p>{data?"Opponent-adjusted offense and defense, fit across the full FBS schedule with the ridge model validated from 2014–2025.":"Validated ridge analytics are not available for this season yet."}</p>
      </div>
      <div className="analytics-overview-hero-image" aria-hidden="true"><img src="/images/Bryce Underwood/Bryce4k.jpg" alt=""/></div>
    </section>

    {data?<>
      <section className="analytics-summary-grid" aria-label="Michigan analytics summary">
        <article className="good"><i aria-hidden="true">O</i><span>OFFENSE</span><strong>#{data.offense.rank}</strong><small>NATIONAL</small><b>{data.offense.rating.toFixed(1)} rating</b></article>
        <article className="good"><i aria-hidden="true">D</i><span>DEFENSE</span><strong>#{data.defense.rank}</strong><small>NATIONAL</small><b>{data.defense.rating.toFixed(1)} rating</b></article>
        <article className="good"><i aria-hidden="true">+</i><span>BEST TRAIT</span><strong>#{best?.rank}</strong><small>{best?.side.toUpperCase()}</small><b>{best?.label}</b></article>
        <article className="concern"><i aria-hidden="true">!</i><span>BIGGEST CONCERN</span><strong>#{concern?.rank}</strong><small>{concern?.side.toUpperCase()}</small><b>{concern?.label}</b></article>
      </section>

      <Profile title="OFFENSIVE PROFILE" side="offense" data={data}/>
      <Profile title="DEFENSIVE PROFILE" side="defense" data={data}/>

      <section className="analytics-story-grid">
        <article className="analytics-story-card strength"><h2>WHAT MICHIGAN DOES WELL</h2>{traits?.strengths.map(item=><div key={`${item.side}-${item.metric}`}><i>✓</i><span><b>{item.label.toUpperCase()}</b><small>{rankDisplay(item.rank,item.field_size)} · {metricDisplay(item.metric,item.value)}</small><p>{item.side} is one of Michigan&apos;s strongest opponent-adjusted national traits.</p></span></div>)}</article>
        <article className="analytics-story-card concern"><h2>WHERE MICHIGAN TRAILS</h2>{traits?.concerns.map(item=><div key={`${item.side}-${item.metric}`}><i>!</i><span><b>{item.label.toUpperCase()}</b><small>{rankDisplay(item.rank,item.field_size)} · {metricDisplay(item.metric,item.value)}</small><p>This is one of Michigan&apos;s lowest-ranked opponent-adjusted traits nationally.</p></span></div>)}</article>
      </section>
    </>:<section className="analytics-overview-section"><div className="analytics-story-card"><h2>RIDGE ANALYTICS UNAVAILABLE</h2><p>This season does not have a validated published ridge artifact. Select a validated season from 2014–2025.</p></div></section>}

    <section className="analytics-overview-section analytics-explore"><h2>EXPLORE ANALYTICS</h2><div className="analytics-explore-grid">
      {explore.map(([href,title,copy,image])=><Link href={`${href}?year=${year}`} className="analytics-explore-card" key={title}><div className="analytics-explore-image" style={{backgroundImage:`linear-gradient(180deg,transparent 30%,rgba(3,20,38,.95)),url('${image}')`}}/><div><h3>{title}</h3><p>{copy}</p><b>›</b></div></Link>)}
    </div><div className="analytics-explore-secondary">
      <Link href={`/analytics/trends?year=${year}`} style={{backgroundImage:"linear-gradient(90deg,rgba(3,20,38,.94),rgba(3,20,38,.56)),url('/images/analytics/overview-trends.png')"}}><div><h3>TRENDS</h3><p>How Michigan changed over the season</p></div><b>›</b></Link>
      <Link href={`/analytics/staff?year=${year}`} style={{backgroundImage:"linear-gradient(90deg,rgba(3,20,38,.94),rgba(3,20,38,.56)),url('/images/analytics/overview-staff.png')"}}><div><h3>STAFF &amp; SCHEME</h3><p>Connect performance to personnel and scheme</p></div><b>›</b></Link>
    </div></section>
  </div>;
}
