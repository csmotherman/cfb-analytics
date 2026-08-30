import { notFound } from "next/navigation";
import VideosPage from "../videos/View";
import VideoOutlinePage from "../videos/[videoSlug]/View";
import RequestsPage from "../requests/View";
import LibraryPage from "../library/[section]/View";
import GameRoomPage from "../games/[gameId]/View";
import ScoutingPage from "../scouting/[report]/View";

export const dynamic = "force-dynamic";

export default async function CreatorWorkspaceRoute({
  params,
  searchParams,
}: {
  params: Promise<{ creatorSlug: string; path: string[] }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { creatorSlug, path } = await params;
  const query = await searchParams;

  if (path.length === 1 && path[0] === "videos") {
    return (
      <VideosPage
        params={Promise.resolve({ creatorSlug })}
        searchParams={Promise.resolve({ filter: typeof query.filter === "string" ? query.filter : undefined })}
      />
    );
  }

  if (path.length === 2 && path[0] === "videos") {
    return (
      <VideoOutlinePage
        params={Promise.resolve({ creatorSlug, videoSlug: path[1] })}
        searchParams={Promise.resolve({ mode: typeof query.mode === "string" ? query.mode : undefined })}
      />
    );
  }

  if (path.length === 1 && path[0] === "requests") {
    return <RequestsPage params={Promise.resolve({ creatorSlug })} />;
  }

  if (path.length === 2 && path[0] === "library") {
    return <LibraryPage params={Promise.resolve({ creatorSlug, section: path[1] })} />;
  }

  if ((path.length === 1 || path.length === 2) && path[0] === "games") {
    return <GameRoomPage params={Promise.resolve({ creatorSlug, gameId: path[1] ?? "all" })} />;
  }

  if ((path.length === 1 || path.length === 2) && path[0] === "scouting") {
    return <ScoutingPage params={Promise.resolve({ creatorSlug, report: path[1] ?? "all" })} />;
  }

  notFound();
}
