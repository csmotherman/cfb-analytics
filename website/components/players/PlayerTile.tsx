import Link from "next/link";
import type { MichiganPlayer } from "../../lib/michigan/types";
import { classLabel } from "../../lib/michigan/format";
export function PlayerTile({ player }: { player: MichiganPlayer }) {
  return <Link className="player-tile" href={`/players/${player.id}`}><div className="player-number">{player.jersey != null ? `#${player.jersey}` : "M"}</div><div><span>{player.position ?? "ATH"} · {classLabel(player.year)}</span><h3>{player.firstName} {player.lastName}</h3><p>{player.height ? `${Math.floor(player.height / 12)}'${player.height % 12}\"` : "—"} · {player.weight ? `${player.weight} lbs` : "—"}</p></div><div className="tile-grade"><small>PROSPECT</small><strong>{player.prospectGrade ?? "NR"}</strong></div><b>VIEW PROFILE →</b></Link>;
}
