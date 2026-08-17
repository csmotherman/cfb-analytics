"use client";

import { useEffect, useMemo, useState } from "react";

import type { BeatTheModelDataset, BeatTheModelGame } from "../lib/beat-the-model";

type Picks = Record<string, string>;
type ViewFilter = "all" | "unpicked" | "disagree";

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
  if (game.status === "final" || game.status === "live") return true;
  if (!game.kickoff) return false;
  const kickoff = new Date(game.kickoff).getTime();
  return Number.isFinite(kickoff) && Date.now() >= kickoff;
}

function gameStatus(game: BeatTheModelGame): string {
  if (game.status === "final") return "Final";
  if (game.status === "live") return "Live";
  return formatKickoff(game.kickoff) ?? "Kickoff TBA";
}

async function shareDisagreement(game: BeatTheModelGame, pick: string) {
  if (!game.modelWinner) return;
  const agrees = pick === game.modelWinner;
  const text = agrees
    ? `I’m taking ${pick} in ${game.awayTeam} at ${game.homeTeam}. The Model agrees. Can you beat it?`
    : `I’m taking ${pick} in ${game.awayTeam} at ${game.homeTeam}. The Model has ${game.modelWinner}. Who’s right?`;
  const url = window.location.href;
  try {
    if (navigator.share) {
      await navigator.share({ title: "Beat the Model", text, url });
      return;
    }
    await navigator.clipboard.writeText(`${text} ${url}`);
  } catch {
    // Sharing is optional and should never interrupt the pick flow.
  }
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
      <span className="btm-pick-action">
        {picked ? "Picked ✓" : modelPending ? "Not open" : disabled ? "Locked" : "Pick"}
      </span>
    </button>
  );
}

function ScoreRows({ game }: { game: BeatTheModelGame }) {
  if (typeof game.actualHomeScore !== "number" || typeof game.actualAwayScore !== "number") return null;
  const winner = actualWinner(game);
  return (
    <div className="btm-live-score" aria-label={`${game.awayTeam} ${game.actualAwayScore}, ${game.homeTeam} ${game.actualHomeScore}`}>
      <div className={winner === game.awayTeam ? "winner" : ""}>
        <span>#{game.awayRank}</span><strong>{game.awayTeam}</strong><em>{game.actualAwayScore}</em>
      </div>
      <div className={winner === game.homeTeam ? "winner" : ""}>
        <span>#{game.homeRank}</span><strong>{game.homeTeam}</strong><em>{game.actualHomeScore}</em>
      </div>
    </div>
  );
}

