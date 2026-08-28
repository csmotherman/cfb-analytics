import { neon } from "@neondatabase/serverless";

function connectionString(): string {
  const value = process.env.DATABASE_URL || process.env.POSTGRES_URL;
  if (!value) {
    throw new Error(
      "Creator Hub database is not configured: set DATABASE_URL or POSTGRES_URL " +
      "(populated automatically once a Postgres/Neon integration is attached to this Vercel project)."
    );
  }
  return value;
}

// Lazy singleton: throwing at import time (module load) would break every
// route in the app, including ones that never touch the database. Only
// throw once something actually tries to query.
let cached: ReturnType<typeof neon> | null = null;
export function sql() {
  if (!cached) cached = neon(connectionString());
  return cached;
}

export type Creator = {
  id: number;
  slug: string;
  name: string;
  pin_hash: string;
  pin_salt: string;
  created_at: string;
};

export type VideoStatus = "idea" | "draft" | "researching" | "ready" | "recorded" | "published" | "archived";

export type CreatorVideo = {
  id: number;
  creator_id: number;
  slug: string;
  title: string;
  thesis: string;
  hook: string;
  status: VideoStatus;
  created_at: string;
  updated_at: string;
};

export type CreatorVideoSection = {
  id: number;
  video_id: number;
  title: string;
  position: number;
  talking_points: string;
  notes: string;
  created_at: string;
  updated_at: string;
};

export type CreatorResearch = {
  id: number;
  creator_id: number;
  title: string;
  summary: string;
  source_url: string;
  body: string;
  created_at: string;
  updated_at: string;
};

export type CreatorVisual = {
  id: number;
  creator_id: number;
  title: string;
  image_url: string;
  takeaway: string;
  why_it_matters: string;
  suggested_talking_point: string;
  source: string;
  created_at: string;
  updated_at: string;
};

export type RequestType = "analytics" | "chart" | "research" | "fact_check";
export type RequestStatus = "open" | "in_progress" | "completed";

export type CreatorRequest = {
  id: number;
  creator_id: number;
  video_id: number;
  section_id: number | null;
  request_type: RequestType;
  what_you_need: string;
  what_proving: string;
  status: RequestStatus;
  created_at: string;
  completed_at: string | null;
};

export type NoteAuthor = "creator" | "carter";

export type CreatorNote = {
  id: number;
  creator_id: number;
  author: NoteAuthor;
  body: string;
  converted_video_id: number | null;
  game_id: number | null;
  created_at: string;
};

export type AttachmentKind = "research" | "visual" | "story";

export type CreatorAttachment = {
  id: number;
  video_id: number;
  section_id: number | null;
  kind: AttachmentKind;
  research_id: number | null;
  visual_id: number | null;
  game_id: number | null;
  story_id: string | null;
  created_at: string;
};

// ---- Creators ----

export async function getCreators(): Promise<Creator[]> {
  const rows = await sql()`select * from creators order by name asc`;
  return rows as Creator[];
}

export async function getCreatorBySlug(slug: string): Promise<Creator | null> {
  const rows = await sql()`select * from creators where slug = ${slug} limit 1`;
  return (rows as Creator[])[0] ?? null;
}

export async function getCreatorById(id: number): Promise<Creator | null> {
  const rows = await sql()`select * from creators where id = ${id} limit 1`;
  return (rows as Creator[])[0] ?? null;
}

// ---- Videos ----

export async function getVideosForCreator(creatorId: number): Promise<CreatorVideo[]> {
  const rows = await sql()`
    select * from creator_videos where creator_id = ${creatorId} order by updated_at desc
  `;
  return rows as CreatorVideo[];
}

export async function getVideoBySlug(creatorId: number, videoSlug: string): Promise<CreatorVideo | null> {
  const rows = await sql()`
    select * from creator_videos where creator_id = ${creatorId} and slug = ${videoSlug} limit 1
  `;
  return (rows as CreatorVideo[])[0] ?? null;
}

export async function getVideoById(id: number): Promise<CreatorVideo | null> {
  const rows = await sql()`select * from creator_videos where id = ${id} limit 1`;
  return (rows as CreatorVideo[])[0] ?? null;
}

// ---- Sections ----

export async function getSectionsForVideo(videoId: number): Promise<CreatorVideoSection[]> {
  const rows = await sql()`
    select * from creator_video_sections where video_id = ${videoId} order by position asc, id asc
  `;
  return rows as CreatorVideoSection[];
}

export async function getSectionById(id: number): Promise<CreatorVideoSection | null> {
  const rows = await sql()`select * from creator_video_sections where id = ${id} limit 1`;
  return (rows as CreatorVideoSection[])[0] ?? null;
}

