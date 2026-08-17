import type { Metadata } from "next";

import { RankingsBrowser } from "../../components/RankingsBrowser";
import { getBeatTheModelDataset, getBeatTheModelRankings } from "../../lib/beat-the-model";

export const metadata: Metadata = {
  title: "Power Rankings",
  description: "Every FBS team ranked each week for Beat the Model slate selection.",
};

export default function RankingsPage() {
  const current = getBeatTheModelDataset();
  const data = getBeatTheModelRankings(current.season, current.week);

  return (
    <>
      <section className="fan-page-intro">
        <div>
          <span className="fan-kicker">POWER RANKINGS</span>
          <h1>Who's strongest right now?</h1>
          <p>Every FBS team gets one weekly power rating. Those ratings choose the biggest matchups for Beat the Model—the prediction model does not choose its own games.</p>
        </div>
      </section>

      <section className="fan-info-strip" aria-label="Ranking details">
        <div><span>Current board</span><strong>{data.season} Week {data.week}</strong></div>
        <div><span>Teams ranked</span><strong>{data.teams.length || "—"}</strong></div>
        <div><span>What power means</span><strong>Neutral-field strength</strong></div>
      </section>

      {data.teams.length ? (
        <RankingsBrowser teams={data.teams} />
      ) : (
        <section className="fan-empty-state">
          <span className="fan-status fan-status-steel">Rankings not published</span>
          <h2>The {data.season} Week {data.week} board is not available yet.</h2>
          <p>Week 1 begins from the final {current.season - 1} power ratings. The full list will appear here automatically when the weekly data is published.</p>
        </section>
      )}

      <section className="fan-explainer-card">
        <span className="fan-kicker">WHY THE RANKINGS MOVE</span>
        <h2>Last season fades as this season proves itself.</h2>
        <p>Week 1 starts at 100% of the previous season's final numeric power rating. Over a team's first four games, that prior fades to 75%, 50%, 25%, then 0% while current-season evidence takes over. The site blends numeric ratings—not poll positions.</p>
      </section>
    </>
  );
}
