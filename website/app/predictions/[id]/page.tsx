import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SharePrediction } from "../../../components/SharePrediction";
import {
  formatKickoff,
  getPredictionById,
  getPredictionDataset,
  predictedWinnerProbability,
} from "../../../lib/predictions";

export function generateStaticParams() {
  const data = getPredictionDataset();
  return [...data.current, ...data.results].map((game) => ({ id: game.id }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const game = getPredictionById(id);
  if (!game) return { title: "Prediction" };
  const probability = Math.round(predictedWinnerProbability(game) * 100);
  return {
    title: `${game.awayTeam} vs ${game.homeTeam} Prediction`,
    description: `${game.predictedWinner} is the model pick at ${probability}%. See the three reasons behind the prediction.`,
  };
}

export default async function PredictionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const game = getPredictionById(id);
  if (!game) notFound();

  const probability = Math.round(predictedWinnerProbability(game) * 100);
  const shareText = `CFB Model: ${game.predictedWinner} over ${game.predictedWinner === game.homeTeam ? game.awayTeam : game.homeTeam}, ${probability}% win probability.`;

  return (
    <>
      <Link className="back-link" href="/predictions">← All predictions</Link>

      <section className="game-hero">
        <div className="game-meta">Week {game.week} · {formatKickoff(game.kickoff)}</div>
        <div className="game-score-grid">
          <div>
            <span>{game.awayTeam}</span>
            <strong>{Math.round(game.projectedAwayScore)}</strong>
          </div>
          <span className="at-mark">at</span>
          <div>
            <span>{game.homeTeam}</span>
            <strong>{Math.round(game.projectedHomeScore)}</strong>
          </div>
        </div>
        <div className="game-pick-row">
          <div>
            <span className="eyebrow">MODEL PICK</span>
            <h1>{game.predictedWinner}</h1>
            <p>{probability}% win probability</p>
          </div>
          <SharePrediction text={shareText} />
        </div>
        <div className="lock-banner">{game.lockedAt ? `Locked ${game.lockedAt}` : "This prediction locks before kickoff."}</div>
      </section>

      <section className="why-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">WHY?</span>
            <h2>Three reasons the model leans {game.predictedWinner}</h2>
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

      <section className="risk-card">
        <span className="eyebrow">WHAT COULD MAKE IT WRONG?</span>
        <h2>The upset path</h2>
        <p>{game.risk}</p>
      </section>

      <section className="detail-bottom">
        <p>That is the entire call: one pick, three reasons, one clear way it could go wrong.</p>
        <Link className="text-link" href="/results">Check the model's record →</Link>
      </section>
    </>
  );
}
