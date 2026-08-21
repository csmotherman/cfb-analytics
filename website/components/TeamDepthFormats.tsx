"use client";

import Link from "next/link";
import {useMemo,useState} from "react";
import type {DepthSlot} from "../lib/michigan/depth-chart";
import type {MichiganPlayer} from "../lib/michigan/types";

type Unit="offense"|"defense"|"special";
type Props={offense:DepthSlot[];defense:DepthSlot[];specialists:DepthSlot[];format:1|2|3};

const yearLabel=(year?:number|null)=>["Fr","So","Jr","Sr","Gr"][Math.max(0,(year??1)-1)]??"—";
const fullName=(p:MichiganPlayer)=>`${p.firstName} ${p.lastName}`;

function UnitTabs({unit,setUnit}:{unit:Unit;setUnit:(u:Unit)=>void}){
  return <div className="tdf-unit-tabs" role="tablist" aria-label="Depth chart unit">
    <button type="button" className={unit==="offense"?"active":""} onClick={()=>setUnit("offense")}>OFFENSE</button>
    <button type="button" className={unit==="defense"?"active":""} onClick={()=>setUnit("defense")}>DEFENSE</button>
    <button type="button" className={unit==="special"?"active":""} onClick={()=>setUnit("special")}>SPECIAL</button>
  </div>;
}

function PlayerLine({player,rank}:{player:MichiganPlayer;rank:number}){
  return <Link className="tdf-player-line" href={`/players/${player.id}`}>
    <b>{rank}</b><span><strong>{fullName(player)}</strong><small>#{player.jersey??"—"} · {yearLabel(player.year)} · {player.position??"ATH"}</small></span><i>›</i>
  </Link>;
}

function FormatOne({slots}:{slots:DepthSlot[]}){
  const [selected,setSelected]=useState(0);
  const active=slots[selected]??slots[0];
  return <div className="tdf-format-one">
    <div className="tdf-field">
      <span className="tdf-endzone">MICHIGAN</span>
      <div className="tdf-field-grid">{slots.map((slot,index)=>{const first=slot.players[0];return <button type="button" key={`${slot.label}-${index}`} className={selected===index?"active":""} onClick={()=>setSelected(index)}><small>{slot.label}</small><strong>{first?`${first.firstName[0]}. ${first.lastName}`:"—"}</strong><span>#{first?.jersey??"—"}</span></button>})}</div>
    </div>
    {active&&<section className="tdf-selected-depth"><header><div><small>SELECTED POSITION</small><h3>{active.label}</h3></div><span>{active.players.length}-DEEP</span></header><div>{active.players.map((p,i)=><PlayerLine player={p} rank={i+1} key={p.id}/>)}</div></section>}
  </div>;
}

function FormatTwo({slots}:{slots:DepthSlot[]}){
  return <div className="tdf-format-two"><div className="tdf-list-head"><span>POS</span><span>PROJECTED DEPTH</span></div>{slots.map((slot,index)=><section className="tdf-depth-row" key={`${slot.label}-${index}`}><strong>{slot.label}</strong><div>{slot.players.map((p,i)=><Link href={`/players/${p.id}`} key={p.id} className={i===0?"starter":""}><b>{i===0?"1":"2"}</b><span>{fullName(p)}<small>#{p.jersey??"—"} · {yearLabel(p.year)}</small></span><i>›</i></Link>)}</div></section>)}</div>;
}

function FormatThree({slots}:{slots:DepthSlot[]}){
  return <div className="tdf-format-three"><div className="tdf-swipe-cue">SWIPE POSITIONS <span>→</span></div><div className="tdf-card-track">{slots.map((slot,index)=>{const first=slot.players[0];const backups=slot.players.slice(1);return <article className="tdf-position-card" key={`${slot.label}-${index}`}><header><span>{slot.label}</span><small>PROJECTED</small></header>{first&&<Link className="tdf-card-starter" href={`/players/${first.id}`}><small>FIRST TEAM</small><strong>{fullName(first)}</strong><span>#{first.jersey??"—"} · {yearLabel(first.year)} · {first.position??slot.label}</span><b>OPEN PROFILE ›</b></Link>}<div className="tdf-card-depth"><small>NEXT UP</small>{backups.length?backups.map((p,i)=><Link href={`/players/${p.id}`} key={p.id}><b>{i+2}</b><span><strong>{fullName(p)}</strong><small>#{p.jersey??"—"} · {yearLabel(p.year)}</small></span><i>›</i></Link>):<p>No listed reserve</p>}</div></article>})}</div></div>;
}

export default function TeamDepthFormats({offense,defense,specialists,format}:Props){
  const [unit,setUnit]=useState<Unit>("offense");
  const slots=useMemo(()=>unit==="offense"?offense:unit==="defense"?defense:specialists,[unit,offense,defense,specialists]);
  return <section className={`tdf-shell tdf-shell-${format}`}>
    <UnitTabs unit={unit} setUnit={setUnit}/>
    <div className="tdf-unit-meta"><span>{unit==="offense"?"PROJECTED OFFENSE":unit==="defense"?"PROJECTED DEFENSE":"SPECIAL TEAMS"}</span><small>{slots.length} POSITIONS · TAP PLAYERS FOR PROFILE</small></div>
    {format===1?<FormatOne slots={slots}/>:format===2?<FormatTwo slots={slots}/>:<FormatThree slots={slots}/>} 
  </section>;
}
