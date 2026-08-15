import Link from "next/link";
import { archetypeRows, avgMargin, fieldWinPct, findPowerRow, rankOf, tournamentRows } from "../../../../lib/data";

function archetypeFor(team:string,season:number){
  return archetypeRows().find((r:any)=>Number(r.season)===season&&String(r.team||r.Team||"").toLowerCase()===team.toLowerCase())||null;
}

function laneTop(arch:any,lane:string){
  return arch?.lanes?.[lane]?.[0]||null;
}

function fanConfidence(value:any){
  const v=String(value||"").toUpperCase();
  if(v==="HIGH") return "High confidence";
  if(v==="MODERATE") return "Moderate confidence";
  if(v==="LOW") return "Low confidence";
  return null;
}

function lanePresentation(arch:any,lane:string){
  const top=laneTop(arch,lane);
  if(!top) return {label:"—",note:null};
  const root=String(top.rootName||top.name||"Closest profile");
  if(top.isClearMatch===false){
    return {label:`Closest fit: ${root}`,note:"No strong single identity"};
  }
  const full=String(top.name||root);
  const modifier=full!==root ? full.replace(root,"").trim() : "";
  const confidence=fanConfidence(top.confidence);
  const note=[modifier||null,confidence].filter(Boolean).join(" · ")||null;
  return {label:root,note};
}

export default async function TeamSeason({params}:{params:Promise<{team:string;season:string}>}){
  const p=await params; const team=decodeURIComponent(p.team); const season=Number(p.season);
  const power=findPowerRow(team,season); const arch=archetypeFor(team,season);
  const teamIdentity=arch?lanePresentation(arch,"team"):{label:"—",note:null};
  const offense=arch?lanePresentation(arch,"offense"):{label:"—",note:null};
  const defense=arch?lanePresentation(arch,"defense"):{label:"—",note:null};
  const scheme=arch?lanePresentation(arch,"scheme"):{label:"—",note:null};
  const total=tournamentRows().length;
  const rank=power?rankOf(power):null;
  const win=power?fieldWinPct(power):null;
  const margin=power?avgMargin(power):null;

  return <>
    <section className="hero">
      <div className="muted">TEAM-SEASON</div>
      <h1>{season} {team}</h1>
      <div className="grid">
        <div>
          <div className="muted">Historical standing</div>
          <div className="big-number">{rank?`#${rank}`:"—"}</div>
          {rank&&total?<div className="muted">out of {total.toLocaleString()} team-seasons</div>:null}
        </div>
        <div>
          <div className="muted">How often they beat the field</div>
          <div className="big-number">{win!==null?(win*100).toFixed(1)+"%":"—"}</div>
          {win!==null?<div className="muted">Expected to beat about {Math.round(win*10)} of every 10 historical teams</div>:null}
        </div>
        <div>
          <div className="muted">Average neutral-field edge</div>
          <div className="big-number">{margin!==null?`${margin>=0?"+":""}${margin.toFixed(1)}`:"—"}</div>
          <div className="muted">model points per matchup</div>
        </div>
      </div>
      <div className="row" style={{marginTop:16}}>
        <Link className="button" href={`/simulator?homeYear=${season}&homeTeam=${encodeURIComponent(team)}`}>Simulate them</Link>
        <Link className="button secondary" href={`/compare?aYear=${season}&aTeam=${encodeURIComponent(team)}`}>Compare them</Link>
      </div>
    </section>

    <section className="panel">
      <h2>What kind of team were they?</h2>
      {arch?<div className="grid">
        <div>
          <div className="muted">Team identity</div>
          <h3>{teamIdentity.label}</h3>
          {teamIdentity.note?<div className="muted">{teamIdentity.note}</div>:null}
        </div>
        <div>
          <div className="muted">Offensive identity</div>
          <h3>{offense.label}</h3>
          {offense.note?<div className="muted">{offense.note}</div>:null}
        </div>
        <div>
          <div className="muted">Defensive identity</div>
          <h3>{defense.label}</h3>
          {defense.note?<div className="muted">{defense.note}</div>:null}
        </div>
        <div>
          <div className="muted">Scheme / style</div>
          <h3>{scheme.label}</h3>
          {scheme.note?<div className="muted">{scheme.note}</div>:null}
        </div>
      </div>:<div className="notice">No archetype row found for this team-season. That is expected for 2025 if the current archetype file only covers 2014–2024.</div>}
    </section>

    <section className="panel">
      <h2>What should a fan know?</h2>
      <p>This pilot is validating the data flow first. Next this section will answer the useful football questions directly: biggest strength, biggest weakness, how they win, what can beat them, offense/defense grades, style, trajectory, and historical similarity.</p>
    </section>
  </>;
}
