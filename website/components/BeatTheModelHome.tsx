import Link from "next/link";

import { BeatTheModelGameView } from "./BeatTheModelGame";
import { getBeatTheModelDataset, getBeatTheModelRankings, modelRecord } from "../lib/beat-the-model";

export function BeatTheModelHome() {
  const data = getBeatTheModelDataset();
  const rankings = getBeatTheModelRankings(data.season, data.week);
  const record = modelRecord(data.games);

  return (
    <>
      <section className="btm-hero">
        <div className="btm-hero-copy">
          <span className="eyebrow">THE WEEKLY COLLEGE FOOTBALL PICKING GAME</span>
          <h1>Beat the Model.</h1>
          <p>Pick the winners of the 15 biggest games of the week. Then see whether you know college football better than The Model.</p>
          <div className="btm-hero-actions">
            <Link className="btm-primary-cta" href="/play">Make your picks</Link>
            <Link className="btm-secondary-cta" href="/rankings">See the rankings</Link>
          </div>
        </div>

        <div className="btm-hero-board" aria-label="Beat the Model rules">
          <div><span>Weekly slate</span><strong>{data.slateSize}</strong><small>biggest matchups</small></div>
          <div><span>Scoring</span><strong>1</strong><small>point per winner</small></div>
          <div><span>The Model</span><strong>?</strong><small>hidden until you pick</small></div>
          <div>
            <span>Model this week</span>
            <strong>{record.games ? `${record.wins}-${record.losses}` : "—"}</strong>
            <small>{record.accuracy == null ? "starts at kickoff" : `${Math.round(record.accuracy * 100)}% correct`}</small>
          </div>
        </div>
      </section>

      <section className="btm-how-strip" aria-label="How Beat the Model works">
        <div><span>01</span><strong>Rank every team</strong><p>Every FBS team gets a weekly power ranking.</p></div>
        <div><span>02</span><strong>Select the biggest 15</strong><p>The slate is chosen from the rankings—not model confidence.</p></div>
        <div><span>03</span><strong>Make your picks</strong><p>The Model stays hidden until you make your own call.</p></div>
        <div><span>04</span><strong>See who won</strong><p>One correct winner equals one point. Highest score wins.</p></div>
      </section>

      <BeatTheModelGameView data={data} />

      <section className="btm-home-grid">
        <article className="btm-home-panel">
          <span className="eyebrow">POWER RANKINGS</span>
          <h2>Every team. Every week.</h2>
          <p>{rankings.teams.length
            ? `${rankings.teams.length} teams are ranked entering Week ${data.week}. Week 1 uses the final ${rankings.sourceSeason ?? data.season - 1} power ratings.`
            : `Week 1 rankings will be generated directly from the final ${data.season - 1} power ratings.`}</p>
          <Link href="/rankings">Open rankings <span aria-hidden="true">→</span></Link>
        </article>

        <article className="btm-home-panel">
          <span className="eyebrow">THE RECEIPTS</span>
          <h2>The Model cannot hide.</h2>
          <p>Every official slate and every model pick stays in the archive after the games finish. No post-game rewrites.</p>
          <Link href="/archive">Open the archive <span aria-hidden="true">→</span></Link>
        </article>
      </section>
    </>
  );
}
