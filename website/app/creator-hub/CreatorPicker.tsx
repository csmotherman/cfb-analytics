"use client";

import { useState } from "react";
import { unlockCreator } from "./actions";

type CreatorOption = { id: number; slug: string; name: string };

export function CreatorPicker({
  creators,
  initialErrorSlug,
}: {
  creators: CreatorOption[];
  initialErrorSlug: string | null;
}) {
  const [open, setOpen] = useState<CreatorOption | null>(
    initialErrorSlug ? creators.find((c) => c.slug === initialErrorSlug) ?? null : null
  );

  return (
    <>
      <div className="ch-creator-grid">
        {creators.map((creator) => (
          <button key={creator.id} type="button" className="ch-creator-card" onClick={() => setOpen(creator)}>
            <b>{creator.name}</b>
            <span>Open workspace →</span>
          </button>
        ))}
      </div>

      {open && (
        <div className="ch-pin-backdrop" onClick={() => setOpen(null)}>
          <div className="ch-pin-modal" onClick={(e) => e.stopPropagation()}>
            <h2>{open.name}</h2>
            <p>Enter your 4-digit PIN to open this workspace.</p>
            <form action={unlockCreator}>
              <input type="hidden" name="creatorId" value={open.id} />
              <input
                className="ch-input ch-pin-input"
                type="password"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={4}
                name="pin"
                autoFocus
                required
              />
              {initialErrorSlug === open.slug && <p className="ch-pin-error">Incorrect PIN. Try again.</p>}
              <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
                <button type="button" className="ch-btn" onClick={() => setOpen(null)}>Cancel</button>
                <button type="submit" className="ch-btn ch-btn-primary" style={{ flex: 1 }}>Unlock</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
