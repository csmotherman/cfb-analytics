import Link from "next/link";
import { GameCard } from "../components/games/GameCard";
import { currentRoster } from "../lib/michigan/roster";
import { nextGame } from "../lib/michigan/games";
import { currentRecruitingClass, nationalRecruits } from "../lib/michigan/recruiting";
import { projectedLineups } from "../lib/michigan/depth-chart";

export default function Home(){const roster=currentRoster();const game=nextGame();const recruiting=currentRecruitingClass();const lineup=projectedLineups();const lineupCount=lineup?lineup.offense.length+lineup.defense.length:null;const nationalRecruitCount=nationalRecruits().length;const graded=roster.filter(p=>p.prospectGrade).sort((a,b)=>(b.compositeRating??0)-(a.compositeRating??0)).slice(0,4);return <div className="command-screen">
  <header className="command-top"><div><span className="eyebrow">2026 MICHIGAN FOOTBALL · PRESEASON</span><h1>THIS IS MICHIGAN.</h1><p>Roster. Recruiting. Schedule. Analytics. One home field.</p></div><img src="/images/winged-helmet-3d.png" alt="Michigan winged football helmet"/></header>
  <section className="command-grid">
    <article className="command-next"><span className="eyebrow">NEXT GAME</span>{game?<GameCard game={game}/>:<strong>Schedule pending</strong>}</article>
    <article className="command-roster"><header><span className="eyebrow">PLAYERS TO KNOW</span><Link href="/team/roster">ALL {roster.length} →</Link></header>{graded.map(p=><Link href={`/players/${p.id}`} key={p.id}><b>#{p.jersey??"—"}</b><span>{p.firstName} {p.lastName}<small>{p.position} · {p.stars?`${p.stars}★`:"NR"}</small></span><strong>{p.prospectGrade}</strong></Link>)}</article>
    <article className="command-recruits"><header><span className="eyebrow">RECRUITING · #{recruiting?.ranking?.rank??"—"}</span><Link href="/recruiting">CLASS HQ →</Link></header>{recruiting?.recruits.slice(0,4).map(r=><Link href={`/recruiting/players/${r.id}`} key={r.id}><b>#{r.ranking??"—"}</b><span>{r.name}<small>{r.position} · {"★".repeat(r.stars??0)}</small></span><strong>{r.grade}</strong></Link>)}</article>
    <nav className="command-actions" aria-label="Michigan destinations"><Link href="/team/depth-chart"><b>{lineupCount??"—"}</b><span>STARTING LINEUP</span></Link><Link href="/analytics"><b>↗</b><span>ANALYTICS</span></Link><Link href="/stories/2026-coaching-staff"><b>KW</b><span>NEW COACHING STAFF</span></Link><Link href="/recruiting/national"><b>{nationalRecruitCount||"—"}</b><span>NATIONAL RECRUITS</span></Link><Link href="/stories"><b>〽</b><span>STORIES</span></Link><Link href="/history"><b>2010</b><span>THE VAULT</span></Link></nav>
  </section>
</div>}
