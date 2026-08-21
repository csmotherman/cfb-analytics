"use client";

import Image from "next/image";
import Link from "next/link";
import {usePathname} from "next/navigation";
import {useEffect,useState} from "react";
import {teamLogoUrl} from "../lib/team-assets";

const desktopLinks=[["/","Home"],["/team","Team"],["/schedule","Schedule"],["/analytics","Analytics"]] as const;
const mobileLinks=[["/","Home"],["/team","Team"],["/schedule","Schedule"],["/analytics","Analytics"]] as const;
const moreLinks=[
  {href:"/articles",label:"News & Analysis",meta:"Stories, previews and notebooks"},
  {href:"/polls",label:"Fan Polls",meta:"Vote and see where fans stand"},
  {href:"/metrics",label:"Metrics",meta:"Definitions for site analytics"},
  {href:"/methodology",label:"Methodology",meta:"How ratings and grades are built"},
  {href:"/new-additions",label:"New Additions",meta:"Freshmen and transfers joining Michigan"},
] as const;

const active=(path:string,href:string)=>href==="/"?path==="/":path.startsWith(href);

function Icon({label}:{label:string}){
  if(label==="Home")return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 10 9-7 9 7v10h-6v-6H9v6H3z"/></svg>;
  if(label==="Team")return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><path d="M2 20c0-4 2-7 6-7s6 3 6 7M10 20c0-4 2-7 6-7s6 3 6 7"/></svg>;
  if(label==="Schedule")return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></svg>;
  if(label==="Analytics")return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>;
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/></svg>;
}

export function SiteNav(){
  const path=usePathname();
  const [moreOpen,setMoreOpen]=useState(false);

  useEffect(()=>{setMoreOpen(false)},[path]);
  useEffect(()=>{
    if(!moreOpen)return;
    const onKey=(event:KeyboardEvent)=>{if(event.key==="Escape")setMoreOpen(false)};
    document.addEventListener("keydown",onKey);
    document.body.classList.add("more-drawer-open");
    return()=>{document.removeEventListener("keydown",onKey);document.body.classList.remove("more-drawer-open")};
  },[moreOpen]);

  return <>
    <header className="site-nav mock-site-nav"><div className="wrap nav-inner mock-nav-inner">
      <Link href="/" className="mock-wordmark" aria-label="Michigan Football Focus home">
        <img src={teamLogoUrl(130,128)} alt="Michigan" width={52} height={52} className="nav-michigan-logo"/>
        <Image src="/brand/michigan-football-focus.png" alt="Michigan Football Focus" width={240} height={72} priority className="nav-brand-logo"/>
      </Link>
      <nav className="desktop-links" aria-label="Primary navigation">{desktopLinks.map(([href,label])=><Link key={href} href={href} className={active(path,href)?"active":""}>{label}</Link>)}</nav>
      <button type="button" className={`mock-menu more-trigger${moreOpen?" active":""}`} aria-label="Open more navigation" aria-expanded={moreOpen} aria-controls="more-drawer" onClick={()=>setMoreOpen(open=>!open)}>
        <svg viewBox="0 0 28 28" aria-hidden="true"><path d="M5 8h18"/><path className="menu-accent" d="M5 14h18"/><path d="M5 20h18"/></svg>
      </button>
    </div></header>

    <nav className="bottom-nav mock-bottom-nav" aria-label="Mobile primary navigation">
      {mobileLinks.map(([href,label])=><Link key={href} href={href} className={active(path,href)?"active":""}><Icon label={label}/><span>{label}</span></Link>)}
      <button type="button" className={moreOpen?"active":""} aria-expanded={moreOpen} aria-controls="more-drawer" onClick={()=>setMoreOpen(open=>!open)}><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/></svg><span>More</span></button>
    </nav>

    <div className={`more-drawer-layer${moreOpen?" open":""}`} aria-hidden={!moreOpen}>
      <button className="more-drawer-backdrop" aria-label="Close more navigation" tabIndex={moreOpen?0:-1} onClick={()=>setMoreOpen(false)}/>
      <aside id="more-drawer" className="more-drawer" role="dialog" aria-modal="true" aria-label="More navigation">
        <header className="more-drawer-header"><div><span>EXPLORE</span><h2>MORE MICHIGAN</h2></div><button type="button" aria-label="Close more navigation" onClick={()=>setMoreOpen(false)}>×</button></header>
        <div className="more-drawer-links">
          {moreLinks.map((item,index)=><Link href={item.href} key={item.href} onClick={()=>setMoreOpen(false)}><span>{String(index+1).padStart(2,"0")}</span><div><strong>{item.label}</strong><small>{item.meta}</small></div><b aria-hidden="true">›</b></Link>)}
        </div>
        <footer className="more-drawer-footer"><span>MICHIGAN FOOTBALL FOCUS</span><small>Everything else, without leaving the page.</small></footer>
      </aside>
    </div>
  </>;
}
