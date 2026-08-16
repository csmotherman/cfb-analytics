"use client";

import {useMemo,useState} from "react";
import type {SituationalRow} from "../lib/data";

type Props={team:string;season:number;rows:SituationalRow[]};
type Totals={plays:number;successes:number;yards:number;firstDowns:number;rushPlays:number;passPlays:number;rushSuccesses:number;passSuccesses:number;rushYards:number;passYards:number;explosiveEligiblePlays:number;explosivePlays:number;conversionAttempts:number;conversions:number;};
type Preset={value:string;label:string;down:number|null;min:number;max:number};

const PRESETS:Preset[]=[
  {value:"first",label:"1st Down",down:1,min:1,max:20},
  {value:"second",label:"2nd Down",down:2,min:1,max:20},
  {value:"third-short",label:"3rd & Short",down:3,min:1,max:3},
  {value:"third-medium",label:"3rd & Medium",down:3,min:4,max:6},
  {value:"third-long",label:"3rd & Long",down:3,min:7,max:20},
  {value:"fourth",label:"4th Down",down:4,min:1,max:20},
];
const ZONES=[
  {value:"all",label:"Anywhere",yard:50,buckets:[] as string[]},
  {value:"own",label:"Own Territory",yard:30,buckets:["own_1_20","own_21_40"]},
  {value:"midfield",label:"Midfield",yard:50,buckets:["midfield"]},
  {value:"opponent",label:"Opp. Territory",yard:70,buckets:["opponent_21_40"]},
  {value:"red_zone",label:"Red Zone",yard:85,buckets:["red_zone"]},
];

function rate(n:number,d:number){return d?n/d:null;}
function pct(v:number|null){return v===null?"—":`${(v*100).toFixed(1)}%`;}
function num(v:number|null,digits=2){return v===null?"—":v.toFixed(digits);}
function fieldLabel(yard:number){if(yard===50)return "50";if(yard<50)return `OWN ${yard}`;return `OPP ${100-yard}`;}
function ordinalDown(d:number|null){if(!d)return "Selected plays";return `${d}${d===1?"st":d===2?"nd":d===3?"rd":"th"}`;}

function FieldGraphic({yard,distance,down,label}:{yard:number;distance:number;down:number|null;label:string}){
  const los=Math.max(0,Math.min(100,yard));
  const first=Math.max(0,Math.min(100,yard+distance));
  const numbers=[10,20,30,40,50,60,70,80,90];
  return <div className="football-field-wrap">
    <div className="football-field-head">
      <div><span>FIELD AREA</span><strong>{label}</strong></div>
      <div><span>SITUATION</span><strong>{down?`${ordinalDown(down)} & ${distance}`:"Selected plays"}</strong></div>
      <div className="field-legend"><i className="legend-los"/>BALL <i className="legend-first"/>TO GAIN</div>
    </div>
    <div className="football-field">
      {Array.from({length:21},(_,i)=><div key={i} className="yard-line" style={{left:`${i*5}%`}}/>)}
      {numbers.map(n=><div key={n} className="yard-number" style={{left:`${n}%`}}>{n<=50?n:100-n}</div>)}
      <div className="endzone endzone-left">OWN</div><div className="endzone endzone-right">OPP</div>
      <div className="los-line" style={{left:`${los}%`}}><span>●</span></div>
      {down?<div className="first-line" style={{left:`${first}%`}}/>:null}
    </div>
    <div className="field-scale"><span>OWN GOAL</span><strong>{fieldLabel(yard)}</strong><span>OPP GOAL</span></div>
  </div>;
}

