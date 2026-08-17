import type { Metadata } from "next";

import { getBeatTheModelDataset, getBeatTheModelRankings } from "../../lib/beat-the-model";

export const metadata: Metadata = {
  title: "Power Rankings",
  description: "Every FBS team ranked each week for Beat the Model slate selection.",
};

function formatRating(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}`;
}

export default function RankingsPage() {
  const current = getBeatTheModelDataset();
  const data = getBeatTheModelRankings(current.season, current.week);

  return (
    <>
      <section className="page-hero compact-hero btm-page-hero">
        <span className="eyebrow">BTM POWER RANKINGS</span>
        <h1>Every team. Every week.</h1>
        <p>These rankings answer one question: how strong is this team right now? They choose the weekly Beat the Model slate. The prediction model does not get to choose its opponents.</p>
      </section>

      <section className="btm-ranking-explainer">
        <div>
          <span>Entering</span>
          <strong>{data.season} Week {data.week}</strong>
        </div>
        <div>
          <span>Week 1 rule</span>
          <strong>Final {data.sourceSeason ?? data.season - 1} ratings</strong>
        </div>
        <div>
          <span>Power rating</span>
          <strong>Neutral-field strength</strong>
        </div>
      </section>

      {data.teams.length ? (
        <section className="btm-rankings-table-wrap">
          <table className="btm-rankings-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Power rating</th>
              </tr>
            </thead>
            <tbody>
              {data.teams.map((row) => (
                <tr key={row.team}>
                  <td><span className="btm-table-rank">#{row.rank}</span></td>
                  <td><strong>{row.team}</strong></td>
                  <td className="btm-rating-value">{formatRating(row.rating)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : (
        <section className="btm-awaiting">
          <div>
            <span className="eyebrow">RANKINGS NOT PUBLISHED</span>
            <h2>Generate the Week 1 rankings from the final {current.season - 1} power ratings.</h2>
            <p>The publisher writes the full ranking table into the deployable website data. It does not use preseason polls, recruiting rankings, or the model's game predictions.</p>
          </div>
          <code>python -m cfb_analytics.analytics.publish_website_archive</code>
        </section>
      )}

      <section className="btm-ranking-note">
        <span className="eyebrow">HOW THE RANKING MOVES</span>
        <p>Week 1 starts at 100% of the previous season's final numeric power rating. Over a team's first four games, that prior fades 75% / 50% / 25% / 0% as current-season evidence takes over. We blend ratings—not ordinal rank positions.</p>
      </section>
    </>
  );
}
