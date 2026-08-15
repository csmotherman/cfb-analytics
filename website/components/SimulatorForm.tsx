"use client";
import { useState } from "react";

type Props={defaultHomeYear?:number;defaultHomeTeam?:string};

type SimResult={
  home:{season:number;team:string};away:{season:number;team:string};simulations:number;
  expectedHomeScore:number;expectedAwayScore:number;expectedMarginHome:number;expectedTotal:number;
  expectedPossessionsPerTeam:number;homeWinProbability:number;awayWinProbability:number;
  marginP10:number;medianMarginHome:number;marginP90:number;residualSd:number;
};

export function SimulatorForm({defaultHomeYear=2019,defaultHomeTeam="LSU"}:Props){
  const [homeYear,setHomeYear]=useState(defaultHomeYear); const [homeTeam,setHomeTeam]=useState(defaultHomeTeam);
  const [awayYear,setAwayYear]=useState(2019); const [awayTeam,setAwayTeam]=useState("Ohio State");
  const [sims,setSims]=useState(10000); const [result,setResult]=useState<SimResult|null>(null); const [error,setError]=useState(""); const [loading,setLoading]=useState(false);
  async function run(e:React.FormEvent){e.preventDefault();setLoading(true);setError("");setResult(null);try{
    const r=await fetch("/api/simulate",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({homeYear,homeTeam,awayYear,awayTeam,sims})});
    const body=await r.json(); if(!r.ok) throw new Error(body.error||"Simulation failed"); setResult(body);
  }catch(e:any){setError(e.message||String(e));}finally{setLoading(false);}}
  return <>
    <form className="panel" onSubmit={run}><div className="row">
      <label className="field"><b>Home year</b><input type="number" value={homeYear} onChange={e=>setHomeYear(Number(e.target.value))}/></label>
      <label className="field"><b>Home team</b><input value={homeTeam} onChange={e=>setHomeTeam(e.target.value)}/></label>
      <label className="field"><b>Away year</b><input type="number" value={awayYear} onChange={e=>setAwayYear(Number(e.target.value))}/></label>
      <label className="field"><b>Away team</b><input value={awayTeam} onChange={e=>setAwayTeam(e.target.value)}/></label>
      <label className="field"><b>Simulations</b><input type="number" min={100} max={250000} step={1000} value={sims} onChange={e=>setSims(Number(e.target.value))}/></label>
      <button className="button" disabled={loading}>{loading?"Simulating…":"Simulate"}</button>
    </div></form>
    {error&&<div className="error">{error}</div>}
    {result&&<section className="panel"><div className="muted">EXPECTED SCORE</div><div className="result-score">{result.home.team} {result.expectedHomeScore.toFixed(1)} — {result.away.team} {result.expectedAwayScore.toFixed(1)}</div>
      <div className="grid" style={{marginTop:18}}>
        <div><div className="muted">Home win</div><div className="big-number">{(result.homeWinProbability*100).toFixed(1)}%</div></div>
        <div><div className="muted">Away win</div><div className="big-number">{(result.awayWinProbability*100).toFixed(1)}%</div></div>
        <div><div className="muted">Home margin</div><div className="big-number">{result.expectedMarginHome>=0?"+":""}{result.expectedMarginHome.toFixed(1)}</div></div>
        <div><div className="muted">Expected total</div><div className="big-number">{result.expectedTotal.toFixed(1)}</div></div>
      </div>
      <p>Margin range: P10 {result.marginP10.toFixed(1)} / median {result.medianMarginHome.toFixed(1)} / P90 {result.marginP90.toFixed(1)}. Expected possessions/team: {result.expectedPossessionsPerTeam.toFixed(1)}.</p>
      <p className="muted">Pilot model output. This is a simulation estimate, not a historical fact or betting line.</p>
    </section>}
  </>;
}
