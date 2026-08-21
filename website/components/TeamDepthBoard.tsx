"use client";

import Link from "next/link";
import {useState} from "react";

type DepthPlayer={id:string;name:string;jersey?:number|string|null;position?:string|null;year?:string|null;image?:string|null};
export type DepthRow={position:string;starter:DepthPlayer[];next:DepthPlayer[];battle?:boolean;note?:string};
type Props={offense:DepthRow[];defense:DepthRow[];special:DepthRow[]};

const Player=({player}: {player:DepthPlayer})=><Link href={`/players/${player.id}`} className="team-depth-player">{player.image?<img src={player.image} alt=""/>:<span className="team-depth-number">#{player.jersey??"—"}</span>}<span><strong>{player.name}</strong><small>#{player.jersey??"—"}{player.year?` · ${player.year}`:""}</small></span></Link>;

export default function TeamDepthBoard({offense,defense,special}:Props){
  const [tab,setTab]=useState<"offense"|"defense"|"special">("offense");
  const rows=tab==="offense"?offense:tab==="defense"?defense:special;
  return <section className="team-depth-board">
    <div className="team-depth-tabs" role="tablist" aria-label="Projected depth chart unit">
      <button type="button" className={tab==="offense"?"active":""} onClick={()=>setTab("offense")}>OFFENSE</button>
      <button type="button" className={tab==="defense"?"active":""} onClick={()=>setTab("defense")}>DEFENSE</button>
      <button type="button" className={tab==="special"?"active":""} onClick={()=>setTab("special")}>SPECIAL TEAMS</button>
    </div>
    <div className="team-depth-columns"><span>POSITION</span><span>PROJECTED FIRST</span><span>NEXT UP</span></div>
    <div className="team-depth-rows">{rows.map(row=><article key={row.position} className={row.battle?"battle":""}>
      <div className="team-depth-position"><strong>{row.position}</strong>{row.battle&&<small>BATTLE</small>}</div>
      <div className="team-depth-players">{row.starter.map(player=><Player key={player.id} player={player}/>)}</div>
      <div className="team-depth-players next">{row.next.map(player=><Player key={player.id} player={player}/>)}</div>
      {row.note&&<p>{row.note}</p>}
    </article>)}</div>
  </section>;
}
