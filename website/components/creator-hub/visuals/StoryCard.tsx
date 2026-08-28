import { teamColors } from "../../../lib/team-colors";
import { formatMetricValue, formatMetricDelta } from "../../../lib/creator-hub/format-metric";
import { Visual16x9Frame } from "./Visual16x9Frame";
import type { GameStory } from "../../../lib/creator-hub/game-story";

export function StoryCard({
  story,
  michiganTeamId,
  opponentTeamId,
  opponentName,
}: {
  story: GameStory;
  michiganTeamId: number | null;
  opponentTeamId: number | null;
  opponentName: string;
}) {
  const gameValue = story.context.gameValue as number | null | undefined;
  const opponentBaseline = story.context.opponentBaseline as number | null | undefined;
  const gamesUsed = story.context.opponentGamesUsed as number | undefined;
  const michigan = teamColors(michiganTeamId);
  const opponent = teamColors(opponentTeamId);
  const values = [Math.abs(gameValue ?? 0), Math.abs(opponentBaseline ?? 0)];
  const max = Math.max(...values, 0.0001);
  const rank = story.percentile.rank;
  const sampleSize = story.percentile.sampleSize;
  const percentile = story.percentile.percentile == null ? null : Math.max(0, Math.min(100, story.percentile.percentile * 100));

  return (
    <Visual16x9Frame title={story.headline} source={`SOAR Analytics · ${story.definitionVersion}`}>
      <div className="ch-storychart">
        <div className="ch-storychart-bars">
          <div className="ch-storychart-row">
            <div className="ch-storychart-label">Michigan</div>
            <div className="ch-storychart-track">
              <div className="ch-storychart-fill" style={{ width: `${Math.max((Math.abs(gameValue ?? 0) / max) * 100, 2)}%`, background: michigan.primary }} />
            </div>
            <strong>{formatMetricValue(story.metric, gameValue)}</strong>
          </div>
          <div className="ch-storychart-row">
            <div className="ch-storychart-label">{opponentName} normal{gamesUsed != null ? ` (${gamesUsed})` : ""}</div>
            <div className="ch-storychart-track">
              <div className="ch-storychart-fill" style={{ width: `${Math.max((Math.abs(opponentBaseline ?? 0) / max) * 100, 2)}%`, background: opponent.primary }} />
            </div>
            <strong>{formatMetricValue(story.metric, opponentBaseline)}</strong>
          </div>
        </div>

        <div className="ch-storychart-footer">
          <div className={`ch-storychart-delta ${story.polarity}`}>
            <span>vs expectation</span>
            <strong>{formatMetricDelta(story.metric, story.delta)}</strong>
          </div>
          {rank != null && (
            <div className="ch-storychart-rank">
              <div className="ch-storychart-rank-head">
                <span>Rank among {opponentName} games</span>
                <strong>#{rank} / {sampleSize}</strong>
              </div>
              {percentile != null && (
                <div className="ch-storychart-rank-track">
                  <span style={{ left: `calc(${percentile}% - 5px)` }} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      {story.signalClass === "LIKELY_NOISY" && <div className="ch-viz-caveat">Small sample -- treat as a lead, not a conclusion.</div>}
    </Visual16x9Frame>
  );
}
