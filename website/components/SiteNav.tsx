"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [["/","Home"],["/team","Team"],["/team/depth-chart","Depth Chart"],["/schedule","Schedule"],["/recruiting","Recruiting"],["/analytics","Analytics"],["/history","History"]] as const;
const mobile = links.slice(0,4);
const active = (path:string,href:string) => {
  if (href === "/") return path === "/";
  if (href === "/team") return path === "/team" || path === "/team/roster" || path.startsWith("/team/positions/");
  return path.startsWith(href);
};

function MobileIcon({label}:{label:string}) {
  if(label === "Home") return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 10 8-6 8 6v9H4z"/><path d="M9 19v-6h6v6"/></svg>;
  if(label === "Team") return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="7" r="3"/><path d="M6 20c0-4 2-7 6-7s6 3 6 7"/></svg>;
  if(label === "Depth Chart") return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 3v18M20 3v18M4 7h16M4 17h16M8 12h8"/><circle cx="12" cy="12" r="2"/></svg>;
  return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></svg>;
}

export function SiteNav() {
  const path=usePathname();
  return <><header className="site-nav"><div className="nav-signal"/><div className="wrap nav-inner">
    <Link href="/" className="wordmark focus-wordmark" aria-label="SOAR Analytics home"><strong>SOAR</strong><span>ANALYTICS<small>MICHIGAN FOOTBALL FOCUS</small></span></Link>
    <nav className="desktop-links" aria-label="Primary navigation">{links.map(([href,label])=><Link key={href} href={href} className={active(path,href)?"active":""} aria-current={active(path,href)?"page":undefined}><span>{label}</span></Link>)}</nav>
    <Link className={`more-link${path.startsWith("/more")?" active":""}`} href="/more"><span>Explore</span><b>＋</b></Link>
  </div></header><nav className="bottom-nav" aria-label="Mobile primary navigation">
    {mobile.map(([href,label])=><Link key={href} href={href} className={active(path,href)?"active":""} aria-current={active(path,href)?"page":undefined}><MobileIcon label={label}/><span>{label}</span></Link>)}
    <Link href="/more" className={path.startsWith("/more")?"active":""}><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/></svg><span>More</span></Link>
  </nav></>;
}
