"use client";

import { useState } from "react";

import type { ArchiveGame, ArchiveWeek, ArchiveWeekSummary } from "../lib/archive";

function compactNumber(value: number): string {
  const rounded = Math.round(value * 10) / 10;
  return Number.isInteger(rounded) ? rounded.toFixed(0) : rounded.toFixed(1);
}

function formatTeamLine(homeMargin: number | null | undefined, homeTeam: string, awayTeam: string): string {
  if (typeof homeMargin !== "number" || !Number.isFinite(homeMargin)) return "—";
  if (Math.abs(homeMargin) < 1e-9) return "Pick'em";
  const favorite = homeMargin > 0 ? homeTeam : awayTeam;
  return `${favorite} -${compactNumber(Math.abs(homeMargin))}`;
}

function formatPercent(value: number | null | undefined): string {
  return typeof value === "number" && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "—";
}

function formatUnits(value: number | null | undefined): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}u`;
}

function ResultMark({ value, push = false }: { value: boolean | null | undefined; push?: boolean }) {
  if (push || value == null) {
    return <span className="archive-mark archive-mark-neutral" aria-label="Not graded">—</span>;
  }
  return value ? (
    <span className="archive-mark archive-mark-win" aria-label="Correct">✓</span>
  ) : (
    <span className="archive-mark archive-mark-loss" aria-label="Incorrect">×</span>
  );
}

function TeamCell({ game, side }: { game: ArchiveGame; side: "home" | "away" }) {
  const team = side === "home" ? game.homeTeam : game.awayTeam;
  const score = side === "home" ? game.actualHomeScore : game.actualAwayScore;
  return (
    <div className="archive-team-cell">
      <strong>{team}</strong>
      {typeof score === "number" ? <span>Final: {score}</span> : null}
    </div>
  );
}

function ArchiveTable({ games }: { games: ArchiveGame[] }) {
  return (
    <div className="archive-table-shell">
      <div className="archive-table-scroll">
        <table className="archive-table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Week</th>
              <th>Home team</th>
              <th>Away team</th>
              <th>Market spread</th>
              <th>Prediction (model)</th>
              <th className="archive-center">ATS correct</th>
              <th className="archive-center">Winner correct</th>
            </tr>
          </thead>
          <tbody>
            {games.map((game) => {
              const modelLine = formatTeamLine(game.modelHomeMargin, game.homeTeam, game.awayTeam);
              const marketLine = formatTeamLine(game.marketHomeMargin, game.homeTeam, game.awayTeam);
              return (
                <tr key={game.id} className={game.recommendedBet ? "archive-recommended-row" : undefined}>
                  <td className="archive-data">{game.season}</td>
                  <td className="archive-data">{game.week}</td>
                  <td><TeamCell game={game} side="home" /></td>
                  <td><TeamCell game={game} side="away" /></td>
                  <td>
                    <div className="archive-line archive-market-line">{marketLine}</div>
                    {game.marketProvider ? <span className="archive-subtext">{game.marketProvider}</span> : null}
                  </td>
                  <td>
                    <div className="archive-model-prediction">
                      <span className="archive-line archive-model-line">{modelLine}</span>
                      {game.recommendedBet ? <span className="archive-bet-pill">BET</span> : null}
                    </div>
                    {game.recommendedBet && game.recommendedBetTeam ? (
                      <span className="archive-subtext archive-bet-subtext">
                        ATS: {game.recommendedBetTeam}
                        {typeof game.recommendedBetConfidence === "number"
                          ? ` · ${(game.recommendedBetConfidence * 100).toFixed(1)}%`
                          : ""}
                      </span>
                    ) : game.evidenceStatus !== "official-oos" ? (
                      <span className="archive-subtext">No official OOS model call</span>
                    ) : null}
                  </td>
                  <td className="archive-center">
                    <ResultMark value={game.atsCorrect} push={game.atsResult === "PUSH"} />
                  </td>
                  <td className="archive-center">
                    <ResultMark value={game.winnerCorrect} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ResultsPanel({ summary }: { summary?: ArchiveWeekSummary }) {
  if (!summary || summary.modelGames === 0) {
    return (
      <div className="archive-results-empty">
        <span className="eyebrow">RESULTS</span>
        <h3>No official OOS model results for this week.</h3>
        <p>The historical games and market lines can still be shown, but this season does not have a supported Prediction-v2 out-of-sample record.</p>
      </div>
    );
  }

  const atsRecord = `${summary.atsWins}-${summary.atsLosses}-${summary.atsPushes}`;
  const betRecord = `${summary.recommendedBetWins}-${summary.recommendedBetLosses}-${summary.recommendedBetPushes}`;
  const unitsClass = typeof summary.recommendedBetUnits === "number"
    ? summary.recommendedBetUnits > 0
      ? "stat-positive"
      : summary.recommendedBetUnits < 0
        ? "stat-negative"
        : ""
    : "";

  return (
    <div className="archive-results-panel">
      <div className="archive-stat-grid">
        <article className="archive-stat-card stat-cyan">
          <span>Model MAE</span>
          <strong>{summary.modelMae == null ? "—" : summary.modelMae.toFixed(2)}</strong>
          <small>points per game</small>
        </article>
        <article className="archive-stat-card stat-mint">
          <span>Winner %</span>
          <strong>{formatPercent(summary.winnerAccuracy)}</strong>
          <small>{summary.winnerWins}-{summary.winnerLosses} straight up</small>
        </article>
        <article className="archive-stat-card stat-amber">
          <span>ATS record</span>
          <strong>{atsRecord}</strong>
          <small>{formatPercent(summary.atsAccuracy)} against the reference spread</small>
        </article>
        <article className={`archive-stat-card stat-units ${unitsClass}`}>
          <span>Recommended-bet profit</span>
          <strong>{formatUnits(summary.recommendedBetUnits)}</strong>
          <small>{summary.recommendedBetSourcePresent ? `${betRecord} · ${summary.recommendedBets} bets` : "Bet source not generated"}</small>
        </article>
      </div>

      <div className="archive-results-note">
        <div>
          <span className="eyebrow">HOW TO READ THIS</span>
          <p>ATS record grades the model's predicted margin against the historical CFBD reference spread. Units only use the model's predeclared recommended bets, not every ATS opinion.</p>
        </div>
        <div className="archive-results-convention">
          <span>Units convention</span>
          <strong>Flat 1u risk · -110</strong>
          <small>Win +0.909u · Loss -1u · Push 0u</small>
        </div>
      </div>
    </div>
  );
}

export function ArchiveWeekView({ data }: { data: ArchiveWeek }) {
  const [tab, setTab] = useState<"games" | "results">("games");

  return (
    <section className="archive-week-workspace">
      <div className="archive-workspace-header">
        <div>
          <span className="eyebrow">{data.label ?? `${data.season} Week ${data.week}`}</span>
          <h2>{data.games.length} games</h2>
        </div>
        <div className="archive-tabs" role="tablist" aria-label="Archive view">
          <button
            type="button"
            role="tab"
            aria-selected={tab === "games"}
            className={tab === "games" ? "active" : ""}
            onClick={() => setTab("games")}
          >
            Games
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === "results"}
            className={tab === "results" ? "active" : ""}
            onClick={() => setTab("results")}
          >
            Results
          </button>
        </div>
      </div>

      {tab === "games" ? <ArchiveTable games={data.games} /> : <ResultsPanel summary={data.summary} />}
    </section>
  );
}
