import Link from "next/link";
import {
  formatKickoff,
  predictedWinnerProbability,
  type PredictionGame,
} from "../lib/predictions";

export function PredictionCard({ game, featured = false }: { game: PredictionGame; featured?: boolean }) {
  const winnerProbability = predictedWinnerProbability(game);
  const homePicked = game.predictedWinner === game.homeTeam;

  return (
    <article className={`prediction-card${featured ? " prediction-card-featured" : ""}`}>
      <div className="prediction-card-topline">
        <span>Week {game.week}</span>
        <span>{formatKickoff(game.kickoff)}</span>
      </div>

      <div className="matchup-row">
        <div className={`team-line${!homePicked ? " picked-team" : ""}`}>
          <span className="team-name">{game.awayTeam}</span>
          <strong>{Math.round(game.projectedAwayScore)}</strong>
        </div>
        <div className={`team-line${homePicked ? " picked-team" : ""}`}>
          <span className="team-name">{game.homeTeam}</span>
          <strong>{Math.round(game.projectedHomeScore)}</strong>
        </div>
      </div>

      <div className="prediction-call">
        <div>
          <span className="eyebrow">MODEL PICK</span>
          <h2>{game.predictedWinner}</h2>
        </div>
        <div className="probability-badge">
          <strong>{Math.round(winnerProbability * 100)}%</strong>
          <span>win probability</span>
        </div>
      </div>

      <div className="prediction-card-footer">
        <span className="lock-note">{game.lockedAt ? "Locked before kickoff" : "Locks before kickoff"}</span>
        <Link className="why-link" href={`/predictions/${game.id}`}>See why <span aria-hidden="true">→</span></Link>
      </div>
    </article>
  );
}
