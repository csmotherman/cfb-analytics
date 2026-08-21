import Link from "next/link";
import {gameDate,gameTime,homeData,opponentOf} from "../lib/home-data";
import {formatMichiganSpread,marketLineFor} from "../lib/market-lines";
import {teamLogoUrl} from "../lib/team-assets";

const grade=(player:ReturnType<typeof homeData>["squad"][number])=>player.grade??"—";

const watchImage=(firstName:string,lastName:string)=>{
  const key=`${firstName} ${lastName}`;
  const images:Record<string,string>={
    "Bryce Underwood":"/images/home/bryce-underwood.png",
    "John Henry Daley":"/images/home/john-henry-daley.png",
    "Jordan Marshall":"/images/home/jordan-marshall.png",
  };
  return images[key]??"/images/home/bryce-underwood.png";
};

export default function Home(){
  const {next,schedule,squad,outlook}=homeData();
  const opponent=next?opponentOf(next):null;
  const market=next?marketLineFor(next.id):null;
  const cfpChance=outlook?`${Math.round(outlook.cfp.noVigImpliedProbability*100)}%`:"—";
  const players=[
    squad.find(p=>p.firstName==="Bryce"&&p.lastName==="Underwood"),
    squad.find(p=>p.firstName==="John Henry"&&p.lastName==="Daley"),
    squad.find(p=>p.firstName==="Jordan"&&p.lastName==="Marshall"),
  ].filter(Boolean) as ReturnType<typeof homeData>["squad"];

  return <div className="mock-home">
    <div className="mock-shell">
      {next&&opponent&&<section className="mock-game-card">
        <div className="mock-hero-photo" aria-hidden="true">
          <img src="/images/Bryce Underwood/Bryce4k.jpg" alt=""/>
        </div>
        <div className="mock-game-content">
          <span className="mock-eyebrow maize">NEXT GAME</span>
          <h1>MICHIGAN</h1>
          <h2><span>VS</span> {opponent.name.toUpperCase()}</h2>
          <div className="mock-game-meta"><span>▣ {gameDate(next)}</span><span>◷ {gameTime(next)}</span><span>▣ {next.venue}</span></div>
          <div className="mock-game-lower">
            <div className="mock-probability"><span>{market?"MARKET WIN CHANCE":"WIN PROBABILITY"}</span><strong>{market?`${Math.round(market.marketWinChance*100)}%`:"—"}</strong><div><i style={{width:market?`${Math.round(market.marketWinChance*100)}%`:"0%"}}/></div><small>{market?`Michigan ${formatMichiganSpread(market.teamSpread)}`:"Available game week"}</small></div>
            <Link href={`/games/${next.id}`} className="mock-outline-button">GAME PREVIEW <b>›</b></Link>
          </div>
        </div>
      </section>}

      <section className="mock-section pulse-section">
        <header><h2>MICHIGAN PULSE</h2><span>UPDATED TODAY</span></header>
        <div className="pulse-scroll">
          <article><small>PROJECTED RECORD</small><strong>—</strong><span>Coming soon</span></article>
          <article><small>TEAM RANKING</small><strong>—</strong><span>National</span></article>
          <article><small>CFP CHANCE</small><strong>{cfpChance}</strong><span>{outlook?"Market outlook":"Coming soon"}</span></article>
          <article><small>TREND</small><strong className="trend-arrow">↗</strong><span>Preseason</span></article>
          {next&&opponent?<article className="pulse-opponent"><small>UPCOMING TEST</small><img src={teamLogoUrl(opponent.id,128)} alt={`${opponent.name} logo`}/><span>{opponent.site==="HOME"?"vs":"@"} {opponent.name} · {gameDate(next)}</span></article>:<article><small>UPCOMING TEST</small><strong>—</strong><span>Schedule TBD</span></article>}
        </div>
      </section>

      <section className="mock-section">
        <header><h2>PLAYERS TO WATCH</h2><Link href="/team">VIEW ALL <b>›</b></Link></header>
        <div className="player-watch-scroll">
          {players.map(player=><Link className="watch-card" href={`/players/${player.id}`} key={player.id}>
            <div className="blank-player-image"><img src={watchImage(player.firstName,player.lastName)} alt={`${player.firstName} ${player.lastName}`}/><span>{player.jersey??"M"}</span></div>
            <div className="watch-copy"><small>#{player.jersey??"—"}</small><h3>{player.firstName}<br/>{player.lastName}</h3><p>{player.position??"ATH"} · {player.year===1?"Freshman":player.year===2?"Sophomore":player.year===3?"Junior":player.year===4?"Senior":"Michigan"}</p><div><b>{grade(player)}</b><span>PLAYER GRADE</span></div></div>
          </Link>)}
        </div>
      </section>

      <section className="mock-section news-section">
        <header><h2>LATEST NEWS</h2><Link href="/articles">VIEW ALL <b>›</b></Link></header>
        <div className="mock-news-list">
          <Link href="/articles"><div className="blank-news-image"/><div><small>NEWS</small><h3>Michigan Football Article Coming Soon</h3><span>Placeholder story</span></div></Link>
          <Link href="/articles"><div className="blank-news-image"/><div><small>ANALYSIS</small><h3>Michigan Football Analysis Coming Soon</h3><span>Placeholder story</span></div></Link>
          <Link href="/articles"><div className="blank-news-image"/><div><small>NOTEBOOK</small><h3>Michigan Football Notebook Coming Soon</h3><span>Placeholder story</span></div></Link>
        </div>
      </section>
    </div>
  </div>;
}
