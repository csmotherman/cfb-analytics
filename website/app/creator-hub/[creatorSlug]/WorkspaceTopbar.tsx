"use client";

import { usePathname } from "next/navigation";
import { lockCreator } from "../actions";

export function WorkspaceTopbar({ creatorSlug, creatorName }: { creatorSlug: string; creatorName: string }) {
  const pathname = usePathname();
  const base = `/creator-hub/${creatorSlug}`;
  const links: [string, string][] = [
    ["Home", base],
    ["Videos", `${base}/videos`],
    ["Game Room", `${base}/games`],
    ["Scouting", `${base}/scouting`],
    ["Requests", `${base}/requests`],
  ];
  const libraryActive = pathname?.startsWith(`${base}/library`);

  return (
    <div className="ch-topbar">
      <div className="ch-topbar-inner">
        <div className="ch-topbar-brand">{creatorName}<small>Creator Hub</small></div>
        <nav className="ch-topbar-nav">
          {links.map(([label, href]) => {
            const active = href === base ? pathname === base : pathname?.startsWith(href);
            return (
              <a key={href} href={href} className={active ? "active" : ""}>{label}</a>
            );
          })}
          <a href={`${base}/library/research`} className={`ch-topbar-library${libraryActive ? " active" : ""}`}>Library</a>
        </nav>
        <div className="ch-topbar-actions">
          <form action={lockCreator}>
            <button type="submit" className="ch-topbar-lock">Lock</button>
          </form>
        </div>
      </div>
    </div>
  );
}
