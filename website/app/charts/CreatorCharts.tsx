"use client";

import {useMemo,useState} from "react";
import type {CreatorGameLibrary,GameMetricView,MichiganGameDossier,TeamMetricProfile} from "../../lib/creator-game-library";
import styles from "./charts.module.css";

const COLORS={bg:"#07111b",panel:"#0d1a28",text:"#f5f8fc",muted:"#9babc0",grid:"#26384b",sky:"#66b8ff",signal:"#d7ff68",danger:"#ff6b72",maize:"#ffcb05",blue:"#4d8dff"};
const RATE_KEYS=["successRate","rushSuccessRate","passSuccessRate","explosivePlayRate"];

const finite=(value:number|null|undefined):value is number=>typeof value==="number"&&Number.isFinite(value);
const rank=(value:number|null|undefined)=>finite(value)?`#${value}`:"—";

function locationLabel(game:MichiganGameDossier){
  if(game.neutral)return "Neutral site";
  const value=String(game.homeAway).toLowerCase();
  if(value==="home")return "Home";
  if(value==="away")return "Away";
  return "Location unavailable";
}

function metricRow(metrics:GameMetricView[],key:string){return metrics.find(metric=>metric.key===key)??null;}
function teamMetric(metrics:TeamMetricProfile[],key:string){return metrics.find(metric=>metric.key===key)??null;}

function formatValue(value:number|null|undefined,unit:string){
  if(!finite(value))return "—";
  return unit==="rate"?`${(value*100).toFixed(1)}%`:`${value.toFixed(2)} yards/play`;
}

function formatDifference(value:number|null|undefined,unit:string){
  if(!finite(value))return "—";
  if(unit==="rate")return `${value>=0?"+":""}${(value*100).toFixed(1)} percentage points`;
  return `${value>=0?"+":""}${value.toFixed(2)} yards/play`;
}

function compactDifference(value:number|null|undefined,unit:string){
  if(!finite(value))return "—";
  if(unit==="rate")return `${value>=0?"+":""}${(value*100).toFixed(1)} percentage pts`;
  return `${value>=0?"+":""}${value.toFixed(2)} yd/play`;
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
  return <button type="button" className={styles.download} onClick={()=>downloadSvg(id,file)}>
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m0 0 5-5m-5 5-5-5M5 19h14"/></svg>
    Download chart
  </button>;
}

function DifferenceBadge({value,unit,invert=false}:{value:number|null;unit:string;invert?:boolean}){
  if(!finite(value))return <span className={styles.neutralText}>No grade</span>;
  const good=invert?value<0:value>0;
  const neutral=Math.abs(value)<1e-9;
  return <strong className={neutral?styles.neutralText:good?styles.goodText:styles.badText}>{formatDifference(value,unit)}</strong>;
}

function audienceSentence(label:string,actual:number|null,expected:number|null,poe:number|null,unit:string,subject:string){
  if(!finite(actual)||!finite(expected)||!finite(poe))return `${label}: not enough supported data to grade this matchup.`;
  if(unit==="rate"){
    const direction=poe>=0?"better":"worse";
    return `${subject} finished at ${formatValue(actual,unit)} versus ${formatValue(expected,unit)} expected — ${Math.abs(poe*100).toFixed(1)} percentage points ${direction} than the matchup model expected.`;
  }
  const direction=poe>=0?"above":"below";
  return `${subject} averaged ${formatValue(actual,unit)} versus ${formatValue(expected,unit)} expected — ${Math.abs(poe).toFixed(2)} yards per play ${direction} expectation.`;
}

function strongestRate(metrics:GameMetricView[],side:"offense"){ 
  return metrics.filter(metric=>metric.unit==="rate"&&finite(metric[side].poe)).sort((a,b)=>Math.abs(b[side].poe as number)-Math.abs(a[side].poe as number))[0]??null;
}

