import Link from "next/link";
import { currentRoster } from "../../../lib/michigan/roster";

export default function PortalPage() {
  const transfers = currentRoster().filter((player) => player.rosterStatus === "TRANSFER");
  const utahTransfers = transfers.filter((player) => player.previousTeam === "Utah").length;

  return <div className="editorial-page">
    <section className="page-banner"><div className="wrap page-banner-inner"><div><span className="kicker">2026 ROSTER MOVEMENT</span><h1>PORTAL IN</h1><p>Verified Michigan arrivals, their previous teams, and the position rooms they enter.</p></div><div className="banner-mark">{transfers.length}</div></div><div className="wrap summary-rail"><span><small>VERIFIED ARRIVALS</small><b>{transfers.length}</b></span><span><small>FROM UTAH</small><b>{utahTransfers}</b></span><span><small>EVIDENCE TYPE</small><b>PRESEASON</b></span></div></section>
    <div className="wrap editorial-stack"><section><header className="section-header"><div><span className="kicker navy">WHO JOINED</span><h2>Experience entering every room.</h2></div><Link href="/team/roster">FULL ROSTER →</Link></header><div className="portal-grid">{transfers.map((player) => <Link href={`/players/${player.id}`} key={player.id}><span>{player.position ?? "ATH"} · FROM {player.previousTeam?.toUpperCase() ?? "TEAM UNAVAILABLE"}</span><strong>{player.firstName}<br/><b>{player.lastName}</b></strong><p>{player.insight?.expectation ?? "Role evaluation begins with verified roster and prior-team evidence."}</p><small>{player.performanceGrade ? `${player.performanceGrade} · 2025 PRODUCTION GRADE` : "PRESEASON ROSTER · NO PRODUCTION GRADE"}</small></Link>)}</div></section><aside className="evidence-note"><b>DEPARTURES</b><p>A verified outgoing-transfer artifact is not published yet. SOAR leaves that list absent rather than reconstructing it from incomplete reporting.</p></aside></div>
  </div>;
}
