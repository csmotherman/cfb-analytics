"use client";

import {useMemo,useState} from "react";
import type {CreatorChartPack,CreatorGame,CreatorProfileMetric,CreatorTeamProfile} from "../../lib/creator-chart-pack";
import styles from "./charts.module.css";

const COLORS={
  bg:"#07111b",
  panel:"#0b1724",
  panel2:"#101f30",
  text:"#f5f8fc",
  muted:"#91a2b7",
  grid:"#26384b",
  sky:"#66b8ff",
  indigo:"#7d8cff",
  signal:"#d7ff68",
  danger:"#ff6b72",
  maize:"#ffcb05",
  michigan:"#2f79bd",
  utah:"#d64444",
  byu:"#4d8dff",
};

type Side="offense"|"defense";

type MetricSlice={actual:number|null;expected:number|null;poe:number|null};

const finite=(value:number|null|undefined):value is number=>typeof value==="number"&&Number.isFinite(value);

function metric(game:CreatorGame|null,key:string,side:Side):MetricSlice|null{
  if(!game)return null;
  const row=game.metrics.find(item=>item.key===key);
  return row?row[side]:null;
}

function displayPoe(value:number|null|undefined,unit:string,compact=false){
  if(!finite(value))return "—";
  if(unit==="rate")return `${value>=0?"+":""}${(value*100).toFixed(compact?0:1)} pp`;
  return `${value>=0?"+":""}${value.toFixed(2)} yd/play`;
}

function displayValue(value:number|null|undefined,unit:string){
  if(!finite(value))return "—";
  if(unit==="rate")return `${(value*100).toFixed(1)}%`;
  return `${value.toFixed(2)} yd/play`;
}

function toChartValue(value:number|null|undefined,unit:string){
  if(!finite(value))return null;
  return unit==="rate"?value*100:value;
}

function rank(value:number|null|undefined){return finite(value)?`#${value}`:"—";}

function shortName(name:string){
  const known:Record<string,string>={
    "Ohio State":"OSU","Michigan State":"MSU","Penn State":"PSU","Northwestern":"NU","Washington":"WASH",
    "Wisconsin":"WISC","Minnesota":"MINN","Indiana":"IND","Illinois":"ILL","Nebraska":"NEB","Rutgers":"RUTG",
    "Maryland":"MD","Purdue":"PUR","Oregon":"ORE","USC":"USC","UCLA":"UCLA","Iowa":"IOWA","Michigan":"MICH",
    "Oklahoma":"OU","Central Michigan":"CMU","New Mexico":"UNM",
  };
  return known[name]??name.split(" ").map(part=>part[0]).join("").slice(0,5).toUpperCase();
}

