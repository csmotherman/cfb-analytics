import type { Metadata } from "next";
import Link from "next/link";
import { CURRENT_MICHIGAN_SEASON, LAST_COMPLETED_SEASON, michiganGames } from "../../lib/michigan";

export const metadata: Metadata = { title: "Michigan Schedule", description: "Michigan's complete season game log with canonical scores and opponents." };

export default function SchedulePage() {
  const season = CURRENT_MICHIGAN_SEASON;
  const games = michiganGames(season);
  return <div className="michigan-home">
    <section className="michigan-page-hero"><span>{season} · PRESEASON</span><h1>The 2026 Michigan schedule.</h1><p>Opponent identity, dates, and locations will appear from validated schedule facts. Scores and game-level SOAR evidence remain absent until games are actually played.</p></section>
    <section className="michigan-schedule">
      {games.map((game) => <article key={game.game_id}>
        <div><span>WEEK {game.week}</span><b className={game.win === 1 ? "win" : "loss"}>{game.win === 1 ? "WIN" : game.loss === 1 ? "LOSS" : "—"}</b></div>
        <h2>{game.home_away === "away" ? "at " : "vs "}{game.opponent}</h2><p>{game.opponent_conference || game.opponent_classification || "Nonconference"}{game.neutral_site ? " · Neutral site" : ""}</p>
        <strong>{game.points_for ?? "—"}<small>–</small>{game.points_against ?? "—"}</strong>
        <footer><span>Off. success {game.successRate != null ? `${(game.successRate * 100).toFixed(1)}%` : "—"}</span><span>Def. allowed {game.successRateAllowed != null ? `${(game.successRateAllowed * 100).toFixed(1)}%` : "—"}</span></footer>
      </article>)}
    </section>
    {games.length === 0 && <section className="michigan-empty"><span>{season} PRESEASON SCHEDULE</span><h1>The schedule contract has not been published yet.</h1><p>No opponents or dates are invented here. Once the 2026 CFBD schedule is acquired and validated, this page can display it without exposing performance cards.</p><Link href={`/football/${LAST_COMPLETED_SEASON}`}>Review Michigan’s 2025 results →</Link></section>}
  </div>;
}
