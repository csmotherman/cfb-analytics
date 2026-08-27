"use client";

import { useState } from "react";

// Plain progressive-enhancement forms underneath -- this only toggles
// visibility client-side; the <form action={...}> still works with JS off.
export function Disclosure({
  trigger,
  title,
  children,
  primary,
}: {
  trigger: string;
  title?: string;
  children: React.ReactNode;
  primary?: boolean;
}) {
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button type="button" className={`ch-btn ${primary ? "ch-btn-primary" : ""}`} onClick={() => setOpen(true)}>
        {trigger}
      </button>
    );
  }

  return (
    <div className="ch-card ch-card-pad" style={{ marginBottom: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <strong style={{ fontSize: 14 }}>{title ?? trigger}</strong>
        <button type="button" className="ch-btn-ghost ch-btn ch-btn-sm" onClick={() => setOpen(false)}>Cancel</button>
      </div>
      {children}
    </div>
  );
}
