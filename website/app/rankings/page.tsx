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
}
