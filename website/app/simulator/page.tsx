import { SimulatorForm } from "../../components/SimulatorForm";

export default async function SimulatorPage({searchParams}:{searchParams:Promise<Record<string,string|string[]|undefined>>}){
  const q=await searchParams;
  const homeYear=Number(Array.isArray(q.homeYear)?q.homeYear[0]:q.homeYear)||2019;
  const homeTeam=String(Array.isArray(q.homeTeam)?q.homeTeam[0]:q.homeTeam||"LSU");
  return <>
    <h1>Historical Game Simulator</h1>
    <p className="muted">Pick any two supported team-seasons. Home field is real here; flip the teams to test the reverse location.</p>
    <SimulatorForm defaultHomeYear={homeYear} defaultHomeTeam={homeTeam}/>
    <div className="notice">First run requires the prepared simulator cache. If needed, from the repo root run <code>python -m cfb_analytics.profiles.game_simulator --prepare</code>.</div>
  </>;
}
