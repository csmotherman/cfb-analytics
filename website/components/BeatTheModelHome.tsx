import Link from "next/link";

import {
  formatKickoff,
  getBeatTheModelDataset,
  getBeatTheModelRankings,
  modelRecord,
} from "../lib/beat-the-model";

function statusCopy(status: string): { label: string; tone: string; detail: string } {
  if (status === "open") {
    return { label: "Picks are open", tone: "mint", detail: "Make your picks before each game kicks off." };
  }
  if (status === "final") {
    return { label: "Week complete", tone: "mint", detail: "See how you and The Model finished." };
  }
  if (status === "awaiting-model") {
    return { label: "Slate is set", tone: "amber", detail: "The Official 15 is published. Picks open when the pregame model snapshot is ready." };
  }
  return { label: "Week is loading", tone: "steel", detail: "The weekly slate will appear here as soon as it is published." };
}

export function BeatTheModelHome() {
  const data = getBeatTheModelDataset();
  const rankings = getBeatTheModelRankings(data.season, data.week);
  const record = modelRecord(data.games);
  const status = statusCopy(data.status);
  const previewGames = data.games.slice(0, 4);
  const topTeams = rankings.teams.slice(0, 5);

  return (
    <>
      <section className="fan-home-hero">
        <div className="fan-hero-copy">
          <span className="fan-kicker">THE WEEKLY COLLEGE FOOTBALL PICK CHALLENGE</span>
          <h1>Think you know college football?</h1>
          <p className="fan-hero-lead">Pick the biggest games of the week, lock in your calls, and see whether you can beat a model that has to play the exact same card.</p>

          <div className="fan-hero-actions">
            <Link className="fan-button fan-button-primary" href="/play">Make my picks</Link>
            <Link className="fan-button fan-button-secondary" href="/rankings">View rankings</Link>
          </div>

          <div className="fan-hero-proof" aria-label="Game rules">
            <span><strong>{data.slateSize}</strong> games</span>
            <span><strong>1</strong> point per winner</span>
            <span><strong>0</strong> spreads or odds</span>
          </div>
        </div>

        <aside className="fan-week-card" aria-label={`Current Beat the Model week: ${data.season} Week ${data.week}`}>
          <div className="fan-week-card-top">
            <div>
              <span className="fan-card-label">THIS WEEK</span>
              <h2>{data.season} Week {data.week}</h2>
            </div>
            <span className={`fan-status fan-status-${status.tone}`}>{status.label}</span>
          </div>

          <div className="fan-week-count">
            <strong>{data.games.length || "—"}</strong>
            <span>of {data.slateSize} matchups published</span>
          </div>

          <p>{status.detail}</p>

          <div className="fan-week-stats">
            <div><span>The Model</span><strong>{record.games ? `${record.wins}-${record.losses}` : "—"}</strong></div>
            <div><span>Power rankings</span><strong>{rankings.teams.length || "—"}</strong></div>
          </div>

          <Link className="fan-week-link" href="/play">Go to this week <span aria-hidden="true">→</span></Link>
        </aside>
      </section>

      <section className="fan-section" aria-labelledby="how-heading">
        <div className="fan-section-heading">
          <div>
            <span className="fan-kicker">HOW TO PLAY</span>
            <h2 id="how-heading">Three steps. No clutter.</h2>
          </div>
          <Link href="/about">How the system works <span aria-hidden="true">→</span></Link>
        </div>

        <div className="fan-step-grid">
          <article>
            <span>1</span>
            <div><strong>Pick a winner</strong><p>Choose one team in each Official 15 matchup.</p></div>
          </article>
          <article>
            <span>2</span>
            <div><strong>Reveal The Model</strong><p>Your choice comes first. The Model stays hidden until you pick.</p></div>
          </article>
          <article>
            <span>3</span>
            <div><strong>Count the wins</strong><p>Correct winner equals one point. Better record wins the week.</p></div>
          </article>
        </div>
      </section>

      <section className="fan-section" aria-labelledby="slate-heading">
        <div className="fan-section-heading">
          <div>
            <span className="fan-kicker">OFFICIAL SLATE</span>
            <h2 id="slate-heading">This week's card</h2>
          </div>
          <Link href="/play">See all {data.slateSize} games <span aria-hidden="true">→</span></Link>
        </div>

        {previewGames.length ? (
          <div className="fan-slate-preview">
            {previewGames.map((game) => (
              <article key={game.id} className="fan-matchup-row">
                <div className="fan-matchup-number">{game.slot}</div>
                <div className="fan-matchup-teams">
                  <div><span>#{game.awayRank}</span><strong>{game.awayTeam}</strong></div>
                  <small>at</small>
                  <div><span>#{game.homeRank}</span><strong>{game.homeTeam}</strong></div>
                </div>
                <div className="fan-matchup-time">{formatKickoff(game.kickoff) ?? "TBA"}</div>
              </article>
            ))}
          </div>
        ) : (
          <div className="fan-empty-state">
            <span className="fan-status fan-status-steel">Not published yet</span>
            <h3>The weekly card is on the way.</h3>
            <p>Once the schedule is published, the 15 strongest ranked matchups will appear here automatically.</p>
          </div>
        )}
      </section>

      <section className="fan-two-column fan-section">
        <article className="fan-feature-panel">
          <div className="fan-section-heading fan-section-heading-tight">
            <div>
              <span className="fan-kicker">POWER RANKINGS</span>
              <h2>Who's strongest right now?</h2>
            </div>
            <Link href="/rankings">Full rankings <span aria-hidden="true">→</span></Link>
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
          ) : (
            <p className="fan-muted">Rankings will appear when the weekly data is published.</p>
          )}
        </article>

        <article className="fan-feature-panel fan-receipts-panel">
          <span className="fan-kicker">THE RECEIPTS</span>
          <h2>The Model's picks stay public.</h2>
          <p>Every official slate, every model call, and every result stays in the archive. Good week or bad week, nothing gets rewritten after kickoff.</p>
          <Link className="fan-text-link" href="/archive">Browse the archive <span aria-hidden="true">→</span></Link>
        </article>
      </section>
    </>
  );
}
