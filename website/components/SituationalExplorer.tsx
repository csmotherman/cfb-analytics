"use client";

import {useMemo,useState} from "react";
import type {SituationalRow} from "../lib/data";

type Props={team:string;season:number;rows:SituationalRow[]};

type Totals={
  plays:number;successes:number;yards:number;firstDowns:number;rushPlays:number;passPlays:number;
  rushSuccesses:number;passSuccesses:number;rushYards:number;passYards:number;
  explosiveEligiblePlays:number;explosivePlays:number;conversionAttempts:number;conversions:number;
};

const BUCKETS=[
  {value:"all",label:"All field positions"},
  {value:"own_1_20",label:"Own 1–20"},
  {value:"own_21_40",label:"Own 21–40"},
  {value:"midfield",label:"Midfield"},
  {value:"opponent_21_40",label:"Opponent 21–40"},
  {value:"red_zone",label:"Red zone"},
];

function rate(n:number,d:number){return d?n/d:null;}
function pct(v:number|null){return v===null?"—":`${(v*100).toFixed(1)}%`;}
function num(v:number|null,digits=2){return v===null?"—":v.toFixed(digits);}

function bucketForBallSpot(yard:number){
  if(yard<=20)return "own_1_20";
  if(yard<=40)return "own_21_40";
  if(yard<60)return "midfield";
  if(yard<80)return "opponent_21_40";
  return "red_zone";
}

function fieldLabel(yard:number){
  if(yard===50)return "50";
  if(yard<50)return `OWN ${yard}`;
  return `OPP ${100-yard}`;
}

function FieldGraphic({yard,distance,down}:{yard:number;distance:number;down:number}){
  const los=Math.max(0,Math.min(100,yard));
  const first=Math.max(0,Math.min(100,yard+distance));
  const numbers=[10,20,30,40,50,60,70,80,90];
  return <div className="football-field-wrap">
    <div className="football-field-head">
      <div><span>FIELD POSITION</span><strong>{fieldLabel(yard)}</strong></div>
      <div><span>SITUATION</span><strong>{down}{down===1?"ST":down===2?"ND":down===3?"RD":"TH"} &amp; {distance}</strong></div>
      <div className="field-legend"><i className="legend-los"/>LOS <i className="legend-first"/>FIRST DOWN</div>
    </div>
    <div className="football-field">
      {Array.from({length:21},(_,i)=><div key={i} className="yard-line" style={{left:`${i*5}%`}}/>)}
      {numbers.map(n=><div key={n} className="yard-number" style={{left:`${n}%`}}>{n<=50?n:100-n}</div>)}
      <div className="endzone endzone-left">OWN</div>
      <div className="endzone endzone-right">OPP</div>
      <div className="los-line" style={{left:`${los}%`}}><span>●</span></div>
      <div className="first-line" style={{left:`${first}%`}}/>
    </div>
    <div className="field-scale"><span>OWN GOAL</span><strong>{fieldLabel(yard)}</strong><span>OPP GOAL</span></div>
  </div>;
}

