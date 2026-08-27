"use client";

import Link from "next/link";
import {useLayoutEffect,useRef} from "react";

const years=Array.from({length:17},(_,i)=>2010+i);

export function AnalyticsYearSwitch({year,basePath="/analytics"}:{year:number;basePath?:string}){
  const railRef=useRef<HTMLElement|null>(null);

  useLayoutEffect(()=>{
    const rail=railRef.current;
    if(!rail)return;

    const positionYear=()=>{
      const target=rail.querySelector<HTMLElement>(`a[data-year="${year}"]`);
      if(!target)return;
      const left=target.offsetLeft-(rail.clientWidth-target.offsetWidth)/2;
      rail.scrollLeft=Math.max(0,left);
    };

    positionYear();
    const frame=requestAnimationFrame(positionYear);
    const timer=window.setTimeout(positionYear,60);
    return()=>{cancelAnimationFrame(frame);window.clearTimeout(timer)};
  },[year]);

  return <nav ref={railRef} className="analytics-year-switch" aria-label="Analytics season">
    <span className="year-calendar" aria-hidden="true">▦</span>
    {years.map(y=><Link
      key={y}
      href={`${basePath}?year=${y}`}
      data-year={y}
      className={year===y?"active":""}
      aria-current={year===y?"page":undefined}
    >{y}{y===2026&&<small>TBD</small>}</Link>)}
  </nav>;
}
