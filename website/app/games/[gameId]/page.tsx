import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {gameById,opponent} from "../../../lib/michigan/games";
import {predictionForGame,describeTeamMargin} from "../../../lib/michigan/predictions";
import {gamePreview,profileRank} from "../../../lib/michigan/game-preview";
import {teamLogoUrl} from "../../../lib/team-assets";

type Props={params:Promise<{gameId:string}>};
const pct=(v:number|null)=>v==null?"—":`${Math.round(v*100)}%`;
const n=(v:number|undefined|null,d=1)=>v==null?"—":v.toFixed(d);

export async function generateMetadata({params}:Props):Promise<Metadata>{
  const game=gameById((await params).gameId);if(!game)return{title:"Game not found"};
  const opp=opponent(game);const title=`Michigan vs ${opp.name} Game Preview`;
  const description=`2026 Michigan vs ${opp.name}: 2025 comparison, roster continuity, transfers, matchup outlook and prediction.`;
  return{title,description};
}

export default async function GameHub({params}:Props){
  const game=gameById((await params).gameId);if(!game)notFound();
  const prediction=predictionForGame(game.id);
  const {opp,michigan2025,opponent2025,michiganMovement,opponentMovement}=gamePreview(game);
  const michRank=profileRank(michigan2025),oppRank=profileRank(opponent2025);
  const home=game.homeId===130;
  const michTransfers=michiganMovement.transfers.slice(0,4),oppTransfers=opponentMovement.transfers.slice(0,4);
  const edge=michigan2025&&opponent2025
    ? michigan2025.successRate-opponent2025.successRate
    : 0;
  const predictionText=prediction?describeTeamMargin(prediction):"Prediction publishes closer to kickoff";

  return <div className="game-preview-page">
    <section className="preview-hero wrap">
      <span className="preview-kicker">WEEK {game.week} · GAME PREVIEW</span>
      <div className="preview-matchup">
        <div><img src={teamLogoUrl(130,128)} alt="Michigan logo"/><strong>MICHIGAN</strong></div>
        <span>VS</span>
        <div><img src={teamLogoUrl(opp.id,128)} alt={`${opp.name} logo`}/><strong>{opp.name.toUpperCase()}</strong></div>
      </div>
      <div className="preview-meta"><span>{home?"MICHIGAN STADIUM":"AWAY"}</span><span>2026</span><span>WEEK {game.week}</span></div>
    </section>

    <div className="wrap preview-stack">
      <section className="preview-section">
        <header><span>01</span><div><small>START HERE</small><h2>WHAT EACH TEAM WAS IN 2025</h2></div></header>
        <div className="team-compare-grid">
          {[{name:"Michigan",logo:130,p:michigan2025,rank:michRank},{name:opp.name,logo:opp.id,p:opponent2025,rank:oppRank}].map(team=><article key={team.name}>
            <div className="compare-team-head"><img src={teamLogoUrl(team.logo,128)} alt=""/><h3>{team.name}</h3></div>
            <div className="compare-stat"><span>2025 PROFILE RANK*</span><strong>{team.rank?`#${team.rank}`:"—"}</strong></div>
            <div className="compare-stat"><span>SUCCESS RATE</span><strong>{team.p?pct(team.p.successRate):"—"}</strong></div>
            <div className="compare-stat"><span>YARDS / GAME</span><strong>{team.p?n(team.p.yardsPerGame,0):"—"}</strong></div>
            <div className="compare-stat"><span>YARDS ALLOWED / GAME</span><strong>{team.p?n(team.p.yardsAllowedPerGame,0):"—"}</strong></div>
          </article>)}
        </div>
        <p className="preview-note">*Profile rank is a transparent four-metric national composite from the repo’s final 2025 success-rate and explosiveness ranks. It is not presented as the final AP poll.</p>
      </section>

      <section className="preview-section">
        <header><span>02</span><div><small>ROSTER RESET</small><h2>RETURNING PRODUCTION & CONTINUITY</h2></div></header>
        <div className="continuity-grid">
          <article><div className="compare-team-head"><img src={teamLogoUrl(130,64)} alt=""/><h3>Michigan</h3></div><strong>{pct(michiganMovement.continuity)}</strong><span>2026 roster with a 2025 Michigan season</span><small>{michiganMovement.returningCount} returning players found in longitudinal roster data</small></article>
          <article><div className="compare-team-head"><img src={teamLogoUrl(opp.id,64)} alt=""/><h3>{opp.name}</h3></div><strong>{pct(opponentMovement.continuity)}</strong><span>2026 roster with a 2025 {opp.name} season</span><small>{opponentMovement.returningCount} returning players found in longitudinal roster data</small></article>
        </div>
        <p className="preview-note">This is a returning-production proxy based on roster continuity because exact snap-weighted returning production is not yet published in this dataset. As player-level production is added, this section can upgrade automatically.</p>
      </section>

      <section className="preview-section">
        <header><span>03</span><div><small>PORTAL IMPACT</small><h2>NEW TRANSFERS & THEIR VALUE</h2></div></header>
        <div className="transfer-columns">
          {[{name:"Michigan",logo:130,m:michiganMovement,list:michTransfers},{name:opp.name,logo:opp.id,m:opponentMovement,list:oppTransfers}].map(team=><article key={team.name}>
            <div className="transfer-team-title"><img src={teamLogoUrl(team.logo,64)} alt=""/><div><h3>{team.name}</h3><span>{team.m.transfers.length} incoming transfers · {team.m.transferValue} class value</span></div></div>
            <div className="transfer-list">{team.list.length?team.list.map((t,i)=><div key={`${t.name}-${i}`}><b>{t.name}</b><span>{t.position} · from {t.from}</span><strong>{t.rating?`${t.rating.toFixed(3)}${t.stars?` · ${t.stars}★`:""}`:t.grade??"Unrated"}</strong></div>):<p>No incoming transfers identified in the current longitudinal directory.</p>}</div>
          </article>)}
        </div>
      </section>

      <section className="preview-section preview-story">
        <header><span>04</span><div><small>THE READ</small><h2>WHAT TO EXPECT</h2></div></header>
        <div className="preview-story-copy">
          <p>Michigan enters this matchup with the stronger 2025 efficiency profile{michRank&&oppRank?` — roughly #${michRank} in this four-metric profile compared with #${oppRank} for ${opp.name}`:""}. The first question is not whether Michigan has more raw talent; it is whether the Wolverines can turn that advantage into an efficient, low-variance opener.</p>
          <p>{edge>0?`Michigan’s 2025 offense produced a ${pct(michigan2025?.successRate??null)} success rate, giving it a clear baseline efficiency edge entering this game.`:`The raw 2025 efficiency gap is smaller than the brand-name gap, which makes early-down execution worth watching.`} The matchup becomes more interesting where continuity and portal turnover change the identity of each roster. A team returning less of its prior-year core can look materially different from its 2025 statistical profile.</p>
          <p>For Michigan, the clean path is straightforward: establish the run game, keep the quarterback ahead of the chains, avoid giving away possessions, and force {opp.name} to sustain long drives. If Michigan controls early downs and explosive plays, the talent gap should become increasingly visible after halftime.</p>
        </div>
      </section>

      <section className="prediction-card">
        <small>MICHIGAN FOOTBALL FOCUS PREDICTION</small>
        <div className="prediction-logos"><img src={teamLogoUrl(130,128)} alt="Michigan"/><span>VS</span><img src={teamLogoUrl(opp.id,128)} alt={opp.name}/></div>
        <h2>{predictionText}</h2>
        <p>{prediction?`Model version ${prediction.modelVersion}. This is a projected margin, not a calibrated win probability.`:"The prediction layer will populate when a published model output exists for this game."}</p>
      </section>

      <nav className="preview-links"><Link href="/schedule">FULL SCHEDULE →</Link><Link href="/analytics">MICHIGAN ANALYTICS →</Link><Link href="/methodology">METHODOLOGY →</Link></nav>
    </div>
  </div>;
}
