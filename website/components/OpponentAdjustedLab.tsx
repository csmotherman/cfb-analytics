'use client';

import {useEffect,useMemo,useState} from "react";
import {useRouter} from "next/navigation";
import type {LabGame,LabMetricMeta,LabTeam,OpponentAdjustedLabData} from "../lib/opponent-adjusted-lab";

type Side="offense"|"defense";
type ChartView="poe"|"actual"|"profile";
type Aggregate={actual:number;expected:number;poe:number;weight:number;games:number};
type RankingRow={team:LabTeam;aggregate:Aggregate;rank:number};

const finite=(value:number|null|undefined):value is number=>typeof value==="number"&&Number.isFinite(value);

function gameLabel(game:LabGame){
  const postseason=!String(game.st).toLowerCase().includes("regular");
  const week=game.w==null?"?":game.w;
  return `${postseason?"POST ":""}W${week} · ${game.on}`;
}

function metricSlice(game:LabGame,metricIndex:number,side:Side){
  const values=game.m[metricIndex];
  if(!values)return {actual:null,expected:null,poe:null,weight:null,supported:false};
  const offset=side==="offense"?0:5;
  return {
    actual:values[offset] as number|null,
    expected:values[offset+1] as number|null,
    poe:values[offset+2] as number|null,
    weight:values[offset+3] as number|null,
    supported:Number(values[offset+4])===1,
  };
}

function aggregateGames(games:LabGame[],metricIndex:number,side:Side):Aggregate|null{
  let weight=0,actual=0,expected=0,poe=0,count=0;
  for(const game of games){
    const metric=metricSlice(game,metricIndex,side);
    if(!metric.supported||!finite(metric.actual)||!finite(metric.expected)||!finite(metric.poe))continue;
    const w=finite(metric.weight)&&metric.weight>0?metric.weight:1;
    weight+=w;
    actual+=metric.actual*w;
    expected+=metric.expected*w;
    poe+=metric.poe*w;
    count+=1;
  }
  return weight>0?{actual:actual/weight,expected:expected/weight,poe:poe/weight,weight,games:count}:null;
}

function formatValue(value:number|null,metric:LabMetricMeta,poe=false){
  if(!finite(value))return "—";
  if(metric.u==="rate")return poe?`${value>=0?"+":""}${(value*100).toFixed(1)} pp`:`${(value*100).toFixed(1)}%`;
  if(metric.k==="yardsPerPlay")return poe?`${value>=0?"+":""}${value.toFixed(2)} yd/play`:`${value.toFixed(2)} yd/play`;
  return `${value>=0&&poe?"+":""}${value.toFixed(2)}`;
}

function scoreLabel(score:number|null){
  if(!finite(score))return "—";
  return score.toFixed(1);
}

function LineChart({games,metricIndex,side,metric}:{games:LabGame[];metricIndex:number;side:Side;metric:LabMetricMeta}){
  const rows=games.map(game=>({game,value:metricSlice(game,metricIndex,side).poe})).filter((row):row is {game:LabGame;value:number}=>finite(row.value));
  if(!rows.length)return <div className="oa-empty-chart">No supported game-level values in this range.</div>;
  const width=920,height=330,left=58,right=24,top=28,bottom=66;
  const values=rows.map(row=>row.value);
  let min=Math.min(0,...values),max=Math.max(0,...values);
  if(Math.abs(max-min)<1e-9){max+=1;min-=1;}
  const pad=(max-min)*.12;
  min-=pad;max+=pad;
  const x=(index:number)=>left+(rows.length===1?(width-left-right)/2:index*(width-left-right)/Math.max(1,rows.length-1));
  const y=(value:number)=>top+(max-value)*(height-top-bottom)/(max-min);
  const path=rows.map((row,index)=>`${index?"L":"M"}${x(index).toFixed(1)},${y(row.value).toFixed(1)}`).join(" ");
  const zeroY=y(0);
  return <div className="oa-chart-wrap">
    <svg className="oa-svg-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${metric.l} performance over expectation by game`}>
      <line x1={left} x2={width-right} y1={zeroY} y2={zeroY} className="oa-zero-line"/>
      <text x={left-10} y={zeroY+4} textAnchor="end" className="oa-axis-label">0</text>
      <path d={path} className="oa-trend-line" fill="none"/>
      {rows.map((row,index)=><g key={`${row.game.id}-${row.game.t}`}>
        <circle cx={x(index)} cy={y(row.value)} r="5.5" className={row.value>=0?"oa-point positive":"oa-point negative"}>
          <title>{gameLabel(row.game)}: {formatValue(row.value,metric,true)}</title>
        </circle>
        <text x={x(index)} y={height-38} textAnchor="middle" className="oa-game-axis">W{row.game.w??"?"}</text>
      </g>)}
    </svg>
    <div className="oa-chart-caption"><b>Positive = better than schedule-adjusted expectation.</b> Each game is graded with that game removed from the rating fit.</div>
  </div>;
}

