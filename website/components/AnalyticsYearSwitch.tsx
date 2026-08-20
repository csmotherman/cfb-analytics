"use client";

import Link from "next/link";
import {useLayoutEffect,useRef} from "react";

const years=Array.from({length:17},(_,i)=>2010+i);

export function AnalyticsYearSwitch({year}:{year:number}){
  const scrollerRef=useRef<HTMLDivElement|null>(null);

  useLayoutEffect(()=>{
    const scroller=scrollerRef.current;
    if(!scroller)return;

    const centerActive=()=>{
      const active=scroller.querySelector<HTMLElement>("a.active");
      if(!active)return;
      const left=active.offsetLeft+active.offsetWidth/2-scroller.clientWidth/2;
      scroller.scrollLeft=Math.max(0,left);
    };

    centerActive();
    const frame=requestAnimationFrame(centerActive);
    const timer=window.setTimeout(centerActive,80);
    const observer=new ResizeObserver(centerActive);
    observer.observe(scroller);

    return()=>{
      cancelAnimationFrame(frame);
      window.clearTimeout(timer);
      observer.disconnect();
    };
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
          >
            <span>{y}</span>
            {y===2026&&<small>TBD</small>}
          </Link>;
        })}
      </div>
    </div>
  </nav>;
}
