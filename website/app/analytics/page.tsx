import Link from "next/link";
import {AnalyticsYearSwitch} from "../../components/AnalyticsYearSwitch";
import {metricDisplay,overviewTraits,rankDisplay,ridgeOverview,type RidgeOverview} from "../../lib/ridge-analytics";

const years=Array.from({length:17},(_,i)=>2010+i);
const metricLabels={ppd:"POINTS / DRIVE",ypd:"YARDS / DRIVE",success:"SUCCESS RATE",scoring:"SCORING DRIVE %"} as const;
const metricCopy={
  ppd:{
    offense:"How efficiently Michigan turns possessions into points after adjusting for opponent strength.",
    defense:"How effectively Michigan keeps opponents from turning possessions into points after adjustment."
  },
  ypd:{
    offense:"How much field position Michigan creates on a typical drive against an average FBS defense.",
    defense:"How much field position Michigan gives up on a typical opponent possession."
  },
  success:{
    offense:"How consistently the offense stays ahead of the sticks and wins down-to-down.",
    defense:"How consistently the defense knocks opposing offenses off schedule."
  },
  scoring:{
    offense:"How often Michigan finishes a possession with points after opponent adjustment.",
    defense:"How often opposing possessions reach the scoreboard against Michigan after adjustment."
  },
} as const;

