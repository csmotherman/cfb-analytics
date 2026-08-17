import Link from "next/link";

import { archiveGameHref, type ArchiveGame } from "../lib/archive";

function formatMargin(value: number): string {
  return `${Math.abs(value).toFixed(1)} pts`;
}

export function ArchiveGameCard({ game }: { game: ArchiveGame }) {
  const hasPrediction = Boolean(game.predictedWinner);
  const modelMargin = typeof game.modelHomeMargin === "number" ? game.modelHomeMargin : null;
  const predictedWinner = game.predictedWinner ?? (modelMargin === null ? null : modelMargin >= 0 ? game.homeTeam : game.awayTeam);
  const marginText = modelMargin === null
    ? null
    : `${modelMargin >= 0 ? game.homeTeam : game.awayTeam} by ${formatMargin(modelMargin)}`;
  const finalAvailable = typeof game.actualAwayScore === "number" && typeof game.actualHomeScore === "number";

  return (
    <article className="archive-game-card">
      <div className="archive-game-meta">
        <span>{game.awayTeam} at {game.homeTeam}</span>
        {game.evidenceStatus === "official-oos" ? <span>Historical OOS model pick</span> : null}
      </div>

      <div className="archive-game-main">
        <div>
          <span className="eyebrow">{hasPrediction || modelMargin !== null ? "MODEL PICK" : "HISTORICAL GAME"}</span>
          <h3>{predictedWinner ?? `${game.awayTeam} at ${game.homeTeam}`}</h3>
          {marginText ? <p>{marginText}</p> : null}
        </div>

        {finalAvailable ? (
          <div className="archive-final-score">
            <span>FINAL</span>
            <strong>{game.awayTeam} {game.actualAwayScore} · {game.homeTeam} {game.actualHomeScore}</strong>
          </div>
        ) : typeof game.actualHomeMargin === "number" ? (
          <div className="archive-final-score">
            <span>FINAL MARGIN</span>
            <strong>{game.actualHomeMargin >= 0 ? game.homeTeam : game.awayTeam} by {Math.abs(game.actualHomeMargin).toFixed(0)}</strong>
          </div>
        ) : null}
      </div>

      <div className="archive-game-footer">
        {typeof game.correct === "boolean" ? (
          <span className={`archive-result ${game.correct ? "archive-result-win" : "archive-result-loss"}`}>
            {game.correct ? "Correct" : "Missed"}
          </span>
        ) : (
          <span className="archive-result archive-result-neutral">Archived</span>
        )}
        <Link className="why-link" href={archiveGameHref(game)}>View game <span aria-hidden="true">→</span></Link>
      </div>
    </article>
  );
}
