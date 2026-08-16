import Link from "next/link";
import { avgMargin, fieldWinPct, findDynamicIdentity, findPowerRow, rankOf, tournamentRows } from "../../../../lib/data";

function label(value:unknown){
  if(value===null||value===undefined||value==="") return "—";
  return String(value).replaceAll("-"," ").replace(/\b\w/g,c=>c.toUpperCase());
}

export default async function TeamSeason({params}:{params:Promise<{team:string;season:string}>}){
  const p=await params; const team=decodeURIComponent(p.team); const season=Number(p.season);
  const power=findPowerRow(team,season); const identity=findDynamicIdentity(team,season);
  const total=tournamentRows().length;
  const rank=power?rankOf(power):null;
  const win=power?fieldWinPct(power):null;
  const margin=power?avgMargin(power):null;
  const style=identity?.identityStyle||{};
  const tags=Array.isArray(identity?.identityTags)?identity.identityTags:[];

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
      <div className="muted">TEAM IDENTITY</div>
      <h2 style={{marginBottom:8}}>{identity?.identityName||"—"}</h2>
      {tags.length?<div style={{marginBottom:14}}>{tags.map(tag=><span className="pill" key={tag}>{tag}</span>)}</div>:null}
      {identity?.identitySummary?<p style={{fontSize:17,lineHeight:1.6}}>{identity.identitySummary}</p>:null}
      {!identity?<div className="notice">No dynamic identity found for this team-season. Generate it with <code>python -m cfb_analytics.profiles.dynamic_profiles</code>.</div>:null}
    </section>

    {identity?<section className="panel">
      <h2>How did they play?</h2>
      <div className="grid">
        <div><div className="muted">Usage</div><h3>{label(style.usage)}</h3></div>
        <div><div className="muted">Method</div><h3>{label(style.method)}</h3></div>
        <div><div className="muted">Drive shape</div><h3>{label(style.paceShape)}</h3></div>
        <div><div className="muted">Efficiency shape</div><h3>{label(style.efficiencyShape)}</h3></div>
        <div><div className="muted">Attack driver</div><h3>{label(style.attackDriver)}</h3></div>
        <div><div className="muted">Commitment</div><h3>{label(style.commitment)}</h3></div>
        <div><div className="muted">Team structure</div><h3>{label(style.teamStructure)}</h3></div>
        <div><div className="muted">Effectiveness</div><h3>{label(style.effectiveness)}</h3></div>
        <div><div className="muted">Offense consistency</div><h3>{label(style.offenseConsistency)}</h3></div>
        <div><div className="muted">Defense consistency</div><h3>{label(style.defenseConsistency)}</h3></div>
      </div>
    </section>:null}

    <section className="panel">
      <h2>What should a fan know?</h2>
      <p>The identity above is season-wide. Tags add the strongest supporting tendencies, quality signals, consistency, and late-season trajectory without replacing the team&apos;s full-season identity.</p>
    </section>
  </>;
}
