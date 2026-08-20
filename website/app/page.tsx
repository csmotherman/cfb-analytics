import Link from "next/link";
import {gameDate,gameTime,homeData,opponentOf} from "../lib/home-data";
import {formatMichiganSpread,marketLineFor} from "../lib/market-lines";
import {teamLogoUrl} from "../lib/team-assets";

const grade=(player:ReturnType<typeof homeData>["squad"][number])=>player.performanceGrade??player.grade??player.importanceTier??"—";

export default function Home(){
  const {next,schedule,roster,squad}=homeData();
  const opponent=next?opponentOf(next):null;
  const market=next?marketLineFor(next.id):null;
  const players=[
    squad.find(p=>p.id==="5141741"),
    squad.find(p=>p.id==="5079574"),
    squad.find(p=>p.id==="5159046"),
  ].filter(Boolean) as ReturnType<typeof homeData>["squad"];

  return <div className="mock-home">
    <div className="mock-shell">
      {next&&opponent&&<section className="mock-game-card">
        <div className="mock-matchup-art">
          <span className="mock-site-label">{opponent.site}</span>
          <div className="mock-logo-matchup">
            <div className="mock-team-logo"><img src={teamLogoUrl(130,256)} alt="Michigan logo"/><strong>MICHIGAN</strong></div>
            <span className="mock-vs">VS</span>
            <div className="mock-team-logo"><img src={teamLogoUrl(opponent.id,256)} alt={`${opponent.name} logo`}/><strong>{opponent.name.toUpperCase()}</strong></div>
          </div>
        </div>
        <div className="mock-game-content">
          <span className="mock-eyebrow maize">NEXT GAME</span>
          <h1>MICHIGAN</h1>
          <h2><span>VS</span> {opponent.name.toUpperCase()}</h2>
          <div className="mock-game-meta"><span>▣ {gameDate(next)}</span><span>◷ {gameTime(next)}</span><span>▣ {next.venue}</span></div>
          <div className="mock-game-lower">
            <div className="mock-probability"><span>{market?"MARKET WIN CHANCE":"WIN PROBABILITY"}</span><strong>{market?`${Math.round(market.marketWinChance*100)}%`:"—"}</strong><div><i style={{width:market?`${Math.round(market.marketWinChance*100)}%`:"0%"}}/></div><small>{market?`Michigan ${formatMichiganSpread(market.teamSpread)}`:"Available game week"}</small></div>
            <Link href="/schedule" className="mock-outline-button">GAME PREVIEW <b>›</b></Link>
          </div>
        </div>
      </section>}

      <section className="mock-section pulse-section">
        <header><h2>MICHIGAN PULSE</h2><span>2026 PRESEASON</span></header>
        <div className="pulse-scroll">
          <article><small>TEAM 147</small><strong>{roster.length}</strong><span>Wolverines</span></article>
          <article><small>SCHEDULE</small><strong>{schedule.length}</strong><span>Games</span></article>
          <article><small>{market?"NEXT GAME CHANCE":"CFP CHANCE"}</small><strong>{market?`${Math.round(market.marketWinChance*100)}%`:"—"}</strong><span>{market?"Market context":"Coming soon"}</span></article>
          <article><small>TREND</small><strong className="trend-arrow">↗</strong><span>New era</span></article>
          <article><small>BIGGEST TEST</small><strong>OU</strong><span>Oklahoma</span></article>
        </div>
      </section>

      <section className="mock-section">
        <header><h2>PLAYERS TO WATCH</h2><Link href="/team">VIEW ALL <b>›</b></Link></header>
        <div className="player-watch-scroll">
          {players.map(player=><Link className="watch-card" href={`/players/${player.id}`} key={player.id}>
            <div className="blank-player-image"><span>{player.jersey??"M"}</span></div>
            <div className="watch-copy"><small>#{player.jersey??"—"}</small><h3>{player.firstName}<br/>{player.lastName}</h3><p>{player.position??"ATH"} · {player.year===1?"Freshman":player.year===2?"Sophomore":player.year===3?"Junior":player.year===4?"Senior":"Michigan"}</p><div><b>{grade(player)}</b><span>PLAYER GRADE</span></div></div>
          </Link>)}
        </div>
      </section>

      <section className="mock-section news-section">
        <header><h2>LATEST NEWS</h2><Link href="/articles">VIEW ALL <b>›</b></Link></header>
        <div className="mock-news-list">
          <Link href="/articles/new-age-era"><div className="blank-news-image"/><div><small>ANALYSIS</small><h3>A New Age: Michigan enters 2026 with a new staff and a new ceiling</h3><span>Season preview</span></div></Link>
          <Link href="/articles/2026-coaching-staff"><div className="blank-news-image"/><div><small>NOTEBOOK</small><h3>Inside Michigan’s new coaching staff</h3><span>2026 preview</span></div></Link>
          <Link href="/recruiting"><div className="blank-news-image"/><div><small>RECRUITING</small><h3>Track Michigan’s roster and recruiting movement</h3><span>Recruiting hub</span></div></Link>
        </div>
      </section>
    </div>
  </div>;
}
