"use client";

import { useMemo, useState } from "react";

import type { BeatTheModelRanking } from "../lib/beat-the-model";

type RankingView = "top25" | "all";

function formatRating(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}`;
}

export function RankingsBrowser({ teams }: { teams: BeatTheModelRanking[] }) {
  const [query, setQuery] = useState("");
  const [view, setView] = useState<RankingView>("top25");
  const leaders = teams.slice(0, 5);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (needle) return teams.filter((team) => team.team.toLowerCase().includes(needle));
    return view === "top25" ? teams.slice(0, 25) : teams;
  }, [query, teams, view]);

  return (
    <section className="fan-rankings-browser" aria-labelledby="rankings-table-heading">
      <div className="fan-ranking-leaders" aria-label="Top five power rankings">
        {leaders.map((team, index) => (
          <article key={team.team} className={index === 0 ? "leader" : ""}>
            <span>#{team.rank}</span>
            <strong>{team.team}</strong>
            <small>{formatRating(team.rating)} power</small>
          </article>
        ))}
      </div>

      <div className="fan-rankings-toolbar">
        <div>
          <span className="fan-kicker">FULL BOARD</span>
          <h2 id="rankings-table-heading">Every FBS team. One board.</h2>
        </div>
        <label className="fan-search-field">
          <span className="sr-only">Search teams</span>
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6" /><path d="m16 16 4 4" /></svg>
          <input
            type="search"
            placeholder="Find your team"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </div>

      {!query ? (
        <div className="fan-ranking-tabs" role="tablist" aria-label="Ranking range">
          <button type="button" className={view === "top25" ? "active" : ""} onClick={() => setView("top25")}>Top 25</button>
          <button type="button" className={view === "all" ? "active" : ""} onClick={() => setView("all")}>All {teams.length}</button>
        </div>
      ) : null}

      <div className="fan-rankings-list" role="table" aria-label="Beat the Model power rankings">
        <div className="fan-ranking-head" role="row">
          <span role="columnheader">Rank</span>
          <span role="columnheader">Team</span>
          <span role="columnheader">Power</span>
        </div>
        {filtered.map((team) => (
          <div className={`fan-ranking-row${team.rank <= 25 ? " top25" : ""}`} role="row" key={team.team}>
            <span className="fan-ranking-number" role="cell">#{team.rank}</span>
            <span className="fan-ranking-team" role="cell">
              <strong>{team.team}</strong>
              {typeof team.gamesBefore === "number" ? (
                <small>{team.gamesBefore === 0 ? "Previous-season carryover" : `${team.gamesBefore} current-season game${team.gamesBefore === 1 ? "" : "s"}`}</small>
              ) : null}
            </span>
            <span className="fan-ranking-rating" role="cell">{formatRating(team.rating)}</span>
          </div>
        ))}
      </div>

      {!filtered.length ? (
        <div className="fan-search-empty">No teams match “{query}”.</div>
      ) : null}
    </section>
  );
}
