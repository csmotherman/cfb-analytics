"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { getSessionCreator } from "../../../lib/creator-hub/auth";
import {
  attachToVideo,
  createNote,
  createRequest,
  createResearch,
  createSection,
  createVideo,
  createVisual,
  convertNoteToVideo,
  deleteSection,
  getAttachmentById,
  getRequestById,
  getResearchById,
  getSectionById,
  getVideoById,
  getVisualById,
  removeAttachment,
  reorderSections,
  getSectionsForVideo,
  updateRequestStatus,
  updateSection,
  updateVideo,
  updateVideoStatus,
  type AttachmentKind,
  type NoteAuthor,
  type RequestType,
  type VideoStatus,
} from "../../../lib/creator-hub/db";
import { findGameStoryPackByGameId, findStory } from "../../../lib/creator-hub/game-story";

// Every action re-derives the creator from the session cookie -- never
// trusts a creatorId submitted from the client -- so one creator's session
// can never write into another creator's workspace.
async function requireCreator() {
  const creator = await getSessionCreator();
  if (!creator) redirect("/creator-hub");
  return creator;
}

function revalidateWorkspace(creatorSlug: string, videoSlug?: string) {
  const base = `/creator-hub/${creatorSlug}`;
  revalidatePath(base);
  revalidatePath(`${base}/videos`);
  revalidatePath(`${base}/requests`);
  revalidatePath(`${base}/research`);
  revalidatePath(`${base}/visuals`);
  revalidatePath(`${base}/notes`);
  revalidatePath(`${base}/games`);
  if (videoSlug) revalidatePath(`${base}/videos/${videoSlug}`);
}

export async function createVideoAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const title = String(formData.get("title") || "").trim();
  if (!title) redirect(`/creator-hub/${creator.slug}/videos`);

  const video = await createVideo(creator.id, {
    title,
    thesis: String(formData.get("thesis") || ""),
    hook: String(formData.get("hook") || ""),
  });
  revalidateWorkspace(creator.slug);
  redirect(`/creator-hub/${creator.slug}/videos/${video.slug}`);
}

export async function updateVideoAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const videoId = Number(formData.get("videoId"));
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);

  await updateVideo(videoId, {
    title: String(formData.get("title") || video.title),
    thesis: String(formData.get("thesis") || ""),
    hook: String(formData.get("hook") || ""),
  });
  revalidateWorkspace(creator.slug, video.slug);
  redirect(`/creator-hub/${creator.slug}/videos/${video.slug}`);
}

export async function updateVideoStatusAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const videoId = Number(formData.get("videoId"));
  const status = String(formData.get("status")) as VideoStatus;
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);

  await updateVideoStatus(videoId, status);
  revalidateWorkspace(creator.slug, video.slug);
}

export async function createSectionAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const videoId = Number(formData.get("videoId"));
  const title = String(formData.get("title") || "").trim();
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id || !title) redirect(`/creator-hub/${creator.slug}`);

  await createSection(videoId, title);
  revalidateWorkspace(creator.slug, video.slug);
}

export async function updateSectionAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const sectionId = Number(formData.get("sectionId"));
  const videoId = Number(formData.get("videoId"));
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);
  const section = await getSectionById(sectionId);
  if (!section || section.video_id !== videoId) redirect(`/creator-hub/${creator.slug}`);

  await updateSection(sectionId, {
    title: String(formData.get("title") || "Untitled section"),
    talking_points: String(formData.get("talking_points") || ""),
    notes: String(formData.get("notes") || ""),
  });
  revalidateWorkspace(creator.slug, video.slug);
}

export async function deleteSectionAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const sectionId = Number(formData.get("sectionId"));
  const videoId = Number(formData.get("videoId"));
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);
  const section = await getSectionById(sectionId);
  if (!section || section.video_id !== videoId) redirect(`/creator-hub/${creator.slug}`);

  await deleteSection(sectionId);
  revalidateWorkspace(creator.slug, video.slug);
}

export async function moveSectionAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const videoId = Number(formData.get("videoId"));
  const sectionId = Number(formData.get("sectionId"));
  const direction = String(formData.get("direction")); // "up" | "down"
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);

  const sections = await getSectionsForVideo(videoId);
  const ids = sections.map((s) => s.id);
  const index = ids.indexOf(sectionId);
  const swapWith = direction === "up" ? index - 1 : index + 1;
  if (index === -1 || swapWith < 0 || swapWith >= ids.length) {
    revalidateWorkspace(creator.slug, video.slug);
    return;
  }
  [ids[index], ids[swapWith]] = [ids[swapWith], ids[index]];
  await reorderSections(ids);
  revalidateWorkspace(creator.slug, video.slug);
}

export async function createResearchAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const title = String(formData.get("title") || "").trim();
  if (!title) redirect(`/creator-hub/${creator.slug}/research`);

  await createResearch(creator.id, {
    title,
    summary: String(formData.get("summary") || ""),
    source_url: String(formData.get("source_url") || ""),
    body: String(formData.get("body") || ""),
  });
  revalidateWorkspace(creator.slug);
  redirect(`/creator-hub/${creator.slug}/research`);
}

