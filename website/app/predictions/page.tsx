import type { Metadata } from "next";
import { PredictionFeed } from "../../components/PredictionFeed";

export const metadata: Metadata = {
  title: "Predictions",
  description: "This week's college football model predictions, projected scores, and explanations.",
};

export default function PredictionsPage() {
  return <PredictionFeed />;
}
