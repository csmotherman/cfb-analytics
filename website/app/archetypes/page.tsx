import Link from "next/link";
import { dynamicIdentityRows } from "../../lib/data";

function label(value:unknown){
  if(value===null||value===undefined||value==="") return "—";
  return String(value).replaceAll("-"," ").replace(/\b\w/g,c=>c.toUpperCase());
}

export default function Archetypes(){
  const rows=dynamicIdentityRows();
  return <>
    <h1>Team Identity Explorer</h1>
    <p className="muted">Dynamic, stats-first identities built from season-wide style, mechanism, effectiveness, structure, consistency, and trajectory. Strength language is only used when the underlying quality earns it.</p>
    {!rows.length?<div className="notice">Missing dynamic identity output. Run <code>python -m cfb_analytics.profiles.dynamic_profiles</code>.</div>:<div className="table-wrap"><table className="table"><thead><tr><th>Season</th><th>Team</th><th>Identity</th><th>Tags</th><th>Usage</th><th>Method</th><th>Structure</th><th>Effectiveness</th></tr></thead><tbody>
      {rows.slice(0,500).map((r:any,i)=>{
        const style=r.identityStyle||{};
        const tags=Array.isArray(r.identityTags)?r.identityTags:[];
        return <tr key={`${r.season}-${r.team}-${i}`}>
          <td>{r.season}</td>
          <td><Link href={`/teams/${encodeURIComponent(String(r.team))}/${r.season}`}><b>{r.team}</b></Link></td>
          <td><b>{r.identityName||"—"}</b></td>
          <td>{tags.length?tags.map((tag:string)=><span className="pill" key={tag}>{tag}</span>):"—"}</td>
          <td>{label(style.usage)}</td>
          <td>{label(style.method)}</td>
          <td>{label(style.teamStructure)}</td>
          <td>{label(style.effectiveness)}</td>
        </tr>;
      })}
    </tbody></table></div>}
  </>;
}
