import Link from "next/link";
import {AnalyticsYearSwitch} from "../../components/AnalyticsYearSwitch";
import {metricDisplay,michiganFanSeason,overviewTraits,pct,rankDisplay,ridgeOverview} from "../../lib/ridge-analytics";

const years=Array.from({length:17},(_,i)=>2010+i);

function SummaryStat({label,value,detail}:{label:string;value:string;detail:string}){
  return <div className="ao-snapshot-stat">
    <span>{label}</span>
    <strong>{value}</strong>
    <small>{detail}</small>
  </div>;
}

function UnitRow({label,value,detail,tone}:{label:string;value:string;detail:string;tone:"good"|"elite"|"neutral"}){
  return <div className="ao-unit-row">
    <div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>
    <b className={`ao-pill ${tone}`}>{tone==="elite"?"ELITE":tone==="good"?"STRONG":"SOLID"}</b>
  </div>;
}

function UnitOverview({side,year,rank,rows,copy}:{side:"OFFENSE"|"DEFENSE";year:number;rank:number;rows:Array<{label:string;value:string;detail:string;tone:"good"|"elite"|"neutral"}>;copy:string}){
  const href=side==="OFFENSE"?`/analytics/offense?year=${year}`:`/analytics/defense?year=${year}`;
  return <article className="ao-unit-card">
    <header>
      <div><small>{side} OVERVIEW</small><strong>#{rank} <span>nationally</span></strong></div>
      <Link href={href}>View all {side.toLowerCase()} →</Link>
    </header>
    <div className="ao-unit-rows">{rows.map(row=><UnitRow key={row.label} {...row}/>)}</div>
    <p>{copy}</p>
  </article>;
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
      ? `Defense set the standard for this Michigan team. The Wolverines paired that strength with an offense that stayed efficient enough to control games and avoid putting the defense in bad spots.`
      : `Michigan's offense drove the team, while the defense complemented it by holding opponents to ${season.pointsPerResolvedPossessionAllowed.toFixed(2)} points per possession.`
    :null;

  const offenseTone=data&&data.offense.rank<=10?"elite" as const:data&&data.offense.rank<=35?"good" as const:"neutral" as const;
  const defenseTone=data&&data.defense.rank<=10?"elite" as const:data&&data.defense.rank<=35?"good" as const:"neutral" as const;

  return <div className="analytics-overview ao-page">
    <AnalyticsYearSwitch year={year}/>

    <section className="ao-hero">
      <div className="ao-hero-copy">
        <span>{year} SEASON OVERVIEW</span>
        <h1>MICHIGAN</h1>
        <p>The quick read on the Wolverines.</p>
      </div>
      <div className="ao-hero-image" aria-hidden="true"><img src="/images/analytics/overview-header.png" alt=""/></div>
    </section>

    {data&&season?<div className="ao-content">
      <section className="ao-card ao-snapshot">
        <h2>SEASON SNAPSHOT</h2>
        <div className="ao-snapshot-grid">
          <SummaryStat label="GAMES" value={String(season.games)} detail={`${year} season`}/>
          <SummaryStat label="OFFENSE" value={`#${data.offense.rank}`} detail="national rank"/>
          <SummaryStat label="DEFENSE" value={`#${data.defense.rank}`} detail="national rank"/>
          <SummaryStat label="YARDS / GAME" value={season.yardsPerGame.toFixed(0)} detail={`${season.yardsPerPlay.toFixed(2)} per play`}/>
          <SummaryStat label="YARDS ALLOWED" value={season.yardsAllowedPerGame.toFixed(0)} detail={`${season.yardsAllowedPerPlay.toFixed(2)} per play`}/>
          <SummaryStat label="SCORING DRIVES" value={pct(season.scoringRatePerPossession)} detail="of possessions"/>
        </div>
      </section>

      {identity&&<section className="ao-card ao-identity">
        <div className="ao-identity-mark">M</div>
        <div><span>TEAM IDENTITY</span><strong>{identity}</strong></div>
      </section>}

      <section className="ao-units">
        <UnitOverview
          side="OFFENSE"
          year={year}
          rank={data.offense.rank}
          rows={[
            {label:"POINTS / DRIVE",value:metricDisplay("ppd",data.offense.metrics.ppd.value),detail:`${rankDisplay(data.offense.metrics.ppd.rank,data.offense.metrics.ppd.field_size)}`,tone:offenseTone},
            {label:"SUCCESS RATE",value:metricDisplay("success",data.offense.metrics.success.value),detail:`${rankDisplay(data.offense.metrics.success.rank,data.offense.metrics.success.field_size)}`,tone:offenseTone},
            {label:"EXPLOSIVE PLAYS",value:pct(season.explosivePlayRate),detail:`#${season.national_explosivePlayRate_rank} nationally`,tone:season.national_explosivePlayRate_rank<=15?"elite":season.national_explosivePlayRate_rank<=40?"good":"neutral"},
          ]}
          copy="Michigan's offense in three numbers: scoring efficiency, consistency, and big-play creation."
        />
        <UnitOverview
          side="DEFENSE"
          year={year}
          rank={data.defense.rank}
          rows={[
            {label:"POINTS ALLOWED / DRIVE",value:metricDisplay("ppd",data.defense.metrics.ppd.value),detail:`${rankDisplay(data.defense.metrics.ppd.rank,data.defense.metrics.ppd.field_size)}`,tone:defenseTone},
            {label:"SUCCESS RATE ALLOWED",value:metricDisplay("success",data.defense.metrics.success.value),detail:`${rankDisplay(data.defense.metrics.success.rank,data.defense.metrics.success.field_size)}`,tone:defenseTone},
            {label:"EXPLOSIVES ALLOWED",value:pct(season.explosivePlayRateAllowed),detail:`#${season.national_explosivePlayRateAllowed_rank} nationally`,tone:season.national_explosivePlayRateAllowed_rank<=15?"elite":season.national_explosivePlayRateAllowed_rank<=40?"good":"neutral"},
          ]}
          copy="Michigan's defense in three numbers: preventing points, winning downs, and limiting chunk plays."
        />
      </section>

      <section className="ao-takeaways">
        <article className="ao-takeaway strength">
          <span>BIGGEST STRENGTH</span>
          {best&&<><strong>#{best.rank} · {best.label}</strong><p>Michigan's best opponent-adjusted trait relative to the rest of the FBS.</p></>}
        </article>
        <article className="ao-takeaway concern">
          <span>BIGGEST CONCERN</span>
          {concern&&<><strong>#{concern.rank} · {concern.label}</strong><p>The clearest area where Michigan trails its other national metrics.</p></>}
        </article>
      </section>

      <section className="ao-deeper">
        <h2>EXPLORE MORE</h2>
        <div className="ao-deeper-grid">
          <Link href={`/analytics/offense?year=${year}`} className="ao-deeper-card" style={{backgroundImage:"linear-gradient(180deg,rgba(3,20,38,.06),rgba(3,20,38,.96)),url('/images/analytics/overview-offense.png')"}}><div><strong>OFFENSE ANALYTICS</strong><span>Efficiency, run/pass splits and situational breakdowns.</span><b>Explore offense →</b></div></Link>
          <Link href={`/analytics/defense?year=${year}`} className="ao-deeper-card" style={{backgroundImage:"linear-gradient(180deg,rgba(3,20,38,.06),rgba(3,20,38,.96)),url('/images/analytics/overview-defense.png')"}}><div><strong>DEFENSE ANALYTICS</strong><span>Stops, pressure, explosives and opponent splits.</span><b>Explore defense →</b></div></Link>
          <Link href={`/analytics/staff?year=${year}`} className="ao-deeper-card" style={{backgroundImage:"linear-gradient(180deg,rgba(3,20,38,.06),rgba(3,20,38,.96)),url('/images/analytics/overview-staff.png')"}}><div><strong>STAFF ANALYTICS</strong><span>Play calling, tendencies and coaching decisions.</span><b>Explore staff →</b></div></Link>
        </div>
      </section>
    </div>:<section className="ao-content"><div className="ao-card ao-empty"><h2>ANALYTICS NOT AVAILABLE YET</h2><p>This season does not have a published Michigan analytics profile. Choose an available season to continue.</p></div></section>}
  </div>;
}
