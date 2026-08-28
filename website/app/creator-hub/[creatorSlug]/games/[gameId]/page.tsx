import Link from "next/link";
import { notFound } from "next/navigation";
import { requireCreatorForSlug } from "../../../actions";
import { findGameStoryPackByGameId } from "../../../../../lib/creator-hub/game-story";
import { getVideosForCreator } from "../../../../../lib/creator-hub/db";
import { TeamLogo } from "../../../../../components/ui/TeamLogo";
import { Disclosure } from "../../Disclosure";
import { StoryCard } from "../../../../../components/creator-hub/visuals/StoryCard";
import { ComparisonBarChart } from "../../../../../components/creator-hub/visuals/ComparisonBarChart";
import { DriveMap } from "../../../../../components/creator-hub/visuals/DriveMap";
import { teamColors } from "../../../../../lib/team-colors";
import { addStoryToVideoAction } from "../../workspace-actions";
import type { GameStory } from "../../../../../lib/creator-hub/game-story";

export const dynamic = "force-dynamic";

const SIGNAL_LABEL: Record<string, string> = { STRONG_SIGNAL: "Strong signal", WATCH: "Watch", LIKELY_NOISY: "Likely noisy" };

function AddToVideoForm({ gameId, story, videos }: { gameId: string; story: GameStory; videos: { id: number; title: string }[] }) {
  return (
    <Disclosure trigger="+ Add to Video" title="Add this story to a video">
      <form action={addStoryToVideoAction}>
        <input type="hidden" name="gameId" value={gameId} />
        <input type="hidden" name="storyId" value={story.id} />
        <div className="ch-field">
          <label>Video</label>
          <select className="ch-select" name="videoId" defaultValue="">
            <option value="">+ New video</option>
            {videos.map((v) => <option key={v.id} value={v.id}>{v.title}</option>)}
          </select>
        </div>
        <div className="ch-field">
          <label>If new: title</label>
          <input className="ch-input" name="newVideoTitle" placeholder={`Michigan vs ...: What Actually Happened`} />
        </div>
        <button type="submit" className="ch-btn ch-btn-primary">Add story as a new section</button>
      </form>
    </Disclosure>
  );
}

export default async function GameRoomPage({ params }: { params: Promise<{ creatorSlug: string; gameId: string }> }) {
  const { creatorSlug, gameId } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);
  const pack = findGameStoryPackByGameId(gameId);
  if (!pack) notFound();

  const videos = await getVideosForCreator(creator.id);
  const michiganColors = teamColors(pack.michiganTeamId);
  const opponentColors = teamColors(pack.opponentTeamId);

  return (
    <>
      <Link href={`/creator-hub/${creator.slug}/games`} className="ch-btn ch-btn-ghost ch-btn-sm" style={{ marginBottom: 18, display: "inline-flex" }}>&larr; Game Room</Link>

      <div className="ch-card ch-card-pad ch-gameroom-header">
        <div className="side" style={{ color: michiganColors.primary }}>
          {pack.michiganTeamId != null && <TeamLogo teamId={pack.michiganTeamId} name="Michigan" size={64} />}
          <span className="score">{pack.pointsFor}</span>
          <span className="name">Michigan</span>
        </div>
        <div className="mid">
          <span className="final">FINAL</span>
          <span className="week">Week {pack.week} &middot; {pack.homeAway === "home" ? "Home" : "Away"}</span>
        </div>
        <div className="side" style={{ color: opponentColors.primary }}>
          {pack.opponentTeamId != null && <TeamLogo teamId={pack.opponentTeamId} name={pack.opponent} size={64} />}
          <span className="score">{pack.pointsAgainst}</span>
          <span className="name">{pack.opponent}</span>
        </div>
      </div>

      <div className="ch-outline-subhead" style={{ marginTop: 28 }}>What actually decided this game</div>

      {pack.stories.map((story, index) => (
        <div key={story.id} className="ch-card ch-card-pad ch-story-block">
          <div className="ch-story-block-head">
            <span className="num">{index + 1}</span>
            <h3>{story.headline}</h3>
            <span className={`ch-story-signal ${story.signalClass.toLowerCase()}`}>{SIGNAL_LABEL[story.signalClass]}</span>
          </div>
          <ul className="ch-story-evidence">
            {story.evidence.map((line, i) => <li key={i}>{line}</li>)}
          </ul>
          <p className="ch-story-why"><strong>Why it matters:</strong> {story.whyItMatters}</p>
          <p className="ch-story-angle"><strong>Video angle:</strong> &ldquo;{story.videoAngle}&rdquo;</p>
          {story.percentile.sampleSizeCaveat && <p className="ch-story-caveat">{story.percentile.sampleSizeCaveat}</p>}

          <div style={{ display: "flex", gap: 8, marginTop: 14, flexWrap: "wrap" }}>
            <Disclosure trigger="Show Visual" title="Visual">
              <StoryCard story={story} michiganTeamId={pack.michiganTeamId} opponentTeamId={pack.opponentTeamId} opponentName={pack.opponent} />
            </Disclosure>
            <AddToVideoForm gameId={pack.gameId} story={story} videos={videos} />
          </div>
        </div>
      ))}

      {pack.stories[0] && (
        <>
          <div className="ch-outline-subhead" style={{ marginTop: 28 }}>Comparison</div>
          <ComparisonBarChart
            title={pack.stories[0].headline}
            metric={pack.stories[0].metric}
            source={`SOAR Analytics · ${pack.stories[0].definitionVersion}`}
            bars={[
              { label: "Michigan", value: pack.stories[0].context.gameValue as number | null, color: michiganColors.primary },
              { label: `${pack.opponent} normal`, value: pack.stories[0].context.opponentBaseline as number | null, color: opponentColors.primary },
            ]}
          />
        </>
      )}

      {pack.driveTimeline.length > 0 && (
        <>
          <div className="ch-outline-subhead" style={{ marginTop: 28 }}>Drive Map</div>
          <DriveMap drives={pack.driveTimeline} michiganTeamId={pack.michiganTeamId} opponentTeamId={pack.opponentTeamId} opponentName={pack.opponent} />
        </>
      )}
    </>
  );
}