function downloadSvg(id:string,filename:string){
  const svg=document.getElementById(id) as SVGSVGElement|null;
  if(!svg)return;
  const clone=svg.cloneNode(true) as SVGSVGElement;
  clone.setAttribute("xmlns","http://www.w3.org/2000/svg");
  const source=`<?xml version="1.0" encoding="UTF-8"?>\n${new XMLSerializer().serializeToString(clone)}`;
  const url=URL.createObjectURL(new Blob([source],{type:"image/svg+xml;charset=utf-8"}));
  const anchor=document.createElement("a");
  anchor.href=url;
  anchor.download=filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function DownloadButton({id,file}:{id:string;file:string}){
  return <button type="button" className={styles.download} onClick={()=>downloadSvg(id,file)} aria-label={`Download ${file}`}>
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m0 0 5-5m-5 5-5-5M5 19h14"/></svg>
    Download SVG
  </button>;
}

function ChartHeader({eyebrow,title,copy,badge}:{eyebrow:string;title:string;copy:string;badge:string}){
  return <header className={styles.chartHeader}>
    <div><span>{eyebrow}</span><h2>{title}</h2><p>{copy}</p></div>
    <b>{badge}</b>
  </header>;
}

function GameTrendChart({pack}:{pack:CreatorChartPack}){
  const [metricKey,setMetricKey]=useState("successRate");
  const [side,setSide]=useState<Side>("offense");
  const meta=pack.metrics.find(item=>item.key===metricKey)??pack.metrics[0];
  const rows=useMemo(()=>pack.michiganGames.map(game=>({
    game,
    value:toChartValue(metric(game,metricKey,side)?.poe,meta.unit),
  })).filter((row):row is {game:CreatorGame;value:number}=>finite(row.value)),[pack.michiganGames,metricKey,side,meta.unit]);
  const maxAbs=Math.max(meta.unit==="rate"?5:.5,...rows.map(row=>Math.abs(row.value)))*1.16;
  const width=1200,height=530,left=70,right=34,top=116,bottom=118;
  const plotH=height-top-bottom;
  const zeroY=top+plotH/2;
  const plotW=width-left-right;
  const slot=plotW/Math.max(1,rows.length);
  const barW=Math.min(56,slot*.58);
  const y=(value:number)=>zeroY-value/maxAbs*(plotH/2);
  const title=`MICHIGAN ${pack.season} • ${side.toUpperCase()} ${meta.label.toUpperCase()} POE`;

  return <>
    <div className={styles.controls}>
      <div className={styles.segmented} aria-label="Side of ball">
        {(["offense","defense"] as Side[]).map(value=><button key={value} className={side===value?styles.active:""} onClick={()=>setSide(value)}>{value}</button>)}
      </div>
      <div className={styles.metricButtons}>
        {pack.metrics.map(item=><button key={item.key} className={metricKey===item.key?styles.active:""} onClick={()=>setMetricKey(item.key)}>{item.label.replace(" rate","")}</button>)}
      </div>
      <DownloadButton id="creator-game-poe" file={`michigan-${pack.season}-${side}-${metricKey}-poe.svg`}/>
    </div>

    <div className={styles.desktopChart}>
      <svg id="creator-game-poe" className={styles.svg} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
        <rect width={width} height={height} rx="24" fill={COLORS.bg}/>
        <text x={left} y="46" fill={COLORS.maize} fontSize="15" fontWeight="800" letterSpacing="2.5">SOAR CHART ROOM • CREATOR EXPORT</text>
        <text x={left} y="78" fill={COLORS.text} fontSize="25" fontWeight="850">{title}</text>
        <text x={left} y="101" fill={COLORS.muted} fontSize="13">Positive = Michigan beat the leave-one-game-out matchup expectation. Opponent rank below each game is full-season adjusted overall.</text>
        {[.5,0,-.5].map((fraction,index)=>{
          const value=maxAbs*fraction*2;
          const yy=y(value);
          return <g key={index}><line x1={left} x2={width-right} y1={yy} y2={yy} stroke={fraction===0?COLORS.muted:COLORS.grid} strokeWidth={fraction===0?1.5:1}/><text x={left-12} y={yy+5} textAnchor="end" fill={COLORS.muted} fontSize="12">{value.toFixed(meta.unit==="rate"?0:1)}</text></g>;
        })}
        {rows.map((row,index)=>{
          const cx=left+slot*(index+.5);
          const yy=y(row.value);
          const positive=row.value>=0;
          const barY=positive?yy:zeroY;
          const barH=Math.max(2,Math.abs(zeroY-yy));
          return <g key={row.game.id}>
            <rect x={cx-barW/2} y={barY} width={barW} height={barH} rx="6" fill={positive?COLORS.signal:COLORS.danger} opacity=".92"/>
            <text x={cx} y={positive?yy-10:yy+18} textAnchor="middle" fill={positive?COLORS.signal:COLORS.danger} fontSize="12" fontWeight="800">{displayPoe(metric(row.game,metricKey,side)?.poe,meta.unit,true)}</text>
            <text x={cx} y={height-72} textAnchor="middle" fill={COLORS.text} fontSize="12" fontWeight="800">{shortName(row.game.opponent)}</text>
            <text x={cx} y={height-53} textAnchor="middle" fill={COLORS.muted} fontSize="11">{row.game.result} {row.game.pf??"—"}-{row.game.pa??"—"}</text>
            <text x={cx} y={height-34} textAnchor="middle" fill={COLORS.sky} fontSize="11">Opp {rank(row.game.opponentOverallRank)}</text>
          </g>;
        })}
        <text x={width-right} y={height-12} textAnchor="end" fill={COLORS.muted} fontSize="10">Ridge {pack.ridge} • home ridge {pack.homeRidge} • target game excluded from expectation fit</text>
      </svg>
    </div>

    <div className={styles.mobileChart}>
      <div className={styles.mobileList}>
        {rows.map(row=>{
          const value=row.value;
          const pct=Math.min(100,Math.abs(value)/maxAbs*100);
          return <div className={styles.mobileGame} key={row.game.id}>
            <div><strong>{row.game.opponent}</strong><span>{row.game.result} {row.game.pf}-{row.game.pa} · Opp {rank(row.game.opponentOverallRank)}</span></div>
            <div className={styles.mobileBar}><i className={value>=0?styles.good:styles.bad} style={{width:`${Math.max(4,pct)}%`}}/></div>
            <b className={value>=0?styles.goodText:styles.badText}>{displayPoe(metric(row.game,metricKey,side)?.poe,meta.unit)}</b>
          </div>;
        })}
      </div>
    </div>
  </>;
}

function ProfileChart({id,title,subtitle,left,right,side,leftColor,rightColor}:{id:string;title:string;subtitle:string;left:CreatorTeamProfile;right:CreatorTeamProfile;side:Side;leftColor:string;rightColor:string}){
  const width=1200,height=590,leftX=338,plotW=770,top=136,rowH=82;
  const rows=left.metrics.map((metric,index)=>({metric,right:right.metrics[index]}));
  const pct=(row:CreatorProfileMetric)=>side==="offense"?row.offensePercentile:row.defensePercentile;
  const ranking=(row:CreatorProfileMetric)=>side==="offense"?row.offenseRank:row.defenseRank;

  return <div>
    <div className={styles.controlsRight}><DownloadButton id={id} file={`${id}.svg`}/></div>
    <div className={styles.desktopChart}>
      <svg id={id} className={styles.svg} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
        <rect width={width} height={height} rx="24" fill={COLORS.bg}/>
        <text x="58" y="45" fill={COLORS.sky} fontSize="15" fontWeight="800" letterSpacing="2.5">2026 PRESEASON CREATOR PACK</text>
        <text x="58" y="78" fill={COLORS.text} fontSize="26" fontWeight="850">{title}</text>
        <text x="58" y="103" fill={COLORS.muted} fontSize="13">{subtitle}</text>
        <g transform="translate(58 120)"><circle r="6" fill={leftColor}/><text x="14" y="5" fill={COLORS.text} fontSize="13" fontWeight="750">{left.name}</text><circle cx="150" r="6" fill={rightColor}/><text x="164" y="5" fill={COLORS.text} fontSize="13" fontWeight="750">{right.name}</text></g>
        {[0,25,50,75,100].map(value=><g key={value}><line x1={leftX+plotW*value/100} x2={leftX+plotW*value/100} y1={top-16} y2={height-46} stroke={COLORS.grid}/><text x={leftX+plotW*value/100} y={height-25} textAnchor="middle" fill={COLORS.muted} fontSize="11">{value}</text></g>)}
        {rows.map(({metric,right:rightMetric},index)=>{
          const y=top+index*rowH;
          const lp=pct(metric)??0;
          const rp=pct(rightMetric)??0;
          return <g key={metric.key}>
            <text x="58" y={y+23} fill={COLORS.text} fontSize="14" fontWeight="750">{metric.label}</text>
            <rect x={leftX} y={y} width={plotW*lp/100} height="20" rx="6" fill={leftColor}/>
            <rect x={leftX} y={y+29} width={plotW*rp/100} height="20" rx="6" fill={rightColor}/>
            <text x={Math.min(leftX+plotW*lp/100+9,1142)} y={y+15} fill={COLORS.text} fontSize="12" fontWeight="800">{rank(ranking(metric))}</text>
            <text x={Math.min(leftX+plotW*rp/100+9,1142)} y={y+44} fill={COLORS.text} fontSize="12" fontWeight="800">{rank(ranking(rightMetric))}</text>
          </g>;
        })}
        <text x={leftX} y={height-8} fill={COLORS.muted} fontSize="10">National percentile →</text>
      </svg>
    </div>
    <div className={styles.mobileChart}>
      <div className={styles.profileMobile}>
        {rows.map(({metric,right:rightMetric})=><div key={metric.key} className={styles.profileMobileRow}>
          <strong>{metric.label}</strong>
          <div><span>{left.name}</span><div className={styles.track}><i style={{width:`${pct(metric)??0}%`,background:leftColor}}/></div><b>{rank(ranking(metric))}</b></div>
          <div><span>{right.name}</span><div className={styles.track}><i style={{width:`${pct(rightMetric)??0}%`,background:rightColor}}/></div><b>{rank(ranking(rightMetric))}</b></div>
        </div>)}
      </div>
    </div>
  </div>;
}

function OklahomaChart({game}:{game:CreatorGame}){
  const rateKeys=["successRate","rushSuccessRate","passSuccessRate"];
  const rateRows=rateKeys.map(key=>({key,row:game.metrics.find(item=>item.key===key)!}));
  const ypp=game.metrics.find(item=>item.key==="yardsPerPlay")!;
  const width=1200,height=500,center=560,range=20,plotW=690;
  const barScale=(value:number)=>Math.min(plotW/2,Math.abs(value)/range*(plotW/2));

  return <>
    <div className={styles.controlsRight}><DownloadButton id="oklahoma-consistency-chart" file="michigan-oklahoma-efficiency-without-consistency.svg"/></div>
    <div className={styles.desktopChart}>
      <svg id="oklahoma-consistency-chart" className={styles.svg} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Michigan versus Oklahoma efficiency without consistency">
        <rect width={width} height={height} rx="24" fill={COLORS.bg}/>
        <text x="58" y="47" fill={COLORS.danger} fontSize="15" fontWeight="800" letterSpacing="2.5">THE BOX SCORE CAN LIE</text>
        <text x="58" y="82" fill={COLORS.text} fontSize="29" fontWeight="850">OKLAHOMA: EFFICIENCY WITHOUT CONSISTENCY</text>
        <text x="58" y="108" fill={COLORS.muted} fontSize="13">Michigan generated enough chunk yardage to beat YPP expectation, but failed to stay on schedule down after down.</text>
        <line x1={center} x2={center} y1="145" y2="378" stroke={COLORS.muted} strokeWidth="1.5"/>
        <text x={center-plotW/2} y="140" fill={COLORS.danger} fontSize="11">WORSE THAN EXPECTED</text>
        <text x={center+plotW/2} y="140" textAnchor="end" fill={COLORS.signal} fontSize="11">BETTER THAN EXPECTED</text>
        {rateRows.map(({row},index)=>{
          const value=(row.offense.poe??0)*100;
          const length=barScale(value);
          const y=185+index*78;
          return <g key={row.key}>
            <text x="58" y={y+16} fill={COLORS.text} fontSize="16" fontWeight="750">{row.label}</text>
            <rect x={value<0?center-length:center} y={y} width={length} height="28" rx="7" fill={value>=0?COLORS.signal:COLORS.danger}/>
            <text x={value<0?center-length-12:center+length+12} y={y+19} textAnchor={value<0?"end":"start"} fill={value>=0?COLORS.signal:COLORS.danger} fontSize="15" fontWeight="850">{displayPoe(row.offense.poe,row.unit)}</text>
          </g>;
        })}
        <rect x="855" y="170" width="286" height="185" rx="18" fill={COLORS.panel2} stroke={COLORS.grid}/>
        <text x="882" y="203" fill={COLORS.sky} fontSize="12" fontWeight="800" letterSpacing="1.5">YARDS PER PLAY</text>
        <text x="882" y="256" fill={COLORS.signal} fontSize="44" fontWeight="900">{displayPoe(ypp.offense.poe,ypp.unit)}</text>
        <text x="882" y="290" fill={COLORS.text} fontSize="14">Actual {displayValue(ypp.offense.actual,ypp.unit)}</text>
        <text x="882" y="315" fill={COLORS.muted} fontSize="14">Expected {displayValue(ypp.offense.expected,ypp.unit)}</text>
        <text x="58" y="430" fill={COLORS.text} fontSize="15" fontWeight="700">Opponent context: Oklahoma full-season adjusted defense {rank(game.opponentDefRank)}.</text>
        <text x="58" y="458" fill={COLORS.muted} fontSize="12">Talking point: a few successful chunks can prop up YPP while an offense repeatedly loses the down-to-down battle.</text>
      </svg>
    </div>
    <div className={styles.mobileChart}>
      <div className={styles.storyMobile}>
        {rateRows.map(({row})=><div key={row.key}><span>{row.label}</span><b className={(row.offense.poe??0)>=0?styles.goodText:styles.badText}>{displayPoe(row.offense.poe,row.unit)}</b></div>)}
        <div><span>Yards per play POE</span><b className={(ypp.offense.poe??0)>=0?styles.goodText:styles.badText}>{displayPoe(ypp.offense.poe,ypp.unit)}</b></div>
      </div>
    </div>
  </>;
}

function BigTenMap({pack}:{pack:CreatorChartPack}){
  const width=1200,height=680,left=84,right=48,top=128,bottom=80;
  const plotW=width-left-right,plotH=height-top-bottom;
  const x=(score:number)=>left+score/100*plotW;
  const y=(score:number)=>top+(100-score)/100*plotH;
  const highlight=new Set(["Michigan","Ohio State","Oregon","Indiana","Washington","Penn State","USC"]);

  return <>
    <div className={styles.controlsRight}><DownloadButton id="big-ten-power-map" file="big-ten-2025-opponent-adjusted-power-map.svg"/></div>
    <div className={styles.desktopChart}>
      <svg id="big-ten-power-map" className={styles.svg} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Big Ten opponent-adjusted offense versus defense power map">
        <rect width={width} height={height} rx="24" fill={COLORS.bg}/>
        <text x="58" y="45" fill={COLORS.sky} fontSize="15" fontWeight="800" letterSpacing="2.5">BIG TEN • OPPONENT ADJUSTED</text>
        <text x="58" y="80" fill={COLORS.text} fontSize="28" fontWeight="850">WHO WAS ACTUALLY GOOD ON BOTH SIDES?</text>
        <text x="58" y="106" fill={COLORS.muted} fontSize="13">Five-metric adjusted offense score on the x-axis. Adjusted defense score on the y-axis. Top-right = complete team.</text>
        {[0,25,50,75,100].map(value=><g key={value}>
          <line x1={x(value)} x2={x(value)} y1={top} y2={height-bottom} stroke={value===50?COLORS.muted:COLORS.grid}/>
          <line x1={left} x2={width-right} y1={y(value)} y2={y(value)} stroke={value===50?COLORS.muted:COLORS.grid}/>
          <text x={x(value)} y={height-bottom+25} textAnchor="middle" fill={COLORS.muted} fontSize="11">{value}</text>
          <text x={left-16} y={y(value)+4} textAnchor="end" fill={COLORS.muted} fontSize="11">{value}</text>
        </g>)}
        <text x={width-right} y={height-23} textAnchor="end" fill={COLORS.muted} fontSize="12">Adjusted offense score →</text>
        <text transform={`translate(24 ${top+plotH/2}) rotate(-90)`} textAnchor="middle" fill={COLORS.muted} fontSize="12">Adjusted defense score →</text>
        <text x={x(76)} y={y(94)} fill={COLORS.signal} opacity=".75" fontSize="12" fontWeight="800">COMPLETE CONTENDERS</text>
        {pack.bigTen.map(team=>{
          const isMichigan=team.name==="Michigan";
          const strong=highlight.has(team.name);
          const radius=isMichigan?9:strong?7:5;
          const fill=isMichigan?COLORS.maize:strong?COLORS.sky:COLORS.indigo;
          return <g key={team.name}>
            <circle cx={x(team.offenseScore)} cy={y(team.defenseScore)} r={radius} fill={fill} stroke={isMichigan?COLORS.text:"none"} strokeWidth="2"><title>{team.name}: Off {team.offenseScore.toFixed(1)}, Def {team.defenseScore.toFixed(1)}, Overall {rank(team.overallRank)}</title></circle>
            <text x={x(team.offenseScore)+9} y={y(team.defenseScore)-8} fill={strong?COLORS.text:COLORS.muted} fontSize={strong?12:9} fontWeight={strong?800:600}>{shortName(team.name)}</text>
          </g>;
        })}
      </svg>
    </div>
    <div className={styles.mobileChart}>
      <div className={styles.bigTenMobile}>
        {pack.bigTen.slice(0,12).map(team=><div key={team.name}><b>{team.overallRank}</b><strong>{team.name}</strong><span>OFF {team.offenseScore.toFixed(1)}</span><span>DEF {team.defenseScore.toFixed(1)}</span></div>)}
      </div>
    </div>
  </>;
}

function InsightCard({game,title,kicker,body,metricKey,side="offense"}:{game:CreatorGame|null;title:string;kicker:string;body:(game:CreatorGame)=>string;metricKey:string;side?:Side}){
  if(!game)return null;
  const row=game.metrics.find(item=>item.key===metricKey);
  const value=row?.[side].poe??null;
  return <article className={styles.insightCard}>
    <span>{kicker}</span>
    <h3>{title}</h3>
    <strong className={finite(value)&&value>=0?styles.goodText:styles.badText}>{row?displayPoe(value,row.unit):"—"}</strong>
    <p>{body(game)}</p>
    <small>{game.result} {game.pf}-{game.pa} vs {game.opponent} · opponent overall {rank(game.opponentOverallRank)}</small>
  </article>;
}

export function CreatorCharts({pack}:{pack:CreatorChartPack}){
  const osu=pack.spotlights.ohioState;
  const washington=pack.spotlights.washington;
  const usc=pack.spotlights.usc;
  const wisconsin=pack.spotlights.wisconsin;

  return <div className={styles.page}>
    <section className={styles.hero}>
      <div className={styles.heroCopy}>
        <span>SOAR ANALYTICS • CREATOR RESEARCH</span>
        <h1>2026 PRESEASON <b>CHART ROOM</b></h1>
        <p>Original visuals built for college-football creators who want more than raw NCAA ranks. Every game-level expectation removes the target game from the fit; full-season profiles recursively adjust for opponent strength.</p>
        <div className={styles.heroBadges}><b>2025 data basis</b><b>Ridge {pack.ridge}</b><b>Home ridge {pack.homeRidge}</b><b>{pack.fieldSize} FBS teams</b></div>
      </div>
      <aside className={styles.heroAside}>
        <span>HOW TO USE THIS PAGE</span>
        <strong>Pick a story. Download the chart. Use the talking point.</strong>
        <p>The visuals are designed to stand alone in a YouTube video, podcast screen share, article, or social post. SVG exports stay sharp at any resolution.</p>
      </aside>
    </section>

    <nav className={styles.jump} aria-label="Chart room sections">
      <a href="#game-story">Game story</a><a href="#oklahoma">Oklahoma</a><a href="#offense-handoff">Beck offense</a><a href="#defense-handoff">Hill defense</a><a href="#big-ten">Big Ten map</a><a href="#talking-points">Talking points</a>
    </nav>

    <section id="game-story" className={styles.section}>
      <ChartHeader eyebrow="CHART 01 · FILM ROOM / SEASON STORY" title="Michigan game-by-game performance over expectation" copy="Switch the side of ball and metric to find where Michigan truly beat or missed the matchup expectation. This is the cleanest chart for building a season narrative around opponent-adjusted performance." badge="Darren + Sam"/>
      <GameTrendChart pack={pack}/>
    </section>

    {pack.spotlights.oklahoma&&<section id="oklahoma" className={styles.section}>
      <ChartHeader eyebrow="CHART 02 · WHY YPP ALONE MISLEADS" title="The Oklahoma game: production without consistency" copy="Michigan's yards per play looked better than the matchup expectation, while success rate, rush success and pass success collapsed. This is a clean visual example of why one efficiency stat never tells the whole story." badge="Film-room ready"/>
      <OklahomaChart game={pack.spotlights.oklahoma}/>
    </section>}

    <section id="offense-handoff" className={styles.section}>
      <ChartHeader eyebrow="CHART 03 · COACHING HANDOFF" title="What Jason Beck is inheriting vs. what Utah produced" copy="A five-metric national-percentile comparison of Michigan's 2025 offense and Utah's 2025 offense. This does not claim Utah's production transfers directly; it shows the statistical environment Beck operated and the one he inherits." badge="Darren"/>
      <ProfileChart id="michigan-utah-offense-profile" title="MICHIGAN OFFENSE vs UTAH OFFENSE" subtitle="Full-season opponent-adjusted profile • five validated core metrics" left={pack.michigan} right={pack.utah} side="offense" leftColor={COLORS.maize} rightColor={COLORS.utah}/>
    </section>

    <section id="defense-handoff" className={styles.section}>
      <ChartHeader eyebrow="CHART 04 · COACHING HANDOFF" title="What Jay Hill is inheriting vs. what BYU produced" copy="The same comparison on defense. A creator can pair this with film to ask where Hill's 2025 BYU defense was materially different from Michigan and which traits may be system-driven." badge="Darren"/>
      <ProfileChart id="michigan-byu-defense-profile" title="MICHIGAN DEFENSE vs BYU DEFENSE" subtitle="Full-season opponent-adjusted profile • national percentile from adjusted rank" left={pack.michigan} right={pack.byu} side="defense" leftColor={COLORS.maize} rightColor={COLORS.byu}/>
    </section>

    <section id="big-ten" className={styles.section}>
      <ChartHeader eyebrow="CHART 05 · CONFERENCE LANDSCAPE" title="The Big Ten power map" copy="Instead of a one-dimensional ranking, place every Big Ten team by adjusted offense and adjusted defense. This is built for preseason tiers, contender discussions, schedule breakdowns and conference preview videos." badge="Sam"/>
      <BigTenMap pack={pack}/>
      <div className={styles.rankTableWrap}>
        <table className={styles.rankTable}>
          <thead><tr><th>Big Ten</th><th>Nat. overall</th><th>Off score</th><th>Nat. off</th><th>Def score</th><th>Nat. def</th></tr></thead>
          <tbody>{pack.bigTen.map(team=><tr key={team.name} className={team.name==="Michigan"?styles.michiganRow:""}><td><b>{team.name}</b></td><td>#{team.overallRank}</td><td>{team.offenseScore.toFixed(1)}</td><td>#{team.offenseRank}</td><td>{team.defenseScore.toFixed(1)}</td><td>#{team.defenseRank}</td></tr>)}</tbody>
        </table>
      </div>
    </section>

    <section id="talking-points" className={styles.section}>
      <ChartHeader eyebrow="CREATOR NOTES" title="Five talking points worth building a segment around" copy="These are derived from the same opponent-adjusted artifact as the charts. They are prompts for analysis, not claims about 2026 outcomes." badge="Copy-ready"/>
      <div className={styles.insights}>
        <InsightCard game={washington} kicker="QUALITY WIN" title="Washington is the proof-of-concept game" metricKey="passSuccessRate" body={game=>{
          const success=metric(game,"successRate","offense");const explosive=metric(game,"explosivePlayRate","offense");const ypp=metric(game,"yardsPerPlay","offense");
          return `Michigan beat offensive expectation in four of five core metrics: success ${displayPoe(success?.poe,"rate")}, pass success ${displayPoe(metric(game,"passSuccessRate","offense")?.poe,"rate")}, explosiveness ${displayPoe(explosive?.poe,"rate")}, and YPP ${displayPoe(ypp?.poe,"yards")}.`;
        }}/>
        <InsightCard game={osu} kicker="RIVALRY FAILURE" title="Opponent strength does not excuse Ohio State" metricKey="successRate" body={game=>`The adjustment already accounts for the opponent. Michigan still missed offensive success expectation by ${displayPoe(metric(game,"successRate","offense")?.poe,"rate")}, rush success by ${displayPoe(metric(game,"rushSuccessRate","offense")?.poe,"rate")}, and pass success by ${displayPoe(metric(game,"passSuccessRate","offense")?.poe,"rate")}.`}/>
        <InsightCard game={usc} kicker="DEFENSIVE BREAKDOWN" title="USC attacked Michigan through the air" metricKey="passSuccessRate" side="defense" body={game=>`Even after adjusting for USC's offense, Michigan's pass-success defense finished ${displayPoe(metric(game,"passSuccessRate","defense")?.poe,"rate")} versus expectation. That is a system-and-execution question worth taking to film.`}/>
        <InsightCard game={wisconsin} kicker="CLEAN OFFENSIVE GAME" title="Wisconsin was the across-the-board performance" metricKey="successRate" body={game=>`Michigan was above offensive expectation in all five validated core metrics, including pass success ${displayPoe(metric(game,"passSuccessRate","offense")?.poe,"rate")} and YPP ${displayPoe(metric(game,"yardsPerPlay","offense")?.poe,"yards")}.`}/>
      </div>
    </section>

    <section className={styles.method}>
      <div><span>METHODOLOGY</span><h2>What these charts actually mean</h2></div>
      <div className={styles.methodGrid}>
        <article><b>Full-season profiles</b><p>Opponent-adjusted offense and defense strengths are fit through the full FBS schedule network with ridge {pack.ridge} and home ridge {pack.homeRidge}.</p></article>
        <article><b>Game POE</b><p>The target game is removed before the expected value is calculated. Actual minus expected is then oriented so positive always means the selected Michigan unit performed better than expectation.</p></article>
        <article><b>Creator guardrail</b><p>These visuals describe 2025 performance and coaching fingerprints. They are evidence for a 2026 discussion, not direct 2026 projections.</p></article>
      </div>
    </section>
  </div>;
}
