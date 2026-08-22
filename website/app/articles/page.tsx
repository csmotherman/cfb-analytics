import type {Metadata} from "next";
import {ArticleLibrary} from "../../components/articles/ArticleLibrary";
import {michiganStories,type MichiganStory} from "../../lib/michigan/stories";

export const metadata:Metadata={title:"Michigan Football Articles",description:"Michigan football reporting connected directly to real data, player profiles and team evidence."};

const westernMichiganPreview:MichiganStory={
  slug:"michigan-western-michigan-2026-preview",
  eyebrow:"WEEK 1 · GAME PREVIEW",
  title:"Michigan vs. Western Michigan: The Data Says Michigan Should Run First and Make Broc Lowry Throw",
  coverQuestion:"Can Michigan turn its biggest matchup edge into a four-touchdown opener?",
  deck:"Michigan owns a massive offensive edge entering Week 1, but Western Michigan is not a typical MAC opener. The defending conference champions have a legitimate run game, a proven quarterback and a defense that was much better than its name recognition suggests.",
  published:"August 21, 2026",
  readMinutes:9,
  tags:[
    {type:"UNIT",slug:"offense",label:"Offense"},
    {type:"UNIT",slug:"defense",label:"Defense"},
    {type:"TOPIC",slug:"game-preview",label:"Game Preview"},
    {type:"TOPIC",slug:"analytics",label:"Analytics"}
  ],
  body:[],
  dataLinks:[
    {label:"Michigan vs. Western Michigan game hub",href:"/games/401858428",description:"View the Ridge comparison and current market spread."},
    {label:"Michigan analytics",href:"/analytics",description:"Explore the opponent-adjusted ratings behind the preview."}
  ]
};

export default function Articles(){
  const stories=[westernMichiganPreview,...michiganStories()];
  return <div className="articles-page"><section className="articles-hero"><div className="wrap"><span className="kicker maize">THE NOTEBOOK</span><h1>STORIES.<br/><b>BACKED BY DATA.</b></h1><p>Find the subject. Read the story. Open the evidence.</p><div><span><b>{stories.length}</b> STORIES</span><span><b>{new Set(stories.flatMap(story=>story.tags.map(item=>item.slug))).size}</b> TOPICS</span></div></div></section><main className="wrap articles-content"><ArticleLibrary stories={stories}/></main></div>;
}
