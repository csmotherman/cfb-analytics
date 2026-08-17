"use client";

import { useMemo, useState } from "react";

import type { ArchiveGame, ArchiveWeek, BeatTheModelArchiveSummary } from "../lib/archive";

function formatPercent(value: number | null | undefined): string {
  return typeof value === "number" && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "—";
}

function ResultMark({ value }: { value: boolean | null | undefined }) {
  if (value == null) return <span className="archive-mark archive-mark-neutral" aria-label="Not graded">—</span>;
  return value ? <span className="archive-mark archive-mark-win" aria-label="Correct">✓</span> : <span className="archive-mark archive-mark-loss" aria-label="Incorrect">×</span>;
}

function TeamCell({ game, side }: { game: ArchiveGame; side: "home" | "away" }) {
  const isHome = side === "home";
  const team = isHome ? game.homeTeam : game.awayTeam;
  const rank = isHome ? game.homeRank : game.awayRank;
  const score = isHome ? game.actualHomeScore : game.actualAwayScore;
  const otherScore = isHome ? game.actualAwayScore : game.actualHomeScore;
  const isWinner = typeof score === "number" && typeof otherScore === "number" && score > otherScore;

  return (
    <div className={`archive-team-score-cell ${isHome ? "archive-home-score-cell" : "archive-away-score-cell"}${isWinner ? " archive-team-winner" : ""}`}>
      {isHome && typeof score === "number" ? <span className="archive-final-score-number">{score}</span> : null}
      <span className="btm-archive-team-label">
        {typeof rank === "number" ? <span className="btm-rank-chip">#{rank}</span> : null}
        <strong>{team}</strong>
      </span>
      {!isHome && typeof score === "number" ? <span className="archive-final-score-number">{score}</span> : null}
    </div>
  );
}

function ArchiveTable({ games }: { games: ArchiveGame[] }) {
  return (
    <div className="archive-table-shell btm-archive-table-shell fan-archive-desktop-table">
      <div className="archive-table-scroll">
        <table className="archive-table btm-archive-table">
          <thead><tr><th>Game</th><th>Home team</th><th>Away team</th><th>The Model</th><th className="archive-center">Result</th></tr></thead>
          <tbody>
            {games.map((game, index) => {
              const winnerRank = game.predictedWinner === game.homeTeam ? game.homeRank : game.awayRank;
              return (
                <tr key={game.id}>
                  <td className="archive-data">{game.beatTheModelSlot ?? index + 1}</td>
                  <td><TeamCell game={game} side="home" /></td>
                  <td><TeamCell game={game} side="away" /></td>
                  <td>{game.predictedWinner ? <div className="btm-archive-model-pick"><span>PICKED</span><strong>{typeof winnerRank === "number" ? `#${winnerRank} ` : ""}{game.predictedWinner}</strong></div> : <span className="archive-missing-value">No model call</span>}</td>
                  <td className="archive-center"><ResultMark value={game.winnerCorrect} /></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MobileArchiveCards({ games }: { games: ArchiveGame[] }) {
  return (
    <div className="fan-archive-mobile-list">
      {games.map((game, index) => {
        const homeWon = typeof game.actualHomeScore === "number" && typeof game.actualAwayScore === "number" && game.actualHomeScore > game.actualAwayScore;
        const awayWon = typeof game.actualHomeScore === "number" && typeof game.actualAwayScore === "number" && game.actualAwayScore > game.actualHomeScore;
        const winnerRank = game.predictedWinner === game.homeTeam ? game.homeRank : game.awayRank;
        return (
          <article className="fan-archive-game-card" key={game.id}>
            <header><span>Game {game.beatTheModelSlot ?? index + 1}</span><ResultMark value={game.winnerCorrect} /></header>
            <div className={`fan-archive-team-row${awayWon ? " winner" : ""}`}><span>{typeof game.awayRank === "number" ? `#${game.awayRank}` : "—"}</span><strong>{game.awayTeam}</strong><em>{typeof game.actualAwayScore === "number" ? game.actualAwayScore : "—"}</em></div>
            <div className={`fan-archive-team-row${homeWon ? " winner" : ""}`}><span>{typeof game.homeRank === "number" ? `#${game.homeRank}` : "—"}</span><strong>{game.homeTeam}</strong><em>{typeof game.actualHomeScore === "number" ? game.actualHomeScore : "—"}</em></div>
            <footer><span>The Model</span><strong>{game.predictedWinner ? `${typeof winnerRank === "number" ? `#${winnerRank} ` : ""}${game.predictedWinner}` : "No model call"}</strong></footer>
          </article>
        );
      })}
    </div>
  );
}

function ResultsPanel({ summary }: { summary: BeatTheModelArchiveSummary }) {
  const record = `${summary.modelWins}-${summary.modelLosses}`;
  return (
    <div className="archive-results-panel btm-results-panel">
      <div className="archive-stat-grid btm-stat-grid">
        <article className="archive-stat-card stat-mint"><span>Model record</span><strong>{record}</strong><small>on this weekly card</small></article>
        <article className="archive-stat-card stat-cyan"><span>Correct picks</span><strong>{summary.modelWins}</strong><small>straight-up winners</small></article>
        <article className="archive-stat-card"><span>Missed picks</span><strong>{summary.modelLosses}</strong><small>kept on the record</small></article>
        <article className="archive-stat-card"><span>Accuracy</span><strong>{formatPercent(summary.modelAccuracy)}</strong><small>{summary.selectedGames} selected games</small></article>
      </div>
      <div className="archive-results-note btm-results-note">
        <div><span className="fan-kicker">WHY THIS COUNTS</span><p>The weekly power rankings selected this card before The Model’s prediction was considered. The Model had to play the same set of games as every fan.</p></div>
      </div>
    </div>
  );
}

export function ArchiveWeekView({ data }: { data: ArchiveWeek }) {
  const [tab, setTab] = useState<"games" | "results">("games");
  const games = useMemo(() => data.games.filter((game) => game.beatTheModelSelected === true).sort((a, b) => (a.beatTheModelSlot ?? 999) - (b.beatTheModelSlot ?? 999)), [data.games]);
  const summary = data.beatTheModel;

  if (!summary || !games.length) {
    return (
      <section className="fan-empty-state archive-btm-missing">
        <span className="fan-status fan-status-steel">No fan card for this week</span>
        <h2>This historical week does not have an Official 15 attached.</h2>
        <p>The broader game archive may exist, but Beat the Model only presents weeks with a valid selected slate and supported model calls.</p>
      </section>
    );
  }

  return (
    <section className="archive-week-workspace btm-archive-workspace">
      <div className="archive-workspace-header fan-archive-week-header">
        <div><span className="fan-kicker">OFFICIAL {summary.slateSize}</span><h2>{data.season} Week {data.week}</h2><p className="btm-archive-subtitle">{summary.selectedGames} matchups. One permanent card.</p></div>
        <div className="archive-tabs" role="tablist" aria-label="Beat the Model archive view">
          <button type="button" role="tab" aria-selected={tab === "games"} className={tab === "games" ? "active" : ""} onClick={() => setTab("games")}>Card</button>
          <button type="button" role="tab" aria-selected={tab === "results"} className={tab === "results" ? "active" : ""} onClick={() => setTab("results")}>Model result</button>
        </div>
      </div>
      {tab === "games" ? <><ArchiveTable games={games} /><MobileArchiveCards games={games} /></> : <ResultsPanel summary={summary} />}
    </section>
  );
}