function GamePicker({library,selectedId,onSelect}:{library:CreatorGameLibrary;selectedId:string;onSelect:(id:string)=>void}){
  return <section className={styles.librarySection} aria-labelledby="game-library-title">
    <div className={styles.sectionIntro}>
      <span>2025 GAME LIBRARY</span>
      <h2 id="game-library-title">Pick a game. Then see what actually happened.</h2>
      <p>Every game opens a full opponent-adjusted dossier. The score tells you who won. These charts tell you <b>who played better or worse than the matchup should have produced.</b></p>
    </div>
    <div className={styles.gameGrid}>
      {library.games.map((game,index)=><button type="button" key={game.id} onClick={()=>onSelect(game.id)} className={`${styles.gameCard} ${selectedId===game.id?styles.selectedGame:""}`}>
        <span>{String(index+1).padStart(2,"0")} · {String(game.seasonType).toLowerCase().includes("regular")?`Week ${game.week??"—"}`:"Postseason"}</span>
        <strong>{game.opponentName}</strong>
        <b className={game.result==="W"?styles.win:game.result==="L"?styles.loss:""}>{game.result} {game.pf??"—"}-{game.pa??"—"}</b>
        <small>Opponent-adjusted: overall {rank(game.opponent.overallRank)} · offense {rank(game.opponent.offenseRank)} · defense {rank(game.opponent.defenseRank)}</small>
      </button>)}
    </div>
  </section>;
}

function MatchupContext({library,game}:{library:CreatorGameLibrary;game:MichiganGameDossier}){
  const michigan=library.michigan;
  return <section className={styles.dossierSection}>
    <header className={styles.gameHero}>
      <div>
        <span>{String(game.seasonType).toLowerCase().includes("regular")?`WEEK ${game.week??"—"}`:"POSTSEASON"} · {locationLabel(game)}</span>
        <h2>Michigan <b>{game.pf??"—"}</b> · {game.opponentName} <b>{game.pa??"—"}</b></h2>
        <p>Full-season opponent-adjusted strength provides the matchup context below. The actual game grade is stricter: <b>this game is removed before its expected performance is calculated.</b></p>
      </div>
      <div className={styles.resultBadge}><span>{game.result}</span><strong>{game.pf??"—"}-{game.pa??"—"}</strong></div>
    </header>

    <div className={styles.contextGrid}>
      <article><span>MICHIGAN OFFENSE</span><strong>{rank(michigan.offenseRank)}</strong><p>National opponent-adjusted offense</p></article>
      <article><span>{game.opponentName.toUpperCase()} DEFENSE</span><strong>{rank(game.opponent.defenseRank)}</strong><p>The unit Michigan's offense actually faced</p></article>
      <article><span>MICHIGAN DEFENSE</span><strong>{rank(michigan.defenseRank)}</strong><p>National opponent-adjusted defense</p></article>
      <article><span>{game.opponentName.toUpperCase()} OFFENSE</span><strong>{rank(game.opponent.offenseRank)}</strong><p>The unit Michigan's defense actually faced</p></article>
    </div>

    <div className={styles.readingGuide}>
      <div><b>Actual</b><p>What the team really did in this game.</p></div>
      <div><b>Expected</b><p>What our schedule-adjusted matchup model expected after accounting for both teams' strength. The target game itself is excluded.</p></div>
      <div><b>Difference from expected</b><p>Actual minus expected. This is the simplest way to ask whether a team overperformed or underperformed the matchup.</p></div>
      <div><b>Percentage points</b><p>A percentage-point difference compares two rates directly. Example: 45% actual versus 40% expected is <strong>5 percentage points better</strong>. It is not a 5% increase.</p></div>
    </div>
  </section>;
}

function MatchupRankTable({library,game}:{library:CreatorGameLibrary;game:MichiganGameDossier}){
  return <section className={styles.dossierSection}>
    <div className={styles.sectionIntro}>
      <span>01 · STRENGTH OF MATCHUP</span>
      <h2>How good were the units Michigan was actually facing?</h2>
      <p>National ranks give the audience a reference point before judging the box score. Rank #1 is best. These are full-season opponent-adjusted ranks.</p>
    </div>
    <div className={styles.tableWrap}><table className={styles.matchupTable}>
      <thead><tr><th>Metric</th><th>Michigan offense</th><th>{game.opponentName} defense</th><th>Michigan defense</th><th>{game.opponentName} offense</th></tr></thead>
      <tbody>{library.metrics.map(meta=>{
        const mich=teamMetric(library.michigan.metrics,meta.key);
        const opp=teamMetric(game.opponent.metrics,meta.key);
        return <tr key={meta.key}><td><strong>{meta.label}</strong><small>{meta.explanation}</small></td><td>{rank(mich?.offenseRank)}</td><td>{rank(opp?.defenseRank)}</td><td>{rank(mich?.defenseRank)}</td><td>{rank(opp?.offenseRank)}</td></tr>;
      })}</tbody>
    </table></div>
  </section>;
}

