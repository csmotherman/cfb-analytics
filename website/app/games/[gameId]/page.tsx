import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {gameById,opponent} from "../../../lib/michigan/games";
import {gamePreview} from "../../../lib/michigan/game-preview";
import {marketLineFor,formatMichiganSpread} from "../../../lib/market-lines";
import {teamLogoUrl} from "../../../lib/team-assets";
import {gameDate,gameTime} from "../../../lib/home-data";

type Props={params:Promise<{gameId:string}>};
const rank=(value:number|undefined|null)=>value==null?"—":`#${value}`;
const rating=(value:number|undefined|null)=>value==null?"—":value.toFixed(1);

export async function generateMetadata({params}:Props):Promise<Metadata>{
  const game=gameById((await params).gameId);
  if(!game)return{title:"Game not found"};
  const opp=opponent(game);
  return{
    title:`Michigan vs ${opp.name} Game Preview`,
    description:`Michigan vs ${opp.name}: opponent-adjusted offense, defense and overall rankings, conference and market outlook.`
  };
}

export default async function GameHub({params}:Props){
  const game=gameById((await params).gameId);
  if(!game)notFound();

  const market=marketLineFor(game.id);
  const {opp,baselineSeason,michigan,opponent:opponentRatings}=gamePreview(game);
  const home=game.homeId===130;

  const michiganConference=home?(game.homeConference??"Big Ten"):(game.awayConference??"Big Ten");
  const opponentConference=home?(game.awayConference??"—"):(game.homeConference??"—");
  const marketMargin=market?Math.abs(market.teamSpread):null;
  const marketLeader=market?(market.teamSpread<=0?"Michigan":opp.name):null;

  return <main className="game-preview-page">
    <div className="preview-app-shell">
      <header className="preview-topbar">
        <Link href="/schedule">‹ SCHEDULE</Link>
        <h1>GAME PREVIEW</h1>
        <span>2026</span>
      </header>

      <section className="preview-matchup-card">
        <div className="preview-matchup">
          <div>
            <img src={teamLogoUrl(130,256)} alt="Michigan logo"/>
            <strong>MICHIGAN</strong>
            <small>{michiganConference}</small>
          </div>
          <span>VS</span>
          <div>
            <img src={teamLogoUrl(opp.id,256)} alt={`${opp.name} logo`}/>
            <strong>{opp.name.toUpperCase()}</strong>
            <small>{opponentConference}</small>
          </div>
        </div>
        <div className="preview-meta">
          <span>{gameDate(game)}</span>
          <span>{gameTime(game)} ET</span>
          <span>{game.venue??(home?"Michigan Stadium":"Away")}</span>
        </div>
      </section>

      <section className="preview-block">
        <div className="preview-section-heading">
          <span>{baselineSeason} OPPONENT-ADJUSTED BASELINE</span>
          <h2>TEAM COMPARISON</h2>
        </div>

        <div className="comparison-table ridge-matchup-table">
          <div className="comparison-head">
            <span><img src={teamLogoUrl(130,64)} alt=""/>MICHIGAN</span>
            <i>NATIONAL RANK</i>
            <span><img src={teamLogoUrl(opp.id,64)} alt=""/>{opp.name.toUpperCase()}</span>
          </div>
          <div><strong>{rank(michigan?.overall.rank)}</strong><span>OVERALL</span><strong>{rank(opponentRatings?.overall.rank)}</strong></div>
          <div className="rating-row"><strong>{rating(michigan?.overall.rating)}</strong><span>OVERALL RATING</span><strong>{rating(opponentRatings?.overall.rating)}</strong></div>
          <div><strong>{rank(michigan?.offense.rank)}</strong><span>OFFENSE</span><strong>{rank(opponentRatings?.offense.rank)}</strong></div>
          <div className="rating-row"><strong>{rating(michigan?.offense.rating)}</strong><span>OFFENSIVE RATING</span><strong>{rating(opponentRatings?.offense.rating)}</strong></div>
          <div><strong>{rank(michigan?.defense.rank)}</strong><span>DEFENSE</span><strong>{rank(opponentRatings?.defense.rank)}</strong></div>
          <div className="rating-row"><strong>{rating(michigan?.defense.rating)}</strong><span>DEFENSIVE RATING</span><strong>{rating(opponentRatings?.defense.rating)}</strong></div>
          <div><strong className="conference-value">{michiganConference}</strong><span>CONFERENCE</span><strong className="conference-value">{opponentConference}</strong></div>
        </div>
        <p className="preview-footnote">Offense and defense are the exact opponent-adjusted Ridge ratings used on the Analytics page: points per drive, yards per drive, success rate and scoring-drive rate, adjusted for opponent strength. Ratings are centered at 100; higher is better. Overall is the equal-weight average of the two unit ratings, then ranked nationally.</p>
      </section>

      <section className="market-preview-card">
        <div className="preview-section-heading market-heading">
          <span>BETTING MARKET</span>
          <h2>MARKET PROJECTION</h2>
        </div>
        {market?<>
          <div className="market-projection-main">
            <small>SPREAD-IMPLIED MARGIN</small>
            <strong>{marketLeader} by {marketMargin?.toFixed(1)}</strong>
            <span>{formatMichiganSpread(market.teamSpread)} · {market.sportsbook}</span>
          </div>
          <div className="market-projection-meta">
            <div><small>MARKET WIN CHANCE</small><strong>{Math.round(market.marketWinChance*100)}%</strong></div>
            <div><small>AS OF</small><strong>{market.asOf}</strong></div>
          </div>
          <p className="market-note">An exact market-implied final score requires both a spread and a game total. The current published feed has the spread, so this page shows the market-implied margin without inventing a total.</p>
        </>:<div className="market-empty"><strong>MARKET LINE NOT YET PUBLISHED</strong><p>This section will populate when a sourced line is available for the matchup.</p></div>}
      </section>

      <Link className="game-preview-article-cta" href="/articles">
        <span>FULL STORY</span>
        <strong>READ THE GAME PREVIEW ARTICLE</strong>
        <b>→</b>
      </Link>
    </div>
  </main>;
}
