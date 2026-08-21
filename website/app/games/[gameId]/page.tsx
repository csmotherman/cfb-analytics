import type {CSSProperties} from "react";
import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {gameById,opponent} from "../../../lib/michigan/games";
import {gamePreview,type MatchupRidgeSide} from "../../../lib/michigan/game-preview";
import {marketLineFor,formatMichiganSpread} from "../../../lib/market-lines";
import {teamLogoUrl} from "../../../lib/team-assets";
import {gameDate,gameTime} from "../../../lib/home-data";
import "./game-preview.css";

type Props={params:Promise<{gameId:string}>};
const rank=(value:number|undefined|null)=>value==null?"—":`#${value}`;
const rating=(value:number|undefined|null)=>value==null?"—":value.toFixed(1);

type ComparisonRowProps={
  label:string;
  michigan:MatchupRidgeSide|undefined;
  opponent:MatchupRidgeSide|undefined;
  opponentName:string;
};

function ComparisonRow({label,michigan,opponent,opponentName}:ComparisonRowProps){
  const hasRatings=michigan?.rating!=null&&opponent?.rating!=null;
  const difference=hasRatings?michigan.rating-opponent.rating:0;
  const absDifference=Math.abs(difference);
  const michiganLeads=difference>=0;
  const leader=hasRatings?(michiganLeads?"MICHIGAN":opponentName.toUpperCase()):"—";
  const width=Math.min(absDifference/30,1)*50;
  const meterStyle={"--advantage-width":`${width}%`} as CSSProperties;

  return <div className="advantage-row">
    <div className="advantage-team-value michigan-value">
      <strong>{rank(michigan?.rank)}</strong>
      <b>{rating(michigan?.rating)}</b>
      <small>NATIONAL RANK · RATING</small>
    </div>

    <div className="advantage-center">
      <span className="advantage-label">{label}</span>
      <strong className={`advantage-number ${michiganLeads?"michigan-leads":"opponent-leads"}`}>
        {hasRatings?`+${absDifference.toFixed(1)}`:"—"}
      </strong>
      <small className={`advantage-winner ${michiganLeads?"michigan-leads":"opponent-leads"}`}>{leader} ADVANTAGE</small>
      <div className={`advantage-meter ${michiganLeads?"to-michigan":"to-opponent"}`} style={meterStyle} aria-label={`${leader} advantage ${absDifference.toFixed(1)} rating points`}>
        <span className="advantage-track-left"/>
        <i/>
        <span className="advantage-track-right"/>
      </div>
      <div className="advantage-scale"><span>OPPONENT</span><b>0</b><span>MICHIGAN</span></div>
    </div>

    <div className="advantage-team-value opponent-value">
      <strong>{rank(opponent?.rank)}</strong>
      <b>{rating(opponent?.rating)}</b>
      <small>NATIONAL RANK · RATING</small>
    </div>
  </div>;
}

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

      <section className="preview-block advantage-comparison-block">
        <div className="preview-section-heading advantage-heading">
          <div>
            <span>{baselineSeason} OPPONENT-ADJUSTED BASELINE</span>
            <h2>TEAM COMPARISON</h2>
          </div>
          <p>Ratings are opponent-adjusted Ridge ratings<br/><b>100 = FBS average</b></p>
        </div>

        <div className="advantage-comparison">
          <div className="advantage-comparison-head">
            <div>
              <img src={teamLogoUrl(130,64)} alt="Michigan logo"/>
              <strong>MICHIGAN</strong>
              <small>{michiganConference}</small>
            </div>
            <span>ADVANTAGE<small>RATING-POINT EDGE</small></span>
            <div>
              <img src={teamLogoUrl(opp.id,64)} alt={`${opp.name} logo`}/>
              <strong>{opp.name.toUpperCase()}</strong>
              <small>{opponentConference}</small>
            </div>
          </div>

          <ComparisonRow label="OVERALL" michigan={michigan?.overall} opponent={opponentRatings?.overall} opponentName={opp.name}/>
          <ComparisonRow label="OFFENSE" michigan={michigan?.offense} opponent={opponentRatings?.offense} opponentName={opp.name}/>
          <ComparisonRow label="DEFENSE" michigan={michigan?.defense} opponent={opponentRatings?.defense} opponentName={opp.name}/>
        </div>

        <p className="preview-footnote">National rank and rating come from the same opponent-adjusted Ridge system used on the Analytics page. Higher rating is better; the centered marker shows the rating-point advantage between the teams.</p>
      </section>

      <section className="market-preview-card compact-market-card">
        <div>
          <small>MARKET PROJECTION</small>
          {market?<><strong>{formatMichiganSpread(market.teamSpread)}</strong><span>{market.sportsbook}</span></>:<strong>NOT YET PUBLISHED</strong>}
        </div>
        <div>
          <small>SPREAD-IMPLIED EDGE</small>
          <strong>{market&&marketMargin!=null?`${marketLeader} by ${marketMargin.toFixed(1)}`:"—"}</strong>
          <span>{market?.asOf??"Waiting for market"}</span>
        </div>
      </section>

      <Link className="game-preview-article-cta" href="/articles">
        <span>FULL STORY</span>
        <strong>FULL GAME PREVIEW &amp; ANALYSIS</strong>
        <b>→</b>
      </Link>
    </div>
  </main>;
}
