import type { Metadata } from "next";
import Link from "next/link";
import { michiganPreseasonProjection } from "../../lib/preseason-power";
import { teamLogoUrl } from "../../lib/team-assets";
import styles from "../../styles/forecastPages.module.css";

export const metadata: Metadata = {
  title: "Michigan 2026 Win Projection",
  description: "Michigan's projected 2026 record and game-by-game win probabilities from a preseason model frozen before Week 1.",
};

const SITE_LABEL = { home: "HOME", away: "AWAY", neutral: "NEUTRAL" } as const;

export default function ProjectionPage(){
  const data = michiganPreseasonProjection();

  if(!data || data.games.length===0){
    return <div className={styles.page}><div className={styles.shell}>
      <section className={`${styles.hero} ${styles.heroCompact}`}>
        <div className={styles.heroContent}>
          <span className={styles.eyebrow}>MICHIGAN 2026</span>
          <h1>SEASON PROJECTION</h1>
          <p className={styles.heroDeck}>Projection is not available yet.</p>
        </div>
      </section>
    </div></div>;
  }

  const { games, winDistribution: wd } = data;
  const weeks = games.map(g=>g.week);
  const minWeek = Math.min(...weeks), maxWeek = Math.max(...weeks);
  const rows: Array<{week:number; game?: typeof games[number]}> = [];
  for(let w=minWeek; w<=maxWeek; w++){
    const game = games.find(g=>g.week===w);
    rows.push({week:w, game});
  }

  const distEntries = Object.entries(wd.distributionPct)
    .map(([wins,pct])=>({wins:Number(wins),pct}))
    .filter(row=>row.pct>0)
    .sort((a,b)=>a.wins-b.wins);
  const maxPct = Math.max(...distEntries.map(row=>row.pct));
  const projectedWins = Math.round(wd.expectedWins);
  const projectedLosses = wd.gamesWithData - projectedWins;

  return <div className={styles.page}><div className={styles.shell}>
    <section className={styles.hero}>
      <div className={styles.heroContent}>
        <span className={styles.eyebrow}>MICHIGAN 2026 · PRESEASON MODEL</span>
        <h1>SEASON PROJECTION</h1>
        <p className={styles.heroDeck}>Every game projected before kickoff using one frozen preseason power rating. No 2026 results are allowed to move the forecast after the season begins.</p>
      </div>

      <div className={styles.heroStats} aria-label="Season projection summary">
        <div className={styles.heroStat}><small>PROJECTED RECORD</small><strong>{projectedWins}-{projectedLosses}</strong></div>
        <div className={styles.heroStat}><small>EXPECTED WINS</small><strong>{wd.expectedWins.toFixed(1)}</strong></div>
        <div className={styles.heroStat}><small>MEDIAN OUTCOME</small><strong>{wd.medianWins}-{wd.gamesWithData-wd.medianWins}</strong></div>
        <div className={styles.heroStat}><small>UNDEFEATED</small><strong>{wd.probUndefeated.toFixed(1)}%</strong></div>
      </div>
    </section>

    <div className={styles.researchNote}>
      <b>BACKTESTED MODEL</b>
      <span>Frozen before Week 1 and walk-forward tested on the 2018-2025 seasons: 12.5-point margin MAE and 77.9% winner accuracy. Inputs are prior-season opponent-adjusted performance, recruiting and QB continuity; no polls or betting lines are used.</span>
    </div>

    <section className={styles.section}>
      <header className={styles.sectionHeader}>
        <h2>WIN TOTAL DISTRIBUTION</h2>
        <span>50,000 SEASON SIMULATIONS</span>
      </header>
      <div className={styles.distributionPanel}>
        <div className={styles.distRows}>
          {distEntries.map(row=><div className={`${styles.distRow}${row.wins===wd.medianWins?` ${styles.distMedian}`:""}`} key={row.wins}>
            <b className={styles.distWins}>{row.wins}W</b>
            <div className={styles.distTrack}><div className={styles.distFill} style={{width:`${Math.max(2,100*row.pct/maxPct)}%`}}/></div>
            <span className={styles.distPct}>{row.pct.toFixed(1)}%</span>
          </div>)}
        </div>
      </div>
    </section>

    <section className={styles.section}>
      <header className={styles.sectionHeader}>
        <h2>GAME BY GAME</h2>
        <span>WEEK BY WEEK</span>
      </header>
      <div className={styles.gameBoard}>
        <div className={styles.gameHeader} aria-hidden="true">
          <span>WEEK</span><span>OPPONENT</span><span>PROJ MARGIN</span><span>WIN PROB</span><span/>
        </div>
        {rows.map(({week,game})=>{
          if(!game) return <div className={styles.byeRow} key={`bye-${week}`}>WEEK {week} · BYE</div>;

          if(!game.dataAvailable) return <div className={styles.gameRow} key={week}>
            <div className={styles.gameWeek}><small>WK</small><b>{week}</b></div>
            <div className={styles.opponent}>
              <div className={styles.opponentCopy}><div className={styles.siteLine}><span className={styles.sitePill}>{SITE_LABEL[game.site]}</span></div><strong>{game.opponent}</strong></div>
            </div>
            <div className={`${styles.metric} ${styles.marginMetric}`}><strong>—</strong><small>PROJ MARGIN</small></div>
            <div className={`${styles.metric} ${styles.probMetric}`}><strong>—</strong><small>NO RATING</small></div>
            <b className={styles.gameArrow}/>
          </div>;

          const favored = (game.winProb ?? 0) >= 0.5;
          const marginLabel = game.predictedMargin!=null ? `${game.predictedMargin>=0?"+":""}${game.predictedMargin.toFixed(1)}` : "—";
          const metricClass = favored?styles.favored:styles.underdog;
          const content = <>
            <div className={styles.gameWeek}><small>WK</small><b>{week}</b></div>
            <div className={styles.opponent}>
              {game.opponentTeamId!=null && <img src={teamLogoUrl(game.opponentTeamId,64)} alt=""/>}
              <div className={styles.opponentCopy}>
                <div className={styles.siteLine}><span className={styles.sitePill}>{SITE_LABEL[game.site]}</span>{game.opponentRank!=null&&<span>#{game.opponentRank}</span>}</div>
                <strong>{game.opponent}</strong>
              </div>
            </div>
            <div className={`${styles.metric} ${styles.marginMetric}`}><strong className={metricClass}>{marginLabel}</strong><small>PROJ MARGIN</small></div>
            <div className={`${styles.metric} ${styles.probMetric}`}><strong className={metricClass}>{Math.round((game.winProb ?? 0)*100)}%</strong><small>WIN PROB</small></div>
            <b className={styles.gameArrow}>›</b>
          </>;

          return game.gameId
            ? <Link className={styles.gameRow} href={`/games/${game.gameId}`} key={week}>{content}</Link>
            : <div className={styles.gameRow} key={week}>{content}</div>;
        })}
      </div>
      <p className={styles.marketNote}>Win probability and margin ranges come from an empirical bootstrap of the model&apos;s own out-of-sample Week 1 prediction errors (2018-2025), not an assumed distribution.</p>
    </section>
  </div></div>;
}
