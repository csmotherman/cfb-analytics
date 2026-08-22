import {createHash} from "node:crypto";
import {NextRequest,NextResponse} from "next/server";
import {FAN_POLLS,fanPollById} from "../../../lib/polls";

export const runtime="nodejs";
export const dynamic="force-dynamic";

type TotalRow={poll_id:string;option_id:string;votes:number|string};
type UserVoteRow={poll_id:string;option_id:string};
type SupabaseConfig={url:string;serviceKey:string;salt:string};

function config():SupabaseConfig|null{
  const url=(process.env.SUPABASE_URL??process.env.NEXT_PUBLIC_SUPABASE_URL??"").replace(/\/$/,"");
  const serviceKey=process.env.SUPABASE_SERVICE_ROLE_KEY??"";
  if(!url||!serviceKey)return null;
  return{url,serviceKey,salt:process.env.POLL_DEVICE_SALT??serviceKey};
}
function hashDevice(deviceId:string,salt:string){return createHash("sha256").update(`${salt}:${deviceId}`).digest("hex");}
async function supabaseFetch(cfg:SupabaseConfig,path:string,init:RequestInit={}){return fetch(`${cfg.url}/rest/v1/${path}`,{...init,cache:"no-store",headers:{apikey:cfg.serviceKey,Authorization:`Bearer ${cfg.serviceKey}`,"Content-Type":"application/json",...(init.headers??{})}});}
function emptyPayload(){return FAN_POLLS.map(poll=>({pollId:poll.id,totalVotes:0,userOptionId:null as string|null,options:poll.options.map(option=>({optionId:option.id,votes:0}))}));}
async function resultsPayload(cfg:SupabaseConfig,deviceHash:string|null){
  const totalsPromise=supabaseFetch(cfg,"poll_vote_totals?select=poll_id,option_id,votes");
  const userPromise=deviceHash?supabaseFetch(cfg,`poll_votes?select=poll_id,option_id&device_hash=eq.${encodeURIComponent(deviceHash)}`):Promise.resolve(null);
  const [totalsResponse,userResponse]=await Promise.all([totalsPromise,userPromise]);
  if(!totalsResponse.ok)throw new Error(`Poll totals request failed (${totalsResponse.status})`);
  if(userResponse&&!userResponse.ok)throw new Error(`Poll vote lookup failed (${userResponse.status})`);
  const totals=await totalsResponse.json() as TotalRow[];
  const userVotes=userResponse?await userResponse.json() as UserVoteRow[]:[];
  const totalMap=new Map(totals.map(row=>[`${row.poll_id}:${row.option_id}`,Number(row.votes)||0]));
  const userMap=new Map(userVotes.map(row=>[row.poll_id,row.option_id]));
  return FAN_POLLS.map(poll=>{const options=poll.options.map(option=>({optionId:option.id,votes:totalMap.get(`${poll.id}:${option.id}`)??0}));return{pollId:poll.id,totalVotes:options.reduce((sum,row)=>sum+row.votes,0),userOptionId:userMap.get(poll.id)??null,options};});
}

export async function GET(request:NextRequest){
  const cfg=config();
  if(!cfg)return NextResponse.json({configured:false,polls:emptyPayload(),message:"Community voting is not connected yet."});
  const deviceId=(request.nextUrl.searchParams.get("deviceId")??"").trim();
  const deviceHash=deviceId?hashDevice(deviceId,cfg.salt):null;
  try{return NextResponse.json({configured:true,polls:await resultsPayload(cfg,deviceHash)});}catch(error){console.error("polls:get",error);return NextResponse.json({configured:true,polls:emptyPayload(),message:"Community results are temporarily unavailable."},{status:502});}
}

export async function POST(request:NextRequest){
  const cfg=config();
  if(!cfg)return NextResponse.json({configured:false,message:"Community voting is not connected yet."},{status:503});
  let body:{pollId?:string;optionId?:string;deviceId?:string};
  try{body=await request.json();}catch{return NextResponse.json({message:"Invalid vote payload."},{status:400});}
  const pollId=String(body.pollId??"").trim(),optionId=String(body.optionId??"").trim(),deviceId=String(body.deviceId??"").trim();
  const poll=fanPollById(pollId);
  if(!poll||!poll.options.some(option=>option.id===optionId))return NextResponse.json({message:"Unknown poll choice."},{status:400});
  if(deviceId.length<8||deviceId.length>200)return NextResponse.json({message:"Invalid device identifier."},{status:400});
  const deviceHash=hashDevice(deviceId,cfg.salt);
  const response=await supabaseFetch(cfg,"poll_votes?on_conflict=poll_id,device_hash",{method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},body:JSON.stringify({poll_id:pollId,device_hash:deviceHash,option_id:optionId,updated_at:new Date().toISOString()})});
  if(!response.ok){console.error("polls:vote",response.status,await response.text());return NextResponse.json({message:"Your vote could not be saved."},{status:502});}
  try{return NextResponse.json({configured:true,polls:await resultsPayload(cfg,deviceHash)});}catch(error){console.error("polls:refresh",error);return NextResponse.json({configured:true,message:"Vote saved. Results are refreshing."});}
}
