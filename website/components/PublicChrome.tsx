"use client";

import { usePathname } from "next/navigation";
import { SiteNav } from "./SiteNav";

// Creator Hub is a separate private application, not another public page --
// it supplies its own shell/nav in app/creator-hub/layout.tsx. The
// matchup graphic is a fullscreen, no-scroll fit-to-viewport page (see
// app/matchup-graphic/[gameId]/FitToScreen.tsx) -- the site nav and
// footer would eat into that budget and break the "no scrolling"
// guarantee, so it also supplies no shell. Everything else keeps the
// public site's nav + footer, unchanged.
export function PublicChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isCreatorHub = pathname?.startsWith("/creator-hub");
  const isMatchupGraphic = pathname?.startsWith("/matchup-graphic");

  if (isCreatorHub || isMatchupGraphic) return <>{children}</>;

  return (
    <>
      <SiteNav />
      <main>{children}</main>
      <footer>
        <div className="wrap footer-inner">
          <div><b>MICHIGAN FOOTBALL FOCUS</b><span>Michigan football, understood.</span></div>
          <nav aria-label="Footer">
            <a href="/articles">Articles</a>
            <a href="/new-additions">New Additions</a>
            <a href="/methodology">Methodology</a>
          </nav>
        </div>
      </footer>
    </>
  );
}
