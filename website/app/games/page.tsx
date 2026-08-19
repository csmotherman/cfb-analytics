import { ScheduleRow } from "../../components/games/GameCard";
import { currentSchedule } from "../../lib/michigan/games";
export default function GamesPage(){const games=currentSchedule();return <div className="page-stack page-pad"><section className="page-hero schedule-hero"><span className="eyebrow">MICHIGAN FOOTBALL</span><h1>2026 SCHEDULE.</h1><p>{games.length} games. Home, road and Big Ten play.</p></section><div className="schedule-list">{games.map(game=><ScheduleRow game={game} key={game.id}/>)}</div></div>}
