import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PlayerTile } from "../../../../components/players/PlayerTile";
import { playersByPosition } from "../../../../lib/michigan/roster";
type Props={params:Promise<{position:string}>};
export async function generateMetadata({params}:Props):Promise<Metadata>{const p=(await params).position.toUpperCase();return{title:`Michigan ${p} Room`,description:`Current 2026 Michigan ${p} roster.`}}
export default async function PositionPage({params}:Props){const position=(await params).position.toUpperCase();const players=playersByPosition(position);if(!players.length)notFound();return <div className="page-stack page-pad"><section className="page-hero"><span className="eyebrow">2026 POSITION ROOM</span><h1>{position}<br/>ROOM.</h1><p>{players.length} Wolverines. Stats and roles update during the season.</p></section><div className="player-grid">{players.map(player=><PlayerTile player={player} key={player.id}/>)}</div></div>}
