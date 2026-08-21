import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {playerById} from "../../../lib/michigan/roster";
import {classLabel,formatHeight} from "../../../lib/michigan/format";
import {michiganStories} from "../../../lib/michigan/stories";

type Props={params:Promise<{playerId:string}>;searchParams:Promise<{tab?:string}>};
const statValue=(value:number)=>Number.isInteger(value)?value.toLocaleString():value.toFixed(1);
const percentileGrade=(value:number|null|undefined)=>value==null?"—":value>=97?"S+":value>=90?"S":value>=80?"A":value>=65?"B":value>=45?"C":value>=25?"D":"F";

export async function generateMetadata({params}:Props):Promise<Metadata>{const p=playerById((await params).playerId);if(!p)return{title:"Player not found",openGraph:{images:[]},twitter:{images:[]}};const title=`${p.firstName} ${p.lastName} | Michigan`;const description=`2026 Michigan ${p.position??"player"} profile, recruiting background and college production.`;const images=p.playerImageUrl?[p.playerImageUrl]:[];return{title,description,openGraph:{title,description,images},twitter:{title,description,images}}}

export default async function PlayerPage({params,searchParams}:Props){
  const p=playerById((await params).playerId);if(!p)notFound();
  const tab=(await searchParams).tab==="stats"?"stats":"overview";
  const insight=p.insight;const hasStats=Boolean(insight?.pastSeasons.some(season=>season.stats.some(stat=>stat.value!==0)));
  const freshman=p.rosterStatus==="FRESHMAN";
  const focusValue=freshman?(p.prospectGrade??(p.stars?`${p.stars}★`:"NR")):(p.performanceGrade??p.prospectGrade??"NR");
  const focusDetail=freshman?(p.nationalRecruitRank?`No. ${p.nationalRecruitRank} national recruit`:p.compositeRating?`${p.compositeRating.toFixed(4)} composite`:"Recruiting profile"):(p.performanceGrade?`${p.nationalPositionPercentile?.toFixed(1)??"—"}th position percentile":"Recruiting baseline");
  const stories=michiganStories().filter(story=>story.playerIds?.includes(p.id));
  const bio=[`${p.firstName} ${p.lastName} is a ${classLabel(p.year).toLowerCase()} ${p.position??"player"} for Michigan.`,p.previousTeam?`He joined Michigan after playing at ${p.previousTeam}.`:null,p.homeCity||p.homeState?`He is from ${[p.homeCity,p.homeState].filter(Boolean).join(", ")}.`:null,p.importanceReason??null].filter(Boolean).join(" ");
  return <article className="player-focus-page"><div className="player-focus-shell">
    <Link href="/team/roster" className="player-focus-back">← BACK TO ROSTER</Link>
    <section className="player-focus-hero">
      <div className="player-focus-photo">{p.playerImageUrl?<img src={p.playerImageUrl} alt={`${p.firstName} ${p.lastName}`}/>:<span className="photo-fallback">M</span>}<strong>#{p.jersey??"—"}</strong></div>
      <div className="player-focus-copy"><span className="player-focus-kicker">{p.position??"ATH"} · {classLabel(p.year)}</span><h1>{p.firstName}<br/><b>{p.lastName}</b></h1><p>{formatHeight(p.height)} · {p.weight?`${p.weight} LBS`:"WEIGHT —"}</p><div className="player-focus-meta"><span>{[p.homeCity,p.homeState].filter(Boolean).join(", ")||"Hometown —"}</span>{p.previousTeam&&<span>Previous: {p.previousTeam}</span>}</div></div>
      <div className="player-focus-grade"><small>{freshman?"RECRUITING GRADE":"PLAYER GRADE"}</small><strong>{focusValue}</strong><span>{focusDetail}</span><i>{freshman?"RECRUITING":"POSITION-BASED PRODUCTION"}</i></div>
    </section>

    <nav className="player-focus-tabs" aria-label="Player profile sections"><Link className={tab==="overview"?"active":""} href={`/players/${p.id}`}>OVERVIEW</Link><Link className={tab==="stats"?"active":""} href={`/players/${p.id}?tab=stats`}>STATS</Link></nav>

    {tab==="overview"?<div className="player-focus-grid">
      <section className="player-focus-card player-focus-profile"><h2>QUICK OVERVIEW</h2><div className="player-focus-lines"><div><span>POSITION</span><strong>{p.position??"—"}</strong></div><div><span>CLASS</span><strong>{classLabel(p.year)}</strong></div><div><span>JERSEY</span><strong>#{p.jersey??"—"}</strong></div><div><span>HEIGHT / WEIGHT</span><strong>{formatHeight(p.height)} · {p.weight?`${p.weight} lbs`:"—"}</strong></div><div><span>HOMETOWN</span><strong>{[p.homeCity,p.homeState].filter(Boolean).join(", ")||"—"}</strong></div></div></section>
      <section className="player-focus-card player-focus-recruiting"><h2>RECRUITING</h2><div className="stars">{p.stars?"★".repeat(p.stars):"—"}</div>{p.compositeRating&&<span className="rating">{p.compositeRating.toFixed(4)} <small>COMPOSITE</small></span>}<div className="player-focus-lines"><div><span>RECRUIT GRADE</span><strong>{p.prospectGrade??"NR"}</strong></div><div><span>NATIONAL RANK</span><strong>{p.nationalRecruitRank?`#${p.nationalRecruitRank}`:"—"}</strong></div><div><span>CLASS</span><strong>{p.recruitClass??"—"}</strong></div><div><span>ORIGINAL COMMITMENT</span><strong>{p.originalCommitment??"—"}</strong></div></div></section>
      <section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">CAREER STATS</span><h2>College production by season.</h2></div></header>{hasStats?<div className="player-focus-season-list">{insight!.pastSeasons.map(season=><article className="player-focus-season" key={`${season.season}-${season.team}`}><header><b>{season.season}</b><span>{season.team}</span></header><div>{season.stats.map(stat=><span key={stat.label}><small>{stat.label}</small><strong>{statValue(stat.value)}</strong></span>)}</div></article>)}</div>:<div className="player-focus-empty"><b>No college box-score production yet.</b><p>{freshman?"Recruiting information is the honest baseline until his first college season begins.":"No non-zero public box-score statistics are currently published for this player."}</p></div>}</section>
      <section className="player-focus-card player-focus-outlook"><h2>PLAYER BIO</h2><p>{bio}</p></section>
      {stories.length>0&&<section className="player-focus-related"><header><h2>RELATED COVERAGE</h2></header><div className="player-focus-related-list">{stories.map(story=><Link href={`/articles/${story.slug}`} key={story.slug}><small>{story.eyebrow}</small><strong>{story.title}</strong><p>{story.deck}</p></Link>)}</div></section>}
    </div>:<div className="player-focus-grid">
      <section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">SEASON STATS</span><h2>Verified college production.</h2></div><small>PUBLIC BOX-SCORE DATA</small></header>{hasStats?<div className="player-focus-season-list">{insight!.pastSeasons.map(season=><article className="player-focus-season" key={`${season.season}-${season.team}`}><header><b>{season.season}</b><span>{season.team}</span></header><div>{season.stats.map(stat=><span key={stat.label}><small>{stat.label}</small><strong>{statValue(stat.value)}</strong></span>)}</div></article>)}</div>:<div className="player-focus-empty"><b>No season statistics yet.</b><p>Stats will appear automatically once verified college production is published.</p></div>}</section>
      <section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">GAME LOG</span><h2>Game-by-game production.</h2></div></header><div className="player-focus-empty"><b>Player-level game logs are not published yet.</b><p>The current game dataset is team-level. This section is ready for the player game-stat feed and will populate without changing the profile layout.</p></div></section>
      {p.performanceGrade&&<section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">GRADE BREAKDOWN</span><h2>How his 2025 production compares nationally.</h2></div><small>{p.productionCohortSize?`${p.productionCohortSize.toLocaleString()} PLAYER COHORT`:"POSITION COHORT"}</small></header><div className="player-grade-grid"><article><small>OVERALL</small><strong>{p.performanceGrade}</strong><span>{p.nationalPositionPercentile?.toFixed(1)??"—"}th percentile</span></article><article><small>PRODUCTION</small><strong>{percentileGrade(p.productionPercentile)}</strong><span>{p.productionPercentile?.toFixed(1)??"—"}th percentile</span></article><article><small>USAGE / ROLE</small><strong>{percentileGrade(p.usagePercentile)}</strong><span>{p.usagePercentile?.toFixed(1)??"—"}th percentile</span></article><article><small>POSITION STANDING</small><strong>{percentileGrade(p.nationalPositionPercentile)}</strong><span>{p.nationalPositionPercentile?.toFixed(1)??"—"}th percentile</span></article></div><p className="player-grade-note">{p.performanceGradeBasis}</p></section>}
    </div>}

    <nav className="player-focus-links" aria-label="Continue exploring"><Link href="/team/roster">FULL ROSTER →</Link><Link href="/analytics">TEAM ANALYTICS →</Link></nav>
  </div></article>;
}
