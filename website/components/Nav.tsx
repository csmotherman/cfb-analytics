"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const primaryLinks = [
  { href: "/play", label: "Play" },
  { href: "/rankings", label: "Rankings" },
  { href: "/archive", label: "Archive" },
  { href: "/about", label: "How it works" },
];

function active(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

function HomeIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 10.7 12 3.8l8.5 6.9v9.1h-5.2v-5.6H8.7v5.6H3.5z" /></svg>; }
function PickIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.8h10a2 2 0 0 1 2 2v12.4a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5.8a2 2 0 0 1 2-2Zm2.1 8 2 2 4-4" /></svg>; }
function RankIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19V9m7 10V5m7 14v-7" /></svg>; }
function ArchiveIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7.5h16v12H4zm-1-3h18v3H3zm6 7h6" /></svg>; }

export function Nav() {
  const pathname = usePathname();
  return (
    <>
      <header className="site-header">
        <nav className="nav shell" aria-label="Primary navigation">
          <Link className="brand" href="/" aria-label="Beat the Model home">
            <span className="brand-mark">B</span>
            <span className="brand-copy"><strong>BEAT THE MODEL</strong><small>College football, picked.</small></span>
          </Link>
          <div className="nav-links">
            {primaryLinks.map((link) => (
              <Link key={link.href} href={link.href} className={`${active(pathname, link.href) ? "active" : ""}${link.href === "/play" ? " nav-play" : ""}`}>{link.label}</Link>
            ))}
          </div>
          <Link className="mobile-info-link" href="/about" aria-label="How Beat the Model works">How it works</Link>
        </nav>
      </header>
      <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
        <Link href="/" className={active(pathname, "/") ? "active" : ""}><HomeIcon /><span>Home</span></Link>
        <Link href="/play" className={active(pathname, "/play") ? "active" : ""}><PickIcon /><span>Play</span></Link>
        <Link href="/rankings" className={active(pathname, "/rankings") ? "active" : ""}><RankIcon /><span>Rankings</span></Link>
        <Link href="/archive" className={active(pathname, "/archive") ? "active" : ""}><ArchiveIcon /><span>Archive</span></Link>
      </nav>
    </>
  );
}
