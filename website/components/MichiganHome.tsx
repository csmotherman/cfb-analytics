import Link from "next/link";
import { LAST_COMPLETED_SEASON, michiganAppData, percentile, rank, supportedMichiganSeasons, type MichiganSeason } from "../lib/michigan";

const METRICS = [
  { key: "successRate", label: "Staying on schedule", detail: "Offensive success rate", format: "percent" },
  { key: "successRateAllowed", label: "Getting offenses off schedule", detail: "Defensive success rate allowed", format: "percent" },
  { key: "explosivePlayRate", label: "Creating big plays", detail: "Explosive play rate", format: "percent" },
  { key: "pointsPerResolvedPossession", label: "Turning drives into points", detail: "Points per resolved possession", format: "number" },
] as const;

function value(row: MichiganSeason, key: string, format: string) {
  const number = Number(row[key]);
  if (!Number.isFinite(number)) return "—";
  return format === "percent" ? `${(number * 100).toFixed(1)}%` : number.toFixed(2);
}

function ordinal(value: number | null) {
  if (value === null) return "—";
  const mod100 = value % 100;
  const suffix = mod100 >= 11 && mod100 <= 13 ? "th" : value % 10 === 1 ? "st" : value % 10 === 2 ? "nd" : value % 10 === 3 ? "rd" : "th";
  return `${value}${suffix}`;
}