function ActualExpectedRates({game,team,kind}:{game:MichiganGameDossier;team:"Michigan"|"Opponent";kind:"offense"}){
  const isMichigan=team==="Michigan";
  const metrics=isMichigan?game.michiganMetrics:game.opponentMetrics;
  const teamName=isMichigan?"Michigan":game.opponentName;
  const rows=RATE_KEYS.map(key=>metricRow(metrics,key)).filter((row):row is GameMetricView=>row!==null&&finite(row.offense.actual)&&finite(row.offense.expected));
  const width=1180,height=560,left=260,right=70,top=118,bottom=54,rowH=92,plotW=width-left-right;
  const id=isMichigan?"michigan-offense-actual-expected":"opponent-offense-actual-expected";
  return <section className={styles.chartBlock}>
    <header className={styles.chartTitle}><div><span>{isMichigan?"02 · MICHIGAN OFFENSE":"04 · OPPONENT OFFENSE"}</span><h3>{isMichigan?`How Michigan's offense performed against ${game.opponentName}`:`How ${game.opponentName}'s offense performed against Michigan`}</h3><p>Actual rate versus the schedule-adjusted expectation. The game itself is removed from the expectation fit.</p></div><DownloadButton id={id} file={`${game.id}-${isMichigan?"michigan":"opponent"}-offense-rates.svg`}/></header>
    <div className={styles.desktopChart}><svg id={id} className={styles.svg} viewBox={`0 0 ${width} ${height}`} role="img">
      <rect width={width} height={height} rx="22" fill={COLORS.bg}/>
      <text x="54" y="42" fill={isMichigan?COLORS.maize:COLORS.sky} fontSize="14" fontWeight="850" letterSpacing="2">{teamName.toUpperCase()} OFFENSE · ACTUAL VS EXPECTED</text>
      <text x="54" y="72" fill={COLORS.text} fontSize="24" fontWeight="850">Was the offense better than this matchup should have allowed?</text>
      <text x="54" y="98" fill={COLORS.muted} fontSize="13">Longer actual bar than expected = offense exceeded expectation on that rate.</text>
      {[0,20,40,60,80].map(value=><g key={value}><line x1={left+plotW*value/80} x2={left+plotW*value/80} y1={top-8} y2={height-bottom} stroke={COLORS.grid}/><text x={left+plotW*value/80} y={height-25} textAnchor="middle" fill={COLORS.muted} fontSize="11">{value}%</text></g>)}
      {rows.map((row,index)=>{
        const y=top+index*rowH; const actual=(row.offense.actual as number)*100; const expected=(row.offense.expected as number)*100;
        return <g key={row.key}><text x="54" y={y+28} fill={COLORS.text} fontSize="14" fontWeight="800">{row.label}</text><text x="54" y={y+50} fill={COLORS.muted} fontSize="11">{compactDifference(row.offense.poe,row.unit)}</text><rect x={left} y={y+4} width={plotW*Math.min(80,actual)/80} height="23" rx="6" fill={isMichigan?COLORS.maize:COLORS.sky}/><rect x={left} y={y+36} width={plotW*Math.min(80,expected)/80} height="15" rx="5" fill={COLORS.muted} opacity=".46"/><text x={Math.min(width-68,left+plotW*Math.min(80,actual)/80+9)} y={y+20} fill={COLORS.text} fontSize="12" fontWeight="800">Actual {actual.toFixed(1)}%</text><text x={Math.min(width-68,left+plotW*Math.min(80,expected)/80+9)} y={y+48} fill={COLORS.muted} fontSize="11">Expected {expected.toFixed(1)}%</text></g>;
      })}
    </svg></div>
    <div className={styles.mobileMetrics}>{rows.map(row=><article key={row.key}><h4>{row.label}</h4><p>{row.explanation}</p><div><span>Actual <b>{formatValue(row.offense.actual,row.unit)}</b></span><span>Expected <b>{formatValue(row.offense.expected,row.unit)}</b></span></div><DifferenceBadge value={row.offense.poe} unit={row.unit}/></article>)}</div>
  </section>;
}