function ActualExpectedChart({games,metricIndex,side,metric}:{games:LabGame[];metricIndex:number;side:Side;metric:LabMetricMeta}){
  const rows=games.map(game=>({game,...metricSlice(game,metricIndex,side)})).filter(row=>row.supported&&finite(row.actual)&&finite(row.expected));
  if(!rows.length)return <div className="oa-empty-chart">No supported actual/expected values in this range.</div>;
  const width=920,height=330,left=58,right=24,top=28,bottom=66;
  const max=Math.max(...rows.flatMap(row=>[Number(row.actual),Number(row.expected)]))*1.12||1;
  const chartWidth=width-left-right;
  const groupWidth=chartWidth/rows.length;
  const barWidth=Math.max(5,Math.min(24,groupWidth*.28));
  const y=(value:number)=>top+(max-value)*(height-top-bottom)/max;
  const base=height-bottom;
  return <div className="oa-chart-wrap">
    <div className="oa-chart-legend"><span><i className="actual"/>Actual</span><span><i className="expected"/>Expected</span></div>
    <svg className="oa-svg-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${metric.l} actual versus schedule-adjusted expectation`}>
      <line x1={left} x2={width-right} y1={base} y2={base} className="oa-axis-line"/>
      {rows.map((row,index)=>{
        const center=left+groupWidth*(index+.5);
        const actual=Number(row.actual),expected=Number(row.expected);
        return <g key={`${row.game.id}-${row.game.t}`}>
          <rect x={center-barWidth-2} y={y(actual)} width={barWidth} height={Math.max(1,base-y(actual))} className="oa-bar actual"><title>{gameLabel(row.game)} actual: {formatValue(actual,metric)}</title></rect>
          <rect x={center+2} y={y(expected)} width={barWidth} height={Math.max(1,base-y(expected))} className="oa-bar expected"><title>{gameLabel(row.game)} expected: {formatValue(expected,metric)}</title></rect>
          <text x={center} y={height-38} textAnchor="middle" className="oa-game-axis">W{row.game.w??"?"}</text>
        </g>;
      })}
    </svg>
    <div className="oa-chart-caption">{side==="defense"?<b>On defense, lower actual values can be better. POE handles the direction automatically.</b>:<b>The gap between actual and expected shows how much the offense beat or missed its matchup expectation.</b>}</div>
  </div>;
}

function ProfileChart({profile}:{profile:Array<{metric:LabMetricMeta;aggregate:Aggregate|null;rank:number|null;field:number}>}){
  return <div className="oa-profile-chart">
    {profile.map(row=>{
      const percentile=row.rank&&row.field>1?100*(row.field-row.rank)/(row.field-1):0;
      return <div className="oa-profile-row" key={row.metric.k}>
        <div className="oa-profile-meta"><span>{row.metric.l}</span><b>{row.rank?`#${row.rank}`:"—"}</b></div>
        <div className="oa-profile-track"><i style={{width:`${Math.max(1,percentile)}%`}}/></div>
        <div className="oa-profile-value">{formatValue(row.aggregate?.poe??null,row.metric,true)}</div>
      </div>;
    })}
    <div className="oa-chart-caption"><b>Bar length = national percentile for the selected window.</b> POE values remain in the metric’s native unit.</div>
  </div>;
}

