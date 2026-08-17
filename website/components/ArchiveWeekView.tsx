"use client";

import { useMemo, useState } from "react";

import type { ArchiveGame, ArchiveWeek } from "../lib/archive";

type ArchiveFilter = "all" | "correct" | "wrong" | "no-call";

function resultFor(game: ArchiveGame): boolean | null {
  if (!game.predictedWinner) return null;
  if (typeof game.winnerCorrect === "boolean") return game.winnerCorrect;
  if (typeof game.actualHomeScore !== "number" || typeof game.actualAwayScore !== "number") return null;
  if (game.actualHomeScore === game.actualAwayScore) return null;
  const winner = game.actualHomeScore > game.actualAwayScore ? game.homeTeam : game.awayTeam;
  return game.predictedWinner === winner;
}

function actualWinner(game: ArchiveGame): string | null {
  if (typeof game.actualHomeScore !== "number" || typeof game.actualAwayScore !== "number") return null;
  if (game.actualHomeScore === game.actualAwayScore) return null;
  return game.actualHomeScore > game.actualAwayScore ? game.homeTeam : game.awayTeam;
}

function formatPercent(value: number | null): string {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}

function ResultBadge({ game }: { game: ArchiveGame }) {
  const result = resultFor(game);
  if (!game.predictedWinner) return <span className="fan-archive-result fan-archive-result-neutral">No model call</span>;
  if (result == null) return <span className="fan-archive-result fan-archive-result-neutral">Not graded</span>;
  return result
    ? <span className="fan-archive-result fan-archive-result-win">Correct ✓</span>
    : <span className="fan-archive-result fan-archive-result-loss">Wrong ×</span>;
}

function WeekGameCard({ game }: { game: ArchiveGame }) {
  const winner = actualWinner(game);
  const modelRank = game.predictedWinner === game.homeTeam ? game.homeRank : game.awayRank;
  return (
    <article className="fan-history-game-card">
      <header>
        <div>
          {game.beatTheModelSelected ? <span className="fan-history-official">Official 15</span> : null}
          <span>{game.seasonType === "postseason" ? "Postseason" : "Regular season"}</span>
        </div>
        <ResultBadge game={game} />
      </header>

      <div className="fan-history-scoreboard">
        <div className={winner === game.awayTeam ? "winner" : ""}>
          <span>{typeof game.awayRank === "number" ? `#${game.awayRank}` : "Away"}</span>
          <strong>{game.awayTeam}</strong>
          <em>{typeof game.actualAwayScore === "number" ? game.actualAwayScore : "—"}</em>
        </div>
        <div className={winner === game.homeTeam ? "winner" : ""}>
          <span>{typeof game.homeRank === "number" ? `#${game.homeRank}` : "Home"}</span>
          <strong>{game.homeTeam}</strong>
          <em>{typeof game.actualHomeScore === "number" ? game.actualHomeScore : "—"}</em>
        </div>
      </div>

      <footer>
        <span>The Model</span>
        {game.predictedWinner ? (
          <strong>{typeof modelRank === "number" ? `#${modelRank} ` : ""}{game.predictedWinner}</strong>
        ) : (
          <strong className="fan-history-no-call">No supported prediction</strong>
        )}
      </footer>
    </article>
  );
}

export function ArchiveWeekView({ data }: { data: ArchiveWeek }) {
  const [filter, setFilter] = useState<ArchiveFilter>("all");

  const stats = useMemo(() => {
    let calls = 0;
    let wins = 0;
    let losses = 0;
    for (const game of data.games) {
      const result = resultFor(game);
      if (result == null) continue;
      calls += 1;
      if (result) wins += 1;
      else losses += 1;
    }
    return {
      games: data.games.length,
      calls,
      wins,
      losses,
      noCalls: data.games.filter((game) => !game.predictedWinner).length,
      accuracy: calls ? wins / calls : null,
    };
  }, [data.games]);

  const visibleGames = useMemo(() => data.games.filter((game) => {
    const result = resultFor(game);
    if (filter === "correct") return result === true;
    if (filter === "wrong") return result === false;
    if (filter === "no-call") return !game.predictedWinner;
    return true;
  }), [data.games, filter]);

  if (!data.games.length) {
    return (
      <section className="fan-empty-state archive-btm-missing">
        <span className="fan-status fan-status-steel">No archived games</span>
        <h2>This week is not available in the published archive.</h2>
        <p>Archive pages only show records that exist in the frozen historical dataset.</p>
      </section>
    );
  }

  return (
    <section className="fan-history-week" aria-labelledby="history-week-heading">
      <div className="fan-history-week-head">
        <div>
          <span className="fan-kicker">WEEKLY RECEIPTS</span>
          <h2 id="history-week-heading">{data.season} Week {data.week}</h2>
          <p>Every archived game from this week. Supported model calls are shown beside the final score and graded exactly as they finished.</p>
        </div>
        <div className="fan-history-week-record">
          <span>Model record</span>
          <strong>{stats.calls ? `${stats.wins}-${stats.losses}` : "No calls"}</strong>
          <small>{formatPercent(stats.accuracy)} accuracy</small>
        </div>
      </div>

      <div className="fan-history-stats" aria-label="Week archive summary">
        <div><span>Games archived</span><strong>{stats.games}</strong></div>
        <div><span>Model calls</span><strong>{stats.calls}</strong></div>
        <div><span>Correct</span><strong>{stats.wins}</strong></div>
        <div><span>Wrong</span><strong>{stats.losses}</strong></div>
      </div>

      <div className="fan-history-filters" role="tablist" aria-label="Filter archived games">
        <button type="button" className={filter === "all" ? "active" : ""} onClick={() => setFilter("all")}>All <span>{stats.games}</span></button>
        <button type="button" className={filter === "correct" ? "active" : ""} onClick={() => setFilter("correct")}>Correct <span>{stats.wins}</span></button>
        <button type="button" className={filter === "wrong" ? "active" : ""} onClick={() => setFilter("wrong")}>Wrong <span>{stats.losses}</span></button>
        {stats.noCalls ? <button type="button" className={filter === "no-call" ? "active" : ""} onClick={() => setFilter("no-call")}>No call <span>{stats.noCalls}</span></button> : null}
      </div>

      {visibleGames.length ? (
        <div className="fan-history-game-grid">
          {visibleGames.map((game) => <WeekGameCard key={game.id} game={game} />)}
        </div>
      ) : (
        <div className="fan-empty-state"><h3>No games match this filter.</h3><p>Choose another result filter to continue browsing the week.</p></div>
      )}

      {stats.noCalls ? (
        <p className="fan-history-footnote">“No model call” means the historical game exists, but the published archive does not contain a supported pregame Prediction-v2 call for that game. Those games are not counted in accuracy.</p>
      ) : null}
    </section>
  );
}