function YardsPerPlayStory({game}:{game:MichiganGameDossier}){
  const mich=metricRow(game.michiganMetrics,"yardsPerPlay");
  const opp=metricRow(game.opponentMetrics,"yardsPerPlay");
  if(!mich||!opp)return null;
  const max=Math.max(8,mich.offense.actual??0,mich.offense.expected??0,opp.offense.actual??0,opp.offense.expected??0)*1.08;
  const width=1180,height=420,left=250,right=65,top=128,rowH=115,plotW=width-left-right;
  return <section className={styles.chartBlock}>
    <header className={styles.chartTitle}><div><span>03 · TOTAL EFFICIENCY</span><h3>Yards per play: the number that can either confirm the story or hide it</h3><p>Yards per play is shown separately because it uses a different unit than the rate metrics above.</p></div><DownloadButton id="game-ypp-story" file={`${game.id}-yards-per-play.svg`}/></header>
    <div className={styles.desktopChart}><svg id="game-ypp-story" className={styles.svg} viewBox={`0 0 ${width} ${height}`} role="img">
      <rect width={width} height={height} rx="22" fill={COLORS.bg}/><text x="54" y="42" fill={COLORS.maize} fontSize="14" fontWeight="850" letterSpacing="2">YARDS PER PLAY · ACTUAL VS EXPECTED</text><text x="54" y="73" fill={COLORS.text} fontSize="24" fontWeight="850">How efficiently did each offense move the ball?</text><text x="54" y="99" fill={COLORS.muted} fontSize="13">Compare the solid actual bar to the faded expected bar. The difference is already opponent adjusted.</text>
      {[0,2,4,6,8].map(value=><g key={value}><line x1={left+plotW*value/max} x2={left+plotW*value/max} y1={top-8} y2={height-55} stroke={COLORS.grid}/><text x={left+plotW*value/max} y={height-27} textAnchor="middle" fill={COLORS.muted} fontSize="11">{value}</text></g>)}
      {[{name:"Michigan offense",row:mich,color:COLORS.maize},{name:`${game.opponentName} offense`,row:opp,color:COLORS.sky}].map((item,index)=>{const y=top+index*rowH;const actual=item.row.offense.actual??0;const expected=item.row.offense.expected??0;return <g key={item.name}><text x="54" y={y+27} fill={COLORS.text} fontSize="15" fontWeight="800">{item.name}</text><text x="54" y={y+51} fill={finite(item.row.offense.poe)&&item.row.offense.poe>=0?COLORS.signal:COLORS.danger} fontSize="12" fontWeight="800">{formatDifference(item.row.offense.poe,"yards")}</text><rect x={left} y={y+2} width={plotW*actual/max} height="27" rx="6" fill={item.color}/><rect x={left} y={y+39} width={plotW*expected/max} height="18" rx="5" fill={COLORS.muted} opacity=".45"/><text x={Math.min(width-70,left+plotW*actual/max+10)} y={y+21} fill={COLORS.text} fontSize="12" fontWeight="800">Actual {actual.toFixed(2)}</text><text x={Math.min(width-70,left+plotW*expected/max+10)} y={y+53} fill={COLORS.muted} fontSize="11">Expected {expected.toFixed(2)}</text></g>})}
    </svg></div>
    <div className={styles.twoStatCards}><article><span>Michigan offense</span><strong>{formatValue(mich.offense.actual,"yards")}</strong><p>Expected {formatValue(mich.offense.expected,"yards")}</p><DifferenceBadge value={mich.offense.poe} unit="yards"/></article><article><span>{game.opponentName} offense</span><strong>{formatValue(opp.offense.actual,"yards")}</strong><p>Expected {formatValue(opp.offense.expected,"yards")}</p><DifferenceBadge value={opp.offense.poe} unit="yards"/></article></div>
  </section>;
}

