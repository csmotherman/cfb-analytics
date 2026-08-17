"use client";

import { useState } from "react";

export function SharePrediction({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  async function share() {
    const url = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({ title: "CFB Model Prediction", text, url });
        return;
      } catch {
        // User cancellation should simply fall through to the copy option.
      }
    }
    await navigator.clipboard.writeText(`${text} ${url}`);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return <button className="share-button" onClick={share}>{copied ? "Copied" : "Share prediction"}</button>;
}
