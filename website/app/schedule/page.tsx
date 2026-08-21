import Link from "next/link";
import {gameDate,gameTime,homeData,logoUrl,opponentOf} from "../../lib/home-data";
import {formatMichiganSpread,marketLines} from "../../lib/market-lines";

export default function Schedule(){
  const {schedule,next}=homeData();
  const lines=new Map(marketLines().map(line=>[line.gameId,line]));
  const home=schedule.filter(game=>game.homeId===130).length;
  const road=schedule.length-home;
  const nextOpponent=next?opponentOf(next):null;
  const nextMarket=next?lines.get(String(next.id)):null;

  return <div className="mock-home schedule-home"><div className="mock-shell">
    <section className="mock-section schedule-intro">
      <header><div><span className="mock-eyebrow maize">2026 MICHIGAN</span><h1>SCHEDULE</h1><p>Every matchup in one clean view. Home, road, date, kickoff and market context when available.</p></div><div className="schedule-kpis"><span><small>GAMES</small><b>{schedule.length}</b></span><span><small>HOME</small><b>{home}</b></span><span><small>AWAY</small><b>{road}</b></span></div></header>
    </section>

    {next&&nextOpponent&&<section className="mock-section schedule-next-card">
      <div className="schedule-next-copy"><span className="mock-eyebrow maize">NEXT GAME · WEEK {next.week}</span><small>{nextOpponent.site}{next.conferenceGame?" · BIG TEN":""}</small><h2>MICHIGAN <span>{nextOpponent.site==="AWAY"?"@":"VS"}</span> {nextOpponent.name.toUpperCase()}</h2><div className="schedule-next-meta"><span>{gameDate(next)}</span><span>{gameTime(next)}</span><span>{next.venue}</span></div>{nextMarket&&<div className="schedule-next-market"><strong>{formatMichiganSpread(nextMarket.teamSpread)}</strong><span>{Math.round(nextMarket.marketWinChance*100)}% MARKET WIN CHANCE</span></div>}<Link className="mock-outline-button" href={`/games/${next.id}`}>GAME PREVIEW <b>›</b></Link></div>
      <div className="schedule-next-logo"><img src={logoUrl(nextOpponent.id)} alt={`${nextOpponent.name} logo`}/></div>
    </section>}

    <section className="mock-section schedule-list-section">
      <header><h2>FULL SCHEDULE</h2><span>WEEK BY WEEK</span></header>
      <div className="schedule-card-list">{schedule.map(game=>{const opponent=opponentOf(game);const market=lines.get(String(game.id));const isNext=next?.id===game.id;return <Link className={`schedule-row-card${isNext?" next":""}`} href={`/games/${game.id}`} key={game.id}>
        <div className="schedule-row-week"><small>WEEK</small><b>{game.week}</b></div>
        <div className="schedule-row-opponent"><img src={logoUrl(opponent.id)} alt=""/><div><small>{opponent.site}{game.conferenceGame?" · BIG TEN":""}</small><strong>{opponent.name}</strong></div></div>
        <div className="schedule-row-date"><span>{gameDate(game)}</span><small>{gameTime(game)}</small></div>
        <div className="schedule-row-market">{market?<><strong>{formatMichiganSpread(market.teamSpread)}</strong><small>{Math.round(market.marketWinChance*100)}% WIN</small></>:<><strong>—</strong><small>NO MARKET</small></>}</div>
        <b className="schedule-row-arrow">›</b>
      </Link>})}</div>
      <p className="schedule-market-note">Market lines are sourced preseason prices. Win chance is model-calibrated context, not a betting recommendation.</p>
    </section>
  </div></div>;
}
