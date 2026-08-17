import type { Metadata } from "next";
import Link from "next/link";

import { BeatTheModelGameView } from "../../components/BeatTheModelGame";
import { getBeatTheModelDataset } from "../../lib/beat-the-model";

export const metadata: Metadata = {
  title: "Play",
  description: "Select and submit your college football picks, reveal The Model one game at a time, and try to win the week.",
};

export default function PlayPage() {
  const data = getBeatTheModelDataset();
  const hasTeamStats = data.games.some((game) => Boolean(game.homePregameStats || game.awayPregameStats));

  return (
    <>
      <section className="fan-page-intro fan-play-intro">
        <div>
          <span className="fan-kicker">{data.season} WEEK {data.week}</span>
          <h1>Put your card on it.</h1>
          <p>
            Pick one winner in every Official {data.slateSize} matchup. Market consensus is there for context. {hasTeamStats
              ? "Open Matchup Intel to compare pregame team performance, then select, review, and submit your pick."
              : "Tap a team, review your choice, then submit it. The Model stays hidden until the pick is confirmed."}
          </p>
        </div>
        <div>
          <div className="fan-rule-row fan-rule-row-intro" aria-label="Beat the Model scoring rules">
            <span><strong>{data.slateSize}</strong> games</span>
            <span><strong>1</strong> point per winner</span>
            <span><strong>SU</strong> straight-up picks</span>
          </div>
          <Link className="fan-text-link fan-play-method-link" href="/about">How games are selected →</Link>
        </div>
      </section>

      <BeatTheModelGameView data={data} />
    </>
  );
}
