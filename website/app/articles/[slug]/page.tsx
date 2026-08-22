import type {Metadata} from "next";
import Link from "next/link";
import {notFound} from "next/navigation";
import {michiganStories,storyBySlug} from "../../../lib/michigan/stories";

type Props={params:Promise<{slug:string}>};

export const dynamicParams=false;
export function generateStaticParams(){return michiganStories().map(story=>({slug:story.slug}));}

export async function generateMetadata({params}:Props):Promise<Metadata>{
  const story=storyBySlug((await params).slug);
  if(!story)return{title:"Article not found"};
  const images=story.coverImage?[story.coverImage]:[];
  return{
    title:story.title,
    description:story.deck,
    openGraph:{type:"article",title:story.title,description:story.deck,images},
    twitter:{card:"summary_large_image",title:story.title,description:story.deck,images}
  };
}

export default async function Article({params}:Props){
  const story=storyBySlug((await params).slug);
  if(!story)notFound();

  return <article className="focus-article">
    <div className="focus-article-shell">
      <header className="focus-article-hero">
        {story.coverImage&&<img src={story.coverImage} alt=""/>}
        <div className="focus-article-hero-fade"/>
        <div className="focus-article-hero-copy">
          <span className="focus-article-eyebrow">{story.eyebrow}</span>
          <h1>{story.title}</h1>
          <p>{story.deck}</p>
          <div className="focus-article-meta">
            {story.published&&<span>{story.published}</span>}
            <span>{story.readMinutes??5} MIN READ</span>
          </div>
        </div>
      </header>

      <div className="focus-article-body">
        {story.body.map((paragraph,index)=><p className={index===0?"focus-article-lede":undefined} key={`${index}-${paragraph.slice(0,24)}`}>{paragraph}</p>)}
      </div>

      {story.dataLinks.length>0&&<section className="focus-article-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>See the numbers behind the story.</h2></div>
        <div className="focus-article-link-grid">
          {story.dataLinks.map(link=><Link href={link.href} key={link.href}><strong>{link.label}</strong><p>{link.description}</p><span>VIEW →</span></Link>)}
        </div>
      </section>}

      {story.sources&&story.sources.length>0&&<section className="focus-article-sources">
        <strong>REPORTING & DATA SOURCES</strong>
        <div>{story.sources.map(source=><a href={source.url} rel="noreferrer" target="_blank" key={source.url}>{source.label} ↗</a>)}</div>
      </section>}

      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}
