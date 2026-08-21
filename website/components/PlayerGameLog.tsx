"use client";

import {useMemo,useState} from "react";
import {teamLogoUrl} from "../lib/team-assets";

type GameStat={category:string;stat:string;value:string|number};
type GameRow={gameId:string;season:number;team:string;teamId?:number|null;week?:number|null;seasonType?:string|null;opponent?:string|null;homeAway?:string|null;result?:string|null;startDate?:string|null;position?:string|null;displayStats:GameStat[]};
export type PlayerGameLogYear={season:number;team?:string|null;teamId?:number|null;games:GameRow[]};

type Props={years:PlayerGameLogYear[]};

const key=(stat:GameStat)=>`${stat.category}:${stat.stat}`;
const value=(v:string|number)=>typeof v==="number"?(Number.isInteger(v)?v.toLocaleString():v.toFixed(1)):v;
const label=(stat:GameStat)=>{
  const labels:Record<string,string>={
    "passing:C/ATT":"C/ATT","passing:YDS":"PASS YDS","passing:TD":"PASS TD","passing:INT":"INT","passing:QBR":"QBR",
    "rushing:CAR":"CAR","rushing:YDS":"RUSH YDS","rushing:AVG":"YPC","rushing:TD":"RUSH TD","rushing:LONG":"LONG",
    "receiving:REC":"REC","receiving:YDS":"REC YDS","receiving:AVG":"YPR","receiving:TD":"REC TD","receiving:LONG":"LONG",
    "fumbles:FUM":"FUM","fumbles:LOST":"LOST",
    "defensive:TOT":"TACKLES","defensive:SOLO":"SOLO","defensive:TFL":"TFL","defensive:SACKS":"SACKS","defensive:QB HUR":"QB HUR","defensive:PD":"PD",
    "interceptions:INT":"INT","interceptions:YDS":"INT YDS","interceptions:TD":"INT TD",
    "kicking:FG":"FG","kicking:LONG":"LONG","kicking:XP":"XP","kicking:PTS":"PTS",
    "punting:NO":"PUNTS","punting:YDS":"PUNT YDS","punting:AVG":"AVG","punting:LONG":"LONG","punting:In 20":"IN 20","punting:TB":"TB",
    "kickReturns:NO":"KR","kickReturns:YDS":"KR YDS","kickReturns:AVG":"KR AVG","kickReturns:LONG":"KR LONG","kickReturns:TD":"KR TD",
    "puntReturns:NO":"PR","puntReturns:YDS":"PR YDS","puntReturns:AVG":"PR AVG","puntReturns:LONG":"PR LONG","puntReturns:TD":"PR TD",
  };
  return labels[key(stat)]??stat.stat;
};

export default function PlayerGameLog({years}:Props){
  const available=useMemo(()=>years.filter(year=>year.games?.length).sort((a,b)=>b.season-a.season),[years]);
  const [season,setSeason]=useState<number|null>(available[0]?.season??null);
  const active=available.find(year=>year.season===season)??available[0];
  const columns=useMemo(()=>active?Array.from(new Map(active.games.flatMap(game=>game.displayStats??[]).map(stat=>[key(stat),stat])).values()):[],[active]);

  if(!active)return <div className="player-focus-empty"><b>No verified game logs yet.</b><p>Game-by-game production will appear when a verified player box-score feed exists for this player.</p></div>;

  return <div className="player-game-log">
    <div className="player-game-year-tabs" role="tablist" aria-label="Game log season">
      {available.map(year=><button key={year.season} type="button" role="tab" aria-selected={active.season===year.season} className={active.season===year.season?"active":""} onClick={()=>setSeason(year.season)}>{year.season}</button>)}
    </div>
    <div className="player-game-season-meta">
      <div>{active.teamId?<img src={teamLogoUrl(active.teamId,64)} alt=""/>:null}<span>{active.team??"College"}</span></div>
      <small>{active.games.length} GAME{active.games.length===1?"":"S"}</small>
    </div>
    <div className="player-stat-table-shell player-game-table-shell">
      <div className="player-stat-swipe" aria-hidden="true">Swipe to see more <span>→</span></div>
      <div className="player-stat-table-wrap" role="region" aria-label={`${active.season} game log. Swipe horizontally to see more columns.`} tabIndex={0}>
        <table className="player-stat-table player-game-table">
          <thead><tr><th className="sticky-game">GAME</th><th>RESULT</th>{columns.map(stat=><th key={key(stat)}>{label(stat)}</th>)}</tr></thead>
          <tbody>{active.games.map(game=><tr key={game.gameId}>
            <td className="sticky-game"><div className="player-game-opponent"><small>{game.week?`WK ${game.week}`:(game.seasonType??"").toUpperCase()}</small><strong>{game.homeAway==="away"?"@ ":"vs "}{game.opponent??"Opponent"}</strong></div></td>
            <td><span className={`player-game-result ${game.result?.startsWith("W")?"win":game.result?.startsWith("L")?"loss":""}`}>{game.result??"—"}</span></td>
            {columns.map(column=>{const stat=game.displayStats?.find(item=>key(item)===key(column));return <td key={key(column)}>{stat==null?"—":value(stat.value)}</td>;})}
          </tr>)}</tbody>
        </table>
      </div>
    </div>
  </div>;
}
