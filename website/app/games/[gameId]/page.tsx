import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {gameById,opponent} from "../../../lib/michigan/games";
import {describeTeamMargin,predictionForGame} from "../../../lib/michigan/predictions";
import {gamePreview,profileRank} from "../../../lib/michigan/game-preview";
import {marketLineFor,formatMichiganSpread} from "../../../lib/market-lines";
import {teamLogoUrl} from "../../../lib/team-assets";
import {gameDate,gameTime} from "../../../lib/home-data";

type Props={params:Promise<{gameId:string}>};
const pct=(v:number|null)=>v==null?"—":`${Math.round(v*100)}%`;
const n=(v:number|undefined|null,d=1)=>v==null?"—":v.toFixed(d);
const shortName=(name:string)=>name==="Western Michigan"?"W. MICHIGAN":name.toUpperCase();
const modelAsOf=(iso:string)=>new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"America/Detroit"}).format(new Date(iso));

export async function generateMetadata({params}:Props):Promise<Metadata>{const game=gameById((await params).gameId);if(!game)return{title:"Game not found"};const opp=opponent(game);return{title:`Michigan vs ${opp.name} Game Preview`,description:`2026 Michigan vs ${opp.name}: model projection, 2025 comparison, roster movement and matchup outlook.`}}

export default async function GameHub({params}:Props){
  const game=gameById((await params).gameId);if(!game)notFound();
  const prediction=predictionForGame(game.id);
  const market=marketLineFor(game.id);
  const {opp,michigan2025,opponent2025,michiganMovement,opponentMovement}=gamePreview(game);
  const michRank=profileRank(michigan2025),oppRank=profileRank(opponent2025);
  const home=game.homeId===130;
  const michTransfers=michiganMovement.transfers.slice(0,3),oppTransfers=opponentMovement.transfers.slice(0,3);
  const stronger2025=michRank&&oppRank?michRank<oppRank:null;
  const transferEdge=(michiganMovement.avgRating??0)-(opponentMovement.avgRating??0);
  const modelSpread=prediction?-prediction.teamPredictedMargin:null;
  const marketImpliedMargin=market?-market.teamSpread:null;
  const modelVsMarket=prediction&&market?prediction.teamPredictedMargin-marketImpliedMargin!:null;

  return <div className="game-preview-page"><div className="preview-app-shell">
    <div className="preview-topbar"><Link href="/schedule">‹ <span>SCHEDULE</span></Link><h1>GAME PREVIEW</h1><span className="preview-share">M</span></div>

    <section className="preview-matchup-card">
      <div className="preview-matchup">
        <div><img src={teamLogoUrl(130,256)} alt="Michigan logo"/><strong>MICHIGAN</strong><small>WOLVERINES</small></div>
        <span>VS</span>
        <div><img src={teamLogoUrl(opp.id,256)} alt={`${opp.name} logo`}/><strong>{opp.name.toUpperCase()}</strong><small>{home?"AT MICHIGAN":"MATCHUP"}</small></div>
      </div>
      <div className="preview-meta"><span>{gameDate(game)}</span><span>{gameTime(game)} ET</span><span>{game.venue??(home?"Michigan Stadium":"Away")}</span></div>
    </section>

    <section className="preview-block model-forecast-block">
      <div className="model-forecast-heading"><div><span className="mock-eyebrow maize">MICHIGAN FOOTBALL FOCUS MODEL</span><h2>MODEL FORECAST</h2></div>{prediction&&<small>FROZEN {modelAsOf(prediction.asOf).toUpperCase()}</small>}</div>
      {prediction?<div className="model-forecast-card">
        <div className="model-margin-hero"><small>PROJECTED MARGIN</small><strong>{describeTeamMargin(prediction)}</strong><span>Spread equivalent: Michigan {modelSpread!>0?"+":""}{modelSpread!.toFixed(1)}</span></div>
        <div className="model-forecast-facts">
          <span><small>MODEL</small><b>19-FACTOR LINEAR</b></span>
          <span><small>TRAINING SAMPLE</small><b>1,754 GAMES</b></span>
          <span><small>TRAINING SEASONS</small><b>9 SEASONS</b></span>
          <span><small>WIN PROBABILITY</small><b>NOT YET CALIBRATED</b></span>
        </div>
        {market&&<div className="model-market-benchmark"><div><small>MARKET BENCHMARK</small><strong>{formatMichiganSpread(market.teamSpread)}</strong><span>{Math.round(market.marketWinChance*100)}% market-calibrated win chance</span></div><div><small>MODEL VS MARKET</small><strong>{modelVsMarket==null?"—":`${modelVsMarket>=0?"Michigan +":"Michigan -"}${Math.abs(modelVsMarket).toFixed(1)} pts`}</strong><span>Difference in expected Michigan margin</span></div></div>}
        <p className="model-boundary">This model predicts point margin, not an exact final score. It uses only information available before kickoff. A model win probability will not be shown until that probability layer is separately calibrated and validated.</p>
      </div>:<div className="model-forecast-card pending"><strong>MODEL FORECAST PENDING</strong><p>This matchup will publish once its pregame feature snapshot is frozen. Future-season results are never used to fill the gap.</p></div>}
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

    <section className="preview-panel matchup-breakdown preview-matchup-read"><h2>MATCHUP READ</h2><article><b>1</b><div><h3>2025 BASELINE</h3><p>{stronger2025?`Michigan owns the stronger 2025 efficiency profile, ranking #${michRank} in our composite versus #${oppRank} for ${opp.name}.`:"The 2025 profile gap is tighter than the names suggest, putting more weight on early-down execution."}</p></div></article><article><b>2</b><div><h3>ROSTER RESET</h3><p>These are not identical versions of the 2025 teams. Michigan returns {michiganMovement.returningCount} players in the longitudinal data; {opp.name} returns {opponentMovement.returningCount}.</p></div></article><article><b>3</b><div><h3>MODEL BOUNDARY</h3><p>The projection is a pregame margin estimate from the frozen 2026 model. Roster context and 2025 comparison are supporting information, not manually added points to the model forecast.</p></div></article></section>

    <section className="preview-panel game-outlook"><h2>GAME OUTLOOK</h2><p>{prediction?`The model currently makes ${describeTeamMargin(prediction)}. That is a point-margin forecast, not a promise about the shape of the game or an exact score.`:"The model forecast is not yet published for this week, so the page does not substitute a hand-built score."} The 2025 comparison and roster movement sections explain the context around the matchup without being passed off as live 2026 results.</p></section>

    <nav className="preview-links"><Link href="/schedule">FULL SCHEDULE →</Link><Link href="/analytics">ANALYTICS →</Link><Link href="/methodology">METHODOLOGY →</Link></nav>
  </div></div>;
}
