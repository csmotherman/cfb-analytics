"use client";

import {useMemo,useState} from "react";
import Link from "next/link";
import type {MichiganStory,StoryTagType} from "../../lib/michigan/stories";
import styles from "../../styles/articles.module.css";

const groupOrder:StoryTagType[]=["UNIT","TOPIC","POSITION"];

const storyMeta=(story:MichiganStory)=>[
  story.eyebrow,
  story.published,
  `${story.readMinutes??5} MIN READ`
].filter(Boolean).join(" · ");

export function ArticleLibrary({stories}:{stories:MichiganStory[]}){
  const [query,setQuery]=useState("");
  const [selected,setSelected]=useState<string[]>([]);

  const tags=useMemo(()=>Array.from(
    new Map(stories.flatMap(story=>story.tags).map(item=>[item.slug,item])).values()
  ).sort((a,b)=>{
    const groupDifference=groupOrder.indexOf(a.type)-groupOrder.indexOf(b.type);
    return groupDifference||a.label.localeCompare(b.label);
  }),[stories]);

  const shown=useMemo(()=>stories.filter(story=>{
    const search=query.trim().toLowerCase();
    const text=`${story.title} ${story.deck} ${story.eyebrow} ${story.coverQuestion??""} ${story.tags.map(item=>item.label).join(" ")}`.toLowerCase();
    return (!search||text.includes(search))&&selected.every(slug=>story.tags.some(item=>item.slug===slug));
  }),[stories,query,selected]);

  const toggle=(slug:string)=>setSelected(current=>current.includes(slug)?current.filter(item=>item!==slug):[...current,slug]);
  const reset=()=>{setQuery("");setSelected([]);};
  const hasFilters=query.trim().length>0||selected.length>0;
  const lead=shown[0];
  const remaining=shown.slice(1);

  return <section className={styles.library} aria-label="Michigan football articles">
    <header className={styles.libraryHeader}>
      <div className={styles.libraryHeading}>
        <span>LATEST COVERAGE</span>
        <h2>WHAT MICHIGAN FANS NEED TO KNOW</h2>
      </div>
      <label className={styles.search}>
        <span>SEARCH STORIES</span>
        <input
          type="search"
          value={query}
          onChange={event=>setQuery(event.target.value)}
          placeholder="Player, matchup, coaching…"
        />
      </label>
    </header>

    <div className={styles.discovery} aria-label="Filter stories">
      <div className={styles.filterRail}>
        <button type="button" className={selected.length===0?styles.active:""} onClick={()=>setSelected([])}>ALL</button>
        {tags.map(item=><button
          type="button"
          className={selected.includes(item.slug)?styles.active:""}
          aria-pressed={selected.includes(item.slug)}
          onClick={()=>toggle(item.slug)}
          key={`${item.type}-${item.slug}`}
        >{item.label.toUpperCase()}</button>)}
      </div>
      <div className={styles.resultCount} aria-live="polite"><b>{shown.length}</b>{shown.length===1?"STORY":"STORIES"}</div>
    </div>

    {lead?<>
      <Link href={`/articles/${lead.slug}`} className={styles.featured}>
        <div className={styles.featuredVisual}>
          {lead.coverImage?<img src={lead.coverImage} alt=""/>:<div className={styles.imageFallback} aria-hidden="true">M</div>}
          <span className={styles.featuredBadge}>{hasFilters?"TOP MATCH":"LATEST"}</span>
        </div>
        <div className={styles.featuredCopy}>
          <span className={styles.eyebrow}>{lead.eyebrow}</span>
          <h3>{lead.title}</h3>
          <p>{lead.deck}</p>
          <div className={styles.featuredFooter}>
            <span>{lead.published??"Michigan Football Focus"} · {lead.readMinutes??5} MIN READ</span>
            <b>READ STORY <i>→</i></b>
          </div>
        </div>
      </Link>

      {remaining.length>0&&<div className={styles.storyList}>
        {remaining.map(story=><Link href={`/articles/${story.slug}`} className={styles.storyRow} key={story.slug}>
          <div className={styles.storyThumb}>
            {story.coverImage?<img src={story.coverImage} alt=""/>:<div className={styles.imageFallback} aria-hidden="true">M</div>}
          </div>
          <div className={styles.storyCopy}>
            <span className={styles.storyMeta}>{storyMeta(story)}</span>
            <h3>{story.title}</h3>
            <p>{story.deck}</p>
          </div>
          <i className={styles.storyArrow} aria-hidden="true">›</i>
        </Link>)}
      </div>}
    </>:<div className={styles.empty}>
      <strong>No stories found.</strong>
      <p>Try a broader search or clear the active topics.</p>
      <button type="button" onClick={reset}>CLEAR FILTERS</button>
    </div>}
  </section>;
}
