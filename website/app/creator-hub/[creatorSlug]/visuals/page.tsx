import { requireCreatorForSlug } from "../../actions";
import { getVisualsForCreator, getVideosForCreator, getAttachmentsForVideo } from "../../../../lib/creator-hub/db";
import { Disclosure } from "../Disclosure";
import { VisualCard } from "../VisualCard";
import { AddToVideoForm } from "../AddToVideoForm";
import { LibraryTabs } from "../LibraryTabs";
import { createVisualAction } from "../workspace-actions";

export const dynamic = "force-dynamic";

export default async function VisualsLibraryPage({ params }: { params: Promise<{ creatorSlug: string }> }) {
  const { creatorSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);
  const [visuals, videos] = await Promise.all([getVisualsForCreator(creator.id), getVideosForCreator(creator.id)]);

  return (
    <>
      <LibraryTabs creatorSlug={creator.slug} active="visuals" />
      <div className="ch-page-head">
        <div><h1>Visuals</h1><p>Charts and graphics, ready to put on screen.</p></div>
        <Disclosure trigger="+ New Visual" primary>
          <form action={createVisualAction}>
            <div className="ch-field"><label>Title</label><input className="ch-input" name="title" required autoFocus /></div>
            <div className="ch-field"><label>Image URL</label><input className="ch-input" name="image_url" placeholder="https://…" /></div>
            <div className="ch-field"><label>Why it matters</label><textarea className="ch-textarea" name="takeaway" rows={2} /></div>
            <div className="ch-field"><label>Suggested talking point</label><textarea className="ch-textarea" name="suggested_talking_point" rows={2} /></div>
            <div className="ch-field"><label>Source</label><input className="ch-input" name="source" /></div>
            <button type="submit" className="ch-btn ch-btn-primary">Save visual</button>
          </form>
        </Disclosure>
      </div>

      {visuals.length === 0 ? <div className="ch-empty">No visuals saved yet.</div> : (
        <div className="ch-attach-grid">
          {visuals.map((v) => (
            <div key={v.id}>
              <VisualCard visual={v} />
              <div style={{ marginTop: 8 }}>
                <AddToVideoForm kind="visual" itemId={v.id} videos={videos} creatorSlug={creator.slug} />
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
