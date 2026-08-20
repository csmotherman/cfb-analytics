"use client";

import Image from "next/image";
import Link from "next/link";
import {usePathname} from "next/navigation";
import {teamLogoUrl} from "../lib/team-assets";

const desktopLinks=[["/team","Team"],["/schedule","Schedule"],["/recruiting","Recruiting"],["/analytics","Analytics"],["/articles","News"]] as const;
const mobileLinks=[["/","Home"],["/team","Team"],["/schedule","Schedule"],["/recruiting","Recruiting"]] as const;

const active=(path:string,href:string)=>href==="/"?path==="/":path.startsWith(href);

function Icon({label}:{label:string}){
  if(label==="Home")return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 10 9-7 9 7v10h-6v-6H9v6H3z"/></svg>;
  if(label==="Team")return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M2 20c0-4 2-7 6-7s6 3 6 7M10 20c0-4 2-7 6-7s6 3 6 7"/></svg>;
  if(label==="Schedule")return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></svg>;
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/></svg>;
}

export function SiteNav(){
  const path=usePathname();
  return <>
    <header className="site-nav mock-site-nav"><div className="wrap nav-inner mock-nav-inner">
      <Link href="/" className="mock-wordmark" aria-label="Michigan Football Focus home">
        <img src={teamLogoUrl(130,128)} alt="Michigan" width={52} height={52} className="nav-michigan-logo"/>
        <Image src="/brand/michigan-football-focus.png" alt="Michigan Football Focus" width={240} height={72} priority className="nav-brand-logo"/>
      </Link>
      <nav className="desktop-links" aria-label="Primary navigation">{desktopLinks.map(([href,label])=><Link key={href} href={href} className={active(path,href)?"active":""}>{label}</Link>)}</nav>
      <Link href="/more" className="mock-menu" aria-label="Open menu">
        <svg viewBox="0 0 28 28" aria-hidden="true">
          <path d="M5 8h18"/>
          <path className="menu-accent" d="M5 14h18"/>
          <path d="M5 20h18"/>
        </svg>
      </Link>
    </div></header>
    <nav className="bottom-nav mock-bottom-nav" aria-label="Mobile primary navigation">
      {mobileLinks.map(([href,label])=><Link key={href} href={href} className={active(path,href)?"active":""}><Icon label={label}/><span>{label}</span></Link>)}
      <Link href="/more" className={path.startsWith("/more")?"active":""}><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/></svg><span>More</span></Link>
    </nav>
  </>;
}
