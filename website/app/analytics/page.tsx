import Link from "next/link";
import {AnalyticsYearSwitch} from "../../components/AnalyticsYearSwitch";
import {OffensiveProfileRadar} from "../../components/OffensiveProfileRadar";
import {offensiveProfile} from "../../lib/offensive-profile";
import {fanTier,fanTierLabel,metricDisplay,michiganFanSeason,michiganRecord,michiganSnapshotRanks,overviewTraits,pct,ridgeOverview} from "../../lib/ridge-analytics";

const years=Array.from({length:17},(_,i)=>2010+i);

type MetricCard={label:string;value:string;rank:number;fieldSize:number;copy:string};

function RankBadge({rank,fieldSize}:{rank:number;fieldSize:number}){
  const tier=fanTier(rank,fieldSize);
  return <span className={`fan-rank-badge ${tier}`}>{fanTierLabel(rank,fieldSize)}</span>;
}

function MetricRow({metric}:{metric:MetricCard}){
  return <article className="fan-metric-row">
    <div className="fan-metric-main">
      <span className="fan-metric-label">{metric.label}</span>
      <strong>{metric.value}</strong>
      <div className="fan-metric-context"><span>#{metric.rank} nationally</span><RankBadge rank={metric.rank} fieldSize={metric.fieldSize}/></div>
    </div>
    <p>{metric.copy}</p>
  </article>;
}

function UnitOverview({side,title,rank,fieldSize,rating,href,metrics}:{side:"offense"|"defense";title:string;rank:number;fieldSize:number;rating:number;href:string;metrics:MetricCard[]}){
  return <section className={`fan-unit-card ${side}`}>
    <div className="fan-unit-head">
      <div>
        <span>{title}</span>
        <div className="fan-unit-rank"><strong>#{rank}</strong><small>NATIONALLY</small></div>
        <RankBadge rank={rank} fieldSize={fieldSize}/>
      </div>
      <div className="fan-unit-rating"><span>TEAM RATING</span><b>{rating.toFixed(1)}</b></div>
    </div>
    <div className="fan-unit-metrics">{metrics.map(metric=><MetricRow key={metric.label} metric={metric}/>)}</div>
    <Link className="fan-view-all" href={href}>View all {side} analytics <span>→</span></Link>
  </section>;
}

