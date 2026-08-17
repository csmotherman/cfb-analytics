"use client";

import { useEffect, useMemo, useState } from "react";

import type { BeatTheModelDataset, BeatTheModelGame } from "../lib/beat-the-model";

type Picks = Record<string, string>;

function storageKey(data: BeatTheModelDataset): string {
  return `beat-the-model:picks:${data.season}:${data.week}`;
}

function formatKickoff(value: string | null | undefined): string | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function actualWinner(game: BeatTheModelGame): string | null {
  if (typeof game.actualHomeScore !== "number" || typeof game.actualAwayScore !== "number") return null;
  if (game.actualHomeScore === game.actualAwayScore) return null;
  return game.actualHomeScore > game.actualAwayScore ? game.homeTeam : game.awayTeam;
}

function isLocked(game: BeatTheModelGame): boolean {
  if (game.status === "final") return true;
  if (!game.kickoff) return false;
  const kickoff = new Date(game.kickoff).getTime();
  return Number.isFinite(kickoff) && Date.now() >= kickoff;
}

function PickButton({
  game,
  team,
  rank,
  picked,
  disabled,
  modelPending,
  onPick,
}: {
  game: BeatTheModelGame;
  team: string;
  rank: number;
  picked: boolean;
  disabled: boolean;
  modelPending: boolean;
  onPick: () => void;
}) {
  return (
    <button
      type="button"
      className={`btm-pick-option${picked ? " selected" : ""}`}
      disabled={disabled}
      onClick={onPick}
      aria-pressed={picked}
      aria-label={`Pick number ${rank} ${team} in ${game.awayTeam} at ${game.homeTeam}`}
    >
      <span className="btm-rank-chip">#{rank}</span>
      <strong>{team}</strong>
      <span>{picked ? "Your pick" : modelPending ? "Soon" : "Pick"}</span>
    </button>
  );
}

function GameCard({ game, pick, onPick }: { game: BeatTheModelGame; pick?: string; onPick: (team: string) => void }) {
  const locked = isLocked(game);
  const modelAvailable = Boolean(game.modelWinner);
  const revealed = modelAvailable && (Boolean(pick) || locked || game.status === "final");
  const winner = actualWinner(game);
  const kickoff = formatKickoff(game.kickoff);
  const userCorrect = pick && winner ? pick === winner : null;
  const modelCorrect = winner && game.modelWinner ? game.modelWinner === winner : null;

  return (
    <article className={`btm-game-card${game.status === "final" ? " final" : ""}`}>
      <div className="btm-game-topline">
        <span>Game {game.slot}</span>
        <span>{kickoff ?? "Kickoff TBA"}</span>
      </div>

      {game.status === "final" && typeof game.actualHomeScore === "number" && typeof game.actualAwayScore === "number" ? (
        <div className="btm-final-score" aria-label={`${game.awayTeam} ${game.actualAwayScore}, ${game.homeTeam} ${game.actualHomeScore}`}>
          <span>FINAL</span>
          <strong>{game.awayTeam} {game.actualAwayScore}</strong>
          <span>—</span>
          <strong>{game.homeTeam} {game.actualHomeScore}</strong>
        </div>
      ) : null}

      <div className="btm-pick-grid">
        <PickButton
          game={game}
          team={game.awayTeam}
          rank={game.awayRank}
          picked={pick === game.awayTeam}
          disabled={locked || !modelAvailable}
          modelPending={!modelAvailable}
          onPick={() => onPick(game.awayTeam)}
        />
        <div className="btm-versus">VS</div>
        <PickButton
          game={game}
          team={game.homeTeam}
          rank={game.homeRank}
          picked={pick === game.homeTeam}
          disabled={locked || !modelAvailable}
          modelPending={!modelAvailable}
          onPick={() => onPick(game.homeTeam)}
        />
      </div>

      <div className={`btm-model-reveal${revealed ? " revealed" : ""}`}>
        {!modelAvailable ? (
          <>
            <div>
              <span>THE MODEL</span>
              <strong>Pregame snapshot pending</strong>
            </div>
            <div className="btm-model-lock" aria-hidden="true">NOT OPEN</div>
          </>
        ) : revealed ? (
          <>
            <div>
              <span>THE MODEL</span>
              <strong>#{game.modelWinner === game.homeTeam ? game.homeRank : game.awayRank} {game.modelWinner}</strong>
            </div>
            {pick ? (
              <div className={`btm-agreement ${pick === game.modelWinner ? "agree" : "disagree"}`}>
                {pick === game.modelWinner ? "You agree" : "You disagree"}
              </div>
            ) : (
              <div className="btm-agreement locked">Pick locked</div>
            )}
            {game.status === "final" ? (
              <div className="btm-result-pair">
                <span className={userCorrect === true ? "correct" : userCorrect === false ? "wrong" : ""}>
                  You {userCorrect === true ? "✓" : userCorrect === false ? "×" : "—"}
                </span>
                <span className={modelCorrect === true ? "correct" : modelCorrect === false ? "wrong" : ""}>
                  Model {modelCorrect === true ? "✓" : modelCorrect === false ? "×" : "—"}
                </span>
              </div>
            ) : null}
          </>
        ) : (
          <>
            <div>
              <span>THE MODEL</span>
              <strong>Hidden until you pick</strong>
            </div>
            <div className="btm-model-lock" aria-hidden="true">LOCKED</div>
          </>
        )}
      </div>
    </article>
  );
}

