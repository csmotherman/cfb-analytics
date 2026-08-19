import type { Metadata } from "next";
import type { CSSProperties } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { TeamLogo } from "../../../../../components/ui/TeamLogo";
import { historicalGame, historicalGames } from "../../../../../lib/michigan/history";

type Props = { params: Promise<{ season: string; gameId: string }> };

const gameDate = (value?: string | null) => value ? new Intl.DateTimeFormat("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric", timeZone: "America/Detroit" }).format(new Date(value)) : "Date unavailable";
const number = (value?: number | null) => value == null || !Number.isFinite(value) ? "—" : value.toLocaleString();

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { season: seasonParam, gameId } = await params;
  const season = Number(seasonParam);
  const game = historicalGame(season, gameId);
  if (!game) return { title: "Historical game not found" };
  return { title: `${game.awayTeam} vs. ${game.homeTeam}, ${season}`, description: `Quarter-by-quarter box score for ${game.awayTeam} vs. ${game.homeTeam} in ${season}.` };
}

export default async function HistoricalGamePage({ params }: Props) {
  const { season: seasonParam, gameId } = await params;
  const season = Number(seasonParam);
  if (!Number.isInteger(season) || season < 2010 || season > 2025) notFound();
  const game = historicalGame(season, gameId);
  if (!game) notFound();

  const games = historicalGames(season);
  const index = games.findIndex((item) => item.id === game.id);
  const previous = index > 0 ? games[index - 1] : null;
  const next = index >= 0 && index < games.length - 1 ? games[index + 1] : null;
  const quarterCount = Math.max(game.awayLineScores?.length ?? 0, game.homeLineScores?.length ?? 0, 4);
  const periods = Array.from({ length: quarterCount }, (_, period) => period < 4 ? String(period + 1) : `OT${period - 3}`);
  const michiganHome = game.homeTeam === "Michigan";
  const michiganPoints = Number(michiganHome ? game.homePoints : game.awayPoints);
  const opponentPoints = Number(michiganHome ? game.awayPoints : game.homePoints);
  const result = michiganPoints > opponentPoints ? "MICHIGAN WIN" : "MICHIGAN LOSS";

  return <div className="historical-box-page">
    <header className="boxscore-hero">
      <div className="boxscore-meta"><span>{game.playoff?.roundName?.toUpperCase() ?? `${game.seasonType.toUpperCase()} · WEEK ${game.week}`}</span><b>{gameDate(game.startDate)}</b><small>{game.venue ?? "Venue unavailable"}{game.neutralSite ? " · NEUTRAL SITE" : ""}</small></div>
      <div className="boxscore-matchup">
        <div><TeamLogo teamId={game.awayId} name={game.awayTeam} size={128}/><span>{game.awayConference ?? ""}</span><h1>{game.awayTeam}</h1><strong>{game.awayPoints ?? "—"}</strong></div>
        <em>FINAL</em>
        <div><TeamLogo teamId={game.homeId} name={game.homeTeam} size={128}/><span>{game.homeConference ?? ""}</span><h1>{game.homeTeam}</h1><strong>{game.homePoints ?? "—"}</strong></div>
      </div>
      <div className={`boxscore-result ${result.endsWith("WIN") ? "win" : "loss"}`}>{result}</div>
    </header>

    <main className="boxscore-content">
      <section className="line-score" aria-labelledby="line-score-title">
        <header><div><span className="kicker navy">BASIC BOX SCORE · ACTUAL</span><h2 id="line-score-title">Scoring by period</h2></div><small>FINAL</small></header>
        <div className="line-score-table" style={{ "--period-count": quarterCount } as CSSProperties}>
          <div className="line-score-row heading"><span>TEAM</span>{periods.map((period) => <b key={period}>{period}</b>)}<strong>F</strong></div>
          <div className="line-score-row"><span><TeamLogo teamId={game.awayId} name={game.awayTeam} size={64}/><b>{game.awayTeam}</b></span>{periods.map((period, i) => <b key={period}>{game.awayLineScores?.[i] ?? "—"}</b>)}<strong>{game.awayPoints ?? "—"}</strong></div>
          <div className="line-score-row"><span><TeamLogo teamId={game.homeId} name={game.homeTeam} size={64}/><b>{game.homeTeam}</b></span>{periods.map((period, i) => <b key={period}>{game.homeLineScores?.[i] ?? "—"}</b>)}<strong>{game.homePoints ?? "—"}</strong></div>
        </div>
      </section>

      <section className="boxscore-facts"><article><span>ATTENDANCE</span><strong>{game.attendance ? number(game.attendance) : "—"}</strong><small>{game.attendance ? "REPORTED" : "NOT REPORTED"}</small></article><article><span>MICHIGAN ELO</span><strong>{number(michiganHome ? game.homePostgameElo : game.awayPostgameElo)}</strong><small>POSTGAME · ACTUAL</small></article><article><span>RATING CHANGE</span><strong>{(() => { const before = michiganHome ? game.homePregameElo : game.awayPregameElo; const after = michiganHome ? game.homePostgameElo : game.awayPostgameElo; return before != null && after != null ? `${after - before >= 0 ? "+" : ""}${after - before}` : "—"; })()}</strong><small>PREGAME TO POSTGAME</small></article><article><span>GAME TYPE</span><strong>{game.conferenceGame ? "BIG TEN" : game.playoff ? "POSTSEASON" : "NON-CON"}</strong><small>{game.neutralSite ? "NEUTRAL" : michiganHome ? "HOME" : "AWAY"}</small></article></section>

      {game.notes && <aside className="boxscore-note"><b>GAME NOTE</b><p>{game.notes}</p></aside>}

      <nav className="boxscore-nav" aria-label="Historical game navigation">
        {previous ? <Link href={`/history/${season}/games/${previous.id}`}>← PREVIOUS GAME</Link> : <span/>}
        <Link href={`/history/${season}`}>{season} SEASON FILE</Link>
        {next ? <Link href={`/history/${season}/games/${next.id}`}>NEXT GAME →</Link> : <span/>}
      </nav>
    </main>
  </div>;
}
