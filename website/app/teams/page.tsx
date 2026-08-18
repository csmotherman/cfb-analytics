import Link from "next/link";
import { latestPublishedSeason, nationalTeams, rank } from "../../lib/michigan";

export default function TeamsPage() {
  const season = latestPublishedSeason();
  const teams = season === null ? [] : nationalTeams(season).sort((a, b) => a.team.localeCompare(b.team));
  return <div className="michigan-home">
    <section className="michigan-page-hero"><span>{season ?? "LATEST"} FBS DIRECTORY</span><h1>Michigan's opponents live in the same system.</h1><p>Open any national profile to understand the comparison behind Michigan's schedule, rankings, and matchup context.</p></section>
    <section className="michigan-team-directory">{teams.map((team) => <Link href={`/teams/${team.slug}/${season}`} key={team.team_id} className={team.team === "Michigan" ? "is-michigan" : ""}><div><strong>{team.team}</strong><span>{team.conference}</span></div><b>#{rank(team, "successRate") ?? "—"}<small> offense</small></b></Link>)}</section>
  </div>;
}
