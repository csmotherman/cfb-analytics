import Link from "next/link";
import { requireCreatorForSlug } from "../../actions";
import { getAllKnownGameStoryPacks } from "../../../../lib/creator-hub/game-story";
import { TeamLogo } from "../../../../components/ui/TeamLogo";

export const dynamic = "force-dynamic";

export default async function GameRoomListPage({ params }: { params: Promise<{ creatorSlug: string }> }) {
  const { creatorSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);
  const packs = getAllKnownGameStoryPacks();

  return (
    <>
      <div className="ch-page-head">
        <div><h1>Game Room</h1><p>What the data revealed, game by game -- not a recap.</p></div>
      </div>

      {packs.length === 0 ? (
        <div className="ch-empty">No game story packs published yet.</div>
      ) : (
        <div className="ch-video-list">
          {packs.map((pack) => {
            const top = pack.stories[0];
            const concern = pack.stories.find((s) => s.polarity === "concern");
            return (
              <Link key={pack.gameId} href={`/creator-hub/${creator.slug}/games/${pack.gameId}`} className="ch-card ch-card-pad ch-game-row">
                <div className="ch-game-row-score">
                  {pack.michiganTeamId != null && <TeamLogo teamId={pack.michiganTeamId} name="Michigan" size={64} className="ch-game-row-logo" />}
                  <span className={pack.win ? "win" : "loss"}>{pack.pointsFor}-{pack.pointsAgainst}</span>
                  {pack.opponentTeamId != null && <TeamLogo teamId={pack.opponentTeamId} name={pack.opponent} size={64} className="ch-game-row-logo" />}
                </div>
                <div className="ch-game-row-body">
                  <div className="meta">Week {pack.week} &middot; vs {pack.opponent}</div>
                  {top && <div className="headline">{top.headline}</div>}
                  {concern && concern !== top && <div className="concern">Also: {concern.headline}</div>}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </>
  );
}
