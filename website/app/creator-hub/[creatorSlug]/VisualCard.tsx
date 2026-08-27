"use client";

import { useState } from "react";
import type { CreatorVisual } from "../../../lib/creator-hub/db";

export function VisualCard({ visual, onRemove }: { visual: CreatorVisual; onRemove?: React.ReactNode }) {
  const [fullscreen, setFullscreen] = useState(false);

  return (
    <div className="ch-attach-card" style={{ padding: 0, overflow: "hidden" }}>
      {visual.image_url && (
        <div className="ch-visual-frame" style={{ aspectRatio: "16/9", borderRadius: "8px 8px 0 0" }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={visual.image_url} alt={visual.title} />
        </div>
      )}
      <div style={{ padding: 12 }}>
        <b>{visual.title}</b>
        {visual.takeaway && <p><b style={{ fontWeight: 700 }}>Why it matters:</b> {visual.takeaway}</p>}
        <div className="actions">
          {visual.image_url && <button type="button" onClick={() => setFullscreen(true)}>Full screen</button>}
          {onRemove}
        </div>
      </div>

      {fullscreen && (
        <div className="ch-visual-fullscreen" onClick={() => setFullscreen(false)}>
          <button className="close" onClick={() => setFullscreen(false)}>Close ✕</button>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={visual.image_url} alt={visual.title} onClick={(e) => e.stopPropagation()} />
        </div>
      )}
    </div>
  );
}
