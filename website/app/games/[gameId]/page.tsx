import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {gameById,opponent} from "../../../lib/michigan/games";
import {predictionForGame} from "../../../lib/michigan/predictions";
import {gamePreview,profileRank} from "../../../lib/michigan/game-preview";
import {teamLogoUrl} from "../../../lib/team-assets";
import {gameDate,gameTime} from "../../../lib/home-data";

type Props={params:Promise<{gameId:string}>};
const pct=(v:number|null)=>v==null?"—":`${Math.round(v*100)}%`;
const n=(v:number|undefined|null,d=1)=>v==null?"—":v.toFixed(d);
const shortName=(name:string)=>name==="Western Michigan"?"W. MICHIGAN":name.toUpperCase();

export async function generateMetadata({params}:Props):Promise<Metadata>{const game=gameById((await params).gameId);if(!game)return{title:"Game not found"};const opp=opponent(game);return{title:`Michigan vs ${opp.name} Game Preview`,description:`2026 Michigan vs ${opp.name}: 2025 comparison, returning roster continuity, transfers, matchup outlook and prediction.`}}

export default async function GameHub({params}:Props){
  const game=gameById((await params).gameId);if(!game)notFound();
  const prediction=predictionForGame(game.id);
  const {opp,michigan2025,opponent2025,michiganMovement,opponentMovement}=gamePreview(game);
  const michRank=profileRank(michigan2025),oppRank=profileRank(opponent2025);
  const home=game.homeId===130;
  const michTransfers=michiganMovement.transfers.slice(0,3),oppTransfers=opponentMovement.transfers.slice(0,3);
  const michScore=prediction?Math.max(0,Math.round(27+prediction.teamPredictedMargin/2)):null;
  const oppScore=prediction?Math.max(0,Math.round(27-prediction.teamPredictedMargin/2)):null;
  const margin=prediction?Math.abs(prediction.teamPredictedMargin).toFixed(1):null;
  const stronger2025=michRank&&oppRank?michRank<oppRank:null;
  const transferEdge=(michiganMovement.avgRating??0)-(opponentMovement.avgRating??0);

  return <div className="game-preview-page"><div className="preview-app-shell">
    <div className="preview-topbar"><Link href="/">‹ <span>HOME</span></Link><h1>GAME PREVIEW</h1><span className="preview-share">↗</span></div>

    <section className="preview-matchup-card">
      <div className="preview-matchup">
        <div><img src={teamLogoUrl(130,256)} alt="Michigan logo"/><strong>MICHIGAN</strong><small>WOLVERINES</small></div>
        <span>VS</span>
        <div><img src={teamLogoUrl(opp.id,256)} alt={`${opp.name} logo`}/><strong>{opp.name.toUpperCase()}</strong><small>{opp.name.includes("Western")?"BRONCOS":"OPPONENT"}</small></div>
      </div>
      <div className="preview-meta"><span>▣ {gameDate(game)}</span><span>◷ {gameTime(game)} ET</span><span>▣ {game.venue??(home?"Michigan Stadium":"Away")}</span></div>
    </section>

    <section className="preview-block">
      <h2>2025 TEAM COMPARISON</h2>
      <div className="comparison-table">
        <div className="comparison-head"><span><img src={teamLogoUrl(130,64)} alt=""/> MICHIGAN</span><i></i><span><img src={teamLogoUrl(opp.id,64)} alt=""/> {shortName(opp.name)}</span></div>
        <div><strong>{michRank?`#${michRank}`:"—"}</strong><span>2025 PROFILE RANK*</span><strong>{oppRank?`#${oppRank}`:"—"}</strong></div>
        <div><strong>{michigan2025?pct(michigan2025.successRate):"—"}</strong><span>OFFENSIVE SUCCESS RATE</span><strong>{opponent2025?pct(opponent2025.successRate):"—"}</strong></div>
        <div><strong>{michigan2025?n(michigan2025.yardsPerGame,1):"—"}</strong><span>YARDS PER GAME</span><strong>{opponent2025?n(opponent2025.yardsPerGame,1):"—"}</strong></div>
        <div><strong>{michigan2025?n(michigan2025.yardsAllowedPerGame,0):"—"}</strong><span>YARDS ALLOWED / GAME</span><strong>{opponent2025?n(opponent2025.yardsAllowedPerGame,0):"—"}</strong></div>
      </div>
      <p className="preview-footnote">*2025 profile rank is the site's four-metric national composite, not the AP poll.</p>
    </section>

    <div className="preview-two-up">
      <section className="preview-panel"><h2>RETURNING PRODUCTION</h2><small>ROSTER CONTINUITY PROXY</small><div className="ring-row"><div><img src={teamLogoUrl(130,64)} alt=""/><strong>{pct(michiganMovement.continuity)}</strong><span>{michiganMovement.returningCount} returners</span></div><div><img src={teamLogoUrl(opp.id,64)} alt=""/><strong>{pct(opponentMovement.continuity)}</strong><span>{opponentMovement.returningCount} returners</span></div></div><p>Share of the 2026 roster also found with the same team in 2025.</p></section>
      <section className="preview-panel"><h2>NEW TRANSFERS</h2><small>TRANSFER CLASS VALUE</small><div className="transfer-value-row"><div><img src={teamLogoUrl(130,64)} alt=""/><strong>{michiganMovement.transferValue}</strong><span>{michiganMovement.transfers.length} additions</span></div><div><img src={teamLogoUrl(opp.id,64)} alt=""/><strong>{opponentMovement.transferValue}</strong><span>{opponentMovement.transfers.length} additions</span></div></div><p>{transferEdge>=0?"Michigan":"Opponent"} holds the stronger portal-value score in the current directory.</p></section>
    </div>

    <section className="preview-panel transfer-detail-panel"><div className="panel-heading"><h2>TRANSFER IMPACT</h2><span>TOP ADDITIONS</span></div><div className="transfer-detail-grid">{[{name:"Michigan",logo:130,list:michTransfers},{name:opp.name,logo:opp.id,list:oppTransfers}].map(team=><div key={team.name}><h3><img src={teamLogoUrl(team.logo,64)} alt=""/>{team.name}</h3>{team.list.length?team.list.map((t,i)=><div className="transfer-person" key={`${t.name}-${i}`}><span><b>{t.name}</b><small>{t.position} · from {t.from}</small></span><strong>{t.rating?t.rating.toFixed(3):t.grade??"—"}</strong></div>):<p>No incoming transfers identified.</p>}</div>)}</div></section>

    <div className="preview-analysis-grid">
      <section className="preview-panel matchup-breakdown"><h2>MATCHUP BREAKDOWN</h2><article><b>◉</b><div><h3>MICHIGAN PROFILE VS {shortName(opp.name)}</h3><p>{stronger2025?`Michigan owns the stronger 2025 efficiency profile, ranking #${michRank} in our composite versus #${oppRank} for ${opp.name}.`:"The 2025 profile gap is tighter than the names suggest, putting more weight on early-down execution."}</p></div></article><article><b>⬟</b><div><h3>ROSTER RESET</h3><p>Continuity matters because these are not identical versions of the 2025 teams. Michigan returns {michiganMovement.returningCount} players in the longitudinal data; {opp.name} returns {opponentMovement.returningCount}.</p></div></article><article><b>★</b><div><h3>X-FACTOR</h3><p>Michigan's clean path is controlling the line of scrimmage, staying ahead of the chains and forcing {opp.name} to sustain long drives without free possessions.</p></div></article></section>
      <section className="preview-panel prediction-box"><h2>PREDICTION</h2><small>ACCORDING TO OUR MODEL</small><div className="score-row"><div><img src={teamLogoUrl(130,128)} alt=""/><strong>{michScore??"—"}</strong></div><span>VS</span><div><img src={teamLogoUrl(opp.id,128)} alt=""/><strong>{oppScore??"—"}</strong></div></div>{prediction?<><div className="pred-margin"><span>PROJECTED MARGIN</span><strong>{prediction.teamPredictedMargin>=0?`MICHIGAN +${margin}`:`MICHIGAN -${margin}`}</strong></div><p>Margin projection only. Win probability remains uncalibrated in the current model.</p></>:<p>Prediction publishes when a model output exists for this matchup.</p>}</section>
    </div>

    <section className="preview-panel game-outlook"><h2>GAME OUTLOOK</h2><p>Michigan enters this matchup with the talent advantage and, where the 2025 data supports it, the stronger efficiency baseline. The important question is how quickly the reshaped 2026 roster turns that advantage into clean football. Expect Michigan to establish the run, protect the quarterback from obvious passing downs and make {opp.name} earn every drive.</p><p>The portal and continuity numbers are the warning against simply replaying last season on paper. New contributors can change both teams quickly. If Michigan avoids turnovers and wins early downs, depth and physicality should become more visible as the game progresses.</p></section>

    <nav className="preview-links"><Link href="/schedule">FULL SCHEDULE →</Link><Link href="/analytics">ANALYTICS →</Link><Link href="/methodology">METHODOLOGY →</Link></nav>
  </div></div>;
}
