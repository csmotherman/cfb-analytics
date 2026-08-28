import { TeamLogo } from "../../ui/TeamLogo";
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
  const favorable = story.delta != null && story.delta > 0;

  return (
    <Visual16x9Frame title={story.headline} source={`SOAR Analytics · ${story.definitionVersion}`}>
      <div className="ch-storycard">
        <div className="ch-storycard-stat" style={{ color: michigan.primary }}>
          {michiganTeamId != null && <TeamLogo teamId={michiganTeamId} name="Michigan" size={64} className="ch-storycard-logo" />}
          <div className="ch-storycard-number">{formatMetricValue(story.metric, gameValue)}</div>
          <div className="ch-storycard-caption">Michigan this game</div>
        </div>

        <div className="ch-storycard-compare">
          <div className="ch-storycard-row">
            <span className="label">{opponentName} normal{gamesUsed != null ? ` (${gamesUsed} games)` : ""}</span>
            <span className="value">{formatMetricValue(story.metric, opponentBaseline)}</span>
          </div>
          <div className={`ch-storycard-delta ${favorable ? "good" : "bad"}`} style={{ borderColor: favorable ? michigan.primary : undefined }}>
            {formatMetricDelta(story.metric, story.delta)} vs. expectation
          </div>
          {story.percentile.rank != null && (
            <div className="ch-storycard-rank">
              {story.percentile.rank === 1 ? "Best" : `#${story.percentile.rank} of ${story.percentile.sampleSize}`} {opponentName} has faced this season
            </div>
          )}
        </div>

        {opponentTeamId != null && <TeamLogo teamId={opponentTeamId} name={opponentName} size={64} className="ch-storycard-opp-logo" />}
      </div>
      {story.signalClass === "LIKELY_NOISY" && <div className="ch-viz-caveat">Small sample -- treat as a lead, not a conclusion.</div>}
    </Visual16x9Frame>
  );
}
