import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {playerById} from "../../../lib/michigan/roster";
import {classLabel,formatHeight} from "../../../lib/michigan/format";
import {michiganStories} from "../../../lib/michigan/stories";
import {readJson} from "../../../lib/server-data";
import {teamLogoUrl} from "../../../lib/team-assets";

type Props={params:Promise<{playerId:string}>;searchParams:Promise<{tab?:string}>};
type CareerStat={category:string;stat:string;value:string|number};
type CareerSeason={season:number;team:string;teamId?:number|null;position?:string|null;positionFamily?:string|null;side?:string|null;displayStats:CareerStat[];hasBoxScoreStats:boolean};
type CareerRow={playerId:string;currentTeam:string;currentPosition?:string|null;seasons:CareerSeason[]};
const statValue=(value:string|number)=>typeof value==="number"?(Number.isInteger(value)?value.toLocaleString():value.toFixed(1)):value;
const percentileGrade=(value:number|null|undefined)=>value==null?"—":value>=97?"S+":value>=90?"S":value>=80?"A":value>=65?"B":value>=45?"C":value>=25?"D":"F";
const statLabel=(stat:CareerStat)=>{const key=`${stat.category}:${stat.stat}`;const labels:Record<string,string>={"passing:COMPLETIONS":"CMP","passing:ATT":"ATT","passing:PCT":"CMP%","passing:YDS":"PASS YDS","passing:TD":"PASS TD","passing:INT":"INT","passing:YPA":"YPA","rushing:CAR":"CAR","rushing:YDS":"RUSH YDS","rushing:YPC":"YPC","rushing:TD":"RUSH TD","receiving:REC":"REC","receiving:YDS":"REC YDS","receiving:YPR":"YPR","receiving:TD":"REC TD","defensive:TOT":"TACKLES","defensive:SOLO":"SOLO","defensive:TFL":"TFL","defensive:SACKS":"SACKS","defensive:QB HUR":"QB HUR","defensive:PD":"PD","interceptions:INT":"INT","kicking:FGM":"FGM","kicking:FGA":"FGA","kicking:PCT":"FG%","kicking:LONG":"LONG","kicking:XPM":"XPM","kicking:PTS":"PTS","punting:NO":"PUNTS","punting:YPP":"AVG","punting:LONG":"LONG","punting:In 20":"IN 20","kickReturns:YDS":"KR YDS","puntReturns:YDS":"PR YDS"};return labels[key]??stat.stat;};

export async function generateMetadata({params}:Props):Promise<Metadata>{const p=playerById((await params).playerId);if(!p)return{title:"Player not found",openGraph:{images:[]},twitter:{images:[]}};const title=`${p.firstName} ${p.lastName} | Michigan`;const description=`2026 Michigan ${p.position??"player"} profile, recruiting background and college production.`;const images=p.playerImageUrl?[p.playerImageUrl]:[];return{title,description,openGraph:{title,description,images},twitter:{title,description,images}}}

