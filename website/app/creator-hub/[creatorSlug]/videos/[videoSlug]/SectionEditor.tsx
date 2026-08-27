"use client";

import { useState } from "react";
import type { CreatorVideoSection } from "../../../../../lib/creator-hub/db";
import { updateSectionAction, deleteSectionAction, moveSectionAction } from "../../workspace-actions";

export function SectionEditor({
  section,
  videoId,
  index,
  count,
  children,
}: {
  section: CreatorVideoSection;
  videoId: number;
  index: number;
  count: number;
  children: React.ReactNode;
}) {
  const [editing, setEditing] = useState(false);
  const points = section.talking_points.split("\n").map((p) => p.trim()).filter(Boolean);

  return (
    <div className="ch-card" style={{ marginBottom: 10 }}>
      <div className="ch-outline-section-head">
        <h3><span className="ch-outline-section-num">{index + 1}</span>{editing ? "Editing…" : section.title}</h3>
        <div style={{ display: "flex", gap: 6 }}>
          {!editing && (
            <>
              <form action={moveSectionAction}>
                <input type="hidden" name="videoId" value={videoId} />
                <input type="hidden" name="sectionId" value={section.id} />
                <input type="hidden" name="direction" value="up" />
                <button type="submit" className="ch-btn ch-btn-ghost ch-btn-sm" disabled={index === 0}>↑</button>
              </form>
              <form action={moveSectionAction}>
                <input type="hidden" name="videoId" value={videoId} />
                <input type="hidden" name="sectionId" value={section.id} />
                <input type="hidden" name="direction" value="down" />
                <button type="submit" className="ch-btn ch-btn-ghost ch-btn-sm" disabled={index === count - 1}>↓</button>
              </form>
              <button type="button" className="ch-btn ch-btn-ghost ch-btn-sm" onClick={() => setEditing(true)}>Edit</button>
            </>
          )}
        </div>
      </div>

      <div className="ch-outline-section-body">
        {editing ? (
          <form
            action={async (formData) => {
              await updateSectionAction(formData);
              setEditing(false);
            }}
          >
            <input type="hidden" name="videoId" value={videoId} />
            <input type="hidden" name="sectionId" value={section.id} />
            <div className="ch-field">
              <label>Section title</label>
              <input className="ch-input" name="title" defaultValue={section.title} required />
            </div>
            <div className="ch-field">
              <label>Talking points</label>
              <span className="hint">One per line</span>
              <textarea className="ch-textarea" name="talking_points" rows={5} defaultValue={section.talking_points} />
            </div>
            <div className="ch-field">
              <label>Notes</label>
              <textarea className="ch-textarea" name="notes" rows={3} defaultValue={section.notes} />
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button type="button" className="ch-btn" onClick={() => setEditing(false)}>Cancel</button>
              <button type="submit" className="ch-btn ch-btn-primary">Save</button>
              <form action={deleteSectionAction} style={{ marginLeft: "auto" }}>
                <input type="hidden" name="videoId" value={videoId} />
                <input type="hidden" name="sectionId" value={section.id} />
                <button type="submit" className="ch-btn ch-btn-danger ch-btn-sm">Delete section</button>
              </form>
            </div>
          </form>
        ) : (
          <>
            {points.length > 0 ? (
              <ul className="ch-talking-points">
                {points.map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            ) : (
              <p className="hint">No talking points yet.</p>
            )}
            {section.notes && <p style={{ marginTop: 10, color: "var(--ch-text-dim)", fontSize: 13 }}>{section.notes}</p>}
            {children}
          </>
        )}
      </div>
    </div>
  );
}
