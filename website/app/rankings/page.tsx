import type { Metadata } from "next";
import { preseasonPowerNational } from "../../lib/preseason-power";
import { teamLogoUrl } from "../../lib/team-assets";
import styles from "../../styles/forecastPages.module.css";

export const metadata: Metadata = {
  title: "2026 Preseason Top 25",
  description: "A preseason college football power ranking built from prior-season results, recruiting, and QB continuity only -- no AP poll, SP+, FPI, or betting lines.",
};

const signed=(value:number|null|undefined)=>value!=null?`${value>=0?"+":""}${value.toFixed(1)}`:"—";
const metricTone=(value:number|null|undefined)=>value==null?"":value>=0?styles.metricPositive:styles.metricNegative;

export default function RankingsPage(){
  const data = preseasonPowerNational();

  if(!data || data.teams.length===0){
    return <div className={styles.page}><div className={styles.shell}>
      <section className={`${styles.hero} ${styles.heroCompact}`}>
        <div className={styles.heroContent}>
          <span className={styles.eyebrow}>2026 PRESEASON</span>
          <h1>TOP 25</h1>
          <p className={styles.heroDeck}>Rankings are not available yet.</p>
        </div>
      </section>
    </div></div>;
  }

  const top25 = data.teams.slice(0,25);
  const podium = top25.slice(0,3);

  return <div className={styles.page}><div className={styles.shell}>
    <section className={`${styles.hero} ${styles.heroCompact}`}>
      <div className={styles.heroContent}>
        <span className={styles.eyebrow}>2026 PRESEASON · MFF POWER RATING</span>
        <h1>TOP 25</h1>
        <p className={styles.heroDeck}>Built only from information available before Week 1: recency-weighted opponent-adjusted performance, recruiting and quarterback continuity. No polls, SP+, FPI or betting lines are model inputs.</p>
      </div>
      <div className={styles.rankHeroRail} aria-label="Top three preseason teams">
        {podium.map(team=><div className={styles.rankHeroItem} key={team.team}>
          <span className={styles.rankHeroNumber}>#{team.rank}</span>
          <div><strong>{team.team}</strong><small>POWER {team.powerScore?.toFixed(1) ?? "—"}</small></div>
        </div>)}
      </div>
    </section>

    <div className={styles.researchNote}>
      <b>RESEARCH MODEL</b>
      <span>{data.disclaimer}</span>
    </div>

    <section className={styles.section}>
      <header className={styles.sectionHeader}>
        <h2>NATIONAL POWER RANKINGS</h2>
        <span>EXPECTED POINTS VS. AVERAGE FBS TEAM</span>
      </header>
      <div className={styles.rankingsShell}>
        <table className={styles.rankingsTable}>
          <thead><tr>
            <th>RK</th>
            <th>TEAM</th>
            <th>POWER</th>
            <th>OFFENSE</th>
            <th>DEFENSE</th>
            <th>RECRUITING</th>
            <th>QB</th>
          </tr></thead>
          <tbody>
            {top25.map(team=>{
              const isMichigan = team.teamId===130;
              const rankClass = team.rank<=4?styles.rankTop4:team.rank<=12?styles.rankTop12:"";
              return <tr key={team.team} className={isMichigan?styles.michiganRow:""}>
                <td className={styles.rankCell} data-label="RANK"><span className={`${styles.rankChip}${rankClass?` ${rankClass}`:""}`}>{team.rank}</span></td>
                <td className={styles.teamCell} data-label="TEAM">
                  <div className={styles.teamInner}>
                    {team.teamId!=null&&<img src={teamLogoUrl(team.teamId,64)} alt=""/>}
                    <div><strong>{team.team}</strong><small>{team.conference??"—"}</small></div>
                  </div>
                </td>
                <td className={styles.powerCell} data-label="POWER">{team.powerScore?.toFixed(1)??"—"}</td>
                <td className={`${styles.offenseCell} ${metricTone(team.offense2025)}`} data-label="OFFENSE">{signed(team.offense2025)}</td>
                <td className={`${styles.defenseCell} ${metricTone(team.defense2025)}`} data-label="DEFENSE">{signed(team.defense2025)}</td>
                <td className={styles.recruitingCell} data-label="RECRUITING">{team.recruiting3yrAvg?.toFixed(0)??"—"}</td>
                <td className={styles.qbCell} data-label="QB">
                  {team.qbReturningFlag===1
                    ? <span className={`${styles.qbBadge} ${styles.qbReturning}`}>RETURNING</span>
                    : team.qbReturningFlag===0
                      ? <span className={`${styles.qbBadge} ${styles.qbNew}`}>NEW</span>
                      : "—"}
                </td>
              </tr>;
            })}
          </tbody>
        </table>
      </div>
      <p className={styles.rankNote}>Power is expected points above an average FBS team on a neutral field. Offense and defense use the same scale, where positive means above average. Recruiting is the 3-year class average. Full backtest methodology and results are available on the <a href="/methodology">methodology page</a>.</p>
    </section>
  </div></div>;
}
