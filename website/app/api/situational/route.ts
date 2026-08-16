import {NextRequest,NextResponse} from "next/server";
import {seasonSituationalRows,type SituationalRow} from "../../../lib/data";

type Totals={plays:number;successes:number;yards:number;firstDowns:number;rushPlays:number;passPlays:number;rushSuccesses:number;passSuccesses:number;rushYards:number;passYards:number;explosiveEligiblePlays:number;explosivePlays:number;conversionAttempts:number;conversions:number;};

const EMPTY:Totals={plays:0,successes:0,yards:0,firstDowns:0,rushPlays:0,passPlays:0,rushSuccesses:0,passSuccesses:0,rushYards:0,passYards:0,explosiveEligiblePlays:0,explosivePlays:0,conversionAttempts:0,conversions:0};
const COUNT_KEYS=Object.keys(EMPTY) as (keyof Totals)[];

function rate(n:number,d:number){return d?n/d:null;}
function pctRank(value:number|null,pop:number[],lowerIsBetter=false){
  if(value===null||!pop.length)return null;
  const vals=pop.filter(Number.isFinite).sort((a,b)=>a-b);
  if(!vals.length)return null;
  const lower=vals.filter(v=>v<value).length;
  const equal=vals.filter(v=>v===value).length;
  let p=100*(lower+0.5*equal)/vals.length;
  if(lowerIsBetter)p=100-p;
  return p;
}
function grade(p:number|null){
  if(p===null)return "—";
  if(p>=97)return "A+"; if(p>=90)return "A"; if(p>=83)return "A-";
  if(p>=77)return "B+"; if(p>=70)return "B"; if(p>=63)return "B-";
  if(p>=57)return "C+"; if(p>=50)return "C"; if(p>=43)return "C-";
  if(p>=37)return "D+"; if(p>=30)return "D"; if(p>=20)return "D-"; return "F";
}
function aggregate(rows:SituationalRow[]){
  const t={...EMPTY};
  for(const r of rows)for(const k of COUNT_KEYS)t[k]+=Number(r[k]||0);
  const calls=t.rushPlays+t.passPlays;
  return {
    ...t,
    successRate:rate(t.successes,t.plays),
    conversionRate:rate(t.conversions,t.conversionAttempts),
    firstDownRate:rate(t.firstDowns,t.plays),
    yardsPerPlay:rate(t.yards,t.plays),
    runRate:rate(t.rushPlays,calls),
    passRate:rate(t.passPlays,calls),
    runSuccessRate:rate(t.rushSuccesses,t.rushPlays),
    passSuccessRate:rate(t.passSuccesses,t.passPlays),
    rushYpp:rate(t.rushYards,t.rushPlays),
    passYpp:rate(t.passYards,t.passPlays),
    explosiveRate:rate(t.explosivePlays,t.explosiveEligiblePlays),
  };
}

export async function GET(req:NextRequest){
  const q=req.nextUrl.searchParams;
  const season=Number(q.get("season"));
  const team=String(q.get("team")||"");
  const side=q.get("side")==="defense"?"defense":"offense";
  const down=Math.max(1,Math.min(4,Number(q.get("down")||3)));
  const distance=Math.max(1,Math.min(99,Number(q.get("distance")||3)));
  const quarter=q.get("quarter")||"all";
  const score=q.get("score")||"all";
  const field=q.get("field")||"all";
  const goalToGo=q.get("goalToGo")==="true";
  const all=seasonSituationalRows(season);
  if(!all.length)return NextResponse.json({error:"No situational data for season"},{status:404});

  const filtered=all.filter(r=>{
    if(r.side!==side||Number(r.down)!==down||Number(r.distance)!==distance)return false;
    if(quarter!=="all"&&String(r.quarter)!==quarter)return false;
    if(score!=="all"&&String(r.scoreState)!==score)return false;
    if(field!=="all"){
      const b=String(r.fieldPositionBucket);
      if(field==="own"&&!['own_1_20','own_21_40'].includes(b))return false;
      if(field==="midfield"&&b!=="midfield")return false;
      if(field==="opponent"&&!['opponent_21_40','red_zone'].includes(b))return false;
      if(field==="red_zone"&&b!=="red_zone")return false;
    }
    if(goalToGo&&!r.goalToGo)return false;
    return true;
  });

  const byTeam=new Map<string,SituationalRow[]>();
  for(const r of filtered){const arr=byTeam.get(r.team)||[];arr.push(r);byTeam.set(r.team,arr);}
  const summaries=[...byTeam.entries()].map(([name,rs])=>({team:name,...aggregate(rs)}));
  const current=summaries.find(x=>x.team.toLowerCase()===team.toLowerCase())||{team,...aggregate([])};
  const eligible=summaries.filter(x=>x.plays>=10);
  const lowerIsBetter=side==="defense";
  const metricKeys=["successRate","conversionRate","firstDownRate","yardsPerPlay","runSuccessRate","passSuccessRate","rushYpp","passYpp","explosiveRate"] as const;
  const percentiles:Record<string,number|null>={};
  const grades:Record<string,string>={};
  for(const key of metricKeys){
    const pop=eligible.map(x=>x[key]).filter((v):v is number=>typeof v==="number"&&Number.isFinite(v));
    const p=pctRank(current[key] as number|null,pop,lowerIsBetter);
    percentiles[key]=p; grades[key]=grade(p);
  }
  const primaryKey=(down===3||down===4)?"conversionRate":"successRate";
  const leaderboard=eligible
    .filter(x=>typeof x[primaryKey]==="number")
    .sort((a,b)=>lowerIsBetter?Number(a[primaryKey])-Number(b[primaryKey]):Number(b[primaryKey])-Number(a[primaryKey]))
    .slice(0,10)
    .map((x,i)=>({rank:i+1,team:x.team,plays:x.plays,value:x[primaryKey],grade:grade(pctRank(x[primaryKey] as number,eligible.map(e=>e[primaryKey]).filter((v):v is number=>typeof v==="number"),lowerIsBetter))}));

  return NextResponse.json({
    team,season,side,down,distance,
    primaryMetric:primaryKey,
    sampleMinimum:10,
    current,
    percentiles,
    grades,
    leaderboard,
    eligibleTeams:eligible.length,
  });
}
