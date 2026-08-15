import { avgMargin, fieldWinPct, findPowerRow, rankOf } from "../../lib/data";

function pct(v:number|null){return v===null?"—":(v*100).toFixed(1)+"%";}
function margin(v:number|null){return v===null?"—":`${v>=0?"+":""}${v.toFixed(1)}`;}

export default async function Compare({searchParams}:{searchParams:Promise<Record<string,string|string[]|undefined>>}){
  const q=await searchParams; const get=(k:string,d:string)=>String(Array.isArray(q[k])?q[k]?.[0]:q[k]??d);
  const aTeam=get("aTeam","Michigan"), bTeam=get("bTeam","Ohio State"); const aYear=Number(get("aYear","2023")), bYear=Number(get("bYear","2019"));
  const a=findPowerRow(aTeam,aYear), b=findPowerRow(bTeam,bYear);
  return <>
    <h1>Compare Teams</h1><p className="muted">Pilot comparison starts with the historical power outputs. We will add full offense/defense/style bars after validating the page flow.</p>
    <form className="panel" method="get"><div className="row">
      <label className="field"><b>Team A year</b><input name="aYear" defaultValue={aYear}/></label><label className="field"><b>Team A</b><input name="aTeam" defaultValue={aTeam}/></label>
      <label className="field"><b>Team B year</b><input name="bYear" defaultValue={bYear}/></label><label className="field"><b>Team B</b><input name="bTeam" defaultValue={bTeam}/></label><button className="button">Compare</button>
    </div></form>
    {(!a||!b)?<div className="error">Could not find one or both team-seasons in the historical tournament directory.</div>:<div className="grid">
      <section className="card"><h2>{aYear} {aTeam}</h2><p>All-time rank: <b>#{rankOf(a)??"—"}</b></p><p>Field win rate: <b>{pct(fieldWinPct(a))}</b></p><p>Avg neutral margin: <b>{margin(avgMargin(a))}</b></p></section>
      <section className="card"><h2>{bYear} {bTeam}</h2><p>All-time rank: <b>#{rankOf(b)??"—"}</b></p><p>Field win rate: <b>{pct(fieldWinPct(b))}</b></p><p>Avg neutral margin: <b>{margin(avgMargin(b))}</b></p></section>
    </div>}
  </>;
}
