import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { GameCard } from "../../../components/games/GameCard";
import { EmptyState } from "../../../components/ui/EmptyState";
import { PredictionPanel } from "../../../components/games/PredictionPanel";
import { gameById, opponent } from "../../../lib/michigan/games";
import { predictionForGame } from "../../../lib/michigan/predictions";
type Props={params:Promise<{gameId:string}>};
export async function generateMetadata({params}:Props):Promise<Metadata>{const game=gameById((await params).gameId);if(!game)return{title:"Game not found",openGraph:{images:[]},twitter:{images:[]}};const opp=opponent(game);const title=`Michigan vs ${opp.name}`;const description=`Michigan vs ${opp.name}, Week ${game.week}.`;return{title,description,openGraph:{title,description,images:[]},twitter:{title,description,images:[]}}}
export default async function GameHub({params}:Props){const game=gameById((await params).gameId);if(!game)notFound();const opp=opponent(game);const prediction=predictionForGame(game.id);return <div className="page-stack"><section className="game-hub-hero"><span className="eyebrow">WEEK {game.week} · 2026</span><h1>MICHIGAN<br/>VS {opp.name.toUpperCase()}</h1><GameCard game={game} featured/></section><section className="page-pad"><PredictionPanel prediction={prediction}/></section><EmptyState eyebrow="MATCHUP" title="Breakdown coming game week."/></div>}
