import { NextResponse } from "next/server";
import { execFile } from "node:child_process";
import path from "node:path";
import { promisify } from "node:util";

const execFileAsync=promisify(execFile);

export async function POST(request:Request){
  try{
    const body=await request.json();
    const homeYear=Number(body.homeYear), awayYear=Number(body.awayYear), sims=Math.max(100,Math.min(250000,Number(body.sims)||10000));
    const homeTeam=String(body.homeTeam||"").trim(), awayTeam=String(body.awayTeam||"").trim();
    if(!homeYear||!awayYear||!homeTeam||!awayTeam) return NextResponse.json({error:"Home/away year and team are required."},{status:400});
    const root=path.resolve(process.cwd(),"..");
    const python=process.env.CFB_PYTHON||path.join(root,".venv","bin","python");
    const args=["website/scripts/simulate_json.py","--home-year",String(homeYear),"--home-team",homeTeam,"--away-year",String(awayYear),"--away-team",awayTeam,"--sims",String(sims)];
    const {stdout,stderr}=await execFileAsync(python,args,{cwd:root,timeout:20000,maxBuffer:2_000_000});
    const line=stdout.trim().split(/\r?\n/).filter(Boolean).at(-1);
    if(!line) throw new Error(stderr||"Simulator produced no JSON output.");
    return NextResponse.json(JSON.parse(line));
  }catch(error:any){
    return NextResponse.json({error:error?.stderr||error?.message||String(error)},{status:500});
  }
}
