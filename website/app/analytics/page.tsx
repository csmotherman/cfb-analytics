import Link from "next/link";

const years=Array.from({length:17},(_,i)=>2010+i);
const blank="—";

export default async function AnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const requested=Number(params.year);
  const year=years.includes(requested)?requested:2025;
  const isTbd=year===2026;

  const summary=[
    {label:"OFFENSE",tone:"good"},
    {label:"DEFENSE",tone:"good"},
    {label:"RUN GAME",tone:"good"},
    {label:"BIGGEST CONCERN",tone:"concern"},
  ];
  const identity=["RUN THE BALL","STAY ON SCHEDULE","CREATE EXPLOSIVES","PREVENT EXPLOSIVES","FINISH DRIVES"];
  const strengths=["RUN THE FOOTBALL EFFICIENTLY","PREVENT EXPLOSIVE PLAYS","CREATE DISRUPTION"];
  const concerns=["FINISHING DRIVES","PASSING CONSISTENCY","RED ZONE TOUCHDOWNS"];
  const explore=[
    {href:"/analytics/offense",title:"OFFENSE",copy:"How Michigan moves the ball",image:"/images/analytics/overview-offense.png"},
    {href:"/analytics/defense",title:"DEFENSE",copy:"How Michigan stops opponents",image:"/images/analytics/overview-defense.png"},
    {href:"/analytics/players",title:"PLAYERS",copy:"Who drives Michigan's success",image:"/images/analytics/overview-players.png"},
    {href:"/analytics/national",title:"NATIONAL COMPARISON",copy:"Where Michigan ranks nationally",image:"/images/analytics/overview-national.png"},
  ];

  return <div className="analytics-overview">
    <nav className="analytics-year-switch" aria-label="Analytics season">
      {years.map(y=><Link key={y} href={`/analytics?year=${y}`} className={year===y?"active":""}>{y}{y===2026&&<small>TBD</small>}</Link>)}
    </nav>

    <section className="analytics-overview-hero">
      <div className="analytics-overview-hero-copy">
        <span>{year} REVIEW{year===2025?" · 2026 OUTLOOK":""}</span>
        <h1>MICHIGAN<br/><b>ANALYTICS</b></h1>
        <p>{isTbd?"2026 analytics will populate as verified game data becomes available.":"The numbers behind where Michigan was elite, where it struggled, and what mattered most that season."}</p>
      </div>
      <div className="analytics-overview-hero-image" aria-hidden="true"><img src="/images/Bryce Underwood/Bryce4k.jpg" alt=""/></div>
    </section>

    <section className="analytics-summary-grid" aria-label="Michigan analytics summary">
      {summary.map(card=><article className={card.tone} key={card.label}><span>{card.label}</span><strong>{blank}</strong><small>NATIONAL</small><b>{blank}</b></article>)}
    </section>

    <section className="analytics-overview-section">
      <h2>MICHIGAN'S IDENTITY</h2>
      <div className="analytics-identity-grid">
        {identity.map(label=><article key={label}><span>{label}</span><strong>{blank}</strong><small>{blank}</small><b>{blank}</b><p>Data coming soon.</p></article>)}
      </div>
    </section>

    <section className="analytics-story-grid">
      <article className="analytics-story-card strength"><h2>WHAT MICHIGAN DOES WELL</h2>{strengths.map(item=><div key={item}><i>✓</i><span><b>{item}</b><small>{blank}</small><p>Data coming soon.</p></span></div>)}</article>
      <article className="analytics-story-card concern"><h2>WHAT MICHIGAN NEEDS TO FIX</h2>{concerns.map(item=><div key={item}><i>!</i><span><b>{item}</b><small>{blank}</small><p>Data coming soon.</p></span></div>)}</article>
    </section>

    <section className="analytics-overview-section analytics-explore">
      <h2>EXPLORE ANALYTICS</h2>
      <div className="analytics-explore-grid">
        {explore.map(card=><Link href={card.href} className="analytics-explore-card" key={card.title}>
          <div className="analytics-explore-image" data-placeholder={card.image}><span>IMAGE</span></div>
          <div><h3>{card.title}</h3><p>{card.copy}</p><b>›</b></div>
        </Link>)}
      </div>
      <div className="analytics-explore-secondary">
        <Link href="/analytics/trends"><span>⌁</span><div><h3>TRENDS</h3><p>Is Michigan getting better?</p></div><b>›</b></Link>
        <Link href="/analytics/staff"><span>⌘</span><div><h3>STAFF &amp; SCHEME</h3><p>What the staff could change</p></div><b>›</b></Link>
      </div>
    </section>
  </div>;
}
