import Link from "next/link";
import { avgMargin, datasetStatus, fieldWinPct, rankOf, tournamentRows } from "../lib/data";

export default function Home(){
  const status=datasetStatus();
  const top=[...tournamentRows()].sort((a,b)=>(rankOf(a)??9999)-(rankOf(b)??9999)).slice(0,5);
  return <>
    <section className="hero">
      <div className="muted">COLLEGE FOOTBALL, EXPLAINED</div>
      <h1>Know your team. Settle the debate.</h1>
      <p>Functional pilot: test rankings, historical teams, comparisons, archetypes and the head-to-head simulator before we spend time making it pretty.</p>
      <div className="row"><Link className="button" href="/teams">Find a Team</Link><Link className="button secondary" href="/simulator">Simulate a Matchup</Link></div>
    </section>

    <h2>What do you want to know?</h2>
    <div className="grid">
      <Link className="card" href="/rankings"><b>Who is the best?</b><p className="muted">All-time model power rankings.</p></Link>
      <Link className="card" href="/simulator"><b>Who would win?</b><p className="muted">Pick any two historical team-seasons.</p></Link>
      <Link className="card" href="/teams"><b>What is my team?</b><p className="muted">Open a team-season profile.</p></Link>
      <Link className="card" href="/compare"><b>Compare two teams</b><p className="muted">Put eras side by side.</p></Link>
    </div>

    <section className="panel"><h2>Data readiness</h2>{status.map(s=><div key={s.relative}>{s.ready?"✅":"⚠️"} <b>{s.label}</b> — <code>{s.relative}</code></div>)}</section>

    <section className="panel"><h2>The teams everyone is chasing</h2>{top.length?top.map(r=><div key={`${r.season}-${r.team}`} style={{marginBottom:10}}><b>#{rankOf(r)} {r.season} {r.team}</b> — field win {fieldWinPct(r)!==null?(fieldWinPct(r)!*100).toFixed(1)+"%":"n/a"}, avg margin {avgMargin(r)!==null?(avgMargin(r)!>=0?"+":"")+avgMargin(r)!.toFixed(1):"n/a"}</div>):<div className="notice">Build the cross-era tournament JSON to populate this section.</div>}</section>
  </>;
}
