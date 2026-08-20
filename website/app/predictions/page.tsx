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
    <section className="page-hero"><span className="eyebrow">2026 PROJECTIONS + MARKET CONTEXT</span><h1>MICHIGAN'S<br/>OUTLOOK.</h1><p>Game projections and separately labeled market-derived playoff context.</p></section>
    {game && <GameCard game={game}/>}
    <PredictionPanel prediction={prediction}/>
    <section><span className="eyebrow">MARKET PLAYOFF OUTLOOK · BENCHMARK</span><div className="pending-grid"><div><span>MARKET CFP CHANCE</span><strong>{outlook?`${(outlook.cfp.noVigImpliedProbability*100).toFixed(1)}%`:"COMING SOON"}</strong></div><div><span>CURRENT MARKET LINE</span><strong>{outlook?`+${outlook.cfp.makePlayoffYesAmerican}`:"—"}</strong></div></div>{outlook&&<p>Market estimate from <a href={outlook.source.url} rel="noreferrer">{outlook.source.name}</a>. Odds move. This is not a model probability and not betting advice.</p>}</section>
    <div className="cta-row"><Link className="button" href="/predictions/cfp">SEE THE CFP PATH</Link></div>
  </div>;
}
