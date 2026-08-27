import Link from "next/link";
import { requireCreatorForSlug } from "../../actions";
import { getRequestsForCreator, getVideosForCreator } from "../../../../lib/creator-hub/db";
import { updateRequestStatusAction } from "../workspace-actions";

export const dynamic = "force-dynamic";

const TYPE_LABEL: Record<string, string> = { analytics: "Analytics", chart: "Chart", research: "Research", fact_check: "Fact check" };

export default async function RequestsPage({ params }: { params: Promise<{ creatorSlug: string }> }) {
  const { creatorSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);
  const [requests, videos] = await Promise.all([getRequestsForCreator(creator.id), getVideosForCreator(creator.id)]);
  const videoTitle = new Map(videos.map((v) => [v.id, v.title]));
  const videoSlug = new Map(videos.map((v) => [v.id, v.slug]));

  const open = requests.filter((r) => r.status !== "completed");
  const completed = requests.filter((r) => r.status === "completed");

  return (
    <>
      <div className="ch-page-head">
        <div><h1>Requests</h1><p>What you've asked Carter for.</p></div>
      </div>

      <section className="ch-section">
        <div className="ch-section-head"><h2>Open</h2><span className="count">{open.length}</span></div>
        {open.length === 0 ? <div className="ch-empty">Nothing outstanding.</div> : (
          <div className="ch-video-list">
            {open.map((r) => (
              <div key={r.id} className="ch-card ch-card-pad">
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                  <div>
                    <p style={{ margin: "0 0 4px", fontWeight: 700, fontSize: 14 }}>{r.what_you_need}</p>
                    <p style={{ margin: 0, fontSize: 12.5, color: "var(--ch-text-dim)" }}>
                      {TYPE_LABEL[r.request_type]} · <Link href={`/creator-hub/${creator.slug}/videos/${videoSlug.get(r.video_id)}`}>{videoTitle.get(r.video_id) ?? "Video"}</Link>
                    </p>
                    {r.what_proving && <p style={{ margin: "6px 0 0", fontSize: 12.5, color: "var(--ch-text-faint)" }}>Proving: {r.what_proving}</p>}
                  </div>
                  <form action={updateRequestStatusAction}>
                    <input type="hidden" name="requestId" value={r.id} />
                    <input type="hidden" name="status" value="completed" />
                    <button type="submit" className="ch-btn ch-btn-sm">Mark done</button>
                  </form>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="ch-section">
        <div className="ch-section-head"><h2>Completed</h2><span className="count">{completed.length}</span></div>
        {completed.length === 0 ? <div className="ch-empty">None yet.</div> : (
          <div className="ch-video-list">
            {completed.map((r) => (
              <div key={r.id} className="ch-card ch-card-pad" style={{ opacity: .75 }}>
                <p style={{ margin: "0 0 4px", fontWeight: 700, fontSize: 14 }}>✓ {r.what_you_need}</p>
                <p style={{ margin: 0, fontSize: 12.5, color: "var(--ch-text-dim)" }}>
                  {TYPE_LABEL[r.request_type]} · <Link href={`/creator-hub/${creator.slug}/videos/${videoSlug.get(r.video_id)}`}>{videoTitle.get(r.video_id) ?? "Video"}</Link>
                </p>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
