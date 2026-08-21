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

function TeamMetric({side,align}:{side:MatchupRidgeSide|undefined;align:"left"|"right"}){
  return <div className={`advantage-team-value ${align==="right"?"opponent-value":"michigan-value"}`}>
    <div className="metric-primary"><strong>{rank(side?.rank)}</strong><small>NATIONAL</small></div>
    <div className="metric-secondary"><b>{rating(side?.rating)}</b><small>RATING</small></div>
  </div>;
}

function ComparisonRow({label,michigan,opponent,opponentName}:ComparisonRowProps){
  const hasRatings=michigan?.rating!=null&&opponent?.rating!=null;
  const difference=hasRatings?michigan.rating-opponent.rating:0;
  const absDifference=Math.abs(difference);
  const michiganLeads=difference>=0;
  const leader=hasRatings?(michiganLeads?"MICHIGAN":opponentName.toUpperCase()):"—";
  const width=Math.min(absDifference/30,1)*50;
  const meterStyle={"--advantage-width":`${width}%`} as CSSProperties;

  return <div className="advantage-row">
    <TeamMetric side={michigan} align="left"/>

    <div className="advantage-center">
      <span className="advantage-label">{label}</span>
      <div className="edge-readout">
        <strong className={michiganLeads?"michigan-leads":"opponent-leads"}>{hasRatings?`+${absDifference.toFixed(1)}`:"—"}</strong>
        <small className={michiganLeads?"michigan-leads":"opponent-leads"}>{hasRatings?`${leader} EDGE`:"NO DATA"}</small>
      </div>
      <div className={`advantage-meter ${michiganLeads?"to-michigan":"to-opponent"}`} style={meterStyle} aria-label={`${leader} advantage ${absDifference.toFixed(1)} rating points`}>
        <span/>
        <i/>
        <span/>
      </div>
      <div className="advantage-scale"><span>MICH</span><b>EVEN</b><span>{opponentName.toUpperCase()}</span></div>
    </div>

    <TeamMetric side={opponent} align="right"/>
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
        <Link href="/schedule">← SCHEDULE</Link>
        <div><span>WEEK {game.week}</span><h1>GAME PREVIEW</h1></div>
        <span>2026</span>
      </header>

      <section className="preview-matchup-card">
        <div className="preview-matchup-kicker">MICHIGAN FOOTBALL · WEEK {game.week}</div>
        <div className="preview-matchup">
          <div className="preview-team michigan-team">
            <img src={teamLogoUrl(130,256)} alt="Michigan logo"/>
            <strong>MICHIGAN</strong>
            <small>{michiganConference}</small>
          </div>
          <div className="preview-versus"><span>VS</span><i/></div>
          <div className="preview-team opponent-team">
            <img src={teamLogoUrl(opp.id,256)} alt={`${opp.name} logo`}/>
            <strong>{opp.name.toUpperCase()}</strong>
            <small>{opponentConference}</small>
          </div>
        </div>
        <div className="preview-meta">
          <span><small>DATE</small><b>{gameDate(game)}</b></span>
          <span><small>KICKOFF</small><b>{gameTime(game)} ET</b></span>
          <span><small>LOCATION</small><b>{game.venue??(home?"Michigan Stadium":"Away")}</b></span>
        </div>
      </section>

      <section className="preview-block advantage-comparison-block">
        <div className="preview-section-heading advantage-heading">
          <div>
            <span>{baselineSeason} OPPONENT-ADJUSTED RIDGE</span>
            <h2>HOW THEY STACK UP</h2>
          </div>
          <p>Higher rating is better.<br/><b>100 = FBS average</b></p>
        </div>

        <div className="advantage-comparison">
          <div className="advantage-comparison-head">
            <div>
              <img src={teamLogoUrl(130,64)} alt="Michigan logo"/>
              <strong>MICHIGAN</strong>
            </div>
            <span>EDGE<small>RATING-POINT DIFFERENCE</small></span>
            <div>
              <img src={teamLogoUrl(opp.id,64)} alt={`${opp.name} logo`}/>
              <strong>{opp.name.toUpperCase()}</strong>
            </div>
          </div>

          <ComparisonRow label="OVERALL" michigan={michigan?.overall} opponent={opponentRatings?.overall} opponentName={opp.name}/>
          <ComparisonRow label="OFFENSE" michigan={michigan?.offense} opponent={opponentRatings?.offense} opponentName={opp.name}/>
          <ComparisonRow label="DEFENSE" michigan={michigan?.defense} opponent={opponentRatings?.defense} opponentName={opp.name}/>
        </div>

        <p className="preview-footnote">National ranks and ratings use the same opponent-adjusted Ridge system as the Analytics page. The center indicator shows which team owns the rating advantage in each category.</p>
      </section>

      <section className="market-preview-card compact-market-card">
        <div className="market-title"><span>MARKET</span><strong>GAME LINE</strong></div>
        <div>
          <small>SPREAD</small>
          {market?<><strong>{formatMichiganSpread(market.teamSpread)}</strong><span>{market.sportsbook}</span></>:<strong>NOT YET PUBLISHED</strong>}
        </div>
        <div>
          <small>IMPLIED EDGE</small>
          <strong>{market&&marketMargin!=null?`${marketLeader} ${marketMargin.toFixed(1)}`:"—"}</strong>
          <span>{market?.asOf??"Waiting for market"}</span>
        </div>
      </section>

      <Link className="game-preview-article-cta" href="/articles">
        <span>DEEP DIVE</span>
        <strong>READ THE FULL GAME PREVIEW</strong>
        <small>Matchups, personnel and what matters most.</small>
        <b>→</b>
      </Link>
    </div>
  </main>;
}
