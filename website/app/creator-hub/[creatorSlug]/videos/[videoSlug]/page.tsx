import Link from "next/link";
import { notFound } from "next/navigation";
import { requireCreatorForSlug } from "../../../actions";
import {
  getAttachmentsForVideo,
  getRequestsForVideo,
  getResearchForCreator,
  getSectionsForVideo,
  getVideoBySlug,
  getVisualsForCreator,
  type CreatorAttachment,
  type CreatorRequest,
} from "../../../../../lib/creator-hub/db";
import { StatusBadge } from "../../StatusBadge";
import { Disclosure } from "../../Disclosure";
import { VisualCard } from "../../VisualCard";
import { SectionEditor } from "./SectionEditor";
import { AttachExisting } from "./AttachExisting";
import { StatusSelect } from "./StatusSelect";
import { createRequestAction, createSectionAction, removeAttachmentAction, updateRequestStatusAction, updateVideoAction } from "../../workspace-actions";

export const dynamic = "force-dynamic";

function AttachmentsBlock({
  attachments,
  research,
  visuals,
  videoId,
}: {
  attachments: CreatorAttachment[];
  research: Map<number, { id: number; title: string; summary: string }>;
  visuals: Map<number, { id: number; title: string; image_url: string; takeaway: string }>;
  videoId: number;
}) {
  if (attachments.length === 0) return null;
  return (
    <div className="ch-attach-grid" style={{ marginTop: 12 }}>
      {attachments.map((a) => {
        if (a.kind === "research" && a.research_id) {
          const r = research.get(a.research_id);
          if (!r) return null;
          return (
            <div key={a.id} className="ch-attach-card">
              <b>{r.title}</b>
              {r.summary && <p>{r.summary}</p>}
              <div className="actions">
                <form action={removeAttachmentAction}>
                  <input type="hidden" name="videoId" value={videoId} />
                  <input type="hidden" name="attachmentId" value={a.id} />
                  <button type="submit">Remove</button>
                </form>
              </div>
            </div>
          );
        }
        if (a.kind === "visual" && a.visual_id) {
          const v = visuals.get(a.visual_id);
          if (!v) return null;
          return (
            <VisualCard
              key={a.id}
              visual={v as any}
              onRemove={
                <form action={removeAttachmentAction}>
                  <input type="hidden" name="videoId" value={videoId} />
                  <input type="hidden" name="attachmentId" value={a.id} />
                  <button type="submit">Remove</button>
                </form>
              }
            />
          );
        }
        return null;
      })}
    </div>
  );
}

function RequestsBlock({ requests }: { requests: CreatorRequest[] }) {
  if (requests.length === 0) return null;
  return (
    <div style={{ marginTop: 12 }}>
      {requests.map((r) => (
        <span key={r.id} className={`ch-request-chip${r.status === "completed" ? " completed" : ""}`}>
          {r.status === "completed" ? "✓" : "⏳"} {r.what_you_need.slice(0, 60)}{r.what_you_need.length > 60 ? "…" : ""}
          {r.status !== "completed" && (
            <form action={updateRequestStatusAction} style={{ display: "inline" }}>
              <input type="hidden" name="requestId" value={r.id} />
              <input type="hidden" name="status" value="completed" />
              <button type="submit" style={{ background: "none", border: "none", cursor: "pointer", padding: 0, marginLeft: 6, font: "inherit", textDecoration: "underline" }}>mark done</button>
            </form>
          )}
        </span>
      ))}
    </div>
  );
}

function RequestForm({ videoId, sectionId }: { videoId: number; sectionId?: number }) {
  return (
    <Disclosure trigger="+ Request Research" title="Request research">
      <form action={createRequestAction}>
        <input type="hidden" name="videoId" value={videoId} />
        {sectionId != null && <input type="hidden" name="sectionId" value={sectionId} />}
        <div className="ch-field"><label>What do you need?</label><textarea className="ch-textarea" name="what_you_need" rows={2} required autoFocus /></div>
        <div className="ch-field"><label>What are you trying to prove?</label><textarea className="ch-textarea" name="what_proving" rows={2} /></div>
        <div className="ch-field">
          <label>Type</label>
          <select className="ch-select" name="request_type">
            <option value="analytics">Analytics</option>
            <option value="chart">Chart</option>
            <option value="research">Research</option>
            <option value="fact_check">Fact check</option>
          </select>
        </div>
        <button type="submit" className="ch-btn ch-btn-primary">Send to Carter</button>
      </form>
    </Disclosure>
  );
}

