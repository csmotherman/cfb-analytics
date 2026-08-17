"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type { BeatTheModelGame, BeatTheModelRanking } from "../lib/beat-the-model";
import { TeamLogo } from "./TeamLogo";

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
  const [draftTeam, setDraftTeam] = useState("");
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setTeam(saved);
        setDraftTeam(saved);
      }
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

  function beginEditing() {
    setDraftTeam(team);
    setEditing(true);
  }

  function save() {
    if (!draftTeam) return;
    setTeam(draftTeam);
    setEditing(false);
    try {
      window.localStorage.setItem(STORAGE_KEY, draftTeam);
    } catch {
      // Keep the in-memory preference if storage is unavailable.
    }
  }

  function cancel() {
    setDraftTeam(team);
    setEditing(false);
  }

  if (!rankings.length) return null;

  return (
    <article className="fan-personal-card">
      <div className="fan-personal-copy">
        <span className="fan-kicker">MY TEAM</span>
        {!ranking ? (
          <>
            <h2>Make the board yours.</h2>
            <p>Choose your team, review it, then save. We’ll keep its rank and weekly matchup easy to find on this device.</p>
          </>
        ) : (
          <>
            <div className="fan-my-team-title fan-my-team-title-logo">
              <TeamLogo team={ranking.team} src={ranking.logo} size="lg" />
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
        <div className="fan-team-picker fan-team-picker-confirm">
          <label htmlFor="favorite-team">Favorite team</label>
          <select
            id="favorite-team"
            value={draftTeam}
            onChange={(event) => setDraftTeam(event.target.value)}
          >
            <option value="">Choose a team</option>
            {rankings.map((entry) => (
              <option key={entry.team} value={entry.team}>#{entry.rank} {entry.team}</option>
            ))}
          </select>
          <div className="fan-team-picker-actions">
            <button type="button" className="fan-button fan-button-primary" disabled={!draftTeam} onClick={save}>Save team</button>
            {ranking ? <button type="button" className="fan-button fan-button-secondary" onClick={cancel}>Cancel</button> : null}
          </div>
        </div>
      ) : (
        <div className="fan-personal-actions">
          {game ? <Link href="/play">Go to matchup <span aria-hidden="true">→</span></Link> : null}
          <button type="button" onClick={beginEditing}>Change team</button>
        </div>
      )}
    </article>
  );
}
