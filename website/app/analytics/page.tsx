import Link from "next/link";
import {AnalyticsYearSwitch} from "../../components/AnalyticsYearSwitch";
import {metricDisplay,michiganFanSeason,overviewTraits,pct,perGame,rankDisplay,ridgeOverview,type RidgeOverview} from "../../lib/ridge-analytics";

const years=Array.from({length:17},(_,i)=>2010+i);

function Profile({title,side,data}:{title:string;side:"offense"|"defense";data:RidgeOverview}){
  const block=data[side];
  const cards=side==="offense"?[
    ["MAKING DRIVES COUNT",metricDisplay("ppd",block.metrics.ppd.value),rankDisplay(block.metrics.ppd.rank,block.metrics.ppd.field_size),"Points Michigan creates on a typical drive after accounting for opponent strength."],
    ["MOVING THE BALL",metricDisplay("ypd",block.metrics.ypd.value),rankDisplay(block.metrics.ypd.rank,block.metrics.ypd.field_size),"How much field position Michigan creates per drive against an average FBS defense."],
    ["STAYING ON SCHEDULE",metricDisplay("success",block.metrics.success.value),rankDisplay(block.metrics.success.rank,block.metrics.success.field_size),"How consistently Michigan wins plays and stays ahead of the chains."],
    ["FINISHING POSSESSIONS",metricDisplay("scoring",block.metrics.scoring.value),rankDisplay(block.metrics.scoring.rank,block.metrics.scoring.field_size),"How often Michigan turns a possession into points after opponent adjustment."],
  ]:[
    ["POINTS ALLOWED / DRIVE",metricDisplay("ppd",block.metrics.ppd.value),rankDisplay(block.metrics.ppd.rank,block.metrics.ppd.field_size),"How difficult Michigan makes it for opponents to turn possessions into points."],
    ["YARDS ALLOWED / DRIVE",metricDisplay("ypd",block.metrics.ypd.value),rankDisplay(block.metrics.ypd.rank,block.metrics.ypd.field_size),"How much field position opponents create per possession after opponent adjustment."],
    ["GETTING OFF SCHEDULE",metricDisplay("success",block.metrics.success.value),rankDisplay(block.metrics.success.rank,block.metrics.success.field_size),"How consistently Michigan prevents opposing offenses from winning down-to-down."],
    ["KEEPING THEM OFF THE BOARD",metricDisplay("scoring",block.metrics.scoring.value),rankDisplay(block.metrics.scoring.rank,block.metrics.scoring.field_size),"How often opposing possessions end with points after accounting for opponent strength."],
  ];
  return <section className="analytics-overview-section">
    <h2>{title}</h2>
    <div className="analytics-identity-grid">
      {cards.map(([label,value,rank,copy])=><article key={label}>
        <i aria-hidden="true">◇</i><span>{label}</span><strong>{value}</strong><small>NATIONAL RANK</small><b>{rank}</b><p>{copy}</p>
      </article>)}
    </div>
  </section>;
}

