import type { GamePrediction } from "../../lib/michigan/predictions";
import { describeTeamMargin } from "../../lib/michigan/predictions";

export function PredictionPanel({ prediction }: { prediction: GamePrediction | null }) {
  if (!prediction) return <section className="empty-state"><span>SOAR PICK</span><h2>Coming game week.</h2></section>;
  return <section className="prediction-panel"><span className="eyebrow">SOAR PICK</span><h2>{describeTeamMargin(prediction)}</h2><div className="pending-grid prediction-facts"><div><span>WINNER</span><strong>{prediction.predictedWinner.toUpperCase()}</strong></div><div><span>SPREAD</span><strong>{prediction.predictedHomeMargin>0?"+":""}{prediction.predictedHomeMargin.toFixed(1)}</strong></div></div></section>;
}
