"use client";

import { useEffect, useMemo, useState } from "react";

import { formatKickoff, type BeatTheModelDataset, type BeatTheModelGame } from "../lib/beat-the-model";

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
  side,
  picked,
  disabled,
  modelPending,
  onPick,
}: {
  game: BeatTheModelGame;
  team: string;
  rank: number;
  side: "Away" | "Home";
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
      <span className="btm-team-copy">
        <strong>{team}</strong>
        <small>{side}</small>
      </span>
      <span className="btm-pick-action">{picked ? "✓ Picked" : modelPending ? "Waiting" : "Pick"}</span>
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
    <article className={`btm-game-card${game.status === "final" ? " final" : ""}${pick ? " has-pick" : ""}`}>
      <header className="btm-game-topline">
        <span>Game {game.slot}</span>
        <span>{game.status === "final" ? "Final" : kickoff ?? "Kickoff TBA"}</span>
      </header>

      {game.status === "final" && typeof game.actualHomeScore === "number" && typeof game.actualAwayScore === "number" ? (
        <div className="btm-final-score" aria-label={`${game.awayTeam} ${game.actualAwayScore}, ${game.homeTeam} ${game.actualHomeScore}`}>
          <span className={winner === game.awayTeam ? "winner" : ""}>{game.awayTeam} <strong>{game.actualAwayScore}</strong></span>
          <em>FINAL</em>
          <span className={winner === game.homeTeam ? "winner" : ""}>{game.homeTeam} <strong>{game.actualHomeScore}</strong></span>
        </div>
      ) : null}

      <div className="btm-pick-grid">
        <PickButton
          game={game}
          team={game.awayTeam}
          rank={game.awayRank}
          side="Away"
          picked={pick === game.awayTeam}
          disabled={locked || !modelAvailable}
          modelPending={!modelAvailable}
          onPick={() => onPick(game.awayTeam)}
        />
        <div className="btm-versus" aria-hidden="true">AT</div>
        <PickButton
          game={game}
          team={game.homeTeam}
          rank={game.homeRank}
          side="Home"
          picked={pick === game.homeTeam}
          disabled={locked || !modelAvailable}
          modelPending={!modelAvailable}
          onPick={() => onPick(game.homeTeam)}
        />
      </div>

      <div className={`btm-model-reveal${revealed ? " revealed" : ""}`}>
        {!modelAvailable ? (
          <>
            <div className="btm-model-copy">
              <span>THE MODEL</span>
              <strong>Pregame pick pending</strong>
              <small>The matchup is set, but picking has not opened yet.</small>
            </div>
            <span className="btm-model-state">Coming soon</span>
          </>
        ) : revealed ? (
          <>
            <div className="btm-model-copy">
              <span>THE MODEL PICKED</span>
              <strong>#{game.modelWinner === game.homeTeam ? game.homeRank : game.awayRank} {game.modelWinner}</strong>
              {pick ? <small>{pick === game.modelWinner ? "Same pick as you" : "Different from your pick"}</small> : <small>Revealed after lock</small>}
            </div>
            {game.status === "final" ? (
              <div className="btm-result-pair">
                <span className={userCorrect === true ? "correct" : userCorrect === false ? "wrong" : ""}>
                  You {userCorrect === true ? "✓" : userCorrect === false ? "×" : "—"}
                </span>
                <span className={modelCorrect === true ? "correct" : modelCorrect === false ? "wrong" : ""}>
                  Model {modelCorrect === true ? "✓" : modelCorrect === false ? "×" : "—"}
                </span>
              </div>
            ) : (
              <span className={`btm-agreement ${pick === game.modelWinner ? "agree" : "disagree"}`}>
                {pick === game.modelWinner ? "You agree" : "You disagree"}
              </span>
            )}
          </>
        ) : (
          <>
            <div className="btm-model-copy">
              <span>THE MODEL</span>
              <strong>Hidden until you pick</strong>
              <small>Make your call without seeing the answer first.</small>
            </div>
            <span className="btm-model-state">Locked</span>
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
  const progress = data.games.length ? Math.round((pickedCount / data.games.length) * 100) : 0;
  const cardComplete = data.games.length > 0 && pickedCount === data.games.length;

  if (!data.games.length) {
    return (
      <section className="fan-empty-state btm-empty-week">
        <span className="fan-status fan-status-steel">{data.season} Week {data.week}</span>
        <h2>The Official {data.slateSize} is not published yet.</h2>
        <p>The weekly scheduler selects the strongest ranked FBS matchups. As soon as the card is ready, every game will appear here.</p>
        <div className="fan-rule-row">
          <span>{data.slateSize} games</span>
          <span>1 point each</span>
          <span>Model hidden first</span>
        </div>
      </section>
    );
  }

  return (
    <section className="btm-play-area" aria-labelledby="official-slate-heading">
      <div className="btm-play-toolbar">
        <div className="btm-play-toolbar-copy">
          <span className={`fan-status ${data.status === "open" ? "fan-status-mint" : data.status === "awaiting-model" ? "fan-status-amber" : "fan-status-steel"}`}>
            {data.status === "open" ? "Picks open" : data.status === "awaiting-model" ? "Picks opening soon" : data.status === "final" ? "Week complete" : "Official slate"}
          </span>
          <h2 id="official-slate-heading">{data.season} Week {data.week}</h2>
          <p>{data.status === "awaiting-model"
            ? "The matchups are set. Picking opens once The Model's frozen pregame calls are attached."
            : data.status === "final"
              ? "The week is final. Your saved picks are scored beside The Model."
              : "Pick one winner in every game. The Model is revealed only after you choose."}</p>
        </div>

        <div className="btm-card-progress" aria-label={`${pickedCount} of ${data.games.length} picks made`}>
          <div>
            <span>{data.status === "awaiting-model" ? "Slate ready" : cardComplete ? "Card complete" : "Your card"}</span>
            <strong>{data.status === "awaiting-model" ? `${data.games.length}/${data.slateSize}` : hydrated ? `${pickedCount}/${data.games.length}` : "—"}</strong>
          </div>
          {data.status !== "awaiting-model" ? (
            <div className="btm-progress-track" aria-hidden="true"><span style={{ width: `${progress}%` }} /></div>
          ) : null}
        </div>
      </div>

      {data.status === "awaiting-model" ? (
        <div className="btm-week-message">
          <div><strong>Matchups are published.</strong><span>You can browse the full card now.</span></div>
          <div><strong>Picking is still locked.</strong><span>It opens automatically when all model calls are frozen.</span></div>
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
