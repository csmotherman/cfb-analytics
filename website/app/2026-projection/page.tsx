import type { Metadata } from "next";
import Link from "next/link";
import { michiganPreseasonProjection } from "../../lib/preseason-power";
import { teamLogoUrl } from "../../lib/team-assets";

export const metadata: Metadata = {
  title: "Michigan 2026 Win Projection",
  description: "Michigan's projected 2026 record, game by game, from a preseason power-rating research model -- not the site's production predictions.",
};

const SITE_LABEL = { home: "HOME", away: "AWAY", neutral: "NEUTRAL" } as const;

export default function ProjectionPage(){
  const data = michiganPreseasonProjection();

  if(!data || data.games.length===0){
    return <div className="mock-home"><div className="mock-shell">
      <section className="mock-section"><header><div><span className="mock-eyebrow maize">MICHIGAN 2026</span><h1>SEASON PROJECTION</h1></div></header><p>Projection is not available yet.</p></section>
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

  return <div className="mock-home"><div className="mock-shell">
    <section className="mock-section pp-hero">
      <header><div>
        <span className="mock-eyebrow maize">MICHIGAN 2026</span>
        <h1>SEASON PROJECTION</h1>
        <p>Every 2026 game projected from a single preseason power rating, held fixed all season -- this is a &quot;before Game 1&quot; view, not an in-season model that updates with real 2026 results as they happen.</p>
      </div></header>

      <div className="pp-hero-record">
        <span><small>PROJECTED RECORD</small><b>{projectedWins}-{projectedLosses}</b></span>
        <span><small>EXPECTED WINS</small><b>{wd.expectedWins.toFixed(1)}</b></span>
        <span><small>MEDIAN OUTCOME</small><b>{wd.medianWins}-{wd.gamesWithData-wd.medianWins}</b></span>
        <span><small>UNDEFEATED</small><b>{wd.probUndefeated.toFixed(1)}%</b></span>
      </div>

      <div className="pp-disclaimer">
        <b>RESEARCH MODEL</b>
        <span>{data.disclaimer}</span>
      </div>
    </section>

    <section className="mock-section" style={{marginTop:22}}>
      <header><h2>WIN TOTAL DISTRIBUTION</h2><span>50,000 SEASON SIMULATIONS</span></header>
      <div className="pp-win-dist">
        {distEntries.map(row=><div className={`pp-win-dist-row${row.wins===wd.medianWins?" pp-median":""}`} key={row.wins}>
          <b>{row.wins}W</b>
          <div className="pp-win-dist-track"><div className="pp-win-dist-fill" style={{width:`${Math.max(2,100*row.pct/maxPct)}%`}}/></div>
          <span>{row.pct.toFixed(1)}%</span>
        </div>)}
      </div>
    </section>

    <section className="mock-section" style={{marginTop:26}}>
      <header><h2>GAME BY GAME</h2><span>WEEK BY WEEK</span></header>
      <div className="pp-game-list">
        {rows.map(({week,game})=>{
          if(!game) return <div className="pp-bye-row" key={`bye-${week}`}>WEEK {week} · BYE</div>;
          if(!game.dataAvailable) return <div className="pp-game-row" key={week}>
            <div className="pp-game-week"><small>WK</small><b>{week}</b></div>
            <div className="pp-game-opponent"><div><small>{SITE_LABEL[game.site]}</small><strong>{game.opponent}</strong></div></div>
            <div className="pp-game-margin"/><div className="pp-game-prob"><b>—</b><small>NO RATING</small></div><b className="pp-game-arrow"/>
          </div>;
          const favored = (game.winProb ?? 0) >= 0.5;
          const marginLabel = game.predictedMargin!=null ? `${game.predictedMargin>=0?"+":""}${game.predictedMargin.toFixed(1)}` : "—";
          const content = <>
            <div className="pp-game-week"><small>WK</small><b>{week}</b></div>
            <div className="pp-game-opponent">
              {game.opponentTeamId!=null && <img src={teamLogoUrl(game.opponentTeamId,64)} alt=""/>}
              <div><small>{SITE_LABEL[game.site]}{game.opponentRank!=null?` · #${game.opponentRank}`:""}</small><strong>{game.opponent}</strong></div>
            </div>
            <div className="pp-game-margin"><strong className={favored?"pp-favored":"pp-underdog"}>{marginLabel}</strong><small>PROJ MARGIN</small></div>
            <div className="pp-game-prob"><b className={favored?"pp-favored":"pp-underdog"}>{Math.round((game.winProb ?? 0)*100)}%</b><small>WIN PROB</small></div>
            <b className="pp-game-arrow">›</b>
          </>;
          return game.gameId
            ? <Link className="pp-game-row" href={`/games/${game.gameId}`} key={week}>{content}</Link>
            : <div className="pp-game-row" key={week}>{content}</div>;
        })}
      </div>
      <p className="schedule-market-note">Win probability and margin ranges come from an empirical bootstrap of the model&apos;s own out-of-sample Week 1 prediction errors (2018-2025), not an assumed distribution.</p>
    </section>
  </div></div>;
}