function GameCard({ game, pick, onPick }: { game: BeatTheModelGame; pick?: string; onPick: (team: string) => void }) {
  const locked = isLocked(game);
  const modelAvailable = Boolean(game.modelWinner);
  const revealed = modelAvailable && (Boolean(pick) || locked || game.status === "final" || game.status === "live");
  const winner = actualWinner(game);
  const userCorrect = pick && winner ? pick === winner : null;
  const modelCorrect = winner && game.modelWinner ? game.modelWinner === winner : null;
  const modelRank = game.modelWinner === game.homeTeam ? game.homeRank : game.awayRank;
  const margin = typeof game.modelMargin === "number" ? Math.abs(game.modelMargin).toFixed(1) : null;

  return (
    <article className={`btm-game-card${pick ? " has-pick" : ""}${game.status === "live" ? " live" : ""}${game.status === "final" ? " final" : ""}`}>
      <header className="btm-game-topline">
        <div><span className="btm-game-number">{game.slot}</span><strong>Game {game.slot}</strong></div>
        <span className={game.status === "live" ? "btm-live-label" : ""}>{gameStatus(game)}</span>
      </header>

      {(game.status === "live" || game.status === "final") ? <ScoreRows game={game} /> : null}

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
          <div className="btm-model-copy">
            <span>THE MODEL</span>
            <strong>Pregame call is being locked</strong>
            <small>The matchup is official. Picking opens when the frozen prediction snapshot is attached.</small>
          </div>
        ) : revealed ? (
          <>
            <div className="btm-model-copy">
              <span>THE MODEL PICKED</span>
              <strong>#{modelRank} {game.modelWinner}{margin ? ` · by ${margin}` : ""}</strong>
              <small>{pick ? (pick === game.modelWinner ? "You made the same call." : `You backed ${pick}. This one is a disagreement.`) : "Revealed after kickoff."}</small>
            </div>

            {game.status === "final" ? (
              <div className="btm-result-pair">
                <span className={userCorrect === true ? "correct" : userCorrect === false ? "wrong" : ""}>You {userCorrect === true ? "✓" : userCorrect === false ? "×" : "—"}</span>
                <span className={modelCorrect === true ? "correct" : modelCorrect === false ? "wrong" : ""}>Model {modelCorrect === true ? "✓" : modelCorrect === false ? "×" : "—"}</span>
              </div>
            ) : pick ? (
              <div className="btm-reveal-actions">
                <span className={`btm-agreement ${pick === game.modelWinner ? "agree" : "disagree"}`}>
                  {pick === game.modelWinner ? "You agree" : "You disagree"}
                </span>
                <button type="button" onClick={() => shareDisagreement(game, pick)}>Share</button>
              </div>
            ) : null}
          </>
        ) : (
          <div className="btm-model-copy btm-model-hidden">
            <span>THE MODEL</span>
            <strong>Hidden until you pick</strong>
            <small>Your opinion comes first. Pick either team to reveal the opponent.</small>
          </div>
        )}
      </div>
    </article>
  );
}

