import type { Metadata } from "next";

import { BeatTheModelGameView } from "../../components/BeatTheModelGame";
import { getBeatTheModelDataset } from "../../lib/beat-the-model";

export const metadata: Metadata = {
  title: "Play",
  description: "Pick the 15 biggest college football games of the week and try to Beat the Model.",
};

export default function PlayPage() {
  const data = getBeatTheModelDataset();

  return (
    <>
      <section className="fan-page-intro fan-play-intro">
        <div>
          <span className="fan-kicker">PLAY</span>
          <h1>Make your picks.</h1>
          <p>Choose a winner in every matchup. You make your call first; then The Model's pick is revealed.</p>
        </div>
        <div className="fan-rule-row fan-rule-row-intro" aria-label="Beat the Model scoring rules">
          <span><strong>{data.slateSize}</strong> games</span>
          <span><strong>1</strong> point per win</span>
          <span><strong>No</strong> confidence points</span>
        </div>
      </section>

      <BeatTheModelGameView data={data} />
    </>
  );
}
