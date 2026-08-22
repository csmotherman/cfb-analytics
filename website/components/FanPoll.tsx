"use client";
import {useCallback,useEffect,useMemo,useState} from "react";
import {FAN_POLLS} from "../lib/polls";

type ResultOption={optionId:string;votes:number};
type PollResult={pollId:string;totalVotes:number;userOptionId:string|null;options:ResultOption[]};
type PollResponse={configured:boolean;polls?:PollResult[];message?:string};
const DEVICE_KEY="mff-poll-device-v1";
function deviceId(){let value=localStorage.getItem(DEVICE_KEY);if(value)return value;value=globalThis.crypto?.randomUUID?.()??`${Date.now()}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;localStorage.setItem(DEVICE_KEY,value);return value;}
function pct(votes:number,total:number){return total?Math.round(votes/total*100):0;}
function voteLabel(count:number){return `${count.toLocaleString()} ${count===1?"vote":"votes"}`;}

export function FanPoll(){
  const [device,setDevice]=useState("");
  const [results,setResults]=useState<PollResult[]>([]);
  const [configured,setConfigured]=useState<boolean|null>(null);
  const [loading,setLoading]=useState(true);
  const [pending,setPending]=useState<string|null>(null);
  const [message,setMessage]=useState("");
  const resultByPoll=useMemo(()=>new Map(results.map(result=>[result.pollId,result])),[results]);

  const load=useCallback(async(id:string,quiet=false)=>{
    if(!quiet)setLoading(true);
    try{
      const response=await fetch(`/api/polls?deviceId=${encodeURIComponent(id)}`,{cache:"no-store"});
      const payload=await response.json() as PollResponse;
      setConfigured(payload.configured);
      if(payload.polls)setResults(payload.polls);
      setMessage(payload.message??"");
    }catch{setMessage("Community results are temporarily unavailable.");}
    finally{if(!quiet)setLoading(false);}
  },[]);

  useEffect(()=>{const id=deviceId();setDevice(id);void load(id);const timer=window.setInterval(()=>{if(document.visibilityState==="visible")void load(id,true);},60000);return()=>window.clearInterval(timer);},[load]);

  const vote=async(pollId:string,optionId:string)=>{
    if(!device||configured!==true||pending)return;
    setPending(pollId);setMessage("");
    try{
      const response=await fetch("/api/polls",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({pollId,optionId,deviceId:device})});
      const payload=await response.json() as PollResponse;
      if(!response.ok)throw new Error(payload.message??"Vote failed");
      if(payload.polls)setResults(payload.polls);else await load(device,true);
      if(payload.message)setMessage(payload.message);
    }catch(error){setMessage(error instanceof Error?error.message:"Your vote could not be saved.");}
    finally{setPending(null);}
  };

  return <>
    <section className="polls-status">
      <div><span>COMMUNITY BOARD</span><strong>{FAN_POLLS.length} live predictions</strong><p>One vote per browser/device profile for each question. Changing your pick replaces the old vote instead of adding another.</p></div>
      <div className="polls-live-state"><i className={configured?"online":""}/><b>{configured===null?"CONNECTING":configured?"LIVE RESULTS":"DATABASE SETUP NEEDED"}</b><small>{configured?"Results refresh every minute":"Voting activates after Supabase is connected"}</small></div>
    </section>
    {message&&<div className="polls-message" role="status">{message}</div>}
    <div className="poll-grid" aria-busy={loading}>
      {FAN_POLLS.map((poll,index)=>{
        const result=resultByPoll.get(poll.id);
        const total=result?.totalVotes??0;
        const userPick=result?.userOptionId??null;
        const reveal=Boolean(userPick);
        return <article className={`poll-card ${userPick?"voted":""}`} key={poll.id}>
          <header><div><span>{poll.category}</span><small>{String(index+1).padStart(2,"0")} / {String(FAN_POLLS.length).padStart(2,"0")}</small></div><h2>{poll.question}</h2><p>{poll.description}</p></header>
          <div className="poll-options">
            {poll.options.map(option=>{
              const votes=result?.options.find(row=>row.optionId===option.id)?.votes??0;
              const percentage=pct(votes,total);
              const selected=userPick===option.id;
              return <button type="button" className={selected?"selected":""} disabled={configured!==true||pending===poll.id} onClick={()=>void vote(poll.id,option.id)} key={option.id} aria-pressed={selected}>
                <span className="poll-option-copy"><strong>{option.label}</strong>{option.detail&&<small>{option.detail}</small>}</span>
                {reveal&&<span className="poll-option-result"><b>{percentage}%</b><small>{voteLabel(votes)}</small></span>}
                {reveal&&<i className="poll-option-bar" style={{"--poll-width":`${percentage}%`} as React.CSSProperties}/>} 
              </button>;
            })}
          </div>
          <footer>{loading&&!result?<span>Loading community results…</span>:userPick?<span><b>YOUR PICK LOCKED</b> · tap another choice to change it</span>:<span>Vote to reveal the community split</span>}<strong>{voteLabel(total)}</strong></footer>
        </article>;
      })}
    </div>
  </>;
}
