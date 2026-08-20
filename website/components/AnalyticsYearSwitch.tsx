"use client";

import Link from "next/link";
import {useEffect,useRef} from "react";

const years=Array.from({length:17},(_,i)=>2010+i);

export function AnalyticsYearSwitch({year}:{year:number}){
  const railRef=useRef<HTMLElement|null>(null);
  useEffect(()=>{
    const rail=railRef.current;
    const active=rail?.querySelector<HTMLElement>("a.active");
    if(!rail||!active)return;
    requestAnimationFrame(()=>active.scrollIntoView({behavior:"auto",block:"nearest",inline:"center"}));
  },[year]);

  return <nav ref={railRef} className="analytics-year-switch" aria-label="Analytics season">
    <span className="year-calendar" aria-hidden="true">▦</span>
    {years.map(y=>{
      const distance=Math.min(4,Math.abs(year-y));
      return <Link
        key={y}
        href={`/analytics?year=${y}`}
        className={year===y?"active":""}
        data-distance={distance}
        aria-current={year===y?"page":undefined}
      >{y}{y===2026&&<small>TBD</small>}</Link>;
    })}
  </nav>;
}
