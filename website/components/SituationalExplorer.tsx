"use client";

import {useEffect,useMemo,useState} from "react";
import type {SituationalRow} from "../lib/data";

type Props={team:string;season:number;rows:SituationalRow[]};
type Summary={
  plays:number;successRate:number|null;conversionRate:number|null;firstDownRate:number|null;yardsPerPlay:number|null;
  runRate:number|null;passRate:number|null;runSuccessRate:number|null;passSuccessRate:number|null;
  rushYpp:number|null;passYpp:number|null;explosiveRate:number|null;
};
type ApiResult={
  current:Summary;
  percentiles:Record<string,number|null>;
  grades:Record<string,string>;
  leaderboard:{rank:number;team:string;plays:number;value:number;grade:string}[];
  primaryMetric:"successRate"|"conversionRate";
  eligibleTeams:number;
  sampleMinimum:number;
};

const FIELD_OPTIONS=[
  {value:"all",label:"Anywhere",yard:50},
  {value:"own",label:"Own territory",yard:30},
  {value:"midfield",label:"Midfield",yard:50},
  {value:"opponent",label:"Opponent territory",yard:70},
  {value:"red_zone",label:"Red zone",yard:85},
];

function pct(v:number|null|undefined){return v===null||v===undefined?"—":`${(v*100).toFixed(1)}%`;}
function num(v:number|null|undefined,digits=2){return v===null||v===undefined?"—":v.toFixed(digits);}
function percentile(v:number|null|undefined){return v===null||v===undefined?"—":`${Math.round(v)}th pct`;}
function ordinalDown(d:number){return `${d}${d===1?"st":d===2?"nd":d===3?"rd":"th"}`;}
function gradeClass(grade:string|undefined){
  const g=grade||"";
  if(g.startsWith("A"))return "grade-badge grade-a";
  if(g.startsWith("B"))return "grade-badge grade-b";
  if(g.startsWith("C"))return "grade-badge grade-c";
  if(g.startsWith("D"))return "grade-badge grade-d";
  if(g==="F")return "grade-badge grade-f";
  return "grade-badge grade-na";
}
function fieldLabel(yard:number){if(yard===50)return "50";if(yard<50)return `OWN ${yard}`;return `OPP ${100-yard}`;}

function FieldGraphic({yard,distance,down,goalToGo}:{yard:number;distance:number;down:number;goalToGo:boolean}){
  const los=Math.max(0,Math.min(100,yard));
  const first=goalToGo?100:Math.max(0,Math.min(100,yard+distance));
  const numbers=[10,20,30,40,50,60,70,80,90];
  return <div className="football-field-wrap compact-field-wrap">
    <div className="football-field-head compact-field-head">
      <div><span>FIELD</span><strong>{fieldLabel(yard)}</strong></div>
      <div><span>SITUATION</span><strong>{ordinalDown(down)} &amp; {goalToGo?"Goal":distance}</strong></div>
      <div className="field-legend"><i className="legend-los"/>BALL <i className="legend-first"/>{goalToGo?"GOAL":"1ST DOWN"}</div>
    </div>
    <div className="football-field compact-football-field">
      {Array.from({length:21},(_,i)=><div key={i} className="yard-line" style={{left:`${i*5}%`}}/>)}
      {numbers.map(n=><div key={n} className="yard-number" style={{left:`${n}%`}}>{n<=50?n:100-n}</div>)}
      <div className="endzone endzone-left">OWN</div><div className="endzone endzone-right">OPP</div>
      <div className="los-line" style={{left:`${los}%`}}><span>●</span></div>
      <div className="first-line" style={{left:`${first}%`}}/>
    </div>
  </div>;
}

function MetricCard({label,value,grade,percentileValue,format="pct"}:{label:string;value:number|null|undefined;grade?:string;percentileValue?:number|null;format?:"pct"|"num"}){
  return <div className="situation-stat graded-situation-stat">
    <div className="stat-card-head"><span>{label}</span><div className={gradeClass(grade)}>{grade||"—"}</div></div>
    <strong>{format==="pct"?pct(value):num(value)}</strong>
    <small>{percentile(percentileValue)} nationally</small>
  </div>;
}

