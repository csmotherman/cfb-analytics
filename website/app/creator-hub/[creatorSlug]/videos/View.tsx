import Link from "next/link";
import { requireCreatorForSlug } from "../../actions";
import { getAttachmentsForVideo, getRequestsForVideo, getSectionsForVideo, getVideosForCreator } from "../../../../lib/creator-hub/db";
import { StatusBadge } from "../StatusBadge";
import { Disclosure } from "../Disclosure";
import { createVideoAction } from "../workspace-actions";

export const dynamic = "force-dynamic";

const FILTERS = [
  { key: "active", label: "Active", match: (s: string) => !["published", "archived"].includes(s) },
  { key: "ready", label: "Ready", match: (s: string) => s === "ready" || s === "recorded" },
  { key: "published", label: "Published", match: (s: string) => s === "published" },
  { key: "archive", label: "Archive", match: (s: string) => s === "archived" },
] as const;

export default async function VideosPage({
  params,
  searchParams,
}: {
  params: Promise<{ creatorSlug: string }>;
  searchParams: Promise<{ filter?: string }>;
}) {
  const { creatorSlug } = await params;
  const { filter } = await searchParams;
  const creator = await requireCreatorForSlug(creatorSlug);
  const videos = await getVideosForCreator(creator.id);

  const activeFilter = FILTERS.find((f) => f.key === filter) ?? FILTERS[0];
  const filtered = videos.filter((v) => activeFilter.match(v.status));

  const meta = await Promise.all(
    filtered.map(async (v) => {
      const [sections, attachments, requests] = await Promise.all([
        getSectionsForVideo(v.id),
        getAttachmentsForVideo(v.id),
        getRequestsForVideo(v.id),
      ]);
      return {
        video: v,
        sections: sections.length,
        visuals: attachments.filter((a) => a.kind === "visual").length,
        completedRequests: requests.filter((r) => r.status === "completed").length,
      };
    })
  );

  return (
    <>
      <div className="ch-page-head">
        <div>
          <h1>Videos</h1>
          <p>Every outline, in one place.</p>
        </div>
        <Disclosure trigger="+ New Video Outline" title="New video outline" primary>
          <form action={createVideoAction}>
            <div className="ch-field"><label>Working title</label><input className="ch-input" name="title" required autoFocus /></div>
            <div className="ch-field"><label>Main idea / thesis</label><textarea className="ch-textarea" name="thesis" rows={2} /></div>
            <div className="ch-field"><label>Hook</label><textarea className="ch-textarea" name="hook" rows={2} /></div>
            <button type="submit" className="ch-btn ch-btn-primary">Create video</button>
          </form>
        </Disclosure>
      </div>

      <div className="ch-filter-row">
        {FILTERS.map((f) => (
          <Link key={f.key} href={`/creator-hub/${creator.slug}/videos?filter=${f.key}`} className={`ch-filter-pill${f.key === activeFilter.key ? " active" : ""}`}>
            {f.label}
          </Link>
        ))}
      </div>

      {meta.length === 0 ? (
        <div className="ch-empty">Nothing in this filter yet.</div>
      ) : (
        <div className="ch-video-list">
          {meta.map(({ video, sections, visuals, completedRequests }) => (
            <Link key={video.id} href={`/creator-hub/${creator.slug}/videos/${video.slug}`} className="ch-card ch-video-card">
              <div className="ch-video-card-main">
                <p className="ch-video-card-title">{video.title} <StatusBadge status={video.status} /></p>
                <div className="ch-video-card-meta">
                  <span>{sections} section{sections === 1 ? "" : "s"}</span>
                  <span>{visuals} visual{visuals === 1 ? "" : "s"}</span>
                  {completedRequests > 0 && <span>{completedRequests} completed request{completedRequests === 1 ? "" : "s"}</span>}
                </div>
              </div>
              <span className="ch-btn ch-btn-sm">Open</span>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
