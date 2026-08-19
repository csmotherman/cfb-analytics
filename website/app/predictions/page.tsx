import Link from "next/link";
import { GameCard } from "../../components/games/GameCard";
import { PredictionPanel } from "../../components/games/PredictionPanel";
import { nextGame } from "../../lib/michigan/games";
import { currentMarketOutlook, predictionForGame } from "../../lib/michigan/predictions";

export default function PredictionsPage() {
  const game = nextGame();
  const prediction = game ? predictionForGame(game.id) : null;
  const outlook = currentMarketOutlook();
  return <div className="page-stack page-pad">
    <section className="page-hero"><span className="eyebrow">2026 FORECAST</span><h1>MICHIGAN'S<br/>OUTLOOK.</h1><p>Game picks, playoff odds and the road ahead.</p></section>
    {game && <GameCard game={game}/>}
    <PredictionPanel prediction={prediction}/>
    <section><span className="eyebrow">PLAYOFF ODDS</span><div className="pending-grid"><div><span>MAKE CFP</span><strong>{outlook?`${(outlook.cfp.noVigImpliedProbability*100).toFixed(1)}%`:"COMING SOON"}</strong></div><div><span>CURRENT LINE</span><strong>{outlook?`+${outlook.cfp.makePlayoffYesAmerican}`:"—"}</strong></div><div><span>EXPECTED WINS</span><strong>COMING SOON</strong></div><div><span>NATIONAL TITLE</span><strong>COMING SOON</strong></div></div>{outlook&&<p>Market estimate from <a href={outlook.source.url} rel="noreferrer">{outlook.source.name}</a>. Odds move. Not betting advice.</p>}</section>
    <div className="cta-row"><Link className="button" href="/predictions/cfp">SEE THE CFP PATH</Link></div>
  </div>;
}
