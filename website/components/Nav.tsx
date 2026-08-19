"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { siteConfig } from "../lib/site-config";

const links = [{ href: "/", label: "HOME" },{ href: "/team", label: "TEAM" },{ href: "/games", label: "GAMES" },{ href: "/analytics", label: "ANALYTICS" },{ href: "/recruiting", label: "RECRUITING" },{ href: "/stories", label: "STORIES" },{ href: "/history", label: "HISTORY" }];
const mobile = [{ href: "/", label: "HOME" },{ href: "/games", label: "GAMES" },{ href: "/team", label: "TEAM" },{ href: "/recruiting", label: "RECRUITS" },{ href: "/stories", label: "STORIES" }];
function active(path: string, href: string) { return href === "/" ? path === "/" : path === href || path.startsWith(`${href}/`); }

export function Nav() { const path = usePathname(); return <><header className="site-header"><nav className="shell app-nav" aria-label="Primary"><Link className="brand" href="/"><span className="brand-mark">S</span><strong>{siteConfig.shortName}</strong></Link><div className="desktop-nav">{links.map((link) => <Link className={active(path, link.href) ? "active" : ""} href={link.href} key={link.href}>{link.label}</Link>)}</div><div className="nav-actions"><Link href="/predictions" className="ask-link">ASK MICHIGAN</Link><span className="profile-dot" aria-label="Profile coming soon" /></div></nav></header><nav className="mobile-bottom-nav" aria-label="Mobile">{mobile.map((link) => <Link className={active(path, link.href) ? "active" : ""} href={link.href} key={link.href}>{link.label}</Link>)}</nav></>; }
