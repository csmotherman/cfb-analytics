import type { Metadata } from "next";
import Link from "next/link";
import {
  formatKickoff,
  getPredictionDataset,
  predictedWinnerProbability,
  seasonRecord,
} from "../../lib/predictions";

export const metadata: Metadata = {
  title: "Results",
  description: "The public record for every locked CFB Model prediction.",
};

export default function ResultsPage() {
  const data = getPredictionDataset();
  const record = seasonRecord(data.results);
  const graded = data.results.filter((game) => game.status === "final");

  return (
    <>
      <section className="page-hero compact-hero">
        <span className="eyebrow">THE RECEIPTS</span>
        <h1>Every pick stays on the record.</h1>
        <p>No disappearing losses. No rewritten predictions after the game.</p>
      </section>

      <section className="record-panel">
        <div>
          <span>Season record</span>
          <strong>{record.games ? `${record.wins}-${record.losses}` : "—"}</strong>
        </div>
        <div>
          <span>Accuracy</span>
          <strong>{record.accuracy === null ? "—" : `${Math.round(record.accuracy * 100)}%`}</strong>
        </div>
        <div>
          <span>Graded picks</span>
          <strong>{record.games}</strong>
        </div>
      </section>

      {graded.length ? (
        <section className="results-list">
          {graded.map((game) => {
            const probability = Math.round(predictedWinnerProbability(game) * 100);
            return (
              <Link className="result-row" href={`/predictions/${game.id}`} key={game.id}>
                <div>
                  <span className={`result-badge ${game.correct ? "result-win" : "result-loss"}`}>
                    {game.correct ? "W" : "L"}
                  </span>
                </div>
                <div className="result-matchup">
                  <strong>{game.awayTeam} at {game.homeTeam}</strong>
                  <span>{formatKickoff(game.kickoff)}</span>
                </div>
                <div className="result-pick">
                  <span>Picked {game.predictedWinner} · {probability}%</span>
                  <strong>{game.actualAwayScore ?? "—"}–{game.actualHomeScore ?? "—"}</strong>
                </div>
              </Link>
            );
          })}
        </section>
      ) : (
        <section className="empty-panel">
          <h2>The record starts with the first live slate.</h2>
          <p>Once games finish, the original locked prediction and final result will appear here automatically.</p>
          <Link className="text-link" href="/predictions">Back to predictions →</Link>
        </section>
      )}
    </>
  );
}
