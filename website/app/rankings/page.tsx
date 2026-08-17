import type { Metadata } from "next";

import { RankingsBrowser } from "../../components/RankingsBrowser";
import { getBeatTheModelDataset, getBeatTheModelRankings } from "../../lib/beat-the-model";

export const metadata: Metadata = {
  title: "Power Rankings",
  description: "Every FBS team ranked every week. These rankings determine the biggest matchups in Beat the Model.",
};

export default function RankingsPage() {
  const current = getBeatTheModelDataset();
  const data = getBeatTheModelRankings(current.season, current.week);

  return (
    <>
      <section className="fan-page-intro">
        <div>
          <span className="fan-kicker">{data.season} WEEK {data.week} POWER RANKINGS</span>
          <h1>Every team. No pollsters.</h1>
          <p>A single opponent-adjusted strength board ranks every FBS team before the week. That board—not The Model’s prediction confidence—decides which matchups become the Official {current.slateSize}.</p>
        </div>
      </section>

      <section className="fan-info-strip" aria-label="Ranking details">
        <div><span>Current board</span><strong>{data.season} Week {data.week}</strong></div>
        <div><span>Teams ranked</span><strong>{data.teams.length || "—"}</strong></div>
        <div><span>Rating meaning</span><strong>Neutral-field strength</strong></div>
      </section>

      {data.teams.length ? (
        <RankingsBrowser teams={data.teams} />
      ) : (
        <section className="fan-empty-state">
          <span className="fan-status fan-status-steel">Rankings not published</span>
          <h2>The {data.season} Week {data.week} board is not available yet.</h2>
          <p>The full ranking will appear automatically when the weekly data is published.</p>
        </section>
      )}

      <section className="fan-principles fan-ranking-principles">
        <article className="fan-principle primary">
          <span className="fan-kicker">EARLY-SEASON RULE</span>
          <h2>Last season fades. This season takes over.</h2>
          <p>Week 1 starts from the previous season’s final numeric power ratings. Over each team’s first four games, that prior fades from 100% to 75%, 50%, 25%, then 0% as current-season evidence takes over.</p>
        </article>
        <article className="fan-principle">
          <span className="fan-kicker">WHY IT EXISTS</span>
          <h2>The rankings pick the fights.</h2>
          <p>The strongest, closest-ranked FBS matchups rise to the top of the weekly card. The prediction model never gets to cherry-pick which games it must face.</p>
        </article>
      </section>
    </>
  );
}
