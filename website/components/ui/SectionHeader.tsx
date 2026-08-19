import type { ReactNode } from "react";
export function SectionHeader({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return <header className="section-header"><div><span>{eyebrow}</span><h2>{title}</h2></div>{children && <p>{children}</p>}</header>;
}
