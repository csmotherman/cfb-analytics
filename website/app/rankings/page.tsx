import type { Metadata } from "next";
import { preseasonPowerNational } from "../../lib/preseason-power";
import { teamLogoUrl } from "../../lib/team-assets";

export const metadata: Metadata = {
  title: "2026 Preseason Top 25",
  description: "A preseason college football power ranking built from prior-season results, recruiting, and QB continuity only -- no AP poll, SP+, FPI, or betting lines.",
};

export default function RankingsPage(){
  const data = preseasonPowerNational();

  if(!data || data.teams.length===0){
    return <div className="mock-home"><div className="mock-shell">
      <section className="mock-section"><header><div><span className="mock-eyebrow maize">2026 PRESEASON</span><h1>TOP 25</h1></div></header><p>Rankings are not available yet.</p></section>
    </div></div>;
  }

  const top25 = data.teams.slice(0, 25);

  return <div className="mock-home"><div className="mock-shell">
    <section className="mock-section">
      <header><div>
        <span className="mock-eyebrow maize">2026 PRESEASON</span>
        <h1>TOP 25</h1>
        <p>A power rating built only from what was known before Week 1: 2023-2025 opponent-adjusted results (recency-weighted), the recruiting class, and QB continuity. No AP poll, SP+, FPI, or betting lines went into it.</p>
      </div></header>

      <div className="pp-disclaimer">
        <b>RESEARCH MODEL</b>
        <span>{data.disclaimer}</span>
      </div>
    </section>

    <section className="mock-section" style={{marginTop:22}}>
      <div className="rankings-table-shell">
      <div className="rankings-swipe"><span>↔</span> SWIPE FOR MORE</div>
      <div className="rankings-table-wrap">
        <table className="rankings-table">
          <thead><tr>
            <th className="rk-rank">RK</th>
            <th className="rk-team">TEAM</th>
            <th>POWER</th>
            <th>OFFENSE</th>
            <th>DEFENSE</th>
            <th>RECRUITING</th>
            <th>QB</th>
          </tr></thead>
          <tbody>
            {top25.map(team=>{
              const isMichigan = team.teamId===130;
              const chipTier = team.rank<=4 ? "top4" : team.rank<=12 ? "top12" : "";
              return <tr key={team.team} className={isMichigan?"rk-michigan":""}>
                <td className="rk-rank"><span className={`rk-rank-chip ${chipTier}`}>{team.rank}</span></td>
                <td className="rk-team">
                  <div className="rk-team-cell">
                    {team.teamId!=null && <img src={teamLogoUrl(team.teamId,64)} alt=""/>}
                    <div><strong>{team.team}</strong><small>{team.conference ?? "—"}</small></div>
                  </div>
                </td>
                <td className="rk-power">{team.powerScore?.toFixed(1) ?? "—"}</td>
                <td>{team.offense2025!=null ? (team.offense2025>=0?"+":"")+team.offense2025.toFixed(1) : "—"}</td>
                <td>{team.defense2025!=null ? (team.defense2025>=0?"+":"")+team.defense2025.toFixed(1) : "—"}</td>
                <td>{team.recruiting3yrAvg?.toFixed(0) ?? "—"}</td>
                <td>{team.qbReturningFlag===1
                  ? <span className="rk-qb yes">RETURNING</span>
                  : team.qbReturningFlag===0 ? <span className="rk-qb no">NEW</span> : "—"}</td>
              </tr>;
            })}
          </tbody>
        </table>
      </div>
      </div>
      <p className="schedule-market-note">Power is expected points above an average FBS team on a neutral field. Offense/defense are the same scale (positive = above average). Recruiting is the 3-year class average (247/Rivals-style composite points). Full backtest methodology and results: <a href="/methodology">/methodology</a>.</p>
    </section>
  </div></div>;
}
