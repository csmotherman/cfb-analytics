<<<<<<< HEAD
import Link from "next/link";
import { avgMargin, fieldWinPct, rankOf, tournamentRows } from "../../lib/data";

export default function Rankings(){
  const rows=[...tournamentRows()].sort((a,b)=>(rankOf(a)??99999)-(rankOf(b)??99999));
  return <>
    <h1>Historical Power Rankings</h1>
    <p className="muted">Pilot view: expected neutral-field strength against the full 2014–2025 historical field. This is model power, not a championship résumé ranking.</p>
    {!rows.length?<div className="notice">Missing tournament output. Run <code>python -m cfb_analytics.profiles.historical_tournament</code>.</div>:
    <div className="table-wrap"><table className="table"><thead><tr><th>#</th><th>Team</th><th>Field win</th><th>Avg margin</th><th>Profile</th></tr></thead><tbody>
      {rows.slice(0,150).map((r,i)=><tr key={`${r.season}-${r.team}`}><td>{rankOf(r)??i+1}</td><td><b>{r.season} {r.team}</b></td><td>{fieldWinPct(r)!==null?(fieldWinPct(r)!*100).toFixed(1)+"%":"—"}</td><td>{avgMargin(r)!==null?`${avgMargin(r)!>=0?"+":""}${avgMargin(r)!.toFixed(1)}`:"—"}</td><td><Link href={`/teams/${encodeURIComponent(r.team)}/${r.season}`}>Open</Link></td></tr>)}
    </tbody></table></div>}
  </>;
=======
import type { Metadata } from "next";
import Link from "next/link";
import { latestPublishedSeason, nationalTeams, rank } from "../../lib/michigan";

export const metadata: Metadata = { title: "National Rankings", description: "Michigan's position across the complete FBS field." };

export default function RankingsPage() {
  const season = latestPublishedSeason();
  const rows = season === null ? [] : nationalTeams(season).sort((a, b) => (rank(a, "successRate") ?? 999) - (rank(b, "successRate") ?? 999));
  return <div className="michigan-home">
    <section className="michigan-page-hero"><span>NATIONAL CONTROL GROUP</span><h1>Every FBS team, measured the same way.</h1><p>Michigan's numbers only mean something when the entire country is calculated first. This board shows offensive success alongside defensive, explosive-play, and drive context.</p></section>
    <section className="michigan-ranking-panel">
      <div className="michigan-ranking-head"><span>Off. rank</span><span>Team</span><span>Conference</span><span>Off. success</span><span>Def. rank</span><span>Explosive rank</span></div>
      {rows.map((row) => <Link className={`michigan-ranking-row${row.team === "Michigan" ? " is-michigan" : ""}`} href={`/teams/${row.slug}/${season}`} key={row.team_id}>
        <b>#{rank(row, "successRate") ?? "—"}</b><strong>{row.team}{row.team === "Michigan" ? <small> YOU ARE HERE</small> : null}</strong><span>{row.conference}</span><em>{row.successRate != null ? `${(row.successRate * 100).toFixed(1)}%` : "—"}</em><i>#{rank(row, "successRateAllowed") ?? "—"}</i><i>#{rank(row, "explosivePlayRate") ?? "—"}</i>
      </Link>)}
    </section>
  </div>;
>>>>>>> 28a9c53 (new design)
}
