import Link from "next/link";
import type { DepthSlot } from "../../lib/michigan/depth-chart";

function Unit({ title, slots, side }: { title: string; slots: DepthSlot[]; side: "offense" | "defense" }) {
  return <section><div className="field-title"><span>{title}</span><small>PRESEASON PICK</small></div><div className={`depth-field ${side}`}><div className="end-zone">MICHIGAN</div><div className="field-players">{slots.map(({ label, player }, index) => <Link href={`/players/${player.id}`} className={`field-player slot-${index}`} key={`${label}-${player.id}`}><span>{label}</span><strong>#{player.jersey ?? "—"}</strong><b>{player.firstName.slice(0, 1)}. {player.lastName}</b><small>{player.prospectGrade ?? "NR"}</small></Link>)}</div></div></section>;
}

export function FieldDepthChart({ offense, defense }: { offense: DepthSlot[]; defense: DepthSlot[] }) {
  return <div className="field-stack"><Unit title="PROJECTED OFFENSE" slots={offense} side="offense"/><Unit title="PROJECTED DEFENSE" slots={defense} side="defense"/></div>;
}