function FanCards({title,cards}:{title:string;cards:Array<[string,string,string,string]>}){
  return <section className="analytics-overview-section">
    <h2>{title}</h2>
    <div className="analytics-identity-grid">
      {cards.map(([label,value,detail,copy])=><article key={label}>
        <i aria-hidden="true">◇</i><span>{label}</span><strong>{value}</strong><small>{detail}</small><p>{copy}</p>
      </article>)}
    </div>
  </section>;
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
      ? `Michigan's identity: the defense was the stronger national unit, while an offense built around a ${pct(season.rushSuccessRate)} rushing success rate had to be more selective through the air.`
      : `Michigan's identity: the offense led the way, with the defense complementing it by limiting opponents to ${season.pointsPerResolvedPossessionAllowed.toFixed(2)} points per possession.`
    :null;
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
        <h1>MICHIGAN<br/><b>ANALYTICS</b></h1><span>{year} TEAM PROFILE</span>
        <p>{data?"How good was Michigan? What traveled, what broke down and where did the Wolverines rank nationally? The model does the hard math underneath — this page tells the football story.":"Opponent-adjusted Michigan analytics are not available for this season yet."}</p>
      </div>
      <div className="analytics-overview-hero-image" aria-hidden="true"><img src="images/analytics/overview-header.png" alt=""/></div>
    </section>

    {data?<>
      <section className="analytics-summary-grid" aria-label="Michigan analytics summary">
        <article className="good"><i>O</i><span>OFFENSE</span><strong>#{data.offense.rank}</strong><small>NATIONALLY</small><b>{data.offense.rating.toFixed(1)} team rating</b></article>
        <article className="good"><i>D</i><span>DEFENSE</span><strong>#{data.defense.rank}</strong><small>NATIONALLY</small><b>{data.defense.rating.toFixed(1)} team rating</b></article>
        <article className="good"><i>+</i><span>BIGGEST EDGE</span><strong>#{best?.rank}</strong><small>{best?.side.toUpperCase()}</small><b>{best?.label}</b></article>
        <article className="concern"><i>!</i><span>BIGGEST CONCERN</span><strong>#{concern?.rank}</strong><small>{concern?.side.toUpperCase()}</small><b>{concern?.label}</b></article>
      </section>

      {identity&&<section className="analytics-overview-section"><div className="analytics-story-card strength"><h2>TEAM IDENTITY</h2><p>{identity}</p></div></section>}

      {season&&<FanCards title="HOW MICHIGAN WINS" cards={[
        ["TOTAL OFFENSE",season.yardsPerGame.toFixed(1),"YARDS / GAME","The simplest measure of how much offense Michigan creates each Saturday."],
        ["YARDS / PLAY",season.yardsPerPlay.toFixed(2),"OFFENSIVE EFFICIENCY","How much Michigan gains every time the ball is snapped."],
        ["THIRD DOWN",pct(season.thirdDownConversionRate),"CONVERSION RATE","How often Michigan extends drives when the offense has to earn another set of downs."],
        ["EXPLOSIVE PLAYS",pct(season.explosivePlayRate),`#${season.national_explosivePlayRate_rank} NATIONALLY`,"How often Michigan creates the chunk plays that flip field position and produce points."],
      ]}/>} 

      {season&&<FanCards title="GROUND GAME VS PASSING GAME" cards={[
        ["RUSHING",`${perGame(season.rushYards,season.games).toFixed(1)} YPG`,`${season.rushYardsPerAttempt.toFixed(2)} YARDS / CARRY`,`${pct(season.rushSuccessRate)} success rate · ${pct(season.rushExplosivePlayRate)} explosive-run rate.`],
        ["PASSING",`${perGame(season.netPassYards,season.games).toFixed(1)} YPG`,`${season.netPassYardsPerDropback.toFixed(2)} NET YARDS / DROPBACK`,`${pct(season.passSuccessRate)} success rate · ${pct(season.passExplosivePlayRate)} explosive-pass rate.`],
        ["RUN CONSISTENCY",pct(season.rushSuccessRate),"SUCCESS RATE","How often the run game creates a positive result for the situation."],
        ["PASS CONSISTENCY",pct(season.passSuccessRate),"SUCCESS RATE","How often Michigan's passing game keeps the offense on schedule."],
      ]}/>} 

      <Profile title="OPPONENT-ADJUSTED OFFENSE" side="offense" data={data}/>

      {season&&<FanCards title="HOW HARD IS MICHIGAN TO SCORE ON?" cards={[
        ["TOTAL DEFENSE",season.yardsAllowedPerGame.toFixed(1),"YARDS ALLOWED / GAME","How much total offense opponents generate against Michigan."],
        ["THIRD DOWN DEFENSE",pct(season.thirdDownConversionRateAllowed),"CONVERSION RATE ALLOWED","How often opponents survive third down against the Wolverines."],
        ["EXPLOSIVE PLAYS ALLOWED",pct(season.explosivePlayRateAllowed),`#${season.national_explosivePlayRateAllowed_rank} NATIONALLY`,`Michigan allowed explosive plays on only ${pct(season.explosivePlayRateAllowed)} of eligible snaps.`],
        ["POINTS / POSSESSION",season.pointsPerResolvedPossessionAllowed.toFixed(2),"ALLOWED","How many points opponents produce on a typical resolved possession."],
        ["RUN DEFENSE",`${season.rushYardsPerAttemptAllowed.toFixed(2)} YPC`,`${pct(season.rushSuccessRateAllowed)} SUCCESS ALLOWED`,"How consistently opponents can stay on schedule by running the football."],
        ["PASS DEFENSE",`${season.netPassYardsPerDropbackAllowed.toFixed(2)} NY/DB`,`${pct(season.passSuccessRateAllowed)} SUCCESS ALLOWED`,"How efficiently opposing passing games move the football against Michigan."],
        ["SACKS",String(season.sacks),`${season.tacklesForLoss} TACKLES FOR LOSS`,"Backfield disruption created by Michigan's defense."],
        ["TAKEAWAYS",String(season.takeaways),`${season.threeAndOutsForced} THREE-AND-OUTS FORCED`,"Possessions Michigan ends without letting the opponent sustain offense."],
      ]}/>} 

      <Profile title="OPPONENT-ADJUSTED DEFENSE" side="defense" data={data}/>

      {season&&<FanCards title="WHEN IT MATTERS" cards={[
        ["3RD DOWN OFFENSE",pct(season.thirdDownConversionRate),"MOVE THE CHAINS","Michigan's conversion rate when two downs are already gone."],
        ["3RD DOWN DEFENSE",pct(season.thirdDownConversionRateAllowed),"GET OFF THE FIELD","Opponent conversion rate on third down."],
        ["RED ZONE OFFENSE",pct(season.redZonePossessionScoringRate),`${pct(season.redZonePossessionTouchdownRate)} TD RATE`,`How often Michigan scores — and scores touchdowns — after reaching the red zone.`],
        ["RED ZONE DEFENSE",pct(season.redZonePossessionScoringRateAllowed),`${pct(season.redZonePossessionTouchdownRateAllowed)} TD RATE ALLOWED`,`How often opponents leave Michigan's red zone with points.`],
      ]}/>} 

      <section className="analytics-story-grid">
        <article className="analytics-story-card strength"><h2>WHAT MICHIGAN DOES BEST</h2>{traits?.strengths.map(item=><div key={`${item.side}-${item.metric}`}><i>✓</i><span><b>{item.label.toUpperCase()}</b><small>{rankDisplay(item.rank,item.field_size)} · {metricDisplay(item.metric,item.value)}</small><p>One of Michigan&apos;s strongest schedule-adjusted advantages compared with the rest of the FBS.</p></span></div>)}</article>
        <article className="analytics-story-card concern"><h2>WHAT COULD COST MICHIGAN</h2>{traits?.concerns.map(item=><div key={`${item.side}-${item.metric}`}><i>!</i><span><b>{item.label.toUpperCase()}</b><small>{rankDisplay(item.rank,item.field_size)} · {metricDisplay(item.metric,item.value)}</small><p>One of Michigan&apos;s weaker schedule-adjusted traits and a place opponents can target.</p></span></div>)}</article>
      </section>
    </>:<section className="analytics-overview-section"><div className="analytics-story-card"><h2>ANALYTICS NOT AVAILABLE YET</h2><p>This season does not have a published opponent-adjusted analytics profile. Choose an available season to explore Michigan&apos;s performance.</p></div></section>}

    <section className="analytics-overview-section analytics-explore"><h2>GO DEEPER</h2><div className="analytics-explore-grid">
      {explore.map(([href,title,copy,image])=><Link href={`${href}?year=${year}`} className="analytics-explore-card" key={title}><div className="analytics-explore-image" style={{backgroundImage:`linear-gradient(180deg,transparent 30%,rgba(3,20,38,.95)),url('${image}')`}}/><div><h3>{title}</h3><p>{copy}</p><b>›</b></div></Link>)}
    </div><div className="analytics-explore-secondary">
      <Link href={`/analytics/trends?year=${year}`} style={{backgroundImage:"linear-gradient(90deg,rgba(3,20,38,.94),rgba(3,20,38,.56)),url('/images/analytics/overview-trends.png')"}}><div><h3>SEASON TRENDS</h3><p>Track where Michigan improved, slipped or changed identity over the season</p></div><b>›</b></Link>
      <Link href={`/analytics/staff?year=${year}`} style={{backgroundImage:"linear-gradient(90deg,rgba(3,20,38,.94),rgba(3,20,38,.56)),url('/images/analytics/overview-staff.png')"}}><div><h3>STAFF &amp; SCHEME</h3><p>Connect Michigan&apos;s results to coaching, personnel and scheme</p></div><b>›</b></Link>
    </div></section>
  </div>;
}
