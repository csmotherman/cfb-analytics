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
      <section className="page-hero compact-hero btm-page-hero">
        <span className="eyebrow">BEAT THE MODEL</span>
        <h1>Make your picks.</h1>
        <p>One winner per game. One point per correct pick. The Model's answer stays hidden until you choose.</p>
      </section>
      <BeatTheModelGameView data={data} />
    </>
  );
}
