import type { MichiganPlayer } from "../../lib/michigan/types";
export function PlayerComparison({players}:{players:MichiganPlayer[]}){return <div className="pending-grid">{players.map(p=><div key={p.id}><span>{p.position??"PLAYER"}</span><strong>{p.firstName} {p.lastName}</strong></div>)}</div>}
