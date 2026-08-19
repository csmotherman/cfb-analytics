import type {Metadata} from "next";
import {ArticleLibrary} from "../../components/articles/ArticleLibrary";
import {michiganStories} from "../../lib/michigan/stories";
export const metadata:Metadata={title:"Michigan Football Articles",description:"Michigan football reporting connected directly to real data, player profiles and team evidence."};
export default function Articles(){const stories=michiganStories();return <div className="articles-page"><section className="articles-hero"><div className="wrap"><span className="kicker maize">THE NOTEBOOK</span><h1>STORIES.<br/><b>BACKED BY DATA.</b></h1><p>Find the subject. Read the story. Open the evidence.</p><div><span><b>{stories.length}</b> STORIES</span><span><b>{new Set(stories.flatMap(story=>story.tags.map(item=>item.slug))).size}</b> TOPICS</span></div></div></section><main className="wrap articles-content"><ArticleLibrary stories={stories}/></main></div>}