function TwoWayExpectation({game}:{game:MichiganGameDossier}){
  const rows=RATE_KEYS.map(key=>({mich:metricRow(game.michiganMetrics,key),opp:metricRow(game.opponentMetrics,key)})).filter((row):row is {mich:GameMetricView;opp:GameMetricView}=>row.mich!==null&&row.opp!==null&&finite(row.mich.offense.poe)&&finite(row.opp.offense.poe));
  const maxAbs=Math.max(5,...rows.flatMap(row=>[Math.abs((row.mich.offense.poe as number)*100),Math.abs((row.opp.offense.poe as number)*100)]))*1.15;
  const width=1180,height=515,left=330,right=80,top=123,rowH=78,center=left+(width-left-right)/2,half=(width-left-right)/2;
  return <section className={styles.chartBlock}>
    <header className={styles.chartTitle}><div><span>05 · WHO BEAT EXPECTATION?</span><h3>Michigan versus {game.opponentName}, graded against what each opponent should have allowed</h3><p>This is the cleanest two-way view. Michigan's offense is on the left; {game.opponentName}'s offense is on the right. Both are judged relative to the defense they faced.</p></div><DownloadButton id="two-way-expectation" file={`${game.id}-two-way-expectation.svg`}/></header>
    <div className={styles.desktopChart}><svg id="two-way-expectation" className={styles.svg} viewBox={`0 0 ${width} ${height}`} role="img">
      <rect width={width} height={height} rx="22" fill={COLORS.bg}/><text x="54" y="43" fill={COLORS.sky} fontSize="14" fontWeight="850" letterSpacing="2">PERFORMANCE RELATIVE TO EXPECTATION</text><text x="54" y="74" fill={COLORS.text} fontSize="24" fontWeight="850">Who actually played above the level the matchup called for?</text><text x="54" y="100" fill={COLORS.muted} fontSize="13">Values are percentage-point differences between actual and expected rates. Farther from center = larger over/underperformance.</text><line x1={center} x2={center} y1={top-12} y2={height-55} stroke={COLORS.muted} strokeWidth="1.5"/><text x={center-16} y={top-18} textAnchor="end" fill={COLORS.maize} fontSize="13" fontWeight="800">Michigan offense</text><text x={center+16} y={top-18} fill={COLORS.sky} fontSize="13" fontWeight="800">{game.opponentName} offense</text>
      {rows.map((row,index)=>{const y=top+index*rowH;const m=(row.mich.offense.poe as number)*100;const o=(row.opp.offense.poe as number)*100;const mw=half*Math.abs(m)/maxAbs;const ow=half*Math.abs(o)/maxAbs;return <g key={row.mich.key}><text x="54" y={y+25} fill={COLORS.text} fontSize="14" fontWeight="800">{row.mich.label}</text><rect x={m>=0?center-mw:center} y={y+4} width={mw} height="24" rx="6" fill={m>=0?COLORS.signal:COLORS.danger} opacity=".92"/><rect x={o>=0?center:center-ow} y={y+36} width={ow} height="24" rx="6" fill={o>=0?COLORS.signal:COLORS.danger} opacity=".92"/><text x={center-12} y={y+22} textAnchor="end" fill={COLORS.text} fontSize="11" fontWeight="800">MICH {compactDifference(row.mich.offense.poe,"rate")}</text><text x={center+12} y={y+54} fill={COLORS.text} fontSize="11" fontWeight="800">{game.opponentName.toUpperCase()} {compactDifference(row.opp.offense.poe,"rate")}</text></g>})}
      <text x={center} y={height-25} textAnchor="middle" fill={COLORS.muted} fontSize="11">Center = exactly what the matchup model expected</text>
    </svg></div>
    <div className={styles.mobileMetrics}>{rows.map(row=><article key={row.mich.key}><h4>{row.mich.label}</h4><p>{row.mich.explanation}</p><div><span>Michigan <b>{formatDifference(row.mich.offense.poe,"rate")}</b></span><span>{game.opponentName} <b>{formatDifference(row.opp.offense.poe,"rate")}</b></span></div></article>)}</div>
  </section>;
}