// ---- Research / Visuals ----

export async function getResearchForCreator(creatorId: number): Promise<CreatorResearch[]> {
  const rows = await sql()`
    select * from creator_research where creator_id = ${creatorId} order by updated_at desc
  `;
  return rows as CreatorResearch[];
}

export async function getResearchById(id: number): Promise<CreatorResearch | null> {
  const rows = await sql()`select * from creator_research where id = ${id} limit 1`;
  return (rows as CreatorResearch[])[0] ?? null;
}

export async function getVisualsForCreator(creatorId: number): Promise<CreatorVisual[]> {
  const rows = await sql()`
    select * from creator_visuals where creator_id = ${creatorId} order by updated_at desc
  `;
  return rows as CreatorVisual[];
}

export async function getVisualById(id: number): Promise<CreatorVisual | null> {
  const rows = await sql()`select * from creator_visuals where id = ${id} limit 1`;
  return (rows as CreatorVisual[])[0] ?? null;
}

// ---- Requests ----

export async function getRequestsForCreator(creatorId: number): Promise<CreatorRequest[]> {
  const rows = await sql()`
    select * from creator_requests where creator_id = ${creatorId} order by created_at desc
  `;
  return rows as CreatorRequest[];
}

export async function getRequestsForVideo(videoId: number): Promise<CreatorRequest[]> {
  const rows = await sql()`
    select * from creator_requests where video_id = ${videoId} order by created_at desc
  `;
  return rows as CreatorRequest[];
}

export async function getRequestById(id: number): Promise<CreatorRequest | null> {
  const rows = await sql()`select * from creator_requests where id = ${id} limit 1`;
  return (rows as CreatorRequest[])[0] ?? null;
}

// ---- Notes ----

export async function getNotesForCreator(creatorId: number): Promise<CreatorNote[]> {
  const rows = await sql()`
    select * from creator_notes where creator_id = ${creatorId} order by created_at desc
  `;
  return rows as CreatorNote[];
}

// ---- Attachments ----

export async function getAttachmentsForVideo(videoId: number): Promise<CreatorAttachment[]> {
  const rows = await sql()`
    select * from creator_attachments where video_id = ${videoId} order by created_at asc
  `;
  return rows as CreatorAttachment[];
}

export async function getAttachmentById(id: number): Promise<CreatorAttachment | null> {
  const rows = await sql()`select * from creator_attachments where id = ${id} limit 1`;
  return (rows as CreatorAttachment[])[0] ?? null;
}

// ============================================================
// Writes
// ============================================================

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .slice(0, 60) || "untitled";
}

async function uniqueVideoSlug(creatorId: number, title: string): Promise<string> {
  const base = slugify(title);
  let candidate = base;
  let n = 2;
  // Small tables, small n -- a loop is simpler and clearer than a single
  // clever query here.
  while (await getVideoBySlug(creatorId, candidate)) {
    candidate = `${base}-${n}`;
    n += 1;
  }
  return candidate;
}

export async function createVideo(
  creatorId: number,
  data: { title: string; thesis?: string; hook?: string }
): Promise<CreatorVideo> {
  const slug = await uniqueVideoSlug(creatorId, data.title);
  const rows = await sql()`
    insert into creator_videos (creator_id, slug, title, thesis, hook, status)
    values (${creatorId}, ${slug}, ${data.title}, ${data.thesis ?? ""}, ${data.hook ?? ""}, 'idea')
    returning *
  `;
  return (rows as CreatorVideo[])[0];
}

export async function updateVideoStatus(videoId: number, status: VideoStatus): Promise<void> {
  await sql()`update creator_videos set status = ${status}, updated_at = now() where id = ${videoId}`;
}

export async function updateVideo(
  videoId: number,
  data: { title: string; thesis: string; hook: string }
): Promise<void> {
  await sql()`
    update creator_videos
    set title = ${data.title}, thesis = ${data.thesis}, hook = ${data.hook}, updated_at = now()
    where id = ${videoId}
  `;
}

export async function touchVideo(videoId: number): Promise<void> {
  await sql()`update creator_videos set updated_at = now() where id = ${videoId}`;
}

export async function createSection(videoId: number, title: string): Promise<CreatorVideoSection> {
  const [{ next }] = (await sql()`
    select coalesce(max(position), -1) + 1 as next from creator_video_sections where video_id = ${videoId}
  `) as { next: number }[];
  const rows = await sql()`
    insert into creator_video_sections (video_id, title, position)
    values (${videoId}, ${title}, ${next})
    returning *
  `;
  await touchVideo(videoId);
  return (rows as CreatorVideoSection[])[0];
}