export default async function VideoOutlinePage({
  params,
}: {
  params: Promise<{ creatorSlug: string; videoSlug: string }>;
}) {
  const { creatorSlug, videoSlug } = await params;
  const creator = await requireCreatorForSlug(creatorSlug);
  const video = await getVideoBySlug(creator.id, videoSlug);
  if (!video) notFound();

  const [sections, attachments, requests, researchList, visualsList] = await Promise.all([
    getSectionsForVideo(video.id),
    getAttachmentsForVideo(video.id),
    getRequestsForVideo(video.id),
    getResearchForCreator(creator.id),
    getVisualsForCreator(creator.id),
  ]);

  const researchMap = new Map(researchList.map((r) => [r.id, r]));
  const visualsMap = new Map(visualsList.map((v) => [v.id, v]));

  const wholeVideoAttachments = attachments.filter((a) => a.section_id === null);
  const wholeVideoRequests = requests.filter((r) => r.section_id === null);

  return (
    <>
      <Link href={`/creator-hub/${creator.slug}/videos`} className="ch-btn ch-btn-ghost ch-btn-sm" style={{ marginBottom: 18, display: "inline-flex" }}>← All videos</Link>

      <div className="ch-outline-head">
        <div className="status-row">
          <StatusBadge status={video.status} />
          <StatusSelect videoId={video.id} status={video.status} />
        </div>
        <h1>{video.title}</h1>
        <span className="updated">Last edited {new Date(video.updated_at).toLocaleString()}</span>
        {video.hook && <p className="ch-outline-hook">{video.hook}</p>}

        <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap" }}>
          <Disclosure trigger="Edit Outline" title="Edit video">
            <form action={updateVideoAction}>
              <input type="hidden" name="videoId" value={video.id} />
              <div className="ch-field"><label>Title</label><input className="ch-input" name="title" defaultValue={video.title} required /></div>
              <div className="ch-field"><label>Thesis</label><textarea className="ch-textarea" name="thesis" rows={2} defaultValue={video.thesis} /></div>
              <div className="ch-field"><label>Hook</label><textarea className="ch-textarea" name="hook" rows={2} defaultValue={video.hook} /></div>
              <button type="submit" className="ch-btn ch-btn-primary">Save</button>
            </form>
          </Disclosure>
          <RequestForm videoId={video.id} />
          <AttachExisting videoId={video.id} sections={sections} research={researchList} visuals={visualsList} />
        </div>
      </div>

      {video.thesis && (
        <div className="ch-card ch-card-pad" style={{ marginBottom: 24 }}>
          <div className="ch-outline-subhead" style={{ marginTop: 0 }}>Thesis</div>
          <p style={{ margin: 0, fontSize: 14 }}>{video.thesis}</p>
        </div>
      )}

      <AttachmentsBlock attachments={wholeVideoAttachments} research={researchMap} visuals={visualsMap} videoId={video.id} />
      <RequestsBlock requests={wholeVideoRequests} />

      <div className="ch-outline-subhead" style={{ marginTop: 28 }}>Outline</div>

      {sections.map((section, index) => {
        const sectionAttachments = attachments.filter((a) => a.section_id === section.id);
        const sectionRequests = requests.filter((r) => r.section_id === section.id);
        return (
          <SectionEditor key={section.id} section={section} videoId={video.id} index={index} count={sections.length}>
            {(sectionAttachments.length > 0 || sectionRequests.length > 0) && (
              <div className="ch-outline-subhead">Analytics &amp; Visuals</div>
            )}
            <AttachmentsBlock attachments={sectionAttachments} research={researchMap} visuals={visualsMap} videoId={video.id} />
            <RequestsBlock requests={sectionRequests} />
            <div style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
              <RequestForm videoId={video.id} sectionId={section.id} />
              <AttachExisting videoId={video.id} sections={sections} research={researchList} visuals={visualsList} defaultSectionId={section.id} />
            </div>
          </SectionEditor>
        );
      })}

      <Disclosure trigger="+ Add Section" title="New section">
        <form action={createSectionAction}>
          <input type="hidden" name="videoId" value={video.id} />
          <div className="ch-field"><label>Section title</label><input className="ch-input" name="title" required autoFocus /></div>
          <button type="submit" className="ch-btn ch-btn-primary">Add section</button>
        </form>
      </Disclosure>
    </>
  );
}