export default async function PlayerPage({params,searchParams}:Props){
  const p=playerById((await params).playerId);if(!p)notFound();
  const tab=(await searchParams).tab==="stats"?"stats":"overview";
  const insight=p.insight;const freshman=p.rosterStatus==="FRESHMAN";
  const careers=readJson<CareerRow[]>("data","published","2026","michigan","player-career-stats.json")??[];
  const career=careers.find(row=>row.playerId===p.id);const careerSeasons=(career?.seasons??[]).filter(season=>season.hasBoxScoreStats);
  const hasStats=careerSeasons.length>0;
  const focusValue=freshman?(p.prospectGrade??(p.stars?`${p.stars}★`:"NR")):(p.performanceGrade??p.prospectGrade??"NR");
  const focusDetail=freshman?(p.nationalRecruitRank?`No. ${p.nationalRecruitRank} national recruit`:p.compositeRating?`${p.compositeRating.toFixed(4)} composite`:"Recruiting profile"):(p.performanceGrade?`${p.nationalPositionPercentile?.toFixed(1)??"—"}th position percentile":"Recruiting baseline");
  const stories=michiganStories().filter(story=>story.playerIds?.includes(p.id));
  const bio=[`${p.firstName} ${p.lastName} is a ${classLabel(p.year).toLowerCase()} ${p.position??"player"} for Michigan.`,p.previousTeam?`He joined Michigan after playing at ${p.previousTeam}.`:null,p.homeCity||p.homeState?`He is from ${[p.homeCity,p.homeState].filter(Boolean).join(", ")}.`:null,p.importanceReason??null].filter(Boolean).join(" ");
  const SeasonCards=()=>hasStats?<div className="player-focus-season-list">{careerSeasons.map(season=><article className="player-focus-season" key={`${season.season}-${season.team}`}><header><div className="player-season-team">{season.teamId?<img src={teamLogoUrl(season.teamId,64)} alt=""/>:<span className="player-season-logo-fallback">M</span>}<div><b>{season.season}</b><span>{season.team}</span></div></div>{season.position&&<em>{season.position}</em>}</header><div>{season.displayStats.map((stat,index)=><span key={`${stat.category}-${stat.stat}-${index}`}><small>{statLabel(stat)}</small><strong>{statValue(stat.value)}</strong></span>)}</div></article>)}</div>:<div className="player-focus-empty"><b>No verified college box-score production yet.</b><p>{freshman?"Recruiting information is the honest baseline until his first college season begins.":"No position-relevant public box-score statistics are currently published for this player."}</p></div>;
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
      <section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">CAREER STATS</span><h2>College production by season.</h2></div><small>{careerSeasons.length?`${careerSeasons.length} VERIFIED SEASON${careerSeasons.length===1?"":"S"}`:"NO VERIFIED SEASONS"}</small></header><SeasonCards/></section>
      <section className="player-focus-card player-focus-outlook"><h2>PLAYER BIO</h2><p>{bio}</p></section>
      {stories.length>0&&<section className="player-focus-related"><header><h2>RELATED COVERAGE</h2></header><div className="player-focus-related-list">{stories.map(story=><Link href={`/articles/${story.slug}`} key={story.slug}><small>{story.eyebrow}</small><strong>{story.title}</strong><p>{story.deck}</p></Link>)}</div></section>}
    </div>:<div className="player-focus-grid">
      <section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">SEASON STATS</span><h2>Full college career.</h2></div><small>TEAM + SEASON VERIFIED</small></header><SeasonCards/></section>
      <section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">GAME LOG</span><h2>Game-by-game production.</h2></div></header><div className="player-focus-empty"><b>Historical player game logs are next.</b><p>Season totals now follow each player across schools. The next data pass will do the same for game-by-game production so transfers retain their complete career game history.</p></div></section>
      {p.performanceGrade&&<section className="player-focus-card player-focus-stats"><header><div><span className="player-focus-kicker">GRADE BREAKDOWN</span><h2>How his 2025 production compares nationally.</h2></div><small>{p.productionCohortSize?`${p.productionCohortSize.toLocaleString()} PLAYER COHORT`:"POSITION COHORT"}</small></header><div className="player-grade-grid"><article><small>OVERALL</small><strong>{p.performanceGrade}</strong><span>{p.nationalPositionPercentile?.toFixed(1)??"—"}th percentile</span></article><article><small>PRODUCTION</small><strong>{percentileGrade(p.productionPercentile)}</strong><span>{p.productionPercentile?.toFixed(1)??"—"}th percentile</span></article><article><small>USAGE / ROLE</small><strong>{percentileGrade(p.usagePercentile)}</strong><span>{p.usagePercentile?.toFixed(1)??"—"}th percentile</span></article><article><small>POSITION STANDING</small><strong>{percentileGrade(p.nationalPositionPercentile)}</strong><span>{p.nationalPositionPercentile?.toFixed(1)??"—"}th percentile</span></article></div><p className="player-grade-note">{p.performanceGradeBasis}</p></section>}
    </div>}

    <nav className="player-focus-links" aria-label="Continue exploring"><Link href="/team/roster">FULL ROSTER →</Link><Link href="/analytics">TEAM ANALYTICS →</Link></nav>
  </div></article>;
}