export async function updateSection(
  sectionId: number,
  data: { title: string; talking_points: string; notes: string }
): Promise<CreatorVideoSection> {
  const rows = await sql()`
    update creator_video_sections
    set title = ${data.title}, talking_points = ${data.talking_points}, notes = ${data.notes}, updated_at = now()
    where id = ${sectionId}
    returning *
  `;
  return (rows as CreatorVideoSection[])[0];
}

export async function reorderSections(orderedIds: number[]): Promise<void> {
  for (let i = 0; i < orderedIds.length; i += 1) {
    await sql()`update creator_video_sections set position = ${i} where id = ${orderedIds[i]}`;
  }
}

export async function deleteSection(sectionId: number): Promise<void> {
  await sql()`delete from creator_video_sections where id = ${sectionId}`;
}

export async function createResearch(
  creatorId: number,
  data: { title: string; summary?: string; source_url?: string; body?: string }
): Promise<CreatorResearch> {
  const rows = await sql()`
    insert into creator_research (creator_id, title, summary, source_url, body)
    values (${creatorId}, ${data.title}, ${data.summary ?? ""}, ${data.source_url ?? ""}, ${data.body ?? ""})
    returning *
  `;
  return (rows as CreatorResearch[])[0];
}

export async function createVisual(
  creatorId: number,
  data: {
    title: string;
    image_url?: string;
    takeaway?: string;
    why_it_matters?: string;
    suggested_talking_point?: string;
    source?: string;
  }
): Promise<CreatorVisual> {
  const rows = await sql()`
    insert into creator_visuals (creator_id, title, image_url, takeaway, why_it_matters, suggested_talking_point, source)
    values (
      ${creatorId}, ${data.title}, ${data.image_url ?? ""}, ${data.takeaway ?? ""},
      ${data.why_it_matters ?? ""}, ${data.suggested_talking_point ?? ""}, ${data.source ?? ""}
    )
    returning *
  `;
  return (rows as CreatorVisual[])[0];
}

export async function createRequest(
  creatorId: number,
  data: {
    video_id: number;
    section_id: number | null;
    request_type: RequestType;
    what_you_need: string;
    what_proving?: string;
  }
): Promise<CreatorRequest> {
  const rows = await sql()`
    insert into creator_requests (creator_id, video_id, section_id, request_type, what_you_need, what_proving)
    values (
      ${creatorId}, ${data.video_id}, ${data.section_id}, ${data.request_type},
      ${data.what_you_need}, ${data.what_proving ?? ""}
    )
    returning *
  `;
  return (rows as CreatorRequest[])[0];
}

export async function updateRequestStatus(requestId: number, status: RequestStatus): Promise<void> {
  if (status === "completed") {
    await sql()`update creator_requests set status = ${status}, completed_at = now() where id = ${requestId}`;
  } else {
    await sql()`update creator_requests set status = ${status} where id = ${requestId}`;
  }
}

export async function createNote(creatorId: number, author: NoteAuthor, body: string, gameId: number | null = null): Promise<CreatorNote> {
  const rows = await sql()`
    insert into creator_notes (creator_id, author, body, game_id) values (${creatorId}, ${author}, ${body}, ${gameId}) returning *
  `;
  return (rows as CreatorNote[])[0];
}

export async function convertNoteToVideo(noteId: number, creatorId: number, title: string): Promise<CreatorVideo> {
  const video = await createVideo(creatorId, { title });
  await sql()`update creator_notes set converted_video_id = ${video.id} where id = ${noteId}`;
  return video;
}

export async function attachToVideo(data: {
  video_id: number;
  section_id: number | null;
  kind: AttachmentKind;
  research_id?: number | null;
  visual_id?: number | null;
  game_id?: number | null;
  story_id?: string | null;
}): Promise<CreatorAttachment> {
  const rows = await sql()`
    insert into creator_attachments (video_id, section_id, kind, research_id, visual_id, game_id, story_id)
    values (
      ${data.video_id}, ${data.section_id}, ${data.kind},
      ${data.kind === "research" ? data.research_id ?? null : null},
      ${data.kind === "visual" ? data.visual_id ?? null : null},
      ${data.kind === "story" ? data.game_id ?? null : null},
      ${data.kind === "story" ? data.story_id ?? null : null}
    )
    returning *
  `;
  await touchVideo(data.video_id);
  return (rows as CreatorAttachment[])[0];
}

export async function removeAttachment(attachmentId: number): Promise<void> {
  await sql()`delete from creator_attachments where id = ${attachmentId}`;
}