export function MichiganHome({ season }: { season?: number }) {
  const data = michiganAppData(season);
  if (!data) return <section className="michigan-empty"><span>Michigan football analytics</span><h1>Season outside the supported window.</h1><p>Michigan season coverage begins in 2010.</p></section>;
  const { team, games, national, conference, conferenceSummary, season: selectedSeason, state } = data;
  if (state === "PRESEASON") return <div className="michigan-home">
    <SeasonNav selected={selectedSeason} />
    <section className="michigan-hero preseason-hero">
      <div className="michigan-hero-copy">
        <span className="michigan-kicker">{selectedSeason} MICHIGAN · PRESEASON</span>
        <h1>The next Michigan season starts here.</h1>
        <p>2026 has not been played. This page will carry schedule, roster, staff, recruiting, returning production, and clearly labeled projections as those source contracts are published—never fabricated performance.</p>
        <div className="michigan-actions"><Link href={`/football/${LAST_COMPLETED_SEASON}`} className="michigan-primary">Review the 2025 season</Link><Link href="/metrics" className="michigan-secondary">How projections will differ</Link></div>
      </div>
      <aside className="michigan-scorecard preseason-card">
        <div><span>Season status</span><strong>PRESEASON</strong><small>Observed record: 0–0</small></div>
        <div className="michigan-preseason-rule"><b>No actual SOAR metrics yet</b><p>Success rate, EPA, explosiveness, drive efficiency, player production, and opponent-adjusted performance remain unavailable until real games occur.</p></div>
      </aside>
    </section>
    <section className="michigan-method"><span>DATA POLICY</span><h2>Upcoming is not the same as observed.</h2><p>Any future model output will be labeled PROJECTED. Historical cards are labeled ACTUAL and are calculated only from games played in that season.</p></section>
  </div>;
  if (!team) return <div className="michigan-home"><SeasonNav selected={selectedSeason} /><section className="michigan-empty"><span>{selectedSeason} · {state}</span><h1>This season is in the historical window, but has not been published yet.</h1><p>National FBS facts must be ingested and validated for {selectedSeason} before Michigan ranks or percentiles can appear.</p><Link href={`/football/${LAST_COMPLETED_SEASON}`}>Open the latest completed season →</Link></section></div>;
  const wins = games.filter((game) => game.win === 1).length;
  const losses = games.filter((game) => game.loss === 1).length;
  const latestGames = [...games].reverse().slice(0, 5);

  return <div className="michigan-home">
    <SeasonNav selected={selectedSeason} />
    <section className="michigan-hero">
      <div className="michigan-hero-copy">
        <span className="michigan-kicker">THE NATIONAL PICTURE, THROUGH A MAIZE &amp; BLUE LENS</span>
        <h1>Know exactly where Michigan stands.</h1>
        <p>Every answer starts with the complete FBS field. See what Michigan did well, where it fell short, and how it compared nationally and inside the Big Ten.</p>
        <div className="michigan-actions">
          <Link href={`/teams/Michigan/${selectedSeason}`} className="michigan-primary">Explore the full profile</Link>
          <Link href="/rankings" className="michigan-secondary">View national rankings</Link>
        </div>
      </div>
      <aside className="michigan-scorecard">
        <div><span>{selectedSeason} season · ACTUAL</span><strong>{wins}–{losses}</strong><small>{team.games} games analyzed</small></div>
        <div className="michigan-scorecard-grid">
          <div><span>FBS teams</span><strong>{national.length}</strong></div>
          <div><span>Big Ten teams</span><strong>{conference.length}</strong></div>
          <div><span>Team ID</span><strong>{team.team_id}</strong></div>
          <div><span>Conference</span><strong>{team.conference}</strong></div>
        </div>
      </aside>
    </section>

    <section className="michigan-section">
      <div className="michigan-section-heading"><div><span>THE 30-SECOND ANSWER</span><h2>Michigan by the numbers</h2></div><p>Ranks are calculated against every FBS team using the same SOAR definitions.</p></div>
      <div className="michigan-metric-grid">
        {METRICS.map((metric) => {
          const nationalRank = rank(team, metric.key);
          const conferenceRank = rank(team, metric.key, "conference");
          const pct = percentile(team, metric.key);
          return <article className="michigan-metric" key={metric.key}>
            <span>{metric.label}</span>
            <strong>{value(team, metric.key, metric.format)}</strong>
            <p>{metric.detail}</p>
            <div><b>#{nationalRank ?? "—"}</b> nationally <i>{ordinal(conferenceRank)} in {team.conference}</i></div>
            <div className="michigan-percentile"><span style={{width: `${Math.max(0, Math.min(100, (pct ?? 0) * 100))}%`}} /></div>
          </article>;
        })}
      </div>
    </section>

    <section className="michigan-split">
      <div className="michigan-panel">
        <div className="michigan-panel-head"><div><span>RECENT RESULTS</span><h2>The latest five</h2></div><Link href={`/teams/Michigan/${selectedSeason}`}>Full season →</Link></div>
        <div className="michigan-game-list">
          {latestGames.map((game) => <div className="michigan-game" key={game.game_id}>
            <b className={game.win === 1 ? "win" : "loss"}>{game.win === 1 ? "W" : game.loss === 1 ? "L" : "—"}</b>
            <div><strong>{game.home_away === "away" ? "at " : game.neutral_site ? "vs " : "vs "}{game.opponent}</strong><span>Week {game.week} · {game.opponent_conference || game.opponent_classification || "Nonconference"}</span></div>
            <em>{game.points_for ?? "—"}<small>–</small>{game.points_against ?? "—"}</em>
          </div>)}
        </div>
      </div>
      <div className="michigan-panel michigan-context">
        <span>BIG TEN CONTEXT</span>
        <h2>{conferenceSummary?.teams ?? conference.length} teams, one measuring stick.</h2>
        <p>The conference view pools underlying numerators and denominators. It never averages ranks or gives small samples equal weight.</p>
        <dl>
          <div><dt>Conference team-games</dt><dd>{conferenceSummary?.games?.toLocaleString() ?? "—"}</dd></div>
          <div><dt>Big Ten offensive success</dt><dd>{conferenceSummary?.successRate != null ? `${(conferenceSummary.successRate * 100).toFixed(1)}%` : "—"}</dd></div>
          <div><dt>Big Ten defensive success allowed</dt><dd>{conferenceSummary?.successRateAllowed != null ? `${(conferenceSummary.successRateAllowed * 100).toFixed(1)}%` : "—"}</dd></div>
        </dl>
        <Link href="/rankings">Compare the full national field →</Link>
      </div>
    </section>

    <section className="michigan-method">
      <span>WHY YOU CAN TRUST IT</span><h2>Michigan is the focus. The nation is the control group.</h2>
      <p>CFBD supplies the facts. The repository’s validated SOAR pipeline reconstructs plays and possessions, calculates the metrics, and publishes ranks. This page only presents those outputs.</p>
      <Link href="/metrics">See how the metrics work →</Link>
    </section>
  </div>;
}

function SeasonNav({ selected }: { selected: number }) {
  return <nav className="michigan-season-nav" aria-label="Michigan season">
    <span>Season</span>
    <div>{supportedMichiganSeasons().map((year) => <Link key={year} href={`/football/${year}`} className={year === selected ? "active" : undefined}>{year}</Link>)}</div>
  </nav>;
}
