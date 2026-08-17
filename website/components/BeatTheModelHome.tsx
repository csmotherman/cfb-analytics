import Link from "next/link";

import { FavoriteTeamCard } from "./FavoriteTeamCard";
import {
  formatKickoff,
  getBeatTheModelDataset,
  getBeatTheModelRankings,
  modelRecord,
} from "../lib/beat-the-model";

function statusCopy(status: string, modelReady?: boolean) {
  if (status === "open") {
    return {
      label: "Picks open",
      tone: "mint",
      headline: "Your Week is ready.",
      detail: "Make all 15 picks before kickoff. The Model is revealed one game at a time after you choose.",
      cta: "Make my picks",
    };
  }
  if (status === "locked") {
    return {
      label: "Games underway",
      tone: "cyan",
      headline: "Saturday is live.",
      detail: "The card is locked. Follow the scoreboard and see whether your picks can hold off The Model.",
      cta: "Follow my card",
    };
  }
  if (status === "final") {
    return {
      label: "Week final",
      tone: "mint",
      headline: "The receipts are in.",
      detail: "See the final card, compare your score with The Model, then get ready for the next board.",
      cta: "See my results",
    };
  }
  if (status === "awaiting-model" || !modelReady) {
    return {
      label: "Official 15 set",
      tone: "amber",
      headline: "The matchups are here.",
      detail: "Browse the Week 1 card now. Picking opens as soon as the frozen pregame model snapshot is attached.",
      cta: "Preview the Official 15",
    };
  }
  return {
    label: "Building the week",
    tone: "steel",
    headline: "The next card is coming.",
    detail: "The weekly scheduler will rank the slate and publish the biggest matchups automatically.",
    cta: "See how it works",
  };
}

function MatchupSpotlight({
  game,
}: {
  game: ReturnType<typeof getBeatTheModelDataset>["games"][number];
}) {
  return (
    <article className="fan-spotlight-card">
      <header>
        <div>
          <span className="fan-kicker">#1 MATCHUP THIS WEEK</span>
          <strong>Official 15 · Game {game.slot}</strong>
        </div>
        <span>{formatKickoff(game.kickoff) ?? "Kickoff TBA"}</span>
      </header>

      <div className="fan-spotlight-matchup">
        <div>
          <span>#{game.awayRank}</span>
          <strong>{game.awayTeam}</strong>
          <small>Away</small>
        </div>
        <em>AT</em>
        <div>
          <span>#{game.homeRank}</span>
          <strong>{game.homeTeam}</strong>
          <small>Home</small>
        </div>
      </div>

      <footer>
        <div>
          <span>THE MODEL</span>
          <strong>{game.modelWinner ? "Hidden until you pick" : "Pregame call locking"}</strong>
        </div>
        <Link href="/play">Go to the matchup <span aria-hidden="true">→</span></Link>
      </footer>
    </article>
  );
}

