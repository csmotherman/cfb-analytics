"use client";

import Link from "next/link";
import { useState } from "react";
import type { DepthSlot } from "../../lib/michigan/depth-chart";
import type { MichiganPlayer } from "../../lib/michigan/types";

const yearLabel = (year?: number | null) => ["Fr", "So", "Jr", "Sr", "Gr"][Math.max(0, (year ?? 1) - 1)] ?? "—";

function PositionCard({ slot, select, selectedId }: { slot: DepthSlot; select: (player: MichiganPlayer, label: string) => void; selectedId: string }) {
  return <article className="depth-position-card">
    <h3>{slot.label}</h3>
    <div>{slot.players.map((player, index) => <button type="button" className={selectedId === player.id ? "active" : ""} onMouseEnter={() => select(player, slot.label)} onFocus={() => select(player, slot.label)} onClick={() => select(player, slot.label)} key={`${player.id}-${index}`}>
      <span>{index + 1}</span><b>#{player.jersey ?? "—"}</b><strong>{player.firstName[0]}. {player.lastName}</strong><small>{yearLabel(player.year)}</small>
    </button>)}</div>
  </article>;
}

function UnitBoard({ title, subtitle, slots, unit, select, selectedId }: { title: string; subtitle: string; slots: DepthSlot[]; unit: string; select: (player: MichiganPlayer, label: string) => void; selectedId: string }) {
  return <section className={`depth-unit-board ${unit}`} aria-labelledby={`${unit}-title`}>
    <header><div><span>PROJECTED TWO-DEEP</span><h2 id={`${unit}-title`}>{title}</h2></div><small>{subtitle}</small></header>
    <div className="depth-formation" aria-label={`${title} projected depth chart`}>{slots.map((slot, index) => <PositionCard slot={slot} select={select} selectedId={selectedId} key={`${unit}-${slot.label}-${index}`}/>)}</div>
  </section>;
}

export function FieldDepthChart({ offense, defense, specialists }: { offense: DepthSlot[]; defense: DepthSlot[]; specialists: DepthSlot[] }) {
  const initial = offense[0]?.players[0];
  const [selected, setSelected] = useState<{ player: MichiganPlayer; label: string } | null>(initial ? { player: initial, label: offense[0].label } : null);
  const choose = (player: MichiganPlayer, label: string) => setSelected({ player, label });
  const player = selected?.player;

  return <section className="depth-experience" aria-label="Interactive Michigan depth chart">
    <div className="depth-board-column">
      <UnitBoard title="OFFENSE" subtitle="Spread · 11 personnel" slots={offense} unit="offense" select={choose} selectedId={player?.id ?? ""}/>
      <UnitBoard title="DEFENSE" subtitle="Nickel · 4–2–5" slots={defense} unit="defense" select={choose} selectedId={player?.id ?? ""}/>
      <UnitBoard title="SPECIALISTS" subtitle="Primary · reserve" slots={specialists} unit="specialists" select={choose} selectedId={player?.id ?? ""}/>
    </div>
    {player && <aside className="depth-player-card" aria-live="polite">
      <div className="depth-player-visual">{player.playerImageUrl ? <img src={player.playerImageUrl} alt=""/> : <strong>{player.jersey ?? "M"}</strong>}<span>{selected?.label}</span></div>
      <div className="depth-player-copy"><small>2026 PROJECTED {selected?.label}</small><h3>{player.firstName}<br/><b>{player.lastName}</b></h3><p>#{player.jersey ?? "—"} · {yearLabel(player.year)} · {player.position ?? selected?.label}</p>
        <div className="depth-evidence"><span><small>{player.rosterStatus === "FRESHMAN" ? "PROSPECT GRADE" : "2025 GRADE"}</small><b>{player.rosterStatus === "FRESHMAN" ? player.prospectGrade ?? "NR" : player.performanceGrade ?? "NG"}</b></span><span><small>ROSTER PATH</small><b>{player.rosterStatus ?? "RETURNER"}</b></span></div>
        <p className="depth-player-read">{player.insight?.expectation ?? "Projected role from the latest published preseason depth chart."}</p><Link href={`/players/${player.id}`}>OPEN PLAYER FILE <span>→</span></Link>
      </div>
    </aside>}
  </section>;
}
