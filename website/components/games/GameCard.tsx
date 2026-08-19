import Link from "next/link";
import type { MichiganScheduleGame } from "../../lib/michigan/types";
import { opponent } from "../../lib/michigan/games";
import { TeamLogo } from "../ui/TeamLogo";
export function GameCard({ game, featured = false }: { game: MichiganScheduleGame; featured?: boolean }) {
  const opp = opponent(game); const date = new Date(game.startDate);
  return <Link className={`game-card ${featured ? "featured" : ""}`} href={`/games/${game.id}`}><header><span>WEEK {game.week}</span><b>{game.completed ? "FINAL · ACTUAL" : "UPCOMING · PRESEASON"}</b></header><div className="game-matchup"><div><TeamLogo teamId={130} name="Michigan" size={featured ? 256 : 128} /><strong>MICHIGAN</strong></div><em>VS</em><div><TeamLogo teamId={opp.id} name={opp.name} size={featured ? 256 : 128} /><strong>{opp.name}</strong></div></div><footer><div><b>{date.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "America/Detroit" })}</b><span>{game.startTimeTBD ? "Kickoff TBD" : date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", timeZone: "America/Detroit" })} ET · {game.venue ?? "Venue TBD"} · TV TBD</span></div><strong>{game.completed ? `${game.homePoints}–${game.awayPoints}` : "GAME HUB →"}</strong></footer></Link>;
}

export function ScheduleRow({ game }: { game: MichiganScheduleGame }) {
  const opp = opponent(game);
  const date = new Date(game.startDate);
  const home = game.homeId === 130;
  const kickoff = game.startTimeTBD ? "TBD" : date.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", timeZone: "America/Detroit" });
  return <Link className="schedule-row" href={`/games/${game.id}`}>
    <div className="schedule-week"><span>WEEK</span><strong>{game.week}</strong></div>
    <TeamLogo teamId={opp.id} name={opp.name} size={64}/>
    <div className="schedule-opponent"><span>{home ? "VS" : "AT"}</span><strong>{opp.name}</strong><small>{game.conferenceGame ? "BIG TEN" : "NON-CONFERENCE"}</small></div>
    <div className="schedule-date"><strong>{date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", timeZone: "America/Detroit" })}</strong><span>{game.venue ?? (home ? "Michigan Stadium" : "Venue TBD")}</span></div>
    <div className="schedule-kick"><strong>{game.completed ? `${game.homePoints}–${game.awayPoints}` : kickoff}</strong><span>{game.completed ? "FINAL" : "ET"}</span></div>
    <b className="schedule-open" aria-hidden="true">→</b>
  </Link>;
}
