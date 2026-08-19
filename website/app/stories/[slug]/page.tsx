import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {storyBySlug} from "../../../lib/michigan/stories";
type Props={params:Promise<{slug:string}>};
export async function generateMetadata({params}:Props):Promise<Metadata>{const story=storyBySlug((await params).slug);if(!story)return{title:"Story not found"};return{title:story.title,description:story.deck,openGraph:{title:story.title,description:story.deck,images:[]},twitter:{title:story.title,description:story.deck,images:[]}}}
export default async function StoryPage({params}:Props){const story=storyBySlug((await params).slug);if(!story)notFound();return <article className="story-page page-pad"><header><span className="eyebrow">{story.eyebrow}</span><h1>{story.title}</h1><p>{story.deck}</p>{story.published&&<small>PUBLISHED {story.published.toUpperCase()}</small>}</header><div className="story-body">{story.body.map(paragraph=><p key={paragraph}>{paragraph}</p>)}</div>{story.sources&&<aside className="story-sources"><strong>SOURCES</strong>{story.sources.map(source=><a href={source.url} rel="noreferrer" target="_blank" key={source.url}>{source.label} ↗</a>)}</aside>}<footer>{story.playerId&&<Link className="button" href={`/players/${story.playerId}`}>OPEN PLAYER PROFILE</Link>}<Link className="button secondary" href="/stories">ALL STORIES</Link></footer></article>}
