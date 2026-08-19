import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { classLabel } from "../../../../lib/michigan/format";
import { historicalRoster } from "../../../../lib/michigan/history";

type Props = { params: Promise<{ season: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const season = Number((await params).season);
  return { title: `${season} Michigan Roster`, description: `Complete ${season} Michigan football roster.` };
}

export default async function HistoricalRosterPage({ params }: Props) {
  const season = Number((await params).season);
  if (!Number.isInteger(season) || season < 2010 || season > 2025) notFound();
  const roster = historicalRoster(season);
  if (!roster.length) notFound();
  return <div className="compact-page">
    <header className="compact-header"><div><span className="eyebrow">MICHIGAN FOOTBALL · {season}</span><h1>{season} Roster</h1></div><div className="compact-kpis"><b>{roster.length}<small>PLAYERS</small></b><b>{new Set(roster.map((player) => player.position).filter(Boolean)).size}<small>POSITIONS</small></b></div></header>
    <Link className="back-link" href={`/history/${season}`}>← BACK TO {season} SEASON</Link>
    <section className="history-roster"><header><span>NO.</span><span>PLAYER</span><span>POS</span><span>CLASS</span><span>SIZE</span><span>HOMETOWN</span></header>{roster.map((player) => <div key={`${player.id}-${player.position}`}><span>{player.jersey ?? "—"}</span><strong>{player.firstName} {player.lastName}</strong><span>{player.position ?? "—"}</span><span>{classLabel(player.year)}</span><span>{player.height ? `${Math.floor(player.height / 12)}′${player.height % 12}″` : "—"} · {player.weight ?? "—"}</span><span>{[player.homeCity, player.homeState].filter(Boolean).join(", ") || "—"}</span></div>)}</section>
  </div>;
}