function AudienceTakeaway({game}:{game:MichiganGameDossier}){
  const mich=strongestRate(game.michiganMetrics,"offense");
  const opp=strongestRate(game.opponentMetrics,"offense");
  const michYpp=metricRow(game.michiganMetrics,"yardsPerPlay");
  const oppYpp=metricRow(game.opponentMetrics,"yardsPerPlay");
  const success=metricRow(game.michiganMetrics,"successRate");
  const divergence=success&&michYpp&&finite(success.offense.poe)&&finite(michYpp.offense.poe)&&Math.sign(success.offense.poe)!==Math.sign(michYpp.offense.poe);
  return <section className={styles.takeaway}>
    <span>06 · WHAT SHOULD THE AUDIENCE REMEMBER?</span>
    <h2>The game in plain English</h2>
    <div className={styles.takeawayGrid}>
      {mich&&<article><b>Michigan offense</b><p>{audienceSentence(mich.label,mich.offense.actual,mich.offense.expected,mich.offense.poe,mich.unit,"Michigan")}</p></article>}
      {opp&&<article><b>{game.opponentName} offense</b><p>{audienceSentence(opp.label,opp.offense.actual,opp.offense.expected,opp.offense.poe,opp.unit,game.opponentName)}</p></article>}
      {michYpp&&<article><b>Michigan total efficiency</b><p>{audienceSentence("Yards per play",michYpp.offense.actual,michYpp.offense.expected,michYpp.offense.poe,michYpp.unit,"Michigan")}</p></article>}
      {oppYpp&&<article><b>{game.opponentName} total efficiency</b><p>{audienceSentence("Yards per play",oppYpp.offense.actual,oppYpp.offense.expected,oppYpp.offense.poe,oppYpp.unit,game.opponentName)}</p></article>}
    </div>
    {divergence&&<div className={styles.storyAlert}><strong>The average can hide the story.</strong><p>Michigan's yards-per-play grade and success-rate grade point in opposite directions. That usually means a few productive plays changed the average while the offense told a different story down to down.</p></div>}
  </section>;
}

function Glossary({library}:{library:CreatorGameLibrary}){
  return <section className={styles.glossary}><span>METRICS, WITHOUT THE JARGON</span><h2>What are these charts actually measuring?</h2><div>{library.metrics.map(metric=><article key={metric.key}><b>{metric.label}</b><p>{metric.explanation}</p></article>)}</div></section>;
}

export function CreatorCharts({library}:{library:CreatorGameLibrary}){
  const [selectedId,setSelectedId]=useState(library.games[0]?.id??"");
  const selected=useMemo(()=>library.games.find(game=>game.id===selectedId)??library.games[0],[library.games,selectedId]);
  if(!selected)return <div className={styles.empty}>No Michigan games are available.</div>;

  return <div className={styles.page}>
    <header className={styles.hero}>
      <div className={styles.heroCopy}><span>CREATOR CHART ROOM · OPPONENT ADJUSTED</span><h1>EVERY GAME.<b>EXPLAINED.</b></h1><p>Choose any Michigan game from 2025. Instead of dumping advanced stats on the audience, each dossier answers the questions that matter: <strong>How strong was the opponent? What was Michigan expected to do? What actually happened? And did the opponent outperform Michigan's own strength?</strong></p><div className={styles.heroBadges}><b>{library.games.length} games</b><b>{library.metrics.length} validated core metrics</b><b>target game excluded from expectation</b><b>ridge {library.ridge}</b></div></div>
      <aside className={styles.heroAside}><span>THE RULE</span><strong>Context before conclusions.</strong><p>A 42% success rate can be excellent against one defense and disappointing against another. Every game page shows the opponent's adjusted strength before grading the performance.</p></aside>
    </header>

    <GamePicker library={library} selectedId={selected.id} onSelect={setSelectedId}/>
    <div className={styles.dossier} key={selected.id}>
      <MatchupContext library={library} game={selected}/>
      <MatchupRankTable library={library} game={selected}/>
      <ActualExpectedRates game={selected} team="Michigan" kind="offense"/>
      <YardsPerPlayStory game={selected}/>
      <ActualExpectedRates game={selected} team="Opponent" kind="offense"/>
      <TwoWayExpectation game={selected}/>
      <AudienceTakeaway game={selected}/>
      <Glossary library={library}/>
    </div>
  </div>;
}
