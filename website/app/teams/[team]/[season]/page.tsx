import type { Metadata } from "next";
import Link from "next/link";
import { findPublishedTeam, publishedTeamGames, rank } from "../../../../lib/michigan";

export async function generateMetadata({ params }: { params: Promise<{ team: string; season: string }> }): Promise<Metadata> {
  const { team: identifier, season: rawSeason } = await params;
  const row = findPublishedTeam(Number(rawSeason), identifier);
  return { title: row ? `${row.team} ${row.season}` : "Team profile", description: row ? `${row.team}'s national SOAR profile for ${row.season}.` : "Published FBS team profile." };
}

const metrics = [["successRate", "Offensive success"], ["successRateAllowed", "Defensive success allowed"], ["explosivePlayRate", "Explosive-play rate"], ["explosivePlayRateAllowed", "Explosive rate allowed"], ["pointsPerResolvedPossession", "Points per drive"], ["pointsPerResolvedPossessionAllowed", "Points allowed per drive"]] as const;

export default async function TeamProfile({ params }: { params: Promise<{ team: string; season: string }> }) {
  const { team: identifier, season: rawSeason } = await params; const season = Number(rawSeason); const team = findPublishedTeam(season, identifier);
  if (!team) return <section className="michigan-empty"><span>TEAM PROFILE</span><h1>Published data unavailable.</h1></section>;
  const games = publishedTeamGames(season, team.slug); const wins = games.filter((game) => game.win === 1).length; const losses = games.filter((game) => game.loss === 1).length;
  return <div className="michigan-home">
    <section className={`michigan-profile-hero${team.team === "Michigan" ? " is-michigan" : ""}`}><span>{season} · {team.conference}</span><h1>{team.team}</h1><div><strong>{wins}–{losses}</strong><p>{games.length} games in the canonical record</p></div>{team.team !== "Michigan" ? <Link href={`/compare?opponent=${team.slug}`}>Compare with Michigan →</Link> : <Link href="/schedule">View Michigan schedule →</Link>}</section>
    <section className="michigan-profile-metrics">{metrics.map(([key, label]) => { const n = Number(team[key]); return <article key={key}><span>{label}</span><strong>{Number.isFinite(n) ? (key.includes("Rate") ? `${(n * 100).toFixed(1)}%` : n.toFixed(2)) : "—"}</strong><p>#{rank(team, key) ?? "—"} nationally · #{rank(team, key, "conference") ?? "—"} in {team.conference}</p></article>; })}</section>
    <section className="michigan-panel"><div className="michigan-panel-head"><div><span>SEASON LEDGER</span><h2>Results</h2></div><Link href="/teams">All teams →</Link></div><div className="michigan-game-list">{[...games].reverse().map((game) => <div className="michigan-game" key={game.game_id}><b className={game.win === 1 ? "win" : "loss"}>{game.win === 1 ? "W" : "L"}</b><div><strong>{game.home_away === "away" ? "at " : "vs "}{game.opponent}</strong><span>Week {game.week} · {game.opponent_conference}</span></div><em>{game.points_for}<small>–</small>{game.points_against}</em></div>)}</div></section>
  </div>;
}
