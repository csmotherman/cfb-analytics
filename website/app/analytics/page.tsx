import Link from "next/link";

const years=Array.from({length:17},(_,i)=>2010+i);
const blank="—";

export default async function AnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const requested=Number(params.year);
  const year=years.includes(requested)?requested:2025;
  const isTbd=year===2026;
  const summary=["OFFENSE","DEFENSE","RUN GAME","BIGGEST CONCERN"];
  const identity=["RUN THE BALL","STAY ON SCHEDULE","CREATE EXPLOSIVES","PREVENT EXPLOSIVES","FINISH DRIVES"];
  const strengths=["RUN THE FOOTBALL EFFICIENTLY","PREVENT EXPLOSIVE PLAYS","CREATE DISRUPTION"];
  const concerns=["FINISHING DRIVES","PASSING CONSISTENCY","RED ZONE TOUCHDOWNS"];
  const explore=[
    ["/analytics/offense","OFFENSE","How Michigan moves the ball","/images/analytics/overview-offense.png"],
    ["/analytics/defense","DEFENSE","How Michigan stops opponents","/images/analytics/overview-defense.png"],
    ["/analytics/players","PLAYERS","Who drives Michigan's success","/images/analytics/overview-players.png"],
    ["/analytics/national","NATIONAL COMPARISON","Where Michigan ranks nationally","/images/analytics/overview-national.png"],
  ] as const;

  return <div className="analytics-overview">
    <nav className="analytics-year-switch" aria-label="Analytics season">
      <span className="year-calendar" aria-hidden="true">▦</span>
      {years.map(y=><Link key={y} href={`/analytics?year=${y}`} className={year===y?"active":""}>{y}{y===2026&&<small>TBD</small>}</Link>)}
    </nav>

    <section className="analytics-overview-hero">
      <div className="analytics-overview-hero-copy">
        <h1>MICHIGAN<br/><b>ANALYTICS</b></h1>
        <span>{year} REVIEW{year===2025?" · 2026 OUTLOOK":""}</span>
        <p>{isTbd?"2026 analytics will populate as verified game data becomes available.":"The numbers behind where Michigan was elite, where it struggled, and what matters most entering the next season."}</p>
      </div>
      <div className="analytics-overview-hero-image" aria-hidden="true"><img src="/images/Bryce Underwood/Bryce4k.jpg" alt=""/></div>
    </section>

    <section className="analytics-summary-grid" aria-label="Michigan analytics summary">
      {summary.map((label,i)=><article className={i===3?"concern":"good"} key={label}><i aria-hidden="true">{i===0?"⌘":i===1?"♢":i===2?"⌁":"◎"}</i><span>{label}</span><strong>{blank}</strong><small>NATIONAL</small><b>{blank}</b></article>)}
    </section>

    <section className="analytics-overview-section"><h2>MICHIGAN'S IDENTITY</h2><div className="analytics-identity-grid">
      {identity.map(label=><article key={label}><i>◇</i><span>{label}</span><strong>{blank}</strong><small>{blank}</small><b>{blank}</b><p>Data coming soon.</p></article>)}
    </div></section>

    <section className="analytics-story-grid">
      <article className="analytics-story-card strength"><h2>WHAT MICHIGAN DOES WELL</h2>{strengths.map(item=><div key={item}><i>✓</i><span><b>{item}</b><small>{blank}</small><p>Data coming soon.</p></span></div>)}</article>
      <article className="analytics-story-card concern"><h2>WHAT MICHIGAN NEEDS TO FIX</h2>{concerns.map(item=><div key={item}><i>!</i><span><b>{item}</b><small>{blank}</small><p>Data coming soon.</p></span></div>)}</article>
    </section>

    <section className="analytics-overview-section analytics-explore"><h2>EXPLORE ANALYTICS</h2><div className="analytics-explore-grid">
      {explore.map(([href,title,copy,image])=><Link href={href} className="analytics-explore-card" key={title}><div className="analytics-explore-image" style={{backgroundImage:`linear-gradient(180deg,transparent 30%,rgba(3,20,38,.95)),url('${image}')`}}/><div><h3>{title}</h3><p>{copy}</p><b>›</b></div></Link>)}
    </div><div className="analytics-explore-secondary">
      <Link href="/analytics/trends"><span>⌁</span><div><h3>TRENDS</h3><p>Is Michigan getting better?</p></div><b>›</b></Link>
      <Link href="/analytics/staff"><span>♟</span><div><h3>STAFF &amp; SCHEME</h3><p>What the new staff could change</p></div><b>›</b></Link>
    </div></section>
  </div>;
}
