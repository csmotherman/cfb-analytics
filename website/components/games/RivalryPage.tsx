import Link from "next/link";
import { TeamLogo } from "../ui/TeamLogo";
import { historicalGames } from "../../lib/michigan/history";

type Props = {
  opponent: string;
  opponentId: number;
  eyebrow: string;
  headline: string;
};

export function RivalryPage({ opponent, opponentId, eyebrow, headline }: Props) {
  const games = Array.from({ length: 16 }, (_, index) => 2010 + index)
    .flatMap(historicalGames)
    .filter((game) => game.homeId === opponentId || game.awayId === opponentId)
    .map((game) => {
      const home = game.homeTeam === "Michigan";
      const pointsFor = Number(home ? game.homePoints : game.awayPoints);
      const pointsAgainst = Number(home ? game.awayPoints : game.homePoints);
      return { ...game, home, pointsFor, pointsAgainst, win: pointsFor > pointsAgainst };
    })
    .sort((a, b) => b.season - a.season || b.week - a.week);
  const wins = games.filter((game) => game.win).length;
  const losses = games.length - wins;

  return (
    <div className="page-stack page-pad">
      <section className="game-hub-hero">
        <span className="eyebrow">{eyebrow} · SINCE 2010</span>
        <div className="game-matchup">
          <div><TeamLogo teamId={130} name="Michigan" size={256} /><strong>MICHIGAN</strong></div>
          <em>VS</em>
          <div><TeamLogo teamId={opponentId} name={opponent} size={256} /><strong>{opponent.toUpperCase()}</strong></div>
        </div>
        <h1>{headline}</h1>
      </section>
      <section className="rivalry-record"><header><div><span className="eyebrow">MODERN ARCHIVE · ACTUAL</span><h2>Michigan is {wins}–{losses} since 2010.</h2></div><small>{games.length} VERIFIED MEETINGS</small></header><div>{games.map((game) => <Link href={`/history/${game.season}/games/${game.id}`} key={game.id}><b className={game.win ? "win" : "loss"}>{game.win ? "W" : "L"}</b><strong>{game.season}</strong><span>{game.home ? "ANN ARBOR" : "ROAD / NEUTRAL"}</span><em>{game.pointsFor}–{game.pointsAgainst}</em><small>BOX SCORE →</small></Link>)}</div><p>Scope is the available SOAR modern archive beginning in 2010; this is not the all-time series record.</p></section>
    </div>
  );
}
