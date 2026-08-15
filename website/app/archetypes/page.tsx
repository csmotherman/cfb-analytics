import { archetypeRows } from "../../lib/data";

function first(r:any,keys:string[]){for(const k of keys){if(r?.[k]!==undefined&&r?.[k]!==null)return String(r[k]);}return "—";}

export default function Archetypes(){
  const rows=archetypeRows();
  return <>
    <h1>Archetype Explorer</h1><p className="muted">Fan-facing identity labels. This page is mainly here to test whether the assignments feel right before we polish presentation.</p>
    {!rows.length?<div className="notice">Missing archetype output. Run <code>python -m cfb_analytics.profiles.layered_archetypes</code>.</div>:<div className="table-wrap"><table className="table"><thead><tr><th>Season</th><th>Team</th><th>Team identity</th><th>Offense</th><th>Defense</th><th>Scheme/style</th></tr></thead><tbody>
      {rows.slice(0,300).map((r:any,i)=><tr key={i}><td>{first(r,["season"])}</td><td><b>{first(r,["team","Team"])}</b></td><td>{first(r,["teamArchetype","teamName","team_label","teamMatch","team_match"])}</td><td>{first(r,["offenseArchetype","offenseName","offense_label","offenseMatch","offense_match"])}</td><td>{first(r,["defenseArchetype","defenseName","defense_label","defenseMatch","defense_match"])}</td><td>{first(r,["schemeArchetype","schemeName","scheme_label","schemeMatch","scheme_match"])}</td></tr>)}
    </tbody></table></div>}
  </>;
}
