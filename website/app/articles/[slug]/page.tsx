import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {storyBySlug} from "../../../lib/michigan/stories";
import {playerById} from "../../../lib/michigan/roster";
type Props={params:Promise<{slug:string}>};
export async function generateMetadata({params}:Props):Promise<Metadata>{const story=storyBySlug((await params).slug);if(!story)return{title:"Article not found"};return{title:story.title,description:story.deck,openGraph:{type:"article",title:story.title,description:story.deck,images:[]},twitter:{card:"summary",title:story.title,description:story.deck,images:[]}};}
export default async function Article({params}:Props){const story=storyBySlug((await params).slug);if(!story)notFound();const players=(story.playerIds??[]).map(playerById).filter(Boolean);return <article className="story-page article-detail page-pad">
  <header className="article-detail-hero"><div><div className="article-detail-tags">{story.tags.map(item=><span key={`${item.type}-${item.slug}`}>{item.label}</span>)}</div><span className="eyebrow">{story.eyebrow}</span><h1>{story.title}</h1><p>{story.deck}</p><small>{story.published?`PUBLISHED ${story.published.toUpperCase()} · `:""}{story.readMinutes??5} MIN READ</small></div></header>
  <div className="story-body">{story.body.map((paragraph,index)=><p className={index===0?"story-lede":undefined} key={paragraph}>{paragraph}</p>)}</div>
  <aside className="story-data"><header><span>DATA BEHIND THE STORY</span><h2>See the evidence.</h2><p>Open the numbers and profiles referenced by this analysis.</p></header><div>{story.dataLinks.map(link=><Link href={link.href} key={link.href}><span>FOCUS DATA</span><strong>{link.label}</strong><p>{link.description}</p><b>EXPLORE →</b></Link>)}</div></aside>
  {story.sources&&<aside className="story-sources"><strong>REPORTING SOURCES</strong>{story.sources.map(source=><a href={source.url} rel="noreferrer" target="_blank" key={source.url}>{source.label} ↗</a>)}</aside>}
  <footer>{players.map(player=>player&&<Link className="button" href={`/players/${player.id}`} key={player.id}>{player.firstName} {player.lastName} →</Link>)}<Link className="button secondary" href="/articles">ALL ARTICLES</Link></footer>
</article>;}
