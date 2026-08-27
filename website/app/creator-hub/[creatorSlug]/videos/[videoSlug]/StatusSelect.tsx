"use client";

import { updateVideoStatusAction } from "../../workspace-actions";

const OPTIONS: [string, string][] = [
  ["idea", "Idea"],
  ["draft", "Draft"],
  ["researching", "Researching"],
  ["ready", "Ready"],
  ["recorded", "Recorded"],
  ["published", "Published"],
  ["archived", "Archived"],
];

export function StatusSelect({ videoId, status }: { videoId: number; status: string }) {
  return (
    <form
      action={updateVideoStatusAction}
      onChange={(e) => (e.currentTarget as HTMLFormElement).requestSubmit()}
    >
      <input type="hidden" name="videoId" value={videoId} />
      <select className="ch-select" name="status" defaultValue={status} style={{ width: "auto", padding: "5px 9px", fontSize: 12 }}>
        {OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
      </select>
    </form>
  );
}