function Profile({title,side,data}:{title:string;side:"offense"|"defense";data:RidgeOverview}){
  const block=data[side];
  const cards=[
    {
      key:"rating",
      label:`${side.toUpperCase()} RATING`,
      value:block.rating.toFixed(1),
      rank:rankDisplay(block.rank,block.field_size),
      copy:`Michigan's complete ${side} profile, combining scoring efficiency, field movement, success rate and scoring-drive rate.`
    },
    ...(Object.keys(metricLabels) as Array<keyof typeof metricLabels>).map(metric=>({
      key:metric,
      label:metricLabels[metric],
      value:metricDisplay(metric,block.metrics[metric].value),
      rank:rankDisplay(block.metrics[metric].rank,block.metrics[metric].field_size),
      copy:metricCopy[metric][side]
    })),
  ];

  return <section className="analytics-overview-section">
    <h2>{title}</h2>
    <div className="analytics-identity-grid">
      {cards.map(card=><article key={card.key}>
        <i aria-hidden="true">◇</i>
        <span>{card.label}</span>
        <strong>{card.value}</strong>
        <small>NATIONAL RANK</small>
        <b>{card.rank}</b>
        <p>{card.copy}</p>
      </article>)}
    </div>
  </section>;
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
    ["/analytics/offense","OFFENSE","See how Michigan creates points, yards and efficient possessions","/images/analytics/overview-offense.png"],
    ["/analytics/defense","DEFENSE","See where Michigan suffocates offenses — and where cracks appear","/images/analytics/overview-defense.png"],
    ["/analytics/players","PLAYERS","Find the players driving Michigan's production and efficiency","/images/analytics/overview-players.png"],
    ["/analytics/national","NATIONAL COMPARISON","Stack Michigan against the rest of college football","/images/analytics/overview-national.png"],
  ] as const;

  return <div className="analytics-overview">
    <AnalyticsYearSwitch year={year}/>

    <section className="analytics-overview-hero">
      <div className="analytics-overview-hero-copy">
        <h1>MICHIGAN<br/><b>ANALYTICS</b></h1>
        <span>{year} TEAM PROFILE</span>
        <p>{data
          ?"Go beyond the box score. See what Michigan does at an elite level, where the Wolverines can be attacked and how every major efficiency metric compares nationally after opponent adjustment."
          :"Opponent-adjusted Michigan analytics are not available for this season yet."}
        </p>
      </div>
      <div className="analytics-overview-hero-image" aria-hidden="true">
        <img src="/images/Bryce Underwood/Bryce4k.jpg" alt=""/>
      </div>
    </section>

    {data?<>
      <section className="analytics-summary-grid" aria-label="Michigan analytics summary">
        <article className="good">
          <i aria-hidden="true">O</i>
          <span>OFFENSIVE PROFILE</span>
          <strong>#{data.offense.rank}</strong>
          <small>NATIONALLY</small>
          <b>{data.offense.rating.toFixed(1)} overall rating</b>
        </article>
        <article className="good">
          <i aria-hidden="true">D</i>
          <span>DEFENSIVE PROFILE</span>
          <strong>#{data.defense.rank}</strong>
          <small>NATIONALLY</small>
          <b>{data.defense.rating.toFixed(1)} overall rating</b>
        </article>
        <article className="good">
          <i aria-hidden="true">+</i>
          <span>BIGGEST EDGE</span>
          <strong>#{best?.rank}</strong>
          <small>{best?.side.toUpperCase()}</small>
          <b>{best?.label}</b>
        </article>
        <article className="concern">
          <i aria-hidden="true">!</i>
          <span>PRESSURE POINT</span>
          <strong>#{concern?.rank}</strong>
          <small>{concern?.side.toUpperCase()}</small>
          <b>{concern?.label}</b>
        </article>
      </section>

      <Profile title="OFFENSIVE IDENTITY" side="offense" data={data}/>
      <Profile title="DEFENSIVE IDENTITY" side="defense" data={data}/>

      <section className="analytics-story-grid">
        <article className="analytics-story-card strength">
          <h2>WHERE MICHIGAN HAS AN EDGE</h2>
          {traits?.strengths.map(item=><div key={`${item.side}-${item.metric}`}>
            <i>✓</i>
            <span>
              <b>{item.label.toUpperCase()}</b>
              <small>{rankDisplay(item.rank,item.field_size)} · {metricDisplay(item.metric,item.value)}</small>
              <p>This is one of Michigan&apos;s strongest opponent-adjusted advantages compared with the rest of the FBS.</p>
            </span>
          </div>)}
        </article>

        <article className="analytics-story-card concern">
          <h2>WHERE MICHIGAN CAN BE ATTACKED</h2>
          {traits?.concerns.map(item=><div key={`${item.side}-${item.metric}`}>
            <i>!</i>
            <span>
              <b>{item.label.toUpperCase()}</b>
              <small>{rankDisplay(item.rank,item.field_size)} · {metricDisplay(item.metric,item.value)}</small>
              <p>This is one of Michigan&apos;s weaker national traits and a place opponents are more likely to find an advantage.</p>
            </span>
          </div>)}
        </article>
      </section>
    </>:<section className="analytics-overview-section">
      <div className="analytics-story-card">
        <h2>ANALYTICS NOT AVAILABLE YET</h2>
        <p>This season does not have a published opponent-adjusted analytics profile. Choose an available season to explore Michigan&apos;s performance.</p>
      </div>
    </section>}

    <section className="analytics-overview-section analytics-explore">
      <h2>GO DEEPER</h2>
      <div className="analytics-explore-grid">
        {explore.map(([href,title,copy,image])=><Link href={`${href}?year=${year}`} className="analytics-explore-card" key={title}>
          <div className="analytics-explore-image" style={{backgroundImage:`linear-gradient(180deg,transparent 30%,rgba(3,20,38,.95)),url('${image}')`}}/>
          <div>
            <h3>{title}</h3>
            <p>{copy}</p>
            <b>›</b>
          </div>
        </Link>)}
      </div>
      <div className="analytics-explore-secondary">
        <Link href={`/analytics/trends?year=${year}`} style={{backgroundImage:"linear-gradient(90deg,rgba(3,20,38,.94),rgba(3,20,38,.56)),url('/images/analytics/overview-trends.png')"}}>
          <div>
            <h3>SEASON TRENDS</h3>
            <p>Track where Michigan improved, slipped or changed identity over the season</p>
          </div>
          <b>›</b>
        </Link>
        <Link href={`/analytics/staff?year=${year}`} style={{backgroundImage:"linear-gradient(90deg,rgba(3,20,38,.94),rgba(3,20,38,.56)),url('/images/analytics/overview-staff.png')"}}>
          <div>
            <h3>STAFF &amp; SCHEME</h3>
            <p>Connect Michigan&apos;s results to coaching, personnel and scheme</p>
          </div>
          <b>›</b>
        </Link>
      </div>
    </section>
  </div>;
}
