import type { Metadata } from "next";
import { findPublishedTeam, latestPublishedSeason, nationalTeams, rank, type MichiganSeason } from "../../lib/michigan";

export const metadata: Metadata = { title: "Compare Michigan", description: "Compare Michigan with any FBS opponent using identical SOAR metrics." };

const comparisons = [
  ["successRate", "Staying on schedule"], ["successRateAllowed", "Defensive down-winning"],
  ["explosivePlayRate", "Creating big plays"], ["explosivePlayRateAllowed", "Preventing big plays"],
  ["pointsPerResolvedPossession", "Points per drive"], ["pointsPerResolvedPossessionAllowed", "Points allowed per drive"],
] as const;

function format(row: MichiganSeason, key: string) { const n = Number(row[key]); return Number.isFinite(n) ? (key.includes("Rate") ? `${(n * 100).toFixed(1)}%` : n.toFixed(2)) : "—"; }

export default async function ComparePage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const season = latestPublishedSeason();
  const query = await searchParams;
  const opponentSlug = String(Array.isArray(query.opponent) ? query.opponent[0] : query.opponent ?? "ohio-state");
  const michigan = season === null ? null : findPublishedTeam(season, "michigan");
  const opponent = season === null ? null : findPublishedTeam(season, opponentSlug);
  const options = season === null ? [] : nationalTeams(season).filter((row) => row.team !== "Michigan").sort((a, b) => a.team.localeCompare(b.team));
  return <div className="michigan-home">
    <section className="michigan-page-hero"><span>HEAD-TO-HEAD PROFILE</span><h1>Put Michigan next to anyone.</h1><p>Same season, same definitions, same national population. Choose a team to see where the matchup's statistical edges begin.</p></section>
    <form className="michigan-compare-form"><label htmlFor="opponent">Compare Michigan with</label><select id="opponent" name="opponent" defaultValue={opponent?.slug ?? opponentSlug}>{options.map((row) => <option value={row.slug} key={row.team_id}>{row.team}</option>)}</select><button>Compare</button></form>
    {michigan && opponent ? <section className="michigan-comparison">
      <header><div><span>MICHIGAN</span><h2>Michigan</h2><p>{michigan.conference}</p></div><b>VS</b><div><span>OPPONENT</span><h2>{opponent.team}</h2><p>{opponent.conference}</p></div></header>
      {comparisons.map(([key, label]) => <div className="michigan-comparison-row" key={key}><strong>{format(michigan, key)}<small>#{rank(michigan, key)} nationally</small></strong><span>{label}</span><strong>{format(opponent, key)}<small>#{rank(opponent, key)} nationally</small></strong></div>)}
    </section> : <div className="notice">Published comparison data is unavailable.</div>}
  </div>;
}
