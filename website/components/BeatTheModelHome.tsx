import Link from "next/link";

import { FavoriteTeamCard } from "./FavoriteTeamCard";
import {
  formatKickoff,
  getBeatTheModelDataset,
  getBeatTheModelRankings,
} from "../lib/beat-the-model";
import { getArchiveAllTimeSummary } from "../lib/archive";

function statusCopy(status: string) {
  if (status === "open") return { label: "Picks open", tone: "mint", cta: "Select my picks" };
  if (status === "locked") return { label: "Games underway", tone: "cyan", cta: "Follow my card" };
  if (status === "final") return { label: "Week final", tone: "mint", cta: "See this week’s results" };
  if (status === "awaiting-model") return { label: "Official 15 set", tone: "amber", cta: "View the 15 matchups" };
  return { label: "Next week loading", tone: "steel", cta: "See how it works" };
}

function percent(value: number | null): string {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}

function MatchupSpotlight({ game }: { game: ReturnType<typeof getBeatTheModelDataset>["games"][number] }) {
  return (
    <article className="fan-spotlight-card">
      <header>
        <div><span className="fan-kicker">BIGGEST MATCHUP</span><strong>Official 15 · Game {game.slot}</strong></div>
        <span>{formatKickoff(game.kickoff) ?? "Kickoff TBA"}</span>
      </header>
      <div className="fan-spotlight-matchup">
        <div><span>#{game.awayRank}</span><strong>{game.awayTeam}</strong><small>Away</small></div>
        <em>AT</em>
        <div><span>#{game.homeRank}</span><strong>{game.homeTeam}</strong><small>Home</small></div>
      </div>
      <footer>
        <div><span>THE MODEL</span><strong>{game.modelWinner ? "Hidden until you pick" : "Pregame call locking"}</strong></div>
        <Link href="/play">Go to this game <span aria-hidden="true">→</span></Link>
      </footer>
    </article>
  );
}

export function BeatTheModelHome() {
  const data = getBeatTheModelDataset();
  const rankings = getBeatTheModelRankings(data.season, data.week);
  const history = getArchiveAllTimeSummary();
  const status = statusCopy(data.status);
  const biggestGame = data.games[0];
  const topTeams = rankings.teams.slice(0, 5);
  const primaryHref = data.status === "awaiting-slate" ? "/about" : "/play";

  return (
    <>
      <section className="fan-challenge-hero">
        <div className="fan-challenge-copy">
          <div className="fan-live-kicker">
            <span className={`fan-status fan-status-${status.tone}`}>{status.label}</span>
            <span>{data.season} · Week {data.week}</span>
          </div>
          <span className="fan-kicker fan-challenge-kicker">BEAT THE MODEL</span>
          <h1>15 games. You pick first. Can you beat the computer?</h1>
          <p>The Model gets the exact same college football matchups you do. Pick every winner before you see its call, then let Saturday decide who knew the week better.</p>
          <div className="fan-hero-actions">
            <Link className="fan-button fan-button-primary fan-primary-challenge-cta" href={primaryHref}>{status.cta}</Link>
            <Link className="fan-button fan-button-secondary" href="/archive">See The Model’s history</Link>
          </div>
          <div className="fan-challenge-rules">
            <div><strong>01</strong><span>Pick a winner in each of the 15 biggest games.</span></div>
            <div><strong>02</strong><span>The Model stays hidden until your call is made.</span></div>
            <div><strong>03</strong><span>One point per correct winner. Better record wins.</span></div>
          </div>
        </div>

        <aside className="fan-challenge-card">
          <span className="fan-kicker">THIS WEEK’S CHALLENGE</span>
          <div className="fan-challenge-card-week"><strong>Week {data.week}</strong><span>{data.games.length || "—"}/{data.slateSize} matchups</span></div>
          <div className="fan-challenge-versus">
            <div><span>YOU</span><strong>?</strong><small>Make your calls</small></div>
            <em>VS</em>
            <div><span>THE MODEL</span><strong>M</strong><small>Same 15 games</small></div>
          </div>
          <Link href={primaryHref}>{status.cta} <span aria-hidden="true">→</span></Link>
        </aside>
      </section>

      {biggestGame ? (
        <section className="fan-section fan-section-first" aria-labelledby="biggest-game-heading">
          <div className="fan-section-heading">
            <div><span className="fan-kicker">START WITH THE BIG ONE</span><h2 id="biggest-game-heading">This week’s #1 matchup.</h2></div>
            <Link href="/play">See all {data.slateSize} games <span aria-hidden="true">→</span></Link>
          </div>
          <MatchupSpotlight game={biggestGame} />
        </section>
      ) : null}

      <section className="fan-proof-section fan-section" aria-labelledby="proof-heading">
        <div className="fan-proof-copy">
          <span className="fan-kicker">WHY TRUST THE CHALLENGE?</span>
          <h2 id="proof-heading">The Model’s misses are public too.</h2>
          <p>We keep the historical game archive and supported pregame calls on the site so fans can validate the opponent instead of trusting a headline accuracy claim.</p>
          <Link className="fan-text-link" href="/archive">Open all-time results and weekly picks <span aria-hidden="true">→</span></Link>
        </div>
        <div className="fan-proof-record">
          <div className="fan-proof-record-main"><span>ALL-TIME GRADED CALLS</span><strong>{history.modelCalls ? `${history.wins}-${history.losses}` : "—"}</strong><small>{percent(history.accuracy)} straight-up accuracy</small></div>
          <div className="fan-proof-record-grid">
            <div><strong>{history.modelCalls.toLocaleString()}</strong><span>graded picks</span></div>
            <div><strong>{history.earliestModelSeason ?? "—"}</strong><span>first supported model season</span></div>
            <div><strong>{history.firstSeason ?? "—"}</strong><span>game archive begins</span></div>
          </div>
        </div>
      </section>

      <FavoriteTeamCard rankings={rankings.teams} games={data.games} />

      <section className="fan-dashboard-grid fan-section">
        <article className="fan-feature-panel fan-rankings-panel">
          <div className="fan-section-heading fan-section-heading-tight">
            <div><span className="fan-kicker">POWER RANKINGS</span><h2>Who does the system think is strongest?</h2></div>
            <Link href="/rankings">All teams <span aria-hidden="true">→</span></Link>
          </div>
          {topTeams.length ? (
            <div className="fan-ranking-preview">
              {topTeams.map((team) => <div key={team.team}><span>#{team.rank}</span><strong>{team.team}</strong><em>{team.rating >= 0 ? "+" : ""}{team.rating.toFixed(1)}</em></div>)}
            </div>
          ) : <p className="fan-muted">The weekly rankings have not been published yet.</p>}
        </article>

        <article className="fan-feature-panel fan-model-panel">
          <span className="fan-kicker">THE RULE THAT MATTERS</span>
          <h2>The Model never chooses its opponents.</h2>
          <p>The rankings choose the weekly 15 first. Only then are The Model’s frozen predictions attached, so it cannot cherry-pick the games it likes.</p>
          <Link className="fan-text-link" href="/about">See how the challenge works <span aria-hidden="true">→</span></Link>
        </article>
      </section>

      <section className="fan-final-cta fan-section">
        <div><span className="fan-kicker">READY?</span><h2>Make the picks before you see the answers.</h2><p>Then come back Saturday and see who won the argument.</p></div>
        <Link className="fan-button fan-button-primary" href={primaryHref}>{status.cta}</Link>
      </section>
    </>
  );
}
