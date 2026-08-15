import Link from "next/link";
import { archetypeRows, avgMargin, fieldWinPct, findPowerRow, rankOf } from "../../../../lib/data";

function archetypeFor(team:string,season:number){
  return archetypeRows().find((r:any)=>Number(r.season)===season&&String(r.team||r.Team||"").toLowerCase()===team.toLowerCase())||null;
}
function first(r:any,keys:string[]){for(const k of keys){if(r?.[k]!==undefined&&r?.[k]!==null)return r[k];}return null;}

export default async function TeamSeason({params}:{params:Promise<{team:string;season:string}>}){
  const p=await params; const team=decodeURIComponent(p.team); const season=Number(p.season);
  const power=findPowerRow(team,season); const arch=archetypeFor(team,season);
  const teamLabel=first(arch,["teamArchetype","teamName","team_label","team"]);
  const off=first(arch,["offenseArchetype","offenseName","offense_label","offense"]);
  const def=first(arch,["defenseArchetype","defenseName","defense_label","defense"]);
  const scheme=first(arch,["schemeArchetype","schemeName","scheme_label","scheme"]);
  return <>
    <section className="hero"><div className="muted">TEAM-SEASON</div><h1>{season} {team}</h1>
      <div className="grid">
        <div><div className="muted">Historical power rank</div><div className="big-number">{power?`#${rankOf(power)??"—"}`:"—"}</div></div>
        <div><div className="muted">Field win rate</div><div className="big-number">{power&&fieldWinPct(power)!==null?(fieldWinPct(power)!*100).toFixed(1)+"%":"—"}</div></div>
        <div><div className="muted">Avg neutral margin</div><div className="big-number">{power&&avgMargin(power)!==null?`${avgMargin(power)!>=0?"+":""}${avgMargin(power)!.toFixed(1)}`:"—"}</div></div>
      </div>
      <div className="row" style={{marginTop:16}}><Link className="button" href={`/simulator?homeYear=${season}&homeTeam=${encodeURIComponent(team)}`}>Simulate them</Link><Link className="button secondary" href={`/compare?aYear=${season}&aTeam=${encodeURIComponent(team)}`}>Compare them</Link></div>
    </section>
    <section className="panel"><h2>Who were they?</h2>{arch?<><p><b>Team:</b> {String(teamLabel||"No clear team label")}</p><p><b>Offense:</b> {String(off||"—")}</p><p><b>Defense:</b> {String(def||"—")}</p><p><b>Scheme/style:</b> {String(scheme||"—")}</p></>:<div className="notice">No archetype row found for this team-season. That is expected for 2025 if the current archetype file only covers 2014–2024.</div>}</section>
    <section className="panel"><h2>Pilot questions</h2><p>This page is intentionally sparse while we validate the data contracts. Next we will fill: biggest strength, biggest weakness, offense/defense grades, style, trajectory and historical similarity.</p></section>
  </>;
}
