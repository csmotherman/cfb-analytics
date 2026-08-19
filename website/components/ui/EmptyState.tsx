import type { ReactNode } from "react";
export function EmptyState({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return <section className="empty-state"><span>{eyebrow}</span><h2>{title}</h2>{children && <p>{children}</p>}</section>;
}
