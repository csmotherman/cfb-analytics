"use client";

import { useMemo, useState } from "react";

import type { BeatTheModelRanking } from "../lib/beat-the-model";

function formatRating(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}`;
}

export function RankingsBrowser({ teams }: { teams: BeatTheModelRanking[] }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return teams;
    return teams.filter((team) => team.team.toLowerCase().includes(needle));
  }, [query, teams]);

  return (
    <section className="fan-rankings-browser" aria-labelledby="rankings-table-heading">
      <div className="fan-rankings-toolbar">
        <div>
          <span className="fan-kicker">ALL FBS TEAMS</span>
          <h2 id="rankings-table-heading">Weekly power rankings</h2>
        </div>
        <label className="fan-search-field">
          <span className="sr-only">Search teams</span>
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6" /><path d="m16 16 4 4" /></svg>
          <input
            type="search"
            placeholder="Search a team"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </div>

      <div className="fan-rankings-list" role="table" aria-label="Beat the Model power rankings">
        <div className="fan-ranking-head" role="row">
          <span role="columnheader">Rank</span>
          <span role="columnheader">Team</span>
          <span role="columnheader">Power</span>
        </div>
        {filtered.map((team) => (
          <div className="fan-ranking-row" role="row" key={team.team}>
            <span className="fan-ranking-number" role="cell">#{team.rank}</span>
            <span className="fan-ranking-team" role="cell">
              <strong>{team.team}</strong>
              {typeof team.gamesBefore === "number" ? <small>{team.gamesBefore} game{team.gamesBefore === 1 ? "" : "s"} of current-season data</small> : null}
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
