"use client";

import { Disclosure } from "../../Disclosure";
import { attachExistingAction } from "../../workspace-actions";
import type { CreatorResearch, CreatorVideoSection, CreatorVisual } from "../../../../../lib/creator-hub/db";

export function AttachExisting({
  videoId,
  sections,
  research,
  visuals,
  defaultSectionId,
}: {
  videoId: number;
  sections: CreatorVideoSection[];
  research: CreatorResearch[];
  visuals: CreatorVisual[];
  defaultSectionId?: number;
}) {
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      <Disclosure trigger="+ Add Research" title="Attach existing research">
        {research.length === 0 ? (
          <p className="hint">No research in the library yet.</p>
        ) : (
          <form action={attachExistingAction}>
            <input type="hidden" name="videoId" value={videoId} />
            <input type="hidden" name="kind" value="research" />
            <div className="ch-field">
              <label>Which research?</label>
              <select className="ch-select" name="itemId" required>
                {research.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
              </select>
            </div>
            <div className="ch-field">
              <label>Attach to</label>
              <select className="ch-select" name="sectionId" defaultValue={defaultSectionId ?? ""}>
                <option value="">Whole video</option>
                {sections.map((s) => <option key={s.id} value={s.id}>{s.title}</option>)}
              </select>
            </div>
            <button type="submit" className="ch-btn ch-btn-primary">Attach</button>
          </form>
        )}
      </Disclosure>

      <Disclosure trigger="+ Add Visual" title="Attach existing visual">
        {visuals.length === 0 ? (
          <p className="hint">No visuals in the library yet.</p>
        ) : (
          <form action={attachExistingAction}>
            <input type="hidden" name="videoId" value={videoId} />
            <input type="hidden" name="kind" value="visual" />
            <div className="ch-field">
              <label>Which visual?</label>
              <select className="ch-select" name="itemId" required>
                {visuals.map((v) => <option key={v.id} value={v.id}>{v.title}</option>)}
              </select>
            </div>
            <div className="ch-field">
              <label>Attach to</label>
              <select className="ch-select" name="sectionId" defaultValue={defaultSectionId ?? ""}>
                <option value="">Whole video</option>
                {sections.map((s) => <option key={s.id} value={s.id}>{s.title}</option>)}
              </select>
            </div>
            <button type="submit" className="ch-btn ch-btn-primary">Attach</button>
          </form>
        )}
      </Disclosure>
    </div>
  );
}
