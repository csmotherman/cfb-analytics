import Link from "next/link";
import type { CreatorVideo } from "../../../lib/creator-hub/db";
import { attachExistingAction } from "./workspace-actions";

export function AddToVideoForm({
  kind,
  itemId,
  videos,
  creatorSlug,
}: {
  kind: "research" | "visual";
  itemId: number;
  videos: CreatorVideo[];
  creatorSlug: string;
}) {
  if (videos.length === 0) {
    return <Link href={`/creator-hub/${creatorSlug}/videos`} className="ch-btn ch-btn-sm">Create a video first</Link>;
  }

  return (
    <form action={attachExistingAction} style={{ display: "flex", gap: 6 }}>
      <input type="hidden" name="kind" value={kind} />
      <input type="hidden" name="itemId" value={itemId} />
      <select className="ch-select" name="videoId" style={{ fontSize: 12, padding: "6px 8px" }} required defaultValue="">
        <option value="" disabled>Add to video…</option>
        {videos.map((v) => <option key={v.id} value={v.id}>{v.title}</option>)}
      </select>
      <button type="submit" className="ch-btn ch-btn-sm">Add</button>
    </form>
  );
}