export default function SituationalExplorer({team,season,rows}:Props){
  const [side,setSide]=useState<"offense"|"defense">("offense");
  const [preset,setPreset]=useState("third-short");
  const [zone,setZone]=useState("all");
  const [quarter,setQuarter]=useState("all");
  const [score,setScore]=useState("all");
  const [goalToGoOnly,setGoalToGoOnly]=useState(false);

  const selected=PRESETS.find(x=>x.value===preset)??PRESETS[2];
  const selectedZone=ZONES.find(x=>x.value===zone)??ZONES[0];
  const displayDistance=Math.round((selected.min+selected.max)/2);

  const filtered=useMemo(()=>rows.filter(r=>{
    if(r.side!==side)return false;
    if(selected.down!==null&&Number(r.down)!==selected.down)return false;
    const d=Number(r.distance);
    if(!Number.isFinite(d)||d<selected.min||d>selected.max)return false;
    if(selectedZone.buckets.length&&!selectedZone.buckets.includes(String(r.fieldPositionBucket)))return false;
    if(quarter!=="all"&&String(r.quarter)!==quarter)return false;
    if(score!=="all"&&r.scoreState!==score)return false;
    if(goalToGoOnly&&!r.goalToGo)return false;
    return true;
  }),[rows,side,selected,selectedZone,quarter,score,goalToGoOnly]);

  const t=useMemo(()=>filtered.reduce<Totals>((a,r)=>{for(const k of Object.keys(a) as (keyof Totals)[])a[k]+=Number(r[k]||0);return a;},{plays:0,successes:0,yards:0,firstDowns:0,rushPlays:0,passPlays:0,rushSuccesses:0,passSuccesses:0,rushYards:0,passYards:0,explosiveEligiblePlays:0,explosivePlays:0,conversionAttempts:0,conversions:0}),[filtered]);
  const calls=t.rushPlays+t.passPlays;
  const defensive=side==="defense";

  return <section className="panel situational-explorer">
    <div className="muted">SITUATIONAL EXPLORER</div>
    <h2>How does {team} perform in this situation?</h2>
    <p className="muted">Pick a common football situation. The field and stats update instantly from the {season} season.</p>

    <div className="simple-explorer-controls">
      <div>
        <div className="control-label">Side of ball</div>
        <div className="segmented">
          <button className={side==="offense"?"active":""} onClick={()=>setSide("offense")}>Offense</button>
          <button className={side==="defense"?"active":""} onClick={()=>setSide("defense")}>Defense</button>
        </div>
      </div>
      <label className="simple-select"><span>Situation</span><select value={preset} onChange={e=>setPreset(e.target.value)}>{PRESETS.map(x=><option key={x.value} value={x.value}>{x.label}</option>)}</select></label>
    </div>

    <div className="zone-chips" aria-label="Field area">
      {ZONES.map(z=><button key={z.value} className={zone===z.value?"active":""} onClick={()=>setZone(z.value)}>{z.label}</button>)}
    </div>

    <FieldGraphic yard={selectedZone.yard} distance={displayDistance} down={selected.down} label={selectedZone.label}/>

    <details className="advanced-filters">
      <summary>More filters</summary>
      <div className="advanced-filter-grid">
        <label className="field"><span>Quarter</span><select value={quarter} onChange={e=>setQuarter(e.target.value)}><option value="all">Full game</option><option value="1">Q1</option><option value="2">Q2</option><option value="3">Q3</option><option value="4">Q4</option><option value="OT">OT</option></select></label>
        <label className="field"><span>Score</span><select value={score} onChange={e=>setScore(e.target.value)}><option value="all">Any score</option><option value="leading">Leading</option><option value="tied">Tied</option><option value="trailing">Trailing</option></select></label>
        <label className="advanced-check"><input type="checkbox" checked={goalToGoOnly} onChange={e=>setGoalToGoOnly(e.target.checked)}/> Goal-to-go only</label>
      </div>
    </details>

    <div className="situation-summary-line"><strong>{t.plays.toLocaleString()} plays</strong><span>{selected.label} · {selectedZone.label}</span></div>

    <div className="situation-stat-grid primary-stats">
      <div className="situation-stat"><span>{defensive?"Success allowed":"Success rate"}</span><strong>{pct(rate(t.successes,t.plays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Conversion allowed":"Conversion rate"}</span><strong>{pct(rate(t.conversions,t.conversionAttempts))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Yards/play allowed":"Yards/play"}</span><strong>{num(rate(t.yards,t.plays))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Opponent run rate":"Run rate"}</span><strong>{pct(rate(t.rushPlays,calls))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Opponent pass rate":"Pass rate"}</span><strong>{pct(rate(t.passPlays,calls))}</strong></div>
      <div className="situation-stat"><span>{defensive?"Explosive allowed":"Explosive rate"}</span><strong>{pct(rate(t.explosivePlays,t.explosiveEligiblePlays))}</strong></div>
    </div>

    <details className="more-stats">
      <summary>More stats</summary>
      <div className="situation-stat-grid">
        <div className="situation-stat"><span>{defensive?"1st downs allowed":"1st-down rate"}</span><strong>{pct(rate(t.firstDowns,t.plays))}</strong></div>
        <div className="situation-stat"><span>{defensive?"Run success allowed":"Run success"}</span><strong>{pct(rate(t.rushSuccesses,t.rushPlays))}</strong></div>
        <div className="situation-stat"><span>{defensive?"Pass success allowed":"Pass success"}</span><strong>{pct(rate(t.passSuccesses,t.passPlays))}</strong></div>
        <div className="situation-stat"><span>{defensive?"Rush YPP allowed":"Rush YPP"}</span><strong>{num(rate(t.rushYards,t.rushPlays))}</strong></div>
        <div className="situation-stat"><span>{defensive?"Pass YPP allowed":"Pass YPP"}</span><strong>{num(rate(t.passYards,t.passPlays))}</strong></div>
      </div>
    </details>

    <p className="situational-note">Field position is currently grouped into validated zones. More detailed quarter, score, and goal-to-go filters are available only when you want them.</p>
  </section>;
}
