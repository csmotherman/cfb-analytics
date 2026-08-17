"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type { BeatTheModelGame, BeatTheModelRanking } from "../lib/beat-the-model";

const STORAGE_KEY = "beat-the-model:favorite-team";

function formatRating(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}`;
}

export function FavoriteTeamCard({
  rankings,
  games,
}: {
  rankings: BeatTheModelRanking[];
  games: BeatTheModelGame[];
}) {
  const [team, setTeam] = useState("");
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved) setTeam(saved);
    } catch {
      // Personalization is optional; the rest of the site works without storage.
    }
  }, []);

  const ranking = useMemo(
    () => rankings.find((entry) => entry.team === team) ?? null,
    [rankings, team],
  );
  const game = useMemo(
    () => games.find((entry) => entry.homeTeam === team || entry.awayTeam === team) ?? null,
    [games, team],
  );

  function save(value: string) {
    setTeam(value);
    setEditing(false);
    try {
      if (value) window.localStorage.setItem(STORAGE_KEY, value);
      else window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Keep the in-memory preference if storage is unavailable.
    }
  }

  if (!rankings.length) return null;

  return (
    <article className="fan-personal-card">
      <div className="fan-personal-copy">
        <span className="fan-kicker">MY TEAM</span>
        {!ranking ? (
          <>
            <h2>Make the board yours.</h2>
            <p>Choose your team once. We’ll keep its rank and weekly matchup easy to find on this device.</p>
          </>
        ) : (
          <>
            <div className="fan-my-team-title">
              <span>#{ranking.rank}</span>
              <h2>{ranking.team}</h2>
            </div>
            <p>
              Power rating <strong>{formatRating(ranking.rating)}</strong>
              {game ? ` · In the Official ${games.length} this week.` : " · Not on this week’s card."}
            </p>
          </>
        )}
      </div>

      {editing || !ranking ? (
        <div className="fan-team-picker">
          <label htmlFor="favorite-team">Favorite team</label>
          <select
            id="favorite-team"
            value={team}
            onChange={(event) => save(event.target.value)}
          >
            <option value="">Choose a team</option>
            {rankings.map((entry) => (
              <option key={entry.team} value={entry.team}>#{entry.rank} {entry.team}</option>
            ))}
          </select>
        </div>
      ) : (
        <div className="fan-personal-actions">
          {game ? <Link href="/play">Go to matchup <span aria-hidden="true">→</span></Link> : null}
          <button type="button" onClick={() => setEditing(true)}>Change team</button>
        </div>
      )}
    </article>
  );
}
