"use client";

import { useEffect, useMemo, useState } from "react";

import type { BeatTheModelDataset, BeatTheModelGame } from "../lib/beat-the-model";
import { formatKickoff } from "../lib/beat-the-model";

type Picks = Record<string, string>;

function storageKey(data: BeatTheModelDataset): string {
  return `beat-the-model:picks:${data.season}:${data.week}`;
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
  onPick,
}: {
  game: BeatTheModelGame;
  team: string;
  rank: number;
  picked: boolean;
  disabled: boolean;
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
      <span>{picked ? "Your pick" : "Pick"}</span>
    </button>
  );
}

function GameCard({ game, pick, onPick }: { game: BeatTheModelGame; pick?: string; onPick: (team: string) => void }) {
  const locked = isLocked(game);
  const revealed = Boolean(pick) || locked || game.status === "final";
  const winner = actualWinner(game);
  const kickoff = formatKickoff(game.kickoff);
  const userCorrect = pick && winner ? pick === winner : null;
  const modelCorrect = winner ? game.modelWinner === winner : null;

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
          disabled={locked}
          onPick={() => onPick(game.awayTeam)}
        />
        <div className="btm-versus">VS</div>
        <PickButton
          game={game}
          team={game.homeTeam}
          rank={game.homeRank}
          picked={pick === game.homeTeam}
          disabled={locked}
          onPick={() => onPick(game.homeTeam)}
        />
      </div>

      <div className={`btm-model-reveal${revealed ? " revealed" : ""}`}>
        {revealed ? (
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
    if (isLocked(game)) return;
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
  const modelWins = finalGames.filter((game) => actualWinner(game) === game.modelWinner).length;

  if (!data.games.length) {
    return (
      <section className="btm-awaiting">
        <div>
          <span className="eyebrow">2026 WEEK {data.week}</span>
          <h2>The Official 15 has not been published yet.</h2>
          <p>Week 1 team rankings are seeded from the final 2025 power ratings. Once the live Week 1 schedule and frozen model predictions are published, the 15 highest-rated eligible matchups will appear here automatically.</p>
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
          <h2 id="official-slate-heading">2026 Week {data.week}</h2>
          <p>Make your choice first. The Model's pick is revealed only after yours.</p>
        </div>
        <div className="btm-progress-card">
          <span>Your card</span>
          <strong>{hydrated ? `${pickedCount}/${data.games.length}` : "—"}</strong>
          <small>picks made</small>
        </div>
      </div>

      {finalGames.length ? (
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