export function BeatTheModelGameView({ data }: { data: BeatTheModelDataset }) {
  const [picks, setPicks] = useState<Picks>({});
  const [hydrated, setHydrated] = useState(false);
  const [filter, setFilter] = useState<ViewFilter>("all");

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
        // Keep the in-memory pick if storage is unavailable.
      }
      return next;
    });
  }

  const pickedCount = useMemo(() => data.games.filter((game) => Boolean(picks[game.id])).length, [data.games, picks]);
  const finalGames = data.games.filter((game) => game.status === "final");
  const liveGames = data.games.filter((game) => game.status === "live");
  const userWins = finalGames.filter((game) => actualWinner(game) && picks[game.id] === actualWinner(game)).length;
  const modelFinalGames = finalGames.filter((game) => Boolean(game.modelWinner));
  const modelWins = modelFinalGames.filter((game) => actualWinner(game) === game.modelWinner).length;
  const progress = data.games.length ? Math.round((pickedCount / data.games.length) * 100) : 0;
  const cardComplete = data.games.length > 0 && pickedCount === data.games.length;
  const disagreements = data.games.filter((game) => picks[game.id] && game.modelWinner && picks[game.id] !== game.modelWinner).length;

  const visibleGames = data.games.filter((game) => {
    if (filter === "unpicked") return !picks[game.id];
    if (filter === "disagree") return Boolean(picks[game.id] && game.modelWinner && picks[game.id] !== game.modelWinner);
    return true;
  });

  if (!data.games.length) {
    return (
      <section className="fan-empty-state btm-empty-week">
        <span className="fan-status fan-status-steel">{data.season} Week {data.week}</span>
        <h2>The Official {data.slateSize} is not published yet.</h2>
        <p>The weekly scheduler ranks the FBS slate and publishes the strongest matchups. When the card is ready, it will appear here automatically.</p>
      </section>
    );
  }

  return (
    <section className="btm-play-area" aria-labelledby="official-slate-heading">
      <div className="btm-play-toolbar">
        <div className="btm-play-toolbar-copy">
          <div className="btm-toolbar-labels">
            <span className={`fan-status ${data.status === "open" ? "fan-status-mint" : data.status === "awaiting-model" ? "fan-status-amber" : data.status === "locked" ? "fan-status-cyan" : "fan-status-steel"}`}>
              {data.status === "open" ? "Picks open" : data.status === "awaiting-model" ? "Official 15 set" : data.status === "locked" ? "Games underway" : data.status === "final" ? "Week final" : "Official slate"}
            </span>
            {liveGames.length ? <span className="btm-live-label">{liveGames.length} live</span> : null}
          </div>
          <h2 id="official-slate-heading">{data.season} Week {data.week} · Official {data.slateSize}</h2>
          <p>{data.status === "awaiting-model"
            ? "The card is published. Picking opens automatically after every selected game has a frozen pregame model call."
            : data.status === "final"
              ? "The week is final. Your saved card is graded beside The Model."
              : data.status === "locked"
                ? "The card is locked. Follow the scores and watch your head-to-head with The Model."
                : "Pick one winner per game. Your pick comes first; then The Model is revealed."}</p>
        </div>

        <div className="btm-card-progress" aria-label={`${pickedCount} of ${data.games.length} picks made`}>
          <div>
            <span>{data.status === "awaiting-model" ? "Games ready" : cardComplete ? "Card complete" : "Your card"}</span>
            <strong>{data.status === "awaiting-model" ? `${data.games.length}/${data.slateSize}` : hydrated ? `${pickedCount}/${data.games.length}` : "—"}</strong>
          </div>
          {data.status !== "awaiting-model" ? <div className="btm-progress-track" aria-hidden="true"><span style={{ width: `${progress}%` }} /></div> : null}
        </div>
      </div>

      {data.status === "awaiting-model" ? (
        <div className="btm-week-message">
          <div><strong>The matchups are official.</strong><span>Browse all 15 and see where every team entered the week.</span></div>
          <div><strong>The Model is still locking.</strong><span>No picks can be made until the full pregame snapshot is ready.</span></div>
        </div>
      ) : finalGames.length || liveGames.length ? (
        <div className="btm-scoreboard">
          <div><span>Your correct picks</span><strong>{userWins}</strong><small>{finalGames.length} final</small></div>
          <div className="btm-scoreboard-center"><span>HEAD TO HEAD</span><strong>{userWins === modelWins ? "TIED" : userWins > modelWins ? `YOU +${userWins - modelWins}` : `MODEL +${modelWins - userWins}`}</strong></div>
          <div><span>The Model</span><strong>{modelWins}</strong><small>{liveGames.length ? `${liveGames.length} live` : `${finalGames.length} final`}</small></div>
        </div>
      ) : null}

      {data.status !== "awaiting-model" ? (
        <div className="btm-pick-controls">
          <div className="btm-filter-tabs" role="tablist" aria-label="Filter games">
            <button type="button" className={filter === "all" ? "active" : ""} onClick={() => setFilter("all")}>All <span>{data.games.length}</span></button>
            <button type="button" className={filter === "unpicked" ? "active" : ""} onClick={() => setFilter("unpicked")}>Unpicked <span>{data.games.length - pickedCount}</span></button>
            <button type="button" className={filter === "disagree" ? "active" : ""} onClick={() => setFilter("disagree")}>Disagreements <span>{disagreements}</span></button>
          </div>
          {cardComplete ? <strong className="btm-card-done">Card complete ✓</strong> : null}
        </div>
      ) : null}

      <div className="btm-game-list">
        {visibleGames.map((game) => (
          <GameCard key={game.id} game={game} pick={picks[game.id]} onPick={(team) => choose(game, team)} />
        ))}
      </div>

      {!visibleGames.length ? (
        <div className="fan-empty-state btm-filter-empty">
          <h3>{filter === "unpicked" ? "You picked every game." : "No disagreements yet."}</h3>
          <p>{filter === "unpicked" ? "Your full card is set. You can still change a pick until that game kicks off." : "Make more picks to find out where you and The Model split."}</p>
          <button type="button" className="fan-button fan-button-secondary" onClick={() => setFilter("all")}>Show the full card</button>
        </div>
      ) : null}
    </section>
  );
}
