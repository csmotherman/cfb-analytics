import { requireCreatorForSlug } from "../../actions";
import { getNotesForCreator } from "../../../../lib/creator-hub/db";
import { Disclosure } from "../Disclosure";
import { LibraryTabs } from "../LibraryTabs";
import { createNoteAction, convertNoteToVideoAction } from "../workspace-actions";

export const dynamic = "force-dynamic";

function timeAgo(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return new Date(iso).toLocaleDateString();
}

export default async function NotesPage({ params }: { params: Promise<{ creatorSlug: string }> }) {
  const { creatorSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);
  const notes = await getNotesForCreator(creator.id);

  return (
    <>
      <LibraryTabs creatorSlug={creator.slug} active="notes" />
      <div className="ch-page-head">
        <div><h1>Notes</h1><p>Loose thoughts, not full outlines yet.</p></div>
        <Disclosure trigger="+ Quick Note" primary>
          <form action={createNoteAction}>
            <div className="ch-field">
              <textarea className="ch-textarea" name="body" rows={3} required autoFocus placeholder="Loose thought worth remembering..." />
            </div>
            <div className="ch-field">
              <label>Posted by</label>
              <select className="ch-select" name="author" defaultValue="creator">
                <option value="creator">{creator.name}</option>
                <option value="carter">Carter</option>
              </select>
            </div>
            <button type="submit" className="ch-btn ch-btn-primary">Save note</button>
          </form>
        </Disclosure>
      </div>

      {notes.length === 0 ? <div className="ch-empty">No notes yet.</div> : (
        <div className="ch-video-list">
          {notes.map((n) => (
            <div key={n.id} className="ch-card ch-note-card">
              <p>{n.body}</p>
              <div className="meta">
                <span>{n.author === "carter" ? "Carter" : creator.name} · {timeAgo(n.created_at)}</span>
                {!n.converted_video_id && (
                  <form action={convertNoteToVideoAction}>
                    <input type="hidden" name="noteId" value={n.id} />
                    <input type="hidden" name="title" value={n.body.slice(0, 60)} />
                    <button type="submit" className="ch-btn ch-btn-sm">Convert to video</button>
                  </form>
                )}
                {n.converted_video_id && <span style={{ color: "var(--ch-good)" }}>→ Converted</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