export default function SituationalExplorer({team,season,rows}:Props){
  const [side,setSide]=useState<"offense"|"defense">("offense");
  const [down,setDown]=useState(3);
  const [minDist,setMinDist]=useState(1);
  const [maxDist,setMaxDist]=useState(3);
  const [quarter,setQuarter]=useState("all");
  const [score,setScore]=useState("all");
  const [fieldBucket,setFieldBucket]=useState("all");
  const [redZoneOnly,setRedZoneOnly]=useState(false);
  const [goalToGoOnly,setGoalToGoOnly]=useState(false);
  const [ballSpot,setBallSpot]=useState(50);

  const filtered=useMemo(()=>rows.filter(r=>{
    if(r.side!==side)return false;
    if(Number(r.down)!==down)return false;
    const d=Number(r.distance);
    if(!Number.isFinite(d)||d<minDist||d>maxDist)return false;
    if(quarter!=="all"&&String(r.quarter)!==quarter)return false;
    if(score!=="all"&&r.scoreState!==score)return false;
    if(fieldBucket!=="all"&&r.fieldPositionBucket!==fieldBucket)return false;
    if(redZoneOnly&&!r.redZone)return false;
    if(goalToGoOnly&&!r.goalToGo)return false;
    return true;
  }),[rows,side,down,minDist,maxDist,quarter,score,fieldBucket,redZoneOnly,goalToGoOnly]);

  const t=useMemo(()=>filtered.reduce<Totals>((a,r)=>{
    for(const k of Object.keys(a) as (keyof Totals)[]) a[k]+=Number(r[k]||0);
    return a;
  },{plays:0,successes:0,yards:0,firstDowns:0,rushPlays:0,passPlays:0,rushSuccesses:0,passSuccesses:0,rushYards:0,passYards:0,explosiveEligiblePlays:0,explosivePlays:0,conversionAttempts:0,conversions:0}),[filtered]);

  const calls=t.rushPlays+t.passPlays;
  const defensive=side==="defense";

  function useBallSpot(value:number){
    setBallSpot(value);
    setFieldBucket(bucketForBallSpot(value));
    setRedZoneOnly(value>=80);
  }

  return <section className="panel situational-explorer">
    <div className="muted">SITUATIONAL EXPLORER</div>
    <h2>{team} in any football situation</h2>
    <p className="muted">Move the ball, change down and distance, and filter game context. The field updates with your selection while the stats recalculate from the {season} situational corpus.</p>

    <div className="situation-toolbar">
      <div className="segmented">
        <button className={side==="offense"?"active":""} onClick={()=>setSide("offense")}>Offense</button>
        <button className={side==="defense"?"active":""} onClick={()=>setSide("defense")}>Defense</button>
      </div>
      <div className="segmented">
        {[1,2,3,4].map(d=><button key={d} className={down===d?"active":""} onClick={()=>setDown(d)}>{d}{d===1?"st":d===2?"nd":d===3?"rd":"th"}</button>)}
      </div>
    </div>

    <div className="situation-controls-grid">
      <label className="field"><span>Distance: {minDist}–{maxDist} yards</span><div className="dual-sliders"><input type="range" min="1" max="20" value={minDist} onChange={e=>setMinDist(Math.min(Number(e.target.value),maxDist))}/><input type="range" min="1" max="20" value={maxDist} onChange={e=>setMaxDist(Math.max(Number(e.target.value),minDist))}/></div></label>
      <label className="field"><span>Ball spot</span><input type="range" min="1" max="99" value={ballSpot} onChange={e=>useBallSpot(Number(e.target.value))}/><small>{fieldLabel(ballSpot)} · stats use {BUCKETS.find(x=>x.value===bucketForBallSpot(ballSpot))?.label}</small></label>
      <label className="field"><span>Quarter</span><select value={quarter} onChange={e=>setQuarter(e.target.value)}><option value="all">Full game</option><option value="1">Q1</option><option value="2">Q2</option><option value="3">Q3</option><option value="4">Q4</option><option value="OT">OT</option></select></label>
      <label className="field"><span>Score state</span><select value={score} onChange={e=>setScore(e.target.value)}><option value="all">Any score</option><option value="leading">Leading</option><option value="tied">Tied</option><option value="trailing">Trailing</option></select></label>
      <label className="field"><span>Field zone</span><select value={fieldBucket} onChange={e=>setFieldBucket(e.target.value)}>{BUCKETS.map(b=><option key={b.value} value={b.value}>{b.label}</option>)}</select></label>
      <div className="field checkbox-field"><span>Special situations</span><label><input type="checkbox" checked={redZoneOnly} onChange={e=>setRedZoneOnly(e.target.checked)}/> Red zone only</label><label><input type="checkbox" checked={goalToGoOnly} onChange={e=>setGoalToGoOnly(e.target.checked)}/> Goal-to-go only</label></div>
    </div>

    <FieldGraphic yard={ballSpot} distance={Math.round((minDist+maxDist)/2)} down={down}/>

    <div className="situation-summary-line"><strong>{t.plays.toLocaleString()} plays</strong><span>{defensive?"Opponent":"Team"} tendency and performance for this exact filter.</span></div>

    <div className="situation-stat-grid">
      <div className="situation-stat"><span>{defensive?"Success allowed":"Success rate"}</span><strong>{pct(rate(t.successes,t.plays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Conversion allowed":"Conversion rate"}</span><strong>{pct(rate(t.conversions,t.conversionAttempts))}</strong></div>
      <div className="situation-stat"><span>{defensive?"1st downs allowed":"1st-down rate"}</span><strong>{pct(rate(t.firstDowns,t.plays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Yards/play allowed":"Yards/play"}</span><strong>{num(rate(t.yards,t.plays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Opponent run rate":"Run rate"}</span><strong>{pct(rate(t.rushPlays,calls))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Opponent pass rate":"Pass rate"}</span><strong>{pct(rate(t.passPlays,calls))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Run success allowed":"Run success"}</span><strong>{pct(rate(t.rushSuccesses,t.rushPlays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Pass success allowed":"Pass success"}</span><strong>{pct(rate(t.passSuccesses,t.passPlays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Rush YPP allowed":"Rush YPP"}</span><strong>{num(rate(t.rushYards,t.rushPlays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Pass YPP allowed":"Pass YPP"}</span><strong>{num(rate(t.passYards,t.passPlays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Explosive allowed":"Explosive rate"}</span><strong>{pct(rate(t.explosivePlays,t.explosiveEligiblePlays))}</strong></div>
    </div>

    <p className="situational-note">Field-position stats are currently stored in validated zones, so moving the ball within the same zone changes the field visual but not the statistical sample until you cross into another zone. Down, distance, quarter, score state, red zone, and goal-to-go filter the actual underlying situational rows.</p>
  </section>;
}
