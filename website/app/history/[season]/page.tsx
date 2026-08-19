import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SeasonSelector } from "../../../components/ui/SeasonSelector";
import { TeamLogo } from "../../../components/ui/TeamLogo";
import { coachingForSeason } from "../../../lib/michigan/coaching";
import { historicalCfpOutlook, historicalGames, historicalGrades, historicalRoster, historicalSeasonStats } from "../../../lib/michigan/history";

type Props = { params: Promise<{ season: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const season = Number((await params).season);
  return { title: `${season} Michigan Football`, description: `${season} Michigan record, grades, postseason and roster.` };
}

export default async function SeasonPage({ params }: Props) {
  const season = Number((await params).season);
  if (!Number.isInteger(season) || season < 2010 || season > 2025) notFound();
  const games = historicalGames(season);
  const roster = historicalRoster(season);
  const totals = historicalSeasonStats(season);
  const grades = historicalGrades(season);
  const cfpOutlook = historicalCfpOutlook(season);
  const coach = coachingForSeason(season);
  const results = games.map((game) => {
    const home = game.homeTeam === "Michigan";
    const pointsFor = home ? game.homePoints : game.awayPoints;
    const pointsAgainst = home ? game.awayPoints : game.homePoints;
    return { ...game, opponent: home ? game.awayTeam : game.homeTeam, opponentId: home ? game.awayId : game.homeId, away: !home, pointsFor, pointsAgainst, win: Number(pointsFor) > Number(pointsAgainst) };
  });
  const wins = results.filter((game) => game.win).length;
  const losses = results.length - wins;
  const playoffGames = results.filter((game) => game.playoff?.competition === "cfp");
  const playoffWins = playoffGames.filter((game) => game.win).length;
  const bigTenTitle = results.some((game) => (/big ten championship/i.test(game.notes ?? "") || (game.week === 14 && game.neutralSite && game.conferenceGame)) && game.win);
  const nationalChampion = playoffGames.some((game) => game.playoff?.round === "championship" && game.win);
  const gamesPlayed = Number(totals.games) || results.length || 1;
  const basicStats = [
    ["Points per game", results.length ? (results.reduce((sum, game) => sum + Number(game.pointsFor ?? 0), 0) / results.length).toFixed(1) : "—"],
    ["Points allowed", results.length ? (results.reduce((sum, game) => sum + Number(game.pointsAgainst ?? 0), 0) / results.length).toFixed(1) : "—"],
    ["Yards per game", totals.totalYards != null ? (totals.totalYards / gamesPlayed).toFixed(1) : "—"],
    ["Yards allowed", totals.totalYardsOpponent != null ? (totals.totalYardsOpponent / gamesPlayed).toFixed(1) : "—"],
    ["Rush yards per game", totals.rushingYards != null ? (totals.rushingYards / gamesPlayed).toFixed(1) : "—"],
    ["Pass yards per game", totals.netPassingYards != null ? (totals.netPassingYards / gamesPlayed).toFixed(1) : "—"],
    ["Turnovers", totals.turnovers?.toLocaleString() ?? "—"],
    ["Takeaways", totals.turnoversOpponent?.toLocaleString() ?? "—"],
  ];

  return <div className="page-stack page-pad history-season-page">
    <SeasonSelector selected={season}/>
    <section className="history-scoreboard">
      <div className="history-scoreboard-title"><span className="eyebrow">MICHIGAN FOOTBALL · SEASON FILE</span><h1>{season}</h1><p>{coach?.head_coach ?? "Head coach unavailable"}</p></div>
      <div className="history-record"><span>FINAL RECORD</span><strong>{wins}–{losses}</strong></div>
      <div className="history-grade-strip"><div><span>OVERALL</span><strong>{grades?.overall ?? "—"}</strong></div><div><span>OFFENSE</span><strong>{grades?.offense ?? "—"}</strong></div><div><span>DEFENSE</span><strong>{grades?.defense ?? "—"}</strong></div></div>
      <div className="season-achievements" aria-label="Season achievements"><span className={bigTenTitle ? "earned" : ""}>BIG TEN · {bigTenTitle ? "CHAMPIONS" : "NO TITLE"}</span><span className={playoffGames.length ? "earned" : ""}>CFP · {playoffGames.length ? `${playoffWins}–${playoffGames.length - playoffWins}` : "DID NOT MAKE"}</span><span className={nationalChampion ? "earned" : ""}>NATIONAL TITLE · {nationalChampion ? "CHAMPIONS" : "NO"}</span></div>
    </section>

    {bigTenTitle && <section className="championship-banner big-ten-banner" aria-label={`${season} Big Ten champions`}><span>CONFERENCE CHAMPIONS</span><strong>BIG TEN<br/>CHAMPIONS</strong><b>{season}</b></section>}

    {nationalChampion && <section className="championship-banner national-title-banner" aria-label={`${season} national champions`}><span>THE TEAM · THE TEAM · THE TEAM</span><strong>NATIONAL<br/>CHAMPIONS</strong><b>{season}</b><p>Michigan finished the job.</p></section>}

    <div className="history-season-layout">
      <main className="history-season-main">
        {cfpOutlook && <section className="cfp-resume-summary" aria-label={`${season} final CFP resume`}><header><span>CFP RÉSUMÉ</span><strong>{(cfpOutlook.selectionChance * 100).toFixed(1)}%</strong><small>FINAL RÉSUMÉ CHANCE</small></header><div><span>RÉSUMÉ RANK</span><strong>#{cfpOutlook.selectionRank}</strong><small>{cfpOutlook.fieldSize}-TEAM FIELD</small></div><div><span>SCHEDULE</span><strong>{(cfpOutlook.strengthOfSchedule * 100).toFixed(1)}%</strong><small>OPPONENT WIN RATE</small></div><div><span>QUALITY WINS</span><strong>{cfpOutlook.qualityWins}</strong><small>VS. .700+ TEAMS</small></div><p>Final résumé comparison using record, schedule, quality wins, scoring margin and conference title.</p></section>}

        {playoffGames.length > 0 && <section className="history-playoff-section"><span className="eyebrow">PLAYOFF RUN</span><div className="season-results playoff-results">{playoffGames.map((game) => <Link href={`/history/${season}/games/${game.id}`} className={`history-game-row playoff-game ${game.win ? "playoff-win" : "playoff-loss"} ${game.playoff?.round === "championship" ? "title-game" : ""}`} key={game.id}><b className={game.win ? "win" : "loss"}>{game.win ? "W" : "L"}</b><TeamLogo teamId={game.opponentId} name={game.opponent} size={64}/><span>{game.playoff?.roundName?.toUpperCase()}</span><strong>vs {game.opponent}</strong><em>{game.pointsFor ?? "—"}–{game.pointsAgainst ?? "—"}</em></Link>)}</div></section>}

        <details className="history-disclosure"><summary><span>FULL SCHEDULE</span><b>{results.length} GAMES · {wins}–{losses}</b></summary><div className="season-results">{results.map((game) => <Link href={`/history/${season}/games/${game.id}`} className={`history-game-row ${game.playoff?.competition === "cfp" ? "all-games-playoff" : ""}`} key={game.id}><b className={game.win ? "win" : "loss"}>{game.win ? "W" : "L"}</b><TeamLogo teamId={game.opponentId} name={game.opponent} size={64}/><span>{game.playoff?.competition === "cfp" ? "CFP" : `WEEK ${game.week}`}</span><strong>{game.away ? "at " : "vs "}{game.opponent}</strong><em>{game.pointsFor ?? "—"}–{game.pointsAgainst ?? "—"}</em></Link>)}</div></details>
      </main>

      <aside className="history-season-rail">
        <section className="history-stat-panel"><header><span>SEASON STATS</span><small>PER GAME</small></header><div>{basicStats.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div></section>
        {roster.length > 0 && <Link className="history-roster-link" href={`/history/${season}/roster`}><span>FULL ROSTER</span><strong>{roster.length}</strong><b>VIEW WOLVERINES →</b></Link>}
      </aside>
    </div>
  </div>;
}
