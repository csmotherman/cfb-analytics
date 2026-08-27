import Link from "next/link";
import { requireCreatorForSlug } from "../actions";
import {
  getNotesForCreator,
  getRequestsForCreator,
  getResearchForCreator,
  getVideosForCreator,
  getVisualsForCreator,
} from "../../../lib/creator-hub/db";
import { StatusBadge } from "./StatusBadge";
import { Disclosure } from "./Disclosure";
import { createNoteAction, createRequestAction, createVideoAction } from "./workspace-actions";

export const dynamic = "force-dynamic";

function timeAgo(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(ms / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "yesterday";
  if (days < 7) return `${days}d ago`;
  return new Date(iso).toLocaleDateString();
}

export default async function CreatorHome({ params }: { params: Promise<{ creatorSlug: string }> }) {
  const { creatorSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);

  const [videos, requests, research, visuals, notes] = await Promise.all([
    getVideosForCreator(creator.id),
    getRequestsForCreator(creator.id),
    getResearchForCreator(creator.id),
    getVisualsForCreator(creator.id),
    getNotesForCreator(creator.id),
  ]);

  const activeVideos = videos.filter((v) => v.status !== "archived" && v.status !== "published").slice(0, 6);
  const weekAgo = Date.now() - 1000 * 60 * 60 * 24 * 7;
  const recentlyCompleted = requests.filter((r) => r.status === "completed" && r.completed_at && new Date(r.completed_at).getTime() > weekAgo);
  const recentResearch = research.filter((r) => new Date(r.created_at).getTime() > weekAgo);
  const recentVisuals = visuals.filter((v) => new Date(v.created_at).getTime() > weekAgo);
  const carterNotes = notes.filter((n) => n.author === "carter" && new Date(n.created_at).getTime() > weekAgo);
  const hasReadyForYou = recentlyCompleted.length + recentResearch.length + recentVisuals.length + carterNotes.length > 0;

  const recentItems = [
    ...research.slice(0, 4).map((r) => ({ kind: "research" as const, id: r.id, title: r.title, updated: r.updated_at })),
    ...visuals.slice(0, 4).map((v) => ({ kind: "visual" as const, id: v.id, title: v.title, updated: v.updated_at })),
  ].sort((a, b) => new Date(b.updated).getTime() - new Date(a.updated).getTime()).slice(0, 6);

  return (
    <>
      <div className="ch-page-head">
        <div>
          <h1>{creator.name}</h1>
        </div>
        <div className="ch-page-actions">
          <Disclosure trigger="+ New Video Outline" title="New video outline" primary>
            <form action={createVideoAction}>
              <div className="ch-field">
                <label>Working title</label>
                <input className="ch-input" name="title" required autoFocus />
              </div>
              <div className="ch-field">
                <label>Main idea / thesis</label>
                <textarea className="ch-textarea" name="thesis" rows={2} />
              </div>
              <div className="ch-field">
                <label>Hook</label>
                <textarea className="ch-textarea" name="hook" rows={2} />
              </div>
              <button type="submit" className="ch-btn ch-btn-primary">Create video</button>
            </form>
          </Disclosure>
          <Disclosure trigger="+ Request" title="Request research">
            <form action={createRequestAction}>
              <div className="ch-field">
                <label>Which video?</label>
                <select className="ch-select" name="videoId" required>
                  {videos.map((v) => <option key={v.id} value={v.id}>{v.title}</option>)}
                </select>
              </div>
              <div className="ch-field">
                <label>What do you need?</label>
                <textarea className="ch-textarea" name="what_you_need" rows={2} required />
              </div>
              <div className="ch-field">
                <label>What are you trying to prove?</label>
                <textarea className="ch-textarea" name="what_proving" rows={2} />
              </div>
              <div className="ch-field">
                <label>Type</label>
                <select className="ch-select" name="request_type">
                  <option value="analytics">Analytics</option>
                  <option value="chart">Chart</option>
                  <option value="research">Research</option>
                  <option value="fact_check">Fact check</option>
                </select>
              </div>
              <button type="submit" className="ch-btn ch-btn-primary" disabled={videos.length === 0}>Send to Carter</button>
              {videos.length === 0 && <p className="hint" style={{ marginTop: 8 }}>Create a video first.</p>}
            </form>
          </Disclosure>
          <Disclosure trigger="+ Quick Note" title="Quick note">
            <form action={createNoteAction}>
              <div className="ch-field">
                <textarea className="ch-textarea" name="body" rows={3} required autoFocus placeholder="Loose thought worth remembering..." />
              </div>
              <input type="hidden" name="author" value="creator" />
              <button type="submit" className="ch-btn ch-btn-primary">Save note</button>
            </form>
          </Disclosure>
        </div>
      </div>

      <section className="ch-section">
        <div className="ch-section-head">
          <h2>Active Videos</h2>
          <Link href={`/creator-hub/${creator.slug}/videos`} className="count">View all →</Link>
        </div>
        {activeVideos.length === 0 ? (
          <div className="ch-empty">No active videos yet. Start one above.</div>
        ) : (
          <div className="ch-video-list">
            {activeVideos.map((v) => (
              <Link key={v.id} href={`/creator-hub/${creator.slug}/videos/${v.slug}`} className="ch-card ch-video-card">
                <div className="ch-video-card-main">
                  <p className="ch-video-card-title">{v.title} <StatusBadge status={v.status} /></p>
                  <div className="ch-video-card-meta"><span>Updated {timeAgo(v.updated_at)}</span></div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {hasReadyForYou && (
        <section className="ch-section">
          <div className="ch-section-head"><h2>Ready For You</h2></div>
          <div className="ch-card ch-card-pad">
            <ul className="ch-talking-points">
              {recentlyCompleted.length > 0 && <li>{recentlyCompleted.length} research request{recentlyCompleted.length === 1 ? "" : "s"} completed</li>}
              {recentResearch.length > 0 && <li>{recentResearch.length} new research item{recentResearch.length === 1 ? "" : "s"} added</li>}
              {recentVisuals.length > 0 && <li>{recentVisuals.length} new chart{recentVisuals.length === 1 ? "" : "s"} added</li>}
              {carterNotes.length > 0 && <li>{carterNotes.length} note{carterNotes.length === 1 ? "" : "s"} from Carter</li>}
            </ul>
          </div>
        </section>
      )}

      <section className="ch-section">
        <div className="ch-section-head">
          <h2>Recent Research &amp; Visuals</h2>
          <Link href={`/creator-hub/${creator.slug}/research`} className="count">Libraries →</Link>
        </div>
        {recentItems.length === 0 ? (
          <div className="ch-empty">Nothing yet.</div>
        ) : (
          <div className="ch-attach-grid">
            {recentItems.map((item) => (
              <Link
                key={`${item.kind}-${item.id}`}
                href={`/creator-hub/${creator.slug}/${item.kind === "research" ? "research" : "visuals"}`}
                className="ch-attach-card"
              >
                <b>{item.title}</b>
                <p>{item.kind === "research" ? "Research" : "Visual"} · {timeAgo(item.updated)}</p>
              </Link>
            ))}
          </div>
        )}
      </section>

      <section className="ch-section">
        <div className="ch-section-head">
          <h2>Ideas / Quick Notes</h2>
          <Link href={`/creator-hub/${creator.slug}/notes`} className="count">View all →</Link>
        </div>
        {notes.length === 0 ? (
          <div className="ch-empty">No notes yet.</div>
        ) : (
          <div className="ch-video-list">
            {notes.slice(0, 4).map((n) => (
              <div key={n.id} className="ch-card ch-note-card">
                <p>{n.body}</p>
                <div className="meta"><span>{n.author === "carter" ? "Carter" : creator.name} · {timeAgo(n.created_at)}</span></div>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
