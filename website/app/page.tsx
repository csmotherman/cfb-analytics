import Link from "next/link";
import {gameDate,gameTime,homeData,opponentOf} from "../lib/home-data";
import {formatMichiganSpread,marketLineFor} from "../lib/market-lines";
import {michiganPollSnapshot} from "../lib/polls";
import {michiganPreseasonProjection,preseasonPowerNational} from "../lib/preseason-power";
import {teamLogoUrl} from "../lib/team-assets";
import modelStyles from "../styles/homeModel.module.css";

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

const pollRank=(rank:number|null)=>rank?`#${rank}`:"—";

export default function Home(){
  const {next,squad,outlook}=homeData();
  const opponent=next?opponentOf(next):null;
  const market=next?marketLineFor(next.id):null;
  const cfpChance=outlook?`${Math.round(outlook.cfp.noVigImpliedProbability*100)}%`:"—";
  const projection=michiganPreseasonProjection();
  const rankings=preseasonPowerNational();
  const michiganPower=rankings?.teams.find(team=>team.teamId===130)??null;
  const modelRank=michiganPower?.rank??michiganPollSnapshot.modelRank;
  const projectedRecord=projection?`${projection.winDistribution.medianWins}-${projection.winDistribution.gamesWithData-projection.winDistribution.medianWins}`:"—";
  const expectedWins=projection?.winDistribution.expectedWins??null;
  const eightToTen=projection?Object.entries(projection.winDistribution.distributionPct).reduce((sum,[wins,pct])=>{
    const value=Number(wins);
    return value>=8&&value<=10?sum+pct:sum;
  },0):null;
  const ninePlus=projection?Object.entries(projection.winDistribution.distributionPct).reduce((sum,[wins,pct])=>Number(wins)>=9?sum+pct:sum,0):null;
  const distribution=projection?[8,9,10].map(wins=>({wins,pct:projection.winDistribution.distributionPct[String(wins)]??0})):[];
  const maxDist=Math.max(1,...distribution.map(row=>row.pct));
  const spotlightGames=projection?.games.filter(game=>["Oklahoma","Oregon","Ohio State"].includes(game.opponent))??[];
  const rankingPreview=rankings?[
    ...rankings.teams.slice(0,5),
    ...(michiganPower&&michiganPower.rank>5?[michiganPower]:[]),
  ]:[];
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
        <header><h2>MICHIGAN PULSE</h2><span>2026 PRESEASON</span></header>
        <div className="pulse-scroll">
          <article className="pulse-ranking-card">
            <small>TEAM RANKING</small>
            <div className="pulse-ranking-list">
              <div><span>AP POLL</span><strong>{pollRank(michiganPollSnapshot.apRank)}</strong></div>
              <div><span>COACHES POLL</span><strong>{pollRank(michiganPollSnapshot.coachesRank)}</strong></div>
              <div className="model-rank"><span>PRESEASON POWER</span><strong>{pollRank(modelRank)}</strong></div>
            </div>
            <span>{michiganPower?"Michigan Football Focus model":michiganPollSnapshot.modelRank?michiganPollSnapshot.label:michiganPollSnapshot.modelStatus}</span>
          </article>
          <article><small>PROJECTED RECORD</small><strong>{projectedRecord}</strong><span>{projection?`${projection.winDistribution.expectedWins.toFixed(1)} expected wins`:"Coming soon"}</span></article>
          <article><small>MARKET CFP CHANCE</small><strong>{cfpChance}</strong><span>{outlook?"Market outlook":"Coming soon"}</span></article>
        </div>
      </section>

      {(projection||rankings)&&<section className={modelStyles.modelSection} aria-labelledby="model-center-title">
        <header className={modelStyles.sectionHeader}>
          <div><span className={modelStyles.eyebrow}>2026 MODEL CENTER</span><h2 id="model-center-title"><span>PRESEASON</span> <em>OUTLOOK</em></h2></div>
          <Link href="/methodology">HOW IT WORKS</Link>
        </header>

        <div className={modelStyles.grid}>
          {projection&&<article className={modelStyles.projectionCard}>
            <div className={modelStyles.cardTop}>
              <div><span className={modelStyles.cardKicker}>MICHIGAN SEASON PROJECTION</span><strong className={modelStyles.record}>{projectedRecord}</strong><span className={modelStyles.recordLabel}>MEDIAN OUTCOME · 50,000 SIMULATIONS</span></div>
              <span className={modelStyles.modelBadge}>PRESEASON MODEL</span>
            </div>

            <div className={modelStyles.statRail}>
              <div><small>EXPECTED WINS</small><strong>{expectedWins?.toFixed(1)??"—"}</strong></div>
              <div><small>8-10 WINS</small><strong>{eightToTen!=null?`${eightToTen.toFixed(1)}%`:"—"}</strong></div>
              <div><small>9+ WINS</small><strong>{ninePlus!=null?`${ninePlus.toFixed(1)}%`:"—"}</strong></div>
            </div>

            <div className={modelStyles.dist}>
              <div className={modelStyles.distHeader}><span>MOST LIKELY WIN TOTALS</span><b>9 WINS LEADS</b></div>
              <div className={modelStyles.distRows}>
                {distribution.map(row=><div className={modelStyles.distRow} key={row.wins}>
                  <span>{row.wins}W</span>
                  <div className={modelStyles.track}><div className={modelStyles.fill} style={{width:`${Math.max(4,(row.pct/maxDist)*100)}%`}}/></div>
                  <span>{row.pct.toFixed(1)}%</span>
                </div>)}
              </div>
            </div>

            <div className={modelStyles.miniGames}>
              {spotlightGames.map(game=>{
                const winPct=Math.round((game.winProb??0)*100);
                const favored=winPct>=50;
                return <div className={modelStyles.miniGame} key={game.week}>
                  <small>WK {game.week}</small>
                  <strong>{game.opponentRank!=null?`#${game.opponentRank} `:""}{game.opponent}</strong>
                  <span className={favored?modelStyles.favored:modelStyles.underdog}>{winPct}% WIN</span>
                </div>;
              })}
            </div>

            <Link href="/2026-projection" className={modelStyles.primaryLink}>FULL GAME-BY-GAME PROJECTION <b>›</b></Link>
          </article>}

          {rankings&&<article className={modelStyles.rankingCard}>
            <div className={modelStyles.rankingHead}>
              <div><span className={modelStyles.cardKicker}>NATIONAL POWER RANKINGS</span><h3>2026 PRESEASON TOP 25</h3></div>
              <span>NO POLL OR<br/>BETTING INPUTS</span>
            </div>
            <div className={modelStyles.rankingList}>
              {rankingPreview.map(team=><div className={modelStyles.rankRow} data-michigan={team.teamId===130?"true":"false"} key={team.team}>
                <span className={modelStyles.rankNumber}>#{team.rank}</span>
                {team.teamId!=null?<img className={modelStyles.teamLogo} src={teamLogoUrl(team.teamId,64)} alt=""/>:<span/>}
                <div className={modelStyles.teamName}><strong>{team.team}</strong><small>{team.conference??"FBS"}</small></div>
                <div className={modelStyles.power}><strong>{team.powerScore?.toFixed(1)??"—"}</strong><small>POWER</small></div>
              </div>)}
            </div>
            <Link href="/rankings" className={modelStyles.rankingLink}>VIEW ALL 25 RANKINGS <b>›</b></Link>
          </article>}
        </div>
      </section>}

      <section className="mock-section">
        <header><h2>PLAYERS TO WATCH</h2><Link href="/players">VIEW ALL <b>›</b></Link></header>
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
          <Link href="/articles/what-to-expect-michigan-offense-2026"><div className="news-image"><img src="/images/articles/jason-beck.png" alt="Jason Beck"/></div><div><small>OFFENSE</small><h3>What to Expect From Michigan’s Offense in 2026</h3><span>Season preview · 9 min read</span></div></Link>
          <Link href="/articles/what-to-expect-michigan-defense-2026"><div className="news-image"><img src="/images/articles/troy-bowles.png" alt="Troy Bowles"/></div><div><small>DEFENSE</small><h3>What to Expect From Michigan’s Defense in 2026</h3><span>Season preview · 7 min read</span></div></Link>
          <Link href="/articles/can-michigan-new-staff-playoff-team"><div className="news-image"><img src="/images/articles/staff-article.png" alt="Michigan coaching staff"/></div><div><small>BIG PICTURE</small><h3>Can Michigan’s New Staff Turn the Wolverines Into a Playoff Team?</h3><span>Staff transition · 8 min read</span></div></Link>
        </div>
      </section>
    </div>
  </div>;
}
