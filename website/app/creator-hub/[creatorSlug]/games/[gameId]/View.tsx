import Link from "next/link";
import { notFound } from "next/navigation";
import { requireCreatorForSlug } from "../../../actions";
import { findGameStoryPackByGameId, getAllKnownGameStoryPacks } from "../../../../../lib/creator-hub/game-story";
import { getVideosForCreator } from "../../../../../lib/creator-hub/db";
import { TeamLogo } from "../../../../../components/ui/TeamLogo";
import { Disclosure } from "../../Disclosure";
import { StoryCard } from "../../../../../components/creator-hub/visuals/StoryCard";
import { OpponentAdjustedTable } from "../../../../../components/creator-hub/visuals/OpponentAdjustedTable";
import { DriveFunnelChart } from "../../../../../components/creator-hub/visuals/DriveFunnelChart";
import { HalfSplitChart } from "../../../../../components/creator-hub/visuals/HalfSplitChart";
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
          <input className="ch-input" name="newVideoTitle" placeholder="Michigan vs ...: What Actually Happened" />
        </div>
        <button type="submit" className="ch-btn ch-btn-primary">Add story as a new section</button>
      </form>
    </Disclosure>
  );
}

function GameRoomList({ creatorSlug }: { creatorSlug: string }) {
  const packs = getAllKnownGameStoryPacks();

  return (
    <>
      <div className="ch-page-head">
        <div><h1>Game Room</h1><p>Charts, tables and drive-level data for every game.</p></div>
      </div>

      {packs.length === 0 ? (
        <div className="ch-empty">No game story packs published yet.</div>
      ) : (
        <div className="ch-video-list">
          {packs.map((pack) => {
            const strongSignals = pack.stories.filter((s) => s.signalClass === "STRONG_SIGNAL").length;
            const concerns = pack.stories.filter((s) => s.polarity === "concern").length;
            return (
              <Link key={pack.gameId} href={`/creator-hub/${creatorSlug}/games/${pack.gameId}`} className="ch-card ch-card-pad ch-game-row">
                <div className="ch-game-row-score">
                  {pack.michiganTeamId != null && <TeamLogo teamId={pack.michiganTeamId} name="Michigan" size={64} className="ch-game-row-logo" />}
                  <span className={pack.win ? "win" : "loss"}>{pack.pointsFor}-{pack.pointsAgainst}</span>
                  {pack.opponentTeamId != null && <TeamLogo teamId={pack.opponentTeamId} name={pack.opponent} size={64} className="ch-game-row-logo" />}
                </div>
                <div className="ch-game-row-body">
                  <div className="meta">{pack.season} · Week {pack.week} · vs {pack.opponent}</div>
                  <div className="headline">{strongSignals} strong signal{strongSignals === 1 ? "" : "s"} · {concerns} concern{concerns === 1 ? "" : "s"} · {pack.driveTimeline.length} drives tracked</div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </>
  );
}

export default async function GameRoomPage({
  params,
}: {
  params: Promise<{ creatorSlug: string; gameId: string }>;
}) {
  const { creatorSlug, gameId } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);

  if (gameId === "all") return <GameRoomList creatorSlug={creator.slug} />;

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
          <span className="week">{pack.season} · Week {pack.week} · {pack.homeAway === "home" ? "Home" : "Away"}</span>
        </div>
        <div className="side" style={{ color: opponentColors.primary }}>
          {pack.opponentTeamId != null && <TeamLogo teamId={pack.opponentTeamId} name={pack.opponent} size={64} />}
          <span className="score">{pack.pointsAgainst}</span>
          <span className="name">{pack.opponent}</span>
        </div>
      </div>

      <div className="ch-dashboard-intro">
        <span>GAME DATA DASHBOARD</span>
        <h2>See the game before reading the takeaways.</h2>
        <p>Every visual below is generated from the published game-story data: opponent-adjusted metrics, possession conversion, success rate splits and drive results.</p>
      </div>

      <OpponentAdjustedTable stories={pack.stories} opponentName={pack.opponent} />

      <div className="ch-data-grid">
        <DriveFunnelChart
          offense={pack.driveFunnel.offense}
          defense={pack.driveFunnel.defense}
          michiganTeamId={pack.michiganTeamId}
          opponentTeamId={pack.opponentTeamId}
          opponentName={pack.opponent}
        />
        {pack.halfSplit && (
          <HalfSplitChart
            michigan={pack.halfSplit.michigan}
            opponent={pack.halfSplit.opponent}
            michiganTeamId={pack.michiganTeamId}
            opponentTeamId={pack.opponentTeamId}
            opponentName={pack.opponent}
          />
        )}
      </div>

      {pack.driveTimeline.length > 0 && (
        <section className="ch-data-panel ch-data-panel-wide">
          <div className="ch-data-panel-head">
            <div>
              <h2>Drive timeline</h2>
              <p>Field position, yards gained and result for every meaningful possession.</p>
            </div>
          </div>
          <DriveMap drives={pack.driveTimeline} michiganTeamId={pack.michiganTeamId} opponentTeamId={pack.opponentTeamId} opponentName={pack.opponent} />
        </section>
      )}

      <div className="ch-outline-subhead" style={{ marginTop: 32 }}>Video angles from the data</div>
      <div className="ch-story-notes-grid">
        {pack.stories.map((story) => (
          <div key={story.id} className="ch-card ch-card-pad ch-story-note">
            <div className="ch-story-note-head">
              <span className={`ch-story-signal ${story.signalClass.toLowerCase()}`}>{SIGNAL_LABEL[story.signalClass]}</span>
              <span className={`ch-story-note-polarity ${story.polarity}`}>{story.polarity}</span>
            </div>
            <h3>{story.headline}</h3>
            <p>{story.videoAngle}</p>
            {story.percentile.sampleSizeCaveat && <p className="ch-story-caveat">{story.percentile.sampleSizeCaveat}</p>}
            <div className="ch-story-note-actions">
              <Disclosure trigger="Open metric chart" title={story.headline}>
                <StoryCard story={story} michiganTeamId={pack.michiganTeamId} opponentTeamId={pack.opponentTeamId} opponentName={pack.opponent} />
              </Disclosure>
              <AddToVideoForm gameId={pack.gameId} story={story} videos={videos} />
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
