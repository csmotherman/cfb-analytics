import Link from "next/link";
import { rankOf, tournamentRows } from "../../lib/data";

export default function Teams(){
  const rows=[...tournamentRows()].sort((a,b)=>Number(b.season)-Number(a.season)||(rankOf(a)??9999)-(rankOf(b)??9999));
  const byTeam=new Map<string,typeof rows>();
  for(const r of rows){const arr=byTeam.get(r.team)||[];arr.push(r);byTeam.set(r.team,arr);}
  const teams=[...byTeam.entries()].sort(([a],[b])=>a.localeCompare(b));
  return <>
    <h1>Teams</h1><p className="muted">Pick a program, then a season. This pilot uses the historical tournament output as the shared team-season directory.</p>
    {!teams.length?<div className="notice">Build the historical tournament first.</div>:<div className="grid">
      {teams.map(([team,seasons])=><div className="card" key={team}><b>{team}</b><div style={{marginTop:8}}>{seasons.slice(0,12).map(r=><Link className="pill" key={r.season} href={`/teams/${encodeURIComponent(team)}/${r.season}`}>{r.season}</Link>)}</div></div>)}
    </div>}
  </>;
}
