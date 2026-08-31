"use client";

import { useState } from "react";

export function BlueprintActions({ src, filename }: { src: string; filename: string }) {
  const [status, setStatus] = useState<"idle" | "copying" | "copied" | "error">("idle");

  async function copyImage() {
    setStatus("copying");
    try {
      const res = await fetch(src);
      const blob = await res.blob();
      await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
      setStatus("copied");
    } catch {
      setStatus("error");
    }
    setTimeout(() => setStatus("idle"), 2200);
  }

  return (
    <div style={{ display: "flex", gap: 10, marginTop: 16, flexWrap: "wrap", alignItems: "center" }}>
      <button onClick={copyImage} className="button primary" style={{ minWidth: 0, cursor: "pointer" }}>
        {status === "copied" ? "COPIED ✓" : status === "copying" ? "COPYING…" : "COPY IMAGE"}
      </button>
      <a href={src} download={filename} className="button ghost" style={{ minWidth: 0 }}>DOWNLOAD PNG</a>
      {status === "error" && <span style={{ fontSize: 11, color: "#f2a08a" }}>Couldn&apos;t copy automatically — right-click (or long-press) the image above to save it instead.</span>}
    </div>
  );
}
