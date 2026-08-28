import { requireCreatorForSlug } from "../../actions";
import { getResearchForCreator, getVideosForCreator, getAttachmentsForVideo } from "../../../../lib/creator-hub/db";
import { Disclosure } from "../Disclosure";
import { AddToVideoForm } from "../AddToVideoForm";
import { LibraryTabs } from "../LibraryTabs";
import { createResearchAction } from "../workspace-actions";

export const dynamic = "force-dynamic";

export default async function ResearchLibraryPage({ params }: { params: Promise<{ creatorSlug: string }> }) {
  const { creatorSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);
  const [research, videos] = await Promise.all([getResearchForCreator(creator.id), getVideosForCreator(creator.id)]);

  const usageByResearch = new Map<number, string[]>();
  const allAttachments = await Promise.all(videos.map((v) => getAttachmentsForVideo(v.id)));
  allAttachments.forEach((atts, i) => {
    atts.forEach((a) => {
      if (a.kind === "research" && a.research_id) {
        const list = usageByResearch.get(a.research_id) ?? [];
        list.push(videos[i].title);
        usageByResearch.set(a.research_id, list);
      }
    });
  });

  return (
    <>
      <LibraryTabs creatorSlug={creator.slug} active="research" />
      <div className="ch-page-head">
        <div><h1>Research</h1><p>Reusable research, attachable to any video.</p></div>
        <Disclosure trigger="+ New Research" primary>
          <form action={createResearchAction}>
            <div className="ch-field"><label>Title</label><input className="ch-input" name="title" required autoFocus /></div>
            <div className="ch-field"><label>Summary</label><textarea className="ch-textarea" name="summary" rows={2} /></div>
            <div className="ch-field"><label>Source URL</label><input className="ch-input" name="source_url" /></div>
            <div className="ch-field"><label>Full notes</label><textarea className="ch-textarea" name="body" rows={4} /></div>
            <button type="submit" className="ch-btn ch-btn-primary">Save research</button>
          </form>
        </Disclosure>
      </div>

      {research.length === 0 ? <div className="ch-empty">No research saved yet.</div> : (
        <div className="ch-attach-grid">
          {research.map((r) => {
            const usedIn = usageByResearch.get(r.id) ?? [];
            return (
              <div key={r.id} className="ch-card ch-card-pad">
                <b style={{ fontSize: 14 }}>{r.title}</b>
                {r.summary && <p style={{ fontSize: 12.5, color: "var(--ch-text-dim)", margin: "6px 0" }}>{r.summary}</p>}
                {r.source_url && <p style={{ fontSize: 11.5 }}><a href={r.source_url} target="_blank" rel="noreferrer" style={{ color: "var(--ch-navy)" }}>Source ↗</a></p>}
                {usedIn.length > 0 && (
                  <p style={{ fontSize: 11.5, color: "var(--ch-text-faint)", marginTop: 8 }}>Used in: {usedIn.join(", ")}</p>
                )}
                <div style={{ marginTop: 10 }}>
                  <AddToVideoForm kind="research" itemId={r.id} videos={videos} creatorSlug={creator.slug} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}