export function BeatTheModelGameView({ data }: { data: BeatTheModelDataset }) {
  const [picks, setPicks] = useState<Picks>({});
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(storageKey(data));
      if (saved) {
        const parsed = JSON.parse(saved) as Picks;
        if (parsed && typeof parsed === "object") setPicks(parsed);
      }
    } catch {
      // Browser storage is optional; the game still works for the current page view.
    }
    setHydrated(true);
  }, [data.season, data.week]);

  function choose(game: BeatTheModelGame, team: string) {
    if (isLocked(game) || !game.modelWinner) return;
    setPicks((current) => {
      const next = { ...current, [game.id]: team };
      try {
        window.localStorage.setItem(storageKey(data), JSON.stringify(next));
      } catch {
        // Ignore storage failures and keep the in-memory pick.
      }
      return next;
    });
  }

  const pickedCount = useMemo(
    () => data.games.filter((game) => Boolean(picks[game.id])).length,
    [data.games, picks],
  );
  const finalGames = data.games.filter((game) => game.status === "final");
  const userWins = finalGames.filter((game) => {
    const winner = actualWinner(game);
    return winner && picks[game.id] === winner;
  }).length;
  const modelFinalGames = finalGames.filter((game) => Boolean(game.modelWinner));
  const modelWins = modelFinalGames.filter((game) => actualWinner(game) === game.modelWinner).length;

  if (!data.games.length) {
    return (
      <section className="btm-awaiting">
        <div>
          <span className="eyebrow">{data.season} WEEK {data.week}</span>
          <h2>The Official 15 has not been published yet.</h2>
          <p>Week 1 team rankings are seeded from the final {data.season - 1} power ratings. The weekly scheduler pulls the live FBS schedule and automatically selects the 15 strongest ranked matchups.</p>
        </div>
        <div className="btm-awaiting-rules">
          <span>15 games</span>
          <span>1 point per winner</span>
          <span>Model hidden until you pick</span>
          <span>No spreads. No odds.</span>
        </div>
      </section>
    );
  }

  return (
    <section className="btm-play-area" aria-labelledby="official-slate-heading">
      <div className="btm-slate-header">
        <div>
          <span className="eyebrow">OFFICIAL {data.slateSize}</span>
          <h2 id="official-slate-heading">{data.season} Week {data.week}</h2>
          <p>{data.status === "awaiting-model"
            ? "The matchups are selected. Picking opens after The Model's frozen pregame snapshot is attached."
            : "Make your choice first. The Model's pick is revealed only after yours."}</p>
        </div>
        <div className="btm-progress-card">
          <span>{data.status === "awaiting-model" ? "Slate" : "Your card"}</span>
          <strong>{data.status === "awaiting-model" ? `${data.games.length}/${data.slateSize}` : hydrated ? `${pickedCount}/${data.games.length}` : "—"}</strong>
          <small>{data.status === "awaiting-model" ? "games selected" : "picks made"}</small>
        </div>
      </div>

      {data.status === "awaiting-model" ? (
        <div className="btm-scoreboard btm-model-pending-banner">
          <div><span>Matchups</span><strong>SET</strong></div>
          <div className="btm-scoreboard-vs">→</div>
          <div><span>Picking</span><strong>SOON</strong></div>
        </div>
      ) : finalGames.length ? (
        <div className="btm-scoreboard">
          <div><span>You</span><strong>{userWins}</strong></div>
          <div className="btm-scoreboard-vs">VS</div>
          <div><span>The Model</span><strong>{modelWins}</strong></div>
        </div>
      ) : null}

      <div className="btm-game-list">
        {data.games.map((game) => (
          <GameCard
            key={game.id}
            game={game}
            pick={picks[game.id]}
            onPick={(team) => choose(game, team)}
          />
        ))}
      </div>
    </section>
  );
}
