"use client";
import {useMemo,useState} from "react";
import Link from "next/link";
import type {MichiganStory,StoryTagType} from "../../lib/michigan/stories";

const groups:StoryTagType[]=["POSITION","UNIT","TOPIC"];
const hooks:Record<string,string>={
  "underwood-marsh-sophomore-connection":"Can one connection unlock Michigan's entire offense?",
  "marshall-hiter-backfield":"Does Michigan have the Big Ten's most dangerous backfield?",
  "john-henry-daley-pressure":"Did Michigan just solve its biggest pass-rush problem?",
  "team-147-leadership-spine":"Who does Michigan trust when the season turns?",
  "2026-coaching-staff":"What will actually change under Michigan's new staff?",
  "2026-class-blueprint":"Which recruit changes Michigan's future first?"
};
const storyHook=(story:MichiganStory)=>hooks[story.slug]??story.coverQuestion??story.title;
const storyType=(story:MichiganStory)=>story.slug.startsWith("player-")?"PLAYER BRIEF":"FEATURE";
export function ArticleLibrary({stories}:{stories:MichiganStory[]}){
  const [query,setQuery]=useState("");
  const [selected,setSelected]=useState<string[]>([]);
  const tags=useMemo(()=>groups.map(type=>({type,tags:Array.from(new Map(stories.flatMap(story=>story.tags).filter(item=>item.type===type).map(item=>[item.slug,item])).values()).sort((a,b)=>a.label.localeCompare(b.label))})).filter(group=>group.tags.length),[stories]);
  const shown=useMemo(()=>stories.filter(story=>{const text=`${story.title} ${story.deck} ${story.tags.map(item=>item.label).join(" ")}`.toLowerCase();return text.includes(query.trim().toLowerCase())&&selected.every(slug=>story.tags.some(item=>item.slug===slug));}),[stories,query,selected]);
  const toggle=(slug:string)=>setSelected(current=>current.includes(slug)?current.filter(item=>item!==slug):[...current,slug]);
  return <>
    <section className="article-tools" aria-label="Find articles"><label><span>SEARCH THE NOTEBOOK</span><input type="search" value={query} onChange={event=>setQuery(event.target.value)} placeholder="Player, position, scheme, recruiting…"/></label><div className="article-filter-groups">{tags.map(group=><div key={group.type}><strong>{group.type}</strong><div>{group.tags.map(item=><button type="button" aria-pressed={selected.includes(item.slug)} onClick={()=>toggle(item.slug)} key={item.slug}>{item.label}</button>)}</div></div>)}</div>{selected.length>0&&<button type="button" className="clear-article-filters" onClick={()=>setSelected([])}>CLEAR ALL FILTERS</button>}</section>
    <section className="article-results" aria-live="polite"><div><b>{shown.length}</b> {shown.length===1?"STORY":"STORIES"}{selected.length?" MATCH YOUR FILTERS":" IN THE NOTEBOOK"}</div>{shown.length?<div className="article-library-grid">{shown.map((story,index)=><Link href={`/articles/${story.slug}`} className={`${index===0&&!query&&!selected.length?"article-library-card lead":"article-library-card"}${story.slug.startsWith("player-")?" player-brief":""}`} key={story.slug}><div className="article-card-copy"><span>{storyType(story)} · {story.eyebrow}</span><h2>{storyHook(story)}</h2><p>{story.deck}</p><div className="article-card-tags">{story.tags.slice(0,3).map(item=><small key={`${item.type}-${item.slug}`}>{item.label}</small>)}</div><b>{story.readMinutes??5} MIN READ <i>→</i></b></div></Link>)}</div>:<div className="article-empty"><strong>No stories found.</strong><p>Try removing a tag or using a broader search.</p></div>}</section>
  </>;
}
