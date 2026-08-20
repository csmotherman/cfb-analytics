"use client";

import Link from "next/link";
import {useEffect,useRef} from "react";

const years=Array.from({length:17},(_,i)=>2010+i);

export function AnalyticsYearSwitch({year}:{year:number}){
  const scrollerRef=useRef<HTMLDivElement|null>(null);

  useEffect(()=>{
    const scroller=scrollerRef.current;
    const active=scroller?.querySelector<HTMLElement>("a.active");
    if(!scroller||!active)return;

    const centerActive=()=>{
      const target=active.offsetLeft-(scroller.clientWidth-active.offsetWidth)/2;
      scroller.scrollTo({left:Math.max(0,target),behavior:"auto"});
    };

    const frame=requestAnimationFrame(centerActive);
    return()=>cancelAnimationFrame(frame);
  },[year]);

  return <nav className="analytics-year-wheel" aria-label="Analytics season">
    <span className="year-calendar" aria-hidden="true">▦</span>
    <div ref={scrollerRef} className="analytics-year-switch">
      <div className="analytics-year-track">
        {years.map(y=>{
          const distance=Math.min(5,Math.abs(year-y));
          return <Link
            key={y}
            href={`/analytics?year=${y}`}
            className={year===y?"active":""}
            data-distance={distance}
            aria-current={year===y?"page":undefined}
          >{y}{y===2026&&<small>TBD</small>}</Link>;
        })}
      </div>
    </div>
  </nav>;
}
