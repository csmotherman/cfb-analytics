import type { Metadata } from "next";
import Link from "next/link";
import { historySeasons } from "../../lib/michigan/history";

export const metadata: Metadata = {title:"Michigan Football History",description:"Explore Michigan football seasons, records, coaches, and team performance from 2010 through 2025."};

export default function History(){
  const seasons=historySeasons();
  const available=seasons.filter(season=>season.available);
  const ranked=[...available].sort((a,b)=>b.wins-a.wins||a.losses-b.losses||b.season-a.season);
  const lead=ranked[0];
  const standouts=ranked.slice(1,5);
  const totalWins=available.reduce((total,season)=>total+season.wins,0);
  const winningSeasons=available.filter(season=>season.wins>season.losses).length;
  const eras=new Set(seasons.map(season=>season.coach)).size;
  return <div className="history-vault">
    <section className="vault-hero"><div className="vault-grid" aria-hidden="true"/><div className="wrap vault-hero-inner"><div className="vault-intro"><span className="kicker maize">MICHIGAN · 2010–2025</span><h1>THE<br/><b>VAULT</b></h1><p>Sixteen seasons of Michigan football—organized for fans who want the record, the context, and the story behind each team.</p><a href="#season-index" className="vault-jump">BROWSE EVERY SEASON <span>↓</span></a></div>{lead&&<Link href={`/history/${lead.season}`} className="vault-feature"><div className="vault-feature-top"><span>START HERE</span><small>TOP RECORD IN THIS ARCHIVE</small></div><strong>{lead.season}</strong><div className="vault-feature-record"><b>{lead.wins}–{lead.losses}</b><span>{lead.coach}<small>HEAD COACH</small></span></div><div className="vault-feature-action">OPEN SEASON FILE <span>→</span></div></Link>}</div><div className="wrap vault-stats" aria-label="Archive summary"><span><small>ARCHIVE</small><b>{seasons.length} seasons</b></span><span><small>RECORDED WINS</small><b>{totalWins}</b></span><span><small>WINNING SEASONS</small><b>{winningSeasons}</b></span><span><small>HEAD COACHES</small><b>{eras}</b></span></div></section>
    <div className="wrap vault-content"><section className="vault-standouts"><header className="vault-section-head"><div><span className="kicker navy">THE HIGH-WATER MARKS</span><h2>Seasons worth opening first.</h2></div><p>Ranked by wins, then fewest losses. Every file opens into the full season record and available team evidence.</p></header><div className="standout-list">{standouts.map((season,index)=><Link href={`/history/${season.season}`} key={season.season}><span className="standout-rank">0{index+2}</span><strong>{season.season}</strong><div><b>{season.wins}–{season.losses}</b><small>{season.coach}</small></div><em>EXPLORE <span>→</span></em></Link>)}</div></section>
    <section className="vault-index" id="season-index"><header className="vault-section-head"><div><span className="kicker navy">SEASON INDEX</span><h2>Choose your year.</h2></div><p>Move chronologically through the modern Michigan archive.</p></header><div className="vault-timeline">{seasons.map(season=><Link href={`/history/${season.season}`} key={season.season} className={season.available?"available":"unavailable"}><span className="timeline-node" aria-hidden="true"/><div className="timeline-year"><strong>{season.season}</strong><small>{season.available?"SEASON FILE":"LIMITED DATA"}</small></div><div className="timeline-record"><b>{season.available?`${season.wins}–${season.losses}`:"—"}</b><span>{season.coach}</span></div><em aria-hidden="true">→</em></Link>)}</div></section></div>
  </div>;
}
