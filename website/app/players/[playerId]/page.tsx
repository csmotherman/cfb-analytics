import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {playerById,playersByPosition} from "../../../lib/michigan/roster";
import {classLabel,formatHeight} from "../../../lib/michigan/format";
import {michiganStories} from "../../../lib/michigan/stories";

type Props={params:Promise<{playerId:string}>};
const statValue=(value:number)=>Number.isInteger(value)?value.toLocaleString():value.toFixed(1);
const stars=(count:number|null|undefined)=>count?`${"★".repeat(count)}${"☆".repeat(Math.max(0,5-count))}`:"NOT RATED";

export async function generateMetadata({params}:Props):Promise<Metadata>{
  const p=playerById((await params).playerId);
  if(!p)return{title:"Player not found",openGraph:{images:[]},twitter:{images:[]}};
  const title=`${p.firstName} ${p.lastName} | Michigan`;
  const description=`Michigan ${p.position??"player"} profile with recruiting background, roster information and verified college production when available.`;
  const images=p.playerImageUrl?[p.playerImageUrl]:[];
  return{title,description,openGraph:{title,description,images},twitter:{title,description,images}};
}

export default async function PlayerPage({params}:Props){
  const p=playerById((await params).playerId);
  if(!p)notFound();

  const insight=p.insight;
  const room=playersByPosition(p.position??"");
  const stories=michiganStories().filter(story=>story.playerIds?.includes(p.id));
  const seasons=insight?.pastSeasons.filter(season=>season.stats.some(stat=>stat.value!==0))??[];
  const hasStats=seasons.length>0;
  const hasProductionGrade=hasStats&&Boolean(p.performanceGrade);
  const gradeLabel=hasProductionGrade?"POSITION GRADE":"RECRUITING GRADE";
  const gradeValue=hasProductionGrade?p.performanceGrade:(p.prospectGrade??(p.stars?`${p.stars}★`:"NR"));
  const gradeDetail=hasProductionGrade
    ?`${p.performanceGradeSeason??2025} production · compared with ${p.position??"position"} peers`
    :p.compositeRating?`${p.compositeRating.toFixed(4)} recruiting composite`:"Recruiting baseline";
  const hometown=[p.homeCity,p.homeState].filter(Boolean).join(", ")||"—";

  return <article className="player-focus-page">
    <div className="player-focus-shell">
      <Link className="player-focus-back" href="/team/roster">← BACK TO ROSTER</Link>

      <header className="player-focus-hero">
        <div className="player-focus-photo">
          {p.playerImageUrl?<img src={p.playerImageUrl} alt={`${p.firstName} ${p.lastName}`}/>:<span className="photo-fallback">M</span>}
          <strong>#{p.jersey??"—"}</strong>
        </div>
        <div className="player-focus-copy">
          <span className="player-focus-kicker">MICHIGAN FOOTBALL · {p.rosterStatus??"ROSTER"}</span>
          <h1>{p.firstName}<br/><b>{p.lastName}</b></h1>
          <p>{p.position??"ATH"} · {classLabel(p.year)}</p>
          <div className="player-focus-meta">
            <span>{formatHeight(p.height)}</span>
            <span>{p.weight?`${p.weight} LBS`:"WEIGHT —"}</span>
            <span>{hometown}</span>
            {p.previousTeam&&<span>FROM {p.previousTeam.toUpperCase()}</span>}
          </div>
        </div>
        <div className="player-focus-grade">
          <small>{gradeLabel}</small>
          <strong>{gradeValue??"NR"}</strong>
          <span>{gradeDetail}</span>
          <i>{hasProductionGrade?"ACTUAL COLLEGE PRODUCTION":"RECRUITING EVIDENCE"}</i>
        </div>
      </header>

      <nav className="player-focus-tabs" aria-label="Player profile sections">
        <a href="#overview">OVERVIEW</a>
        <a href="#recruiting">RECRUITING</a>
        {hasStats&&<a href="#stats">STATS</a>}
        <a href="#outlook">OUTLOOK</a>
      </nav>

      <div className="player-focus-grid" id="overview">
        <section className="player-focus-card player-focus-recruiting" id="recruiting">
          <h2>RECRUITING PROFILE</h2>
          <div className="stars">{stars(p.stars)}</div>
          {p.compositeRating&&<span className="rating">{p.compositeRating.toFixed(4)} <small>COMPOSITE</small></span>}
          <div className="player-focus-lines">
            <div><span>Recruiting grade</span><strong>{p.prospectGrade??"NR"}</strong></div>
            <div><span>National rank</span><strong>{p.nationalRecruitRank?`#${p.nationalRecruitRank}`:"—"}</strong></div>
            <div><span>Recruiting class</span><strong>{p.recruitClass??"—"}</strong></div>
            <div><span>Original commitment</span><strong>{p.originalCommitment??"—"}</strong></div>
          </div>
        </section>

        <section className="player-focus-card player-focus-profile">
          <h2>PLAYER PROFILE</h2>
          <div className="player-focus-lines">
            <div><span>Class</span><strong>{classLabel(p.year)}</strong></div>
            <div><span>Position</span><strong>{p.position??"—"}</strong></div>
            <div><span>Jersey</span><strong>#{p.jersey??"—"}</strong></div>
            <div><span>Hometown</span><strong>{hometown}</strong></div>
            <div><span>Height</span><strong>{formatHeight(p.height)}</strong></div>
            <div><span>Weight</span><strong>{p.weight?`${p.weight} lbs`:"—"}</strong></div>
            <div><span>Position room</span><strong>{room.length} players</strong></div>
          </div>
        </section>

        <section className="player-focus-card player-focus-outlook" id="outlook">
          <h2>2026 OUTLOOK</h2>
          <p>{insight?.expectation??"Role and expectations will become clearer as the season develops."}</p>
          {insight?.expectationBasis&&<p>{insight.expectationBasis}</p>}
          <div className="player-focus-signals">
            <article><small>STRENGTH SIGNALS</small>{insight?.strengths.length?insight.strengths.map(item=><p key={item}>+ {item}</p>):<p>Evaluation currently rests on roster and recruiting evidence.</p>}</article>
            <article><small>WHAT TO WATCH</small>{insight?.growthAreas.length?insight.growthAreas.map(item=><p key={item}>— {item}</p>):<p>College usage will define the next stage of the profile.</p>}</article>
          </div>
        </section>

        <section className="player-focus-card player-focus-stats" id="stats">
          <header><div><span className="player-focus-kicker">COLLEGE PRODUCTION</span><h2>{hasStats?"VERIFIED PAST-SEASON STATS":"STATS WILL APPEAR WHEN HE PLAYS"}</h2></div><small>PUBLIC BOX-SCORE DATA ONLY</small></header>
          {hasStats?<div className="player-focus-season-list">{seasons.map(season=><article className="player-focus-season" key={`${season.season}-${season.team}`}><header><b>{season.season}</b><span>{season.team}</span></header><div>{season.stats.map(stat=><span key={stat.label}><small>{stat.label}</small><strong>{statValue(stat.value)}</strong></span>)}</div></article>)}</div>:<div className="player-focus-empty"><b>No verified college statistics yet.</b><p>Nothing is being filled with zeroes or projections. Until real college usage exists, this profile stays anchored to recruiting and roster information.</p></div>}
        </section>

        {stories.length>0&&<section className="player-focus-card player-focus-related"><header><div><span className="player-focus-kicker">LATEST COVERAGE</span><h2>STORIES FEATURING {p.firstName.toUpperCase()}</h2></div><Link href="/articles">ALL ARTICLES →</Link></header><div className="player-focus-related-list">{stories.map(story=><Link href={`/articles/${story.slug}`} key={story.slug}><small>{story.eyebrow}</small><strong>{story.title}</strong><p>{story.deck}</p></Link>)}</div></section>}

        <nav className="player-focus-links" aria-label="Continue exploring">
          <Link href={`/team/positions/${(p.position??"").toLowerCase()}`}>POSITION ROOM →</Link>
          <Link href="/team/roster">FULL ROSTER →</Link>
          <Link href="/analytics">TEAM ANALYTICS →</Link>
        </nav>
      </div>
    </div>
  </article>;
}