export default async function AnalyticsPage({searchParams}:{searchParams:Promise<{year?:string}>}){
  const params=await searchParams;
  const requested=Number(params.year);
  const year=years.includes(requested)?requested:2025;
  const data=ridgeOverview(year);
  const season=michiganFanSeason(year);
  const record=michiganRecord(year);
  const snapshotRanks=michiganSnapshotRanks(year);
  const profile=offensiveProfile(year);
  const traits=data?overviewTraits(data):null;
  const best=traits?.strengths[0]??null;
  const concern=traits?.concerns[0]??null;

  const identity=data&&season
    ? data.defense.rank<data.offense.rank
      ? `Michigan's defense was the stronger national unit. The Wolverines were hardest to beat when they forced offenses off schedule and let the run game control the flow of the game.`
      : `Michigan's offense was the stronger national unit. The Wolverines were at their best when they stayed ahead of the chains and consistently turned drives into points.`
    :null;

  const offenseMetrics:MetricCard[]=data&&season?[
    {label:"Making Drives Count",value:`${metricDisplay("ppd",data.offense.metrics.ppd.value)} pts / drive`,rank:data.offense.metrics.ppd.rank,fieldSize:data.offense.metrics.ppd.field_size,copy:"How efficiently Michigan turns a possession into points after accounting for the strength of the defense it faced."},
    {label:"Staying Ahead of the Chains",value:metricDisplay("success",data.offense.metrics.success.value),rank:data.offense.metrics.success.rank,fieldSize:data.offense.metrics.success.field_size,copy:"How often Michigan wins the down and keeps the offense out of obvious passing situations."},
    {label:"Big-Play Ability",value:pct(season.explosivePlayRate),rank:season.national_explosivePlayRate_rank,fieldSize:data.offense.field_size,copy:"How often Michigan creates a chunk play that can flip field position or change a drive in one snap."},
  ]:[];

  const defenseMetrics:MetricCard[]=data&&season?[
    {label:"Keeping Teams Off the Board",value:`${metricDisplay("ppd",data.defense.metrics.ppd.value)} pts / drive`,rank:data.defense.metrics.ppd.rank,fieldSize:data.defense.metrics.ppd.field_size,copy:"How well Michigan limits opponent scoring after accounting for the strength of the offenses it faced."},
    {label:"Knocking Offenses Off Schedule",value:metricDisplay("success",data.defense.metrics.success.value),rank:data.defense.metrics.success.rank,fieldSize:data.defense.metrics.success.field_size,copy:"How often Michigan prevents the offense from getting the result it needs on a play and creates tougher next downs."},
    {label:"Preventing Big Plays",value:pct(season.explosivePlayRateAllowed),rank:season.national_explosivePlayRateAllowed_rank,fieldSize:data.defense.field_size,copy:"How rarely Michigan allows the explosive gains that turn normal possessions into immediate scoring threats."},
  ]:[];

  const offensivePointsPerPlay=season&&season.offensivePlays?season.possessionPoints/season.offensivePlays:0;
  const defensivePointsPerPlay=season&&season.defensivePlays?season.possessionPointsAllowed/season.defensivePlays:0;

  return <div className="analytics-overview fan-overview">
    <AnalyticsYearSwitch year={year}/>
    <section className="analytics-overview-hero fan-overview-hero">
      <div className="analytics-overview-hero-copy"><h1>MICHIGAN<br/><b>ANALYTICS</b></h1><span>{year} SEASON OVERVIEW</span><p>{data?"The quick answer to three questions: how good was Michigan, what defined the team, and where did the Wolverines stand nationally?":"Michigan analytics are not available for this season yet."}</p></div>
      <div className="analytics-overview-hero-image" aria-hidden="true"><img src="/images/analytics/overview-header.png" alt=""/></div>
    </section>

    {data&&season?<>
      <section className="fan-section fan-snapshot">
        <div className="fan-section-title"><div><span>THE QUICK READ</span><h2>SEASON SNAPSHOT</h2></div></div>
        <div className="fan-snapshot-grid">
          {record&&<article className="fan-record-card">
            <span>RECORD</span>
            <strong>{record.record}</strong>
            <div className="fan-record-splits">
              <small><b>{record.regular.record}</b><em>REGULAR SEASON</em></small>
              <small><b>{record.postseason.games?record.postseason.record:"—"}</b><em>POSTSEASON</em></small>
            </div>
          </article>}

          <article className="fan-snapshot-rating-card">
            <span>OFFENSIVE RATING</span>
            <strong>{data.offense.rating.toFixed(1)}</strong>
            <RankBadge rank={data.offense.rank} fieldSize={data.offense.field_size}/>
            <small>#{data.offense.rank} NATIONALLY</small>
          </article>

          <article className="fan-snapshot-rating-card">
            <span>DEFENSIVE RATING</span>
            <strong>{data.defense.rating.toFixed(1)}</strong>
            <RankBadge rank={data.defense.rank} fieldSize={data.defense.field_size}/>
            <small>#{data.defense.rank} NATIONALLY</small>
          </article>

          <article className="fan-snapshot-yardage-card">
            <span>OFFENSE</span>
            <small className="fan-snapshot-subtitle">YARDS / GAME</small>
            <strong>{season.yardsPerGame.toFixed(0)}</strong>
            {snapshotRanks&&<RankBadge rank={snapshotRanks.yardsPerGame} fieldSize={snapshotRanks.fieldSize}/>} 
            {snapshotRanks&&<small>#{snapshotRanks.yardsPerGame} NATIONALLY</small>}
            <div className="fan-snapshot-secondary"><b>{season.yardsPerPlay.toFixed(2)}</b> YARDS / PLAY{snapshotRanks&&<em>#{snapshotRanks.yardsPerPlay} nationally</em>}</div>
          </article>

          <article className="fan-snapshot-yardage-card">
            <span>DEFENSE</span>
            <small className="fan-snapshot-subtitle">YARDS ALLOWED / GAME</small>
            <strong>{season.yardsAllowedPerGame.toFixed(0)}</strong>
            {snapshotRanks&&<RankBadge rank={snapshotRanks.yardsAllowedPerGame} fieldSize={snapshotRanks.fieldSize}/>} 
            {snapshotRanks&&<small>#{snapshotRanks.yardsAllowedPerGame} NATIONALLY</small>}
            <div className="fan-snapshot-secondary"><b>{season.yardsAllowedPerPlay.toFixed(2)}</b> YARDS / PLAY{snapshotRanks&&<em>#{snapshotRanks.yardsAllowedPerPlay} nationally</em>}</div>
          </article>

          {snapshotRanks&&<article className="fan-snapshot-points-card">
            <span>OFFENSE</span>
            <small className="fan-snapshot-subtitle">POINTS / PLAY</small>
            <strong>{offensivePointsPerPlay.toFixed(3)}</strong>
            <RankBadge rank={snapshotRanks.pointsPerPlay} fieldSize={snapshotRanks.fieldSize}/>
            <small>#{snapshotRanks.pointsPerPlay} NATIONALLY</small>
          </article>}

          {snapshotRanks&&<article className="fan-snapshot-points-card">
            <span>DEFENSE</span>
            <small className="fan-snapshot-subtitle">POINTS ALLOWED / PLAY</small>
            <strong>{defensivePointsPerPlay.toFixed(3)}</strong>
            <RankBadge rank={snapshotRanks.pointsAllowedPerPlay} fieldSize={snapshotRanks.fieldSize}/>
            <small>#{snapshotRanks.pointsAllowedPerPlay} NATIONALLY</small>
          </article>}
        </div>
      </section>

      {identity&&<section className="fan-section fan-identity"><span>TEAM IDENTITY</span><p>{identity}</p></section>}

      <OffensiveProfileRadar season={year} data={profile}/>

      <section className="fan-section"><div className="fan-section-title"><div><span>HOW GOOD ARE THEY?</span><h2>OFFENSE &amp; DEFENSE</h2></div><p>Every ranked metric is compared with the full FBS.</p></div><div className="fan-units-grid"><UnitOverview side="offense" title="OFFENSE" rank={data.offense.rank} fieldSize={data.offense.field_size} rating={data.offense.rating} href={`/analytics/offense?year=${year}`} metrics={offenseMetrics}/><UnitOverview side="defense" title="DEFENSE" rank={data.defense.rank} fieldSize={data.defense.field_size} rating={data.defense.rating} href={`/analytics/defense?year=${year}`} metrics={defenseMetrics}/></div></section>

      <section className="fan-section"><div className="fan-section-title"><div><span>WHAT DEFINES THIS TEAM?</span><h2>THE GOOD &amp; THE BAD</h2></div></div><div className="fan-story-grid">
        {best&&<article className="fan-story-card strength"><span className="fan-story-kicker">BIGGEST STRENGTH</span><h3>{best.label}</h3><div className="fan-story-rank"><strong>#{best.rank}</strong><span>NATIONALLY</span><RankBadge rank={best.rank} fieldSize={best.field_size}/></div><p>{best.explanation}</p></article>}
        {concern&&<article className="fan-story-card concern"><span className="fan-story-kicker">BIGGEST CONCERN</span><h3>{concern.label}</h3><div className="fan-story-rank"><strong>#{concern.rank}</strong><span>NATIONALLY</span><RankBadge rank={concern.rank} fieldSize={concern.field_size}/></div><p>{concern.explanation}</p></article>}
      </div></section>

      <section className="fan-section analytics-explore"><div className="fan-section-title"><div><span>WANT THE DETAILS?</span><h2>GO DEEPER</h2></div></div><div className="fan-explore-grid">
        <Link href={`/analytics/offense?year=${year}`} className="fan-explore-card"><div className="fan-explore-image" style={{backgroundImage:"linear-gradient(180deg,rgba(3,20,38,.04),rgba(3,20,38,.96)),url('/images/analytics/overview-offense.png')"}}/><div><span>FULL BREAKDOWN</span><h3>OFFENSE ANALYTICS</h3><p>Run/pass splits, drives, downs, explosiveness and scoring.</p><b>Explore offense →</b></div></Link>
        <Link href={`/analytics/defense?year=${year}`} className="fan-explore-card"><div className="fan-explore-image" style={{backgroundImage:"linear-gradient(180deg,rgba(3,20,38,.04),rgba(3,20,38,.96)),url('/images/analytics/overview-defense.png')"}}/><div><span>FULL BREAKDOWN</span><h3>DEFENSE ANALYTICS</h3><p>Run/pass defense, havoc, drives, downs and scoring prevention.</p><b>Explore defense →</b></div></Link>
        <Link href={`/analytics/staff?year=${year}`} className="fan-explore-card"><div className="fan-explore-image" style={{backgroundImage:"linear-gradient(180deg,rgba(3,20,38,.04),rgba(3,20,38,.96)),url('/images/analytics/overview-staff.png')"}}/><div><span>COACHING LENS</span><h3>STAFF ANALYTICS</h3><p>Play calling, tendencies, personnel usage and how scheme shaped results.</p><b>Explore staff →</b></div></Link>
      </div></section>
    </>:<>
      <OffensiveProfileRadar season={year} data={profile}/>
      <section className="fan-section"><div className="fan-story-card concern"><h3>Full season snapshot not available yet</h3><p>{profile?"This season predates the site's team-rating pipeline, but the offensive profile above is computed directly from that year's play-by-play.":"This season does not have a published Michigan analytics profile. Choose an available season to continue."}</p></div></section>
    </>}
  </div>;
}
