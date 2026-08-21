"use client";

import Link from "next/link";
import {useMemo,useState} from "react";
import {teamLogoUrl} from "../lib/team-assets";

export type NewAdditionRow={
  id:string;
  firstName:string;
  lastName:string;
  position:string;
  jersey:number|null;
  classLabel:string;
  type:"FRESHMAN"|"TRANSFER";
  previousTeam:string|null;
  previousTeamId:number|null;
  recruitRating:number|null;
  stars:number|null;
  nationalRecruitRank:number|null;
};

type Props={freshmen:NewAdditionRow[];transfers:NewAdditionRow[]};

type FreshmanSort="rating-desc"|"rating-asc";

function Rating({player}:{player:NewAdditionRow}){
  if(player.recruitRating==null)return <div className="new-addition-rating unavailable"><strong>—</strong><small>RATING</small></div>;
  return <div className="new-addition-rating">
    <strong>{player.recruitRating.toFixed(4).replace(/^0/,"")}</strong>
    <small>{player.stars?`${player.stars}★`:"RATING"}{player.nationalRecruitRank?` · #${player.nationalRecruitRank}`:""}</small>
  </div>;
}

function Path({player}:{player:NewAdditionRow}){
  const freshman=player.type==="FRESHMAN";
  const origin=freshman?"HIGH SCHOOL":(player.previousTeam??"Previous team");
  return <div className="new-addition-path">
    <div className="new-addition-origin">
      {freshman?<span className="hs-badge">HS</span>:player.previousTeamId?<img src={teamLogoUrl(player.previousTeamId,64)} alt={`${origin} logo`}/>:<span className="hs-badge">—</span>}
      <small>{origin}</small>
    </div>
    <b>→</b>
    <div className="new-addition-origin michigan-destination"><img src={teamLogoUrl(130,64)} alt="Michigan logo"/><small>MICHIGAN</small></div>
  </div>;
}

export function NewAdditionsTabs({freshmen,transfers}:Props){
  const [tab,setTab]=useState<"freshmen"|"transfers">("freshmen");
  const [freshmanSort,setFreshmanSort]=useState<FreshmanSort>("rating-desc");

  const sortedFreshmen=useMemo(()=>[...freshmen].sort((a,b)=>{
    const aRating=a.recruitRating??-1;
    const bRating=b.recruitRating??-1;
    const ratingDiff=freshmanSort==="rating-desc"?bRating-aRating:aRating-bRating;
    return ratingDiff||`${a.lastName}${a.firstName}`.localeCompare(`${b.lastName}${b.firstName}`);
  }),[freshmen,freshmanSort]);

  const players=tab==="freshmen"?sortedFreshmen:transfers;

  return <section className="new-additions-directory">
    <div className="new-additions-tabs" role="tablist" aria-label="New addition type">
      <button type="button" role="tab" aria-selected={tab==="freshmen"} className={tab==="freshmen"?"active":""} onClick={()=>setTab("freshmen")}>FRESHMEN <span>{freshmen.length}</span></button>
      <button type="button" role="tab" aria-selected={tab==="transfers"} className={tab==="transfers"?"active":""} onClick={()=>setTab("transfers")}>TRANSFERS <span>{transfers.length}</span></button>
    </div>

    <div className="new-additions-toolbar">
      <div><span>{tab==="freshmen"?"2026 RECRUITING CLASS":"2026 TRANSFER CLASS"}</span><strong>{tab==="freshmen"?"Incoming freshmen":"Incoming transfers"}</strong></div>
      {tab==="freshmen"&&<button type="button" className="recruit-sort" onClick={()=>setFreshmanSort(sort=>sort==="rating-desc"?"rating-asc":"rating-desc")}>
        RECRUIT RATING <b>{freshmanSort==="rating-desc"?"HIGH → LOW":"LOW → HIGH"}</b>
      </button>}
    </div>

    <div className={`new-additions-head ${tab==="freshmen"?"freshman-head":"transfer-head"}`}>
      <span>PLAYER</span><span>CLASS</span>{tab==="freshmen"&&<span>RECRUIT RATING</span>}<span>PATH TO MICHIGAN</span>
    </div>

    <div className="new-additions-list">
      {players.map(player=><Link href={`/players/${player.id}`} key={player.id} className={`new-addition-row ${player.type==="FRESHMAN"?"freshman-row":"transfer-row"}`}>
        <div className="new-addition-player"><strong>{player.firstName} {player.lastName}</strong><small>{player.position}{player.jersey!=null?` · #${player.jersey}`:""}</small></div>
        <div className="new-addition-class"><strong>{player.classLabel}</strong><small>{player.type}</small></div>
        {player.type==="FRESHMAN"&&<Rating player={player}/>} 
        <Path player={player}/>
        <span className="new-addition-arrow">›</span>
      </Link>)}
    </div>
  </section>;
}
