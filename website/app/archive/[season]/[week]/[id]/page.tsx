import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { SharePrediction } from "../../../../../components/SharePrediction";
import { getArchiveGame } from "../../../../../lib/archive";

export async function generateMetadata({ params }: { params: Promise<{ season: string; week: string; id: string }> }): Promise<Metadata> {
  const { season: seasonRaw, week: weekRaw, id } = await params;
  const game = getArchiveGame(Number(seasonRaw), Number(weekRaw), id);
  if (!game || game.beatTheModelSelected !== true) return { title: "Beat the Model archived game" };
  return {
    title: `${game.awayTeam} vs ${game.homeTeam} · Beat the Model`,
    description: `See The Model's archived pick for ${game.awayTeam} at ${game.homeTeam}.`,
  };
}

export default async function ArchiveGamePage({ params }: { params: Promise<{ season: string; week: string; id: string }> }) {
  const { season: seasonRaw, week: weekRaw, id } = await params;
  const season = Number(seasonRaw);
  const week = Number(weekRaw);
  const game = getArchiveGame(season, week, id);
  if (!game || game.beatTheModelSelected !== true) notFound();

  const modelMargin = typeof game.modelHomeMargin === "number" ? game.modelHomeMargin : null;
  const predictedWinner = game.predictedWinner ?? (modelMargin === null ? null : modelMargin >= 0 ? game.homeTeam : game.awayTeam);
  const predictedRank = predictedWinner === game.homeTeam ? game.homeRank : game.awayRank;
  const shareText = predictedWinner
    ? `Beat the Model archive: The Model took ${predictedWinner} in ${game.season} Week ${game.week}.`
    : `${game.season} Week ${game.week}: ${game.awayTeam} at ${game.homeTeam}.`;

  return (
    <>
      <Link className="back-link" href={`/archive/${season}/${week}`}>← {season} Week {week}</Link>

      <section className="game-hero btm-detail-hero">
        <div className="game-meta">Official {game.beatTheModelSlot ?? ""} · {season} Week {week}</div>
        <div className="game-score-grid">
          <div>
            <span>{typeof game.awayRank === "number" ? `#${game.awayRank} ` : ""}{game.awayTeam}</span>
            <strong>{typeof game.actualAwayScore === "number" ? game.actualAwayScore : "—"}</strong>
          </div>
          <span className="at-mark">FINAL</span>
          <div>
            <span>{typeof game.homeRank === "number" ? `#${game.homeRank} ` : ""}{game.homeTeam}</span>
            <strong>{typeof game.actualHomeScore === "number" ? game.actualHomeScore : "—"}</strong>
          </div>
        </div>

        <div className="game-pick-row">
          <div>
            <span className="eyebrow">THE MODEL PICKED</span>
            <h1>{predictedWinner ? `${typeof predictedRank === "number" ? `#${predictedRank} ` : ""}${predictedWinner}` : "No archived model call"}</h1>
            {modelMargin !== null ? <p>Projected margin {Math.abs(modelMargin).toFixed(1)}</p> : null}
          </div>
          <SharePrediction text={shareText} />
        </div>
        <div className="lock-banner">This game was selected by the weekly power rankings, not by The Model's confidence or prediction.</div>
      </section>

      {game.reasons?.length ? (
        <section className="why-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">WHY?</span>
              <h2>Why The Model made the call</h2>
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
      ) : null}

      <section className="archive-outcome-panel btm-outcome-panel">
        <span className="eyebrow">RESULT</span>
        {typeof game.actualAwayScore === "number" && typeof game.actualHomeScore === "number" ? (
          <h2>{game.awayTeam} {game.actualAwayScore} · {game.homeTeam} {game.actualHomeScore}</h2>
        ) : (
          <h2>Final result not included in this archive record.</h2>
        )}
        {typeof game.winnerCorrect === "boolean" ? <p>The Model earned <strong>{game.winnerCorrect ? "1 point" : "0 points"}</strong> on this game.</p> : null}
      </section>
    </>
  );
}
