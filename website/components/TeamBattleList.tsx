"use client";

import {useState} from "react";

export type TeamBattle={position:string;title:string;players:string[];detail:string};

export default function TeamBattleList({battles}:{battles:TeamBattle[]}){
  const [open,setOpen]=useState<number|null>(null);
  return <div className="team-battle-list">
    {battles.map((battle,index)=>{
      const active=open===index;
      return <article className={active?"active":""} key={`${battle.position}-${index}`}>
        <button type="button" onClick={()=>setOpen(active?null:index)} aria-expanded={active}>
          <span><small>{battle.position}</small><strong>{battle.title}</strong><em>{battle.players.join(" · ")}</em></span>
          <b>{active?"−":"+"}</b>
        </button>
        {active&&<div className="team-battle-detail"><p>{battle.detail}</p></div>}
      </article>;
    })}
  </div>;
}