export function OpponentAdjustedLab({data,seasons}:{data:OpponentAdjustedLabData;seasons:number[]}){
  const router=useRouter();
  const michigan=data.teams.find(team=>team.n.toLowerCase()==="michigan");
  const [teamId,setTeamId]=useState(michigan?.id??data.teams[0]?.id??"");
  const [side,setSide]=useState<Side>("offense");
  const [metricIndex,setMetricIndex]=useState(0);
  const [startIndex,setStartIndex]=useState(0);
  const [endIndex,setEndIndex]=useState(999);
  const [chartView,setChartView]=useState<ChartView>("poe");

  const selectedTeam=useMemo(()=>data.teams.find(team=>team.id===teamId)??data.teams[0],[data.teams,teamId]);
  const allTeamGames=useMemo(()=>data.games.filter(game=>game.t===selectedTeam?.id).sort((a,b)=>a.p-b.p||a.id.localeCompare(b.id)),[data.games,selectedTeam]);

  useEffect(()=>{
    setStartIndex(0);
    setEndIndex(Math.max(0,allTeamGames.length-1));
  },[selectedTeam?.id,allTeamGames.length]);

  const safeStart=Math.min(startIndex,Math.max(0,allTeamGames.length-1));
  const safeEnd=Math.min(Math.max(safeStart,endIndex),Math.max(0,allTeamGames.length-1));
  const selectedGames=allTeamGames.slice(safeStart,safeEnd+1);
  const windowStart=selectedGames[0]?.p??0;
  const windowEnd=selectedGames[selectedGames.length-1]?.p??999;
  const metric=data.metrics[metricIndex]??data.metrics[0];

  const selectedAggregate=useMemo(()=>aggregateGames(selectedGames,metricIndex,side),[selectedGames,metricIndex,side]);

  const rankingRows=useMemo<RankingRow[]>(()=>{
    const rows=data.teams.flatMap(team=>{
      const games=data.games.filter(game=>game.t===team.id&&game.p>=windowStart&&game.p<=windowEnd);
      const aggregate=aggregateGames(games,metricIndex,side);
      return aggregate?[{team,aggregate,rank:0}]:[];
    }).sort((a,b)=>b.aggregate.poe-a.aggregate.poe||a.team.n.localeCompare(b.team.n));
    return rows.map((row,index)=>({...row,rank:index+1}));
  },[data.teams,data.games,windowStart,windowEnd,metricIndex,side]);

  const selectedMetricRank=rankingRows.find(row=>row.team.id===selectedTeam?.id)?.rank??null;

  const profile=useMemo(()=>data.metrics.map((metricMeta,index)=>{
    const rows=data.teams.flatMap(team=>{
      const games=data.games.filter(game=>game.t===team.id&&game.p>=windowStart&&game.p<=windowEnd);
      const aggregate=aggregateGames(games,index,side);
      return aggregate?[{teamId:team.id,aggregate}]:[];
    }).sort((a,b)=>b.aggregate.poe-a.aggregate.poe);
    const rank=rows.findIndex(row=>row.teamId===selectedTeam?.id);
    const aggregate=aggregateGames(selectedGames,index,side);
    return {metric:metricMeta,aggregate,rank:rank>=0?rank+1:null,field:rows.length};
  }),[data.metrics,data.teams,data.games,windowStart,windowEnd,side,selectedTeam?.id,selectedGames]);

  const fullRating=selectedTeam?.m[metricIndex];
  const fullValue=side==="offense"?fullRating?.[0]??null:fullRating?.[2]??null;
  const fullRank=side==="offense"?fullRating?.[1]??null:fullRating?.[3]??null;
  const unitRank=side==="offense"?selectedTeam?.or:selectedTeam?.dr;
  const unitScore=side==="offense"?selectedTeam?.os:selectedTeam?.ds;
  const wins=selectedGames.filter(game=>finite(game.pf)&&finite(game.pa)&&Number(game.pf)>Number(game.pa)).length;
  const losses=selectedGames.filter(game=>finite(game.pf)&&finite(game.pa)&&Number(game.pf)<Number(game.pa)).length;
  const tableRows=useMemo(()=>{
    const top=rankingRows.slice(0,25);
    const selected=rankingRows.find(row=>row.team.id===selectedTeam?.id);
    return selected&&selected.rank>25?[...top,selected]:top;
  },[rankingRows,selectedTeam?.id]);

  const setPreset=(count:number|null)=>{
    if(count==null){setStartIndex(0);setEndIndex(Math.max(0,allTeamGames.length-1));return;}
    const end=Math.max(0,allTeamGames.length-1);
    setStartIndex(Math.max(0,end-count+1));
    setEndIndex(end);
  };

  if(!selectedTeam||!metric)return <div className="oa-empty">Opponent-adjusted data is unavailable.</div>;

  return <div className="oa-lab">
    <section className="oa-hero">
      <div>
        <span className="oa-eyebrow">COLLEGE FOOTBALL · OPPONENT ADJUSTED</span>
        <h1>ANALYTICS <b>LAB</b></h1>
        <p>Build your own view of any FBS team. One game, any stretch of games, or the full season — graded against the strength of the opponents actually faced.</p>
      </div>
      <div className="oa-method-card">
        <span>MODEL</span>
        <strong>Schedule Adjusted</strong>
        <div><b>Ridge {data.ridge:g}</b><b>Home {data.homeRidge:g}</b></div>
        <small>Strict leave-one-game-out grading</small>
      </div>
    </section>

    <section className="oa-builder">
      <div className="oa-builder-heading"><div><span>CHART BUILDER</span><h2>Choose the question.</h2></div><p>Every control updates the charts and rankings below.</p></div>
      <div className="oa-control-grid">
        <label><span>Season</span><select value={data.season} onChange={event=>router.push(`/analytics?year=${event.target.value}`)}>{seasons.map(year=><option key={year} value={year}>{year}</option>)}</select></label>
        <label className="oa-team-control"><span>Team</span><select value={selectedTeam.id} onChange={event=>setTeamId(event.target.value)}>{[...data.teams].sort((a,b)=>a.n.localeCompare(b.n)).map(team=><option key={team.id} value={team.id}>{team.n}{team.c?` · ${team.c}`:""}</option>)}</select></label>
        <label><span>Metric</span><select value={metricIndex} onChange={event=>setMetricIndex(Number(event.target.value))}>{data.metrics.map((item,index)=><option key={item.k} value={index}>{item.l}</option>)}</select></label>
        <div className="oa-segment-control"><span>Side of ball</span><div><button className={side==="offense"?"active":""} onClick={()=>setSide("offense")}>Offense</button><button className={side==="defense"?"active":""} onClick={()=>setSide("defense")}>Defense</button></div></div>
        <label><span>From</span><select value={safeStart} onChange={event=>{const next=Number(event.target.value);setStartIndex(next);if(next>safeEnd)setEndIndex(next);}}>{allTeamGames.map((game,index)=><option key={`${game.id}-${index}`} value={index}>{gameLabel(game)}</option>)}</select></label>
        <label><span>Through</span><select value={safeEnd} onChange={event=>{const next=Number(event.target.value);setEndIndex(next);if(next<safeStart)setStartIndex(next);}}>{allTeamGames.map((game,index)=><option key={`${game.id}-${index}`} value={index}>{gameLabel(game)}</option>)}</select></label>
      </div>
      <div className="oa-presets"><span>Quick range</span><button onClick={()=>setPreset(null)}>Full season</button><button onClick={()=>setPreset(5)}>Last 5</button><button onClick={()=>setPreset(3)}>Last 3</button>{selectedGames.length===1&&<b>Single-game view</b>}</div>
    </section>

    <section className="oa-team-head">
      <div><span>{data.season} · {side.toUpperCase()}</span><h2>{selectedTeam.n}</h2><p>{safeStart===0&&safeEnd===allTeamGames.length-1?"Full season":`${gameLabel(selectedGames[0])} → ${gameLabel(selectedGames[selectedGames.length-1])}`}</p></div>
      <div className="oa-summary-grid">
        <article><span>FULL-SEASON {side.toUpperCase()}</span><strong>#{unitRank}</strong><small>{scoreLabel(unitScore??null)} composite</small></article>
        <article><span>SELECTED {metric.l.toUpperCase()}</span><strong>{selectedMetricRank?`#${selectedMetricRank}`:"—"}</strong><small>{rankingRows.length} FBS teams</small></article>
        <article><span>PERFORMANCE VS EXPECTED</span><strong className={(selectedAggregate?.poe??0)>=0?"positive":"negative"}>{formatValue(selectedAggregate?.poe??null,metric,true)}</strong><small>{selectedAggregate?.games??0} supported games</small></article>
        <article><span>RECORD IN RANGE</span><strong>{wins}-{losses}</strong><small>{selectedGames.length} games selected</small></article>
      </div>
    </section>

    <section className="oa-chart-card">
      <div className="oa-chart-head"><div><span>CREATE A VISUAL</span><h3>{metric.l} · {side}</h3></div><div className="oa-view-tabs"><button className={chartView==="poe"?"active":""} onClick={()=>setChartView("poe")}>POE trend</button><button className={chartView==="actual"?"active":""} onClick={()=>setChartView("actual")}>Actual vs expected</button><button className={chartView==="profile"?"active":""} onClick={()=>setChartView("profile")}>Adjusted profile</button></div></div>
      {chartView==="poe"&&<LineChart games={selectedGames} metricIndex={metricIndex} side={side} metric={metric}/>} 
      {chartView==="actual"&&<ActualExpectedChart games={selectedGames} metricIndex={metricIndex} side={side} metric={metric}/>} 
      {chartView==="profile"&&<ProfileChart profile={profile}/>} 
    </section>

    <section className="oa-two-column">
      <article className="oa-stat-panel">
        <div className="oa-panel-title"><span>SELECTED WINDOW</span><h3>What the model sees</h3></div>
        <dl>
          <div><dt>Actual</dt><dd>{formatValue(selectedAggregate?.actual??null,metric)}</dd></div>
          <div><dt>Expected</dt><dd>{formatValue(selectedAggregate?.expected??null,metric)}</dd></div>
          <div><dt>Performance over expected</dt><dd className={(selectedAggregate?.poe??0)>=0?"positive":"negative"}>{formatValue(selectedAggregate?.poe??null,metric,true)}</dd></div>
          <div><dt>National span rank</dt><dd>{selectedMetricRank?`#${selectedMetricRank} / ${rankingRows.length}`:"—"}</dd></div>
        </dl>
      </article>
      <article className="oa-stat-panel">
        <div className="oa-panel-title"><span>FULL SEASON</span><h3>Adjusted team strength</h3></div>
        <dl>
          <div><dt>{metric.l} adjusted value</dt><dd>{formatValue(fullValue,metric)}</dd></div>
          <div><dt>{metric.l} national rank</dt><dd>{fullRank?`#${fullRank}`:"—"}</dd></div>
          <div><dt>Offense composite</dt><dd>#{selectedTeam.or} · {scoreLabel(selectedTeam.os)}</dd></div>
          <div><dt>Defense composite</dt><dd>#{selectedTeam.dr} · {scoreLabel(selectedTeam.ds)}</dd></div>
        </dl>
      </article>
    </section>

    <section className="oa-ranking-card">
      <div className="oa-panel-title"><span>NATIONAL RANKINGS</span><h3>{metric.l} performance over expected</h3><p>Same week window for every FBS team. Positive POE is better on both offense and defense.</p></div>
      <div className="oa-table-scroll"><table><thead><tr><th>RK</th><th>TEAM</th><th>G</th><th>ACTUAL</th><th>EXPECTED</th><th>POE</th></tr></thead><tbody>{tableRows.map((row,index)=><tr key={row.team.id} className={row.team.id===selectedTeam.id?"selected":""}><td>{row.rank}</td><td><b>{row.team.n}</b><small>{row.team.c}</small></td><td>{row.aggregate.games}</td><td>{formatValue(row.aggregate.actual,metric)}</td><td>{formatValue(row.aggregate.expected,metric)}</td><td className={row.aggregate.poe>=0?"positive":"negative"}>{formatValue(row.aggregate.poe,metric,true)}</td>{index===24&&selectedMetricRank&&selectedMetricRank>25?<></>:null}</tr>)}</tbody></table></div>
    </section>

    <section className="oa-game-log">
      <div className="oa-panel-title"><span>GAME-BY-GAME</span><h3>Actual → Expected → POE</h3></div>
      <div className="oa-table-scroll"><table><thead><tr><th>GAME</th><th>SCORE</th><th>ACTUAL</th><th>EXPECTED</th><th>POE</th></tr></thead><tbody>{selectedGames.map(game=>{const values=metricSlice(game,metricIndex,side);return <tr key={`${game.id}-${game.t}`}><td><b>{gameLabel(game)}</b><small>{game.ha?game.ha.toUpperCase():game.n?"NEUTRAL":""}</small></td><td>{finite(game.pf)&&finite(game.pa)?`${game.pf}-${game.pa}`:"—"}</td><td>{formatValue(values.actual,metric)}</td><td>{formatValue(values.expected,metric)}</td><td className={(values.poe??0)>=0?"positive":"negative"}>{formatValue(values.poe,metric,true)}</td></tr>;})}</tbody></table></div>
    </section>

    <section className="oa-methodology">
      <span>HOW TO READ THIS</span>
      <div><h3>Opponent strength is part of the number.</h3><p>Full-season ranks come from the schedule-adjusted offense/defense model. Game and custom-range views use retrospective leave-one-game-out expectations, so a game never grades itself. Range POE is weighted by the underlying play sample, then compared with every FBS team over the same season window.</p></div>
      <aside><b>Validated core</b><span>Success rate</span><span>Rush success</span><span>Pass success</span><span>Explosive rate</span><span>Yards / play</span></aside>
    </section>
  </div>;
}