export async function createVisualAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const title = String(formData.get("title") || "").trim();
  if (!title) redirect(`/creator-hub/${creator.slug}/visuals`);

  await createVisual(creator.id, {
    title,
    image_url: String(formData.get("image_url") || ""),
    takeaway: String(formData.get("takeaway") || ""),
    why_it_matters: String(formData.get("why_it_matters") || ""),
    suggested_talking_point: String(formData.get("suggested_talking_point") || ""),
    source: String(formData.get("source") || ""),
  });
  revalidateWorkspace(creator.slug);
  redirect(`/creator-hub/${creator.slug}/visuals`);
}

export async function createRequestAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const videoId = Number(formData.get("videoId"));
  const sectionIdRaw = formData.get("sectionId");
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);

  await createRequest(creator.id, {
    video_id: videoId,
    section_id: sectionIdRaw ? Number(sectionIdRaw) : null,
    request_type: String(formData.get("request_type") || "analytics") as RequestType,
    what_you_need: String(formData.get("what_you_need") || ""),
    what_proving: String(formData.get("what_proving") || ""),
  });
  revalidateWorkspace(creator.slug, video.slug);
  redirect(`/creator-hub/${creator.slug}/requests`);
}

export async function updateRequestStatusAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const requestId = Number(formData.get("requestId"));
  const status = String(formData.get("status")) as "open" | "in_progress" | "completed";
  const request = await getRequestById(requestId);
  if (!request || request.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);

  await updateRequestStatus(requestId, status);
  const video = await getVideoById(request.video_id);
  revalidateWorkspace(creator.slug, video?.slug);
}

export async function createNoteAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const body = String(formData.get("body") || "").trim();
  if (!body) redirect(`/creator-hub/${creator.slug}/notes`);

  const author = (String(formData.get("author") || "creator") as NoteAuthor);
  await createNote(creator.id, author, body);
  revalidateWorkspace(creator.slug);
  redirect(`/creator-hub/${creator.slug}/notes`);
}

export async function convertNoteToVideoAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const noteId = Number(formData.get("noteId"));
  const title = String(formData.get("title") || "").trim() || "Untitled video";

  const video = await convertNoteToVideo(noteId, creator.id, title);
  revalidateWorkspace(creator.slug);
  redirect(`/creator-hub/${creator.slug}/videos/${video.slug}`);
}

export async function attachExistingAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const videoId = Number(formData.get("videoId"));
  const sectionIdRaw = formData.get("sectionId");
  const kind = String(formData.get("kind")) as AttachmentKind;
  const itemId = Number(formData.get("itemId"));
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);
  if (kind === "research") {
    const research = await getResearchById(itemId);
    if (!research || research.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);
  } else {
    const visual = await getVisualById(itemId);
    if (!visual || visual.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);
  }

  await attachToVideo({
    video_id: videoId,
    section_id: sectionIdRaw ? Number(sectionIdRaw) : null,
    kind,
    research_id: kind === "research" ? itemId : null,
    visual_id: kind === "visual" ? itemId : null,
  });
  revalidateWorkspace(creator.slug, video.slug);
  redirect(`/creator-hub/${creator.slug}/videos/${video.slug}`);
}

export async function removeAttachmentAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const attachmentId = Number(formData.get("attachmentId"));
  const videoId = Number(formData.get("videoId"));
  const video = await getVideoById(videoId);
  if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}`);
  const attachment = await getAttachmentById(attachmentId);
  if (!attachment || attachment.video_id !== videoId) redirect(`/creator-hub/${creator.slug}`);

  await removeAttachment(attachmentId);
  revalidateWorkspace(creator.slug, video.slug);
}

export async function addStoryToVideoAction(formData: FormData): Promise<void> {
  const creator = await requireCreator();
  const gameId = Number(formData.get("gameId"));
  const storyId = String(formData.get("storyId") || "");
  const existingVideoId = formData.get("videoId");
  const newVideoTitle = String(formData.get("newVideoTitle") || "").trim();

  // The story's content (headline, evidence, video angle) is re-derived
  // from the published game-stories.json artifact server-side, never
  // trusted from the client -- the form only submits gameId/storyId.
  const pack = findGameStoryPackByGameId(gameId);
  const story = pack ? findStory(pack, storyId) : null;
  if (!pack || !story) redirect(`/creator-hub/${creator.slug}/games`);

  let video;
  if (existingVideoId && Number(existingVideoId) > 0) {
    video = await getVideoById(Number(existingVideoId));
    if (!video || video.creator_id !== creator.id) redirect(`/creator-hub/${creator.slug}/games`);
  } else {
    const title = newVideoTitle || `Michigan vs ${pack.opponent}: What Actually Happened`;
    video = await createVideo(creator.id, { title, thesis: story.whyItMatters });
  }

  const talkingPoints = [story.videoAngle, ...story.evidence].join("\n");
  const section = await createSection(video.id, story.headline);
  await updateSection(section.id, { title: story.headline, talking_points: talkingPoints, notes: "" });
  await attachToVideo({
    video_id: video.id,
    section_id: section.id,
    kind: "story",
    game_id: gameId,
    story_id: storyId,
  });

  revalidateWorkspace(creator.slug, video.slug);
  redirect(`/creator-hub/${creator.slug}/videos/${video.slug}`);
}
