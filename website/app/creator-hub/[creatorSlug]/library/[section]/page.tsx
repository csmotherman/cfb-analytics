import { notFound } from "next/navigation";
import { requireCreatorForSlug } from "../../../actions";
import {
  getAttachmentsForVideo,
  getNotesForCreator,
  getResearchForCreator,
  getVideosForCreator,
  getVisualsForCreator,
} from "../../../../../lib/creator-hub/db";
import { AddToVideoForm } from "../../AddToVideoForm";
import { Disclosure } from "../../Disclosure";
import { LibraryTabs } from "../../LibraryTabs";
import { VisualCard } from "../../VisualCard";
import {
  convertNoteToVideoAction,
  createNoteAction,
  createResearchAction,
  createVisualAction,
} from "../../workspace-actions";

export const dynamic = "force-dynamic";

type LibrarySection = "research" | "visuals" | "notes";
type CreatorView = { id: number; slug: string; name: string };

const LIBRARY_SECTIONS = new Set<LibrarySection>(["research", "visuals", "notes"]);

function timeAgo(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return new Date(iso).toLocaleDateString();
}

async function ResearchPanel({ creator }: { creator: CreatorView }) {
  const [research, videos] = await Promise.all([
    getResearchForCreator(creator.id),
    getVideosForCreator(creator.id),
  ]);

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

async function VisualsPanel({ creator }: { creator: CreatorView }) {
  const [visuals, videos] = await Promise.all([
    getVisualsForCreator(creator.id),
    getVideosForCreator(creator.id),
  ]);

  return (
    <>
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

async function NotesPanel({ creator }: { creator: CreatorView }) {
  const notes = await getNotesForCreator(creator.id);

  return (
    <>
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

export default async function LibraryPage({
  params,
}: {
  params: Promise<{ creatorSlug: string; section: string }>;
}) {
  const { creatorSlug, section } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);

  if (!LIBRARY_SECTIONS.has(section as LibrarySection)) notFound();
  const active = section as LibrarySection;
  const creatorView: CreatorView = { id: creator.id, slug: creator.slug, name: creator.name };

  return (
    <>
      <LibraryTabs creatorSlug={creator.slug} active={active} />
      {active === "research" && <ResearchPanel creator={creatorView} />}
      {active === "visuals" && <VisualsPanel creator={creatorView} />}
      {active === "notes" && <NotesPanel creator={creatorView} />}
    </>
  );
}
