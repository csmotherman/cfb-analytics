import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { SharePrediction } from "../../../../../components/SharePrediction";
import { getArchiveGame } from "../../../../../lib/archive";

export async function generateMetadata({ params }: { params: Promise<{ season: string; week: string; id: string }> }): Promise<Metadata> {
  const { season: seasonRaw, week: weekRaw, id } = await params;
  const game = getArchiveGame(Number(seasonRaw), Number(weekRaw), id);
  if (!game) return { title: "Archived game" };
  return {
    title: `${game.awayTeam} vs ${game.homeTeam} · ${game.season} Archive`,
    description: game.predictedWinner
      ? `See the archived model call for ${game.awayTeam} at ${game.homeTeam}.`
      : `See the archived ${game.season} matchup between ${game.awayTeam} and ${game.homeTeam}.`,
  };
}

export default async function ArchiveGamePage({ params }: { params: Promise<{ season: string; week: string; id: string }> }) {
  const { season: seasonRaw, week: weekRaw, id } = await params;
  const season = Number(seasonRaw);
  const week = Number(weekRaw);
  const game = getArchiveGame(season, week, id);
  if (!game) notFound();

  const modelMargin = typeof game.modelHomeMargin === "number" ? game.modelHomeMargin : null;
  const predictedWinner = game.predictedWinner ?? (modelMargin === null ? null : modelMargin >= 0 ? game.homeTeam : game.awayTeam);
  const loser = predictedWinner === game.homeTeam ? game.awayTeam : game.homeTeam;
  const probability = typeof game.homeWinProbability === "number"
    ? Math.round((predictedWinner === game.homeTeam ? game.homeWinProbability : 1 - game.homeWinProbability) * 100)
    : null;
  const shareText = predictedWinner
    ? `CFB Model archive: ${predictedWinner} over ${loser} in ${game.season} Week ${game.week}.`
    : `${game.season} Week ${game.week}: ${game.awayTeam} at ${game.homeTeam}.`;

  return (
    <>
      <Link className="back-link" href={`/archive/${season}/${week}`}>← {season} Week {week}</Link>

      <section className="game-hero">
        <div className="game-meta">{season} · Week {week} · Archived game</div>
        <div className="game-score-grid">
          <div>
            <span>{game.awayTeam}</span>
            <strong>{typeof game.projectedAwayScore === "number" ? Math.round(game.projectedAwayScore) : "—"}</strong>
          </div>
          <span className="at-mark">at</span>
          <div>
            <span>{game.homeTeam}</span>
            <strong>{typeof game.projectedHomeScore === "number" ? Math.round(game.projectedHomeScore) : "—"}</strong>
          </div>
        </div>

        <div className="game-pick-row">
          <div>
            <span className="eyebrow">{predictedWinner ? "ARCHIVED MODEL PICK" : "HISTORICAL SLATE"}</span>
            <h1>{predictedWinner ?? `${game.awayTeam} at ${game.homeTeam}`}</h1>
            {probability !== null ? <p>{probability}% win probability</p> : modelMargin !== null ? (
              <p>Projected margin: {modelMargin >= 0 ? game.homeTeam : game.awayTeam} by {Math.abs(modelMargin).toFixed(1)}</p>
            ) : null}
          </div>
          <SharePrediction text={shareText} />
        </div>
        <div className="lock-banner">
          {game.evidenceStatus === "official-oos"
            ? "Historical out-of-sample model prediction."
            : "Historical archive entry. No prediction claim is added unless the source data supports one."}
        </div>
      </section>

      {game.reasons?.length ? (
        <section className="why-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">WHY?</span>
              <h2>Why the model made the call</h2>
            </div>
          </div>
          <div className="reason-grid">
            {game.reasons.slice(0, 3).map((reason, index) => (
              <article className="reason-card" key={`${reason.title}-${index}`}>
                <span className="reason-number">0{index + 1}</span>
                <span className="eyebrow">{reason.eyebrow}</span>
                <h3>{reason.title}</h3>
                <p>{reason.detail}</p>
              </article>
            ))}
          </div>
        </section>
      ) : (
        <section className="empty-panel archive-detail-note">
          <h2>No invented explanation.</h2>
          <p>This historical record does not contain the three fan-facing reasons used by the live product, so the archive leaves them blank instead of reconstructing a story after the result is known.</p>
        </section>
      )}

      <section className="archive-outcome-panel">
        <span className="eyebrow">WHAT HAPPENED?</span>
        {typeof game.actualAwayScore === "number" && typeof game.actualHomeScore === "number" ? (
          <h2>{game.awayTeam} {game.actualAwayScore} · {game.homeTeam} {game.actualHomeScore}</h2>
        ) : typeof game.actualHomeMargin === "number" ? (
          <h2>{game.actualHomeMargin >= 0 ? game.homeTeam : game.awayTeam} won by {Math.abs(game.actualHomeMargin).toFixed(0)}</h2>
        ) : (
          <h2>Final result not included in this archive record.</h2>
        )}
        {typeof game.correct === "boolean" ? <p>The archived model pick was <strong>{game.correct ? "correct" : "incorrect"}</strong>.</p> : null}
      </section>
    </>
  );
}
