"use client";

import Link from "next/link";
import {usePathname} from "next/navigation";

const primary=[
  ["/analytics","Overview"],
  ["/analytics/offense","Offense"],
  ["/analytics/defense","Defense"],
  ["/analytics/players","Players"],
] as const;

const secondary=[
  ["/analytics/national","National"],
  ["/analytics/trends","Trends"],
  ["/analytics/staff","Staff & Scheme"],
] as const;

const isActive=(path:string,href:string)=>href==="/analytics"?path==="/analytics":path.startsWith(href);

export function AnalyticsNav(){
  const path=usePathname();
  return <nav className="analytics-subnav" aria-label="Analytics navigation">
    <div className="analytics-subnav-primary">
      {primary.map(([href,label])=><Link key={href} href={href} className={isActive(path,href)?"active":""}>{label}</Link>)}
      <details className="analytics-more">
        <summary>More</summary>
        <div>{secondary.map(([href,label])=><Link key={href} href={href} className={isActive(path,href)?"active":""}>{label}</Link>)}</div>
      </details>
    </div>
  </nav>;
}
