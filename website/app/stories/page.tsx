import Link from "next/link";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { michiganStories } from "../../lib/michigan/stories";

export default function StoriesPage() {
  const stories = michiganStories();
  return <div className="page-stack page-pad">
    <section className="page-hero"><span className="eyebrow">THE MICHIGAN NOTEBOOK</span><h1>THE TEAM.<br/>THE STORIES.</h1><p>Players, recruiting, rivalries and Saturdays in Ann Arbor.</p></section>
    <section><SectionHeader eyebrow="LATEST" title="From inside the roster.">Michigan football, one story at a time.</SectionHeader><div className="story-grid">{stories.map((story, index) => <Link className={index === 0 ? "story-card featured" : "story-card"} href={`/stories/${story.slug}`} key={story.slug}><span>{story.eyebrow}</span><h2>{story.title}</h2><p>{story.deck}</p><b>READ THE STORY →</b></Link>)}</div></section>
  </div>;
}