export default function SituationalExplorer({team,season,rows}:Props){
  const [side,setSide]=useState<"offense"|"defense">("offense");
  const [down,setDown]=useState(3);
  const [distance,setDistance]=useState(3);
  const [quarter,setQuarter]=useState("all");
  const [score,setScore]=useState("all");
  const [field,setField]=useState("all");
  const [goalToGo,setGoalToGo]=useState(false);
  const [data,setData]=useState<ApiResult|null>(null);
  const [loading,setLoading]=useState(false);

  const fieldOption=FIELD_OPTIONS.find(x=>x.value===field)??FIELD_OPTIONS[0];
  const visualYard=goalToGo?Math.max(80,100-distance):fieldOption.yard;

  useEffect(()=>{
    const controller=new AbortController();
    const params=new URLSearchParams({team,season:String(season),side,down:String(down),distance:String(distance),quarter,score,field,goalToGo:String(goalToGo)});
    setLoading(true);
    fetch(`/api/situational?${params.toString()}`,{signal:controller.signal})
      .then(r=>r.ok?r.json():Promise.reject(new Error("Unable to load situation")))
      .then((json:ApiResult)=>setData(json))
      .catch(err=>{if(err?.name!=="AbortError")setData(null);})
      .finally(()=>setLoading(false));
    return ()=>controller.abort();
  },[team,season,side,down,distance,quarter,score,field,goalToGo]);

  const c=data?.current;
  const defensive=side==="defense";
  const performanceMetrics=useMemo(()=>[
    {key:"successRate",label:defensive?"Success allowed":"Success rate",value:c?.successRate,format:"pct" as const},
    down>=3
      ?{key:"conversionRate",label:defensive?"Conversion allowed":"Conversion rate",value:c?.conversionRate,format:"pct" as const}
      :{key:"firstDownRate",label:defensive?"1st downs allowed":"1st-down rate",value:c?.firstDownRate,format:"pct" as const},
    {key:"yardsPerPlay",label:defensive?"Yards/play allowed":"Yards/play",value:c?.yardsPerPlay,format:"num" as const},
    {key:"explosiveRate",label:defensive?"Explosive plays allowed":"Explosive rate",value:c?.explosiveRate,format:"pct" as const},
    {key:"runSuccessRate",label:defensive?"Run success allowed":"Run success",value:c?.runSuccessRate,format:"pct" as const},
    {key:"passSuccessRate",label:defensive?"Pass success allowed":"Pass success",value:c?.passSuccessRate,format:"pct" as const},
  ],[c,defensive,down]);

  if(!rows.length)return null;

  return <section className="panel situational-explorer">
    <div className="muted">SITUATIONAL EXPLORER</div>
    <h2>How does {team} perform here?</h2>
    <p className="muted">Choose the side of the ball, down, and yards needed. Everything below updates to that exact situation.</p>

    <div className="explorer-top-filters">
      <div className="top-filter-block">
        <div className="control-label">Side of ball</div>
        <div className="segmented">
          <button className={side==="offense"?"active":""} onClick={()=>setSide("offense")}>Offense</button>
          <button className={side==="defense"?"active":""} onClick={()=>setSide("defense")}>Defense</button>
        </div>
      </div>
      <div className="top-filter-block">
        <div className="control-label">Down</div>
        <div className="segmented">
          {[1,2,3,4].map(d=><button key={d} className={down===d?"active":""} onClick={()=>setDown(d)}>{ordinalDown(d)}</button>)}
        </div>
      </div>
      <label className="distance-filter"><span>Yards to {goalToGo?"goal":"1st down"}</span><div><input type="range" min="1" max="20" value={distance} onChange={e=>setDistance(Number(e.target.value))}/><strong>{distance}{distance===20?"+":""}</strong></div></label>
      <details className="additional-features">
        <summary>Additional features</summary>
        <div className="advanced-filter-grid top-advanced-grid">
          <label className="field"><span>Field area</span><select value={field} onChange={e=>setField(e.target.value)}>{FIELD_OPTIONS.map(x=><option key={x.value} value={x.value}>{x.label}</option>)}</select></label>
          <label className="field"><span>Quarter</span><select value={quarter} onChange={e=>setQuarter(e.target.value)}><option value="all">Full game</option><option value="1">Q1</option><option value="2">Q2</option><option value="3">Q3</option><option value="4">Q4</option><option value="OT">OT</option></select></label>
          <label className="field"><span>Score state</span><select value={score} onChange={e=>setScore(e.target.value)}><option value="all">Any score</option><option value="leading">Leading</option><option value="tied">Tied</option><option value="trailing">Trailing</option></select></label>
          <label className="advanced-check"><input type="checkbox" checked={goalToGo} onChange={e=>setGoalToGo(e.target.checked)}/> Goal-to-go</label>
        </div>
      </details>
    </div>

    <FieldGraphic yard={visualYard} distance={distance} down={down} goalToGo={goalToGo}/>

    <div className="explorer-results-head">
      <div><div className="muted">RESULTS</div><h3>{ordinalDown(down)} &amp; {goalToGo?"Goal":distance} · {side==="offense"?"Offense":"Defense"}</h3></div>
      <div className="sample-count">{loading?"Updating…":`${(c?.plays||0).toLocaleString()} plays`}</div>
    </div>

    <div className="situation-stat-grid primary-stats">
      {performanceMetrics.map(m=><MetricCard key={m.key} label={m.label} value={m.value} format={m.format} grade={data?.grades?.[m.key]} percentileValue={data?.percentiles?.[m.key]}/>) }
    </div>

    <div className="tendency-row">
      <div><span>{defensive?"Opponent run rate":"Run rate"}</span><strong>{pct(c?.runRate)}</strong></div>
      <div><span>{defensive?"Opponent pass rate":"Pass rate"}</span><strong>{pct(c?.passRate)}</strong></div>
      <div><span>Sample size</span><strong>{(c?.plays||0).toLocaleString()}</strong></div>
    </div>

    <div className="leaderboard-panel">
      <div className="leaderboard-title-row">
        <div><div className="muted">TOP 10 IN THE COUNTRY</div><h3>{down>=3?"Best conversion performance":"Best success-rate performance"}</h3></div>
        <small>Minimum {data?.sampleMinimum??10} plays · {data?.eligibleTeams??0} teams eligible</small>
      </div>
      <div className="situation-leaderboard">
        {(data?.leaderboard||[]).map(row=><div className={`leaderboard-row ${row.team.toLowerCase()===team.toLowerCase()?"current-team":""}`} key={row.team}>
          <strong className="leader-rank">#{row.rank}</strong><span className="leader-team">{row.team}</span><span>{row.plays} plays</span><strong>{pct(row.value)}</strong><span className={gradeClass(row.grade)}>{row.grade}</span>
        </div>)}
        {!loading&&!data?.leaderboard?.length?<div className="muted">Not enough qualifying samples for this exact situation.</div>:null}
      </div>
    </div>

    <p className="situational-note">Grades are season-relative percentiles for the same situation. A 50th-percentile performance is a C. Defensive performance metrics are reversed so allowing less is graded better. Run/pass rates are tendencies, so they are shown without a letter grade.</p>
  </section>;
}