export function BeatTheModelHome() {
  const data = getBeatTheModelDataset();
  const rankings = getBeatTheModelRankings(data.season, data.week);
  const record = modelRecord(data.games);
  const status = statusCopy(data.status, data.modelReady);
  const biggestGame = data.games[0];
  const previewGames = data.games.slice(1, 5);
  const topTeams = rankings.teams.slice(0, 5);
  const primaryHref = data.status === "awaiting-slate" ? "/about" : "/play";

  return (
    <>
      <section className="fan-home-hero">
        <div className="fan-hero-copy">
          <div className="fan-live-kicker">
            <span className={`fan-status fan-status-${status.tone}`}>{status.label}</span>
            <span>{data.season} · Week {data.week}</span>
          </div>
          <h1>Think you know college football?</h1>
          <p className="fan-hero-lead">
            Pick the winners of the week’s biggest games. Then see whether your football instincts can beat a model playing the exact same card.
          </p>

          <div className="fan-hero-actions">
            <Link className="fan-button fan-button-primary" href={primaryHref}>{status.cta}</Link>
            <Link className="fan-button fan-button-secondary" href="/rankings">See all power rankings</Link>
          </div>

          <div className="fan-hero-proof" aria-label="Beat the Model rules">
            <span><strong>{data.slateSize}</strong> biggest games</span>
            <span><strong>1</strong> point per correct winner</span>
            <span><strong>You</strong> pick before The Model</span>
          </div>
        </div>

        <aside className="fan-command-card" aria-label={`Current challenge: ${data.season} Week ${data.week}`}>
          <div className="fan-command-card-head">
            <span className="fan-kicker">CURRENT CHALLENGE</span>
            <span className={`fan-status fan-status-${status.tone}`}>{status.label}</span>
          </div>
          <h2>{status.headline}</h2>
          <p>{status.detail}</p>

          <div className="fan-command-numbers">
            <div><strong>{data.games.length || "—"}</strong><span>matchups</span></div>
            <div><strong>{rankings.teams.length || "—"}</strong><span>teams ranked</span></div>
            <div><strong>{record.games ? `${record.wins}-${record.losses}` : "—"}</strong><span>model this week</span></div>
          </div>

          <Link href={primaryHref} className="fan-command-link">{status.cta} <span aria-hidden="true">→</span></Link>
        </aside>
      </section>

      {biggestGame ? (
        <section className="fan-section fan-section-first" aria-labelledby="biggest-game-heading">
          <div className="fan-section-heading">
            <div>
              <span className="fan-kicker">START HERE</span>
              <h2 id="biggest-game-heading">The biggest game on the card.</h2>
            </div>
            <Link href="/play">See all {data.slateSize} <span aria-hidden="true">→</span></Link>
          </div>
          <MatchupSpotlight game={biggestGame} />
        </section>
      ) : null}

      <section className="fan-section" aria-labelledby="why-heading">
        <div className="fan-section-heading">
          <div>
            <span className="fan-kicker">THE GAME</span>
            <h2 id="why-heading">One simple argument every week.</h2>
          </div>
          <Link href="/about">Why it’s fair <span aria-hidden="true">→</span></Link>
        </div>

        <div className="fan-value-grid">
          <article>
            <span className="fan-value-number">01</span>
            <h3>Make your call</h3>
            <p>No spreads. No confidence points. Pick the team you think wins.</p>
          </article>
          <article>
            <span className="fan-value-number">02</span>
            <h3>Face The Model</h3>
            <p>The Model’s pick stays hidden until your pick is made, then the disagreement is yours to defend.</p>
          </article>
          <article>
            <span className="fan-value-number">03</span>
            <h3>Keep the receipts</h3>
            <p>The original calls and final results stay in the archive. Nobody gets to rewrite Saturday.</p>
          </article>
        </div>
      </section>

      <FavoriteTeamCard rankings={rankings.teams} games={data.games} />

      <section className="fan-dashboard-grid fan-section">
        <article className="fan-feature-panel fan-rankings-panel">
          <div className="fan-section-heading fan-section-heading-tight">
            <div>
              <span className="fan-kicker">POWER RANKINGS</span>
              <h2>The board that picks the games.</h2>
            </div>
            <Link href="/rankings">All teams <span aria-hidden="true">→</span></Link>
          </div>
          {topTeams.length ? (
            <div className="fan-ranking-preview">
              {topTeams.map((team) => (
                <div key={team.team}>
                  <span>#{team.rank}</span>
                  <strong>{team.team}</strong>
                  <em>{team.rating >= 0 ? "+" : ""}{team.rating.toFixed(1)}</em>
                </div>
              ))}
            </div>
          ) : <p className="fan-muted">The weekly rankings have not been published yet.</p>}
        </article>

        <article className="fan-feature-panel fan-model-panel">
          <div className="fan-model-badge">M</div>
          <span className="fan-kicker">THE OPPONENT</span>
          <h2>The Model has nowhere to hide.</h2>
          <p>It plays the same Official 15 as every fan. Its pregame calls are frozen, scored straight up, and kept public after the final whistle.</p>
          <Link className="fan-text-link" href="/archive">Check the receipts <span aria-hidden="true">→</span></Link>
        </article>
      </section>

      {previewGames.length ? (
        <section className="fan-section" aria-labelledby="more-games-heading">
          <div className="fan-section-heading">
            <div>
              <span className="fan-kicker">ALSO ON THE CARD</span>
              <h2 id="more-games-heading">More games worth arguing about.</h2>
            </div>
          </div>
          <div className="fan-slate-preview">
            {previewGames.map((game) => (
              <Link key={game.id} href="/play" className="fan-matchup-row">
                <span className="fan-matchup-number">{game.slot}</span>
                <div className="fan-matchup-teams">
                  <div><span>#{game.awayRank}</span><strong>{game.awayTeam}</strong></div>
                  <small>at</small>
                  <div><span>#{game.homeRank}</span><strong>{game.homeTeam}</strong></div>
                </div>
                <span className="fan-matchup-time">{formatKickoff(game.kickoff) ?? "TBA"}</span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <section className="fan-final-cta fan-section">
        <div>
          <span className="fan-kicker">YOUR TURN</span>
          <h2>Don’t tell us you know ball. Put a card on it.</h2>
          <p>The same games. The same scoring. You against The Model.</p>
        </div>
        <Link className="fan-button fan-button-primary" href={primaryHref}>{status.cta}</Link>
      </section>
    </>
  );
}
