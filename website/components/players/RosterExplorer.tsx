"use client";
import Link from "next/link";
import {useMemo,useState} from "react";
import type {MichiganPlayer} from "../../lib/michigan/types";

const classLabel=(year?:number|null)=>year===1?"Fr":year===2?"So":year===3?"Jr":year===4?"Sr":year===5?"Gr":"—";
const statusLabel=(status?:string|null)=>status==="FRESHMAN"?"Freshman":status==="TRANSFER"?"Transfer":"Returning";

export function RosterExplorer({players}:{players:MichiganPlayer[]}){
  const [query,setQuery]=useState("");
  const [position,setPosition]=useState("ALL");
  const [year,setYear]=useState("ALL");
  const [status,setStatus]=useState("ALL");
  const positions=["ALL",...Array.from(new Set(players.map(p=>p.position).filter(Boolean) as string[])).sort()];
  const shown=useMemo(()=>players.filter(p=>{
    const text=`${p.firstName} ${p.lastName} ${p.position??""} ${p.jersey??""} ${p.homeCity??""} ${p.homeState??""}`.toLowerCase();
    return (position==="ALL"||p.position===position)&&(year==="ALL"||String(p.year)===year)&&(status==="ALL"||p.rosterStatus===status)&&text.includes(query.trim().toLowerCase());
  }).sort((a,b)=>((a.position??"").localeCompare(b.position??""))||((Number(a.jersey)||999)-(Number(b.jersey)||999))||a.lastName.localeCompare(b.lastName)),[players,query,position,year,status]);

  return <section className="roster-directory">
    <div className="roster-directory-tools">
      <label className="roster-search"><span>SEARCH</span><input aria-label="Search roster" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Name, number, position, hometown..."/></label>
      <div className="roster-filter-row">
        <label><span>POSITION</span><select aria-label="Filter position" value={position} onChange={e=>setPosition(e.target.value)}>{positions.map(p=><option key={p} value={p}>{p==="ALL"?"All positions":p}</option>)}</select></label>
        <label><span>CLASS</span><select aria-label="Filter class" value={year} onChange={e=>setYear(e.target.value)}><option value="ALL">All classes</option><option value="1">Freshman</option><option value="2">Sophomore</option><option value="3">Junior</option><option value="4">Senior</option><option value="5">Graduate</option></select></label>
        <label><span>STATUS</span><select aria-label="Filter roster status" value={status} onChange={e=>setStatus(e.target.value)}><option value="ALL">All players</option><option value="RETURNING">Returning</option><option value="TRANSFER">Transfers</option><option value="FRESHMAN">Freshmen</option></select></label>
      </div>
      <div className="roster-directory-count"><b>{shown.length}</b><span>PLAYERS</span></div>
    </div>

    <div className="roster-directory-table" role="table" aria-label="Michigan roster directory">
      <div className="roster-directory-head" role="row"><span>PLAYER</span><span>POS</span><span>CLASS</span><span>STATUS</span><span>HOMETOWN</span><span></span></div>
      {shown.map(player=><Link href={`/players/${player.id}`} className="roster-directory-row" role="row" key={player.id}>
        <span className="roster-directory-player"><b>#{player.jersey??"—"}</b><strong>{player.firstName} {player.lastName}</strong></span>
        <span>{player.position??"ATH"}</span>
        <span>{classLabel(player.year)}</span>
        <span>{statusLabel(player.rosterStatus)}</span>
        <span>{[player.homeCity,player.homeState].filter(Boolean).join(", ")||"—"}</span>
        <span className="roster-directory-arrow">→</span>
      </Link>)}
    </div>
    {shown.length===0&&<div className="roster-directory-empty">No players match those filters.</div>}
  </section>;
}
