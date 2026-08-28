import type { ReactNode } from "react";

export function Visual16x9Frame({ title, source, children }: { title: string; source: string; children: ReactNode }) {
  return (
    <div className="ch-viz-frame">
      <div className="ch-viz-frame-inner">
        <div className="ch-viz-title">{title}</div>
        <div className="ch-viz-body">{children}</div>
        <div className="ch-viz-source">{source}</div>
      </div>
    </div>
  );
}
