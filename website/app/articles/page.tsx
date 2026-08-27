import type {Metadata} from "next";
import {ArticleLibrary} from "../../components/articles/ArticleLibrary";
import {michiganStories,type MichiganStory} from "../../lib/michigan/stories";
import styles from "../../styles/articles.module.css";

export const metadata:Metadata={title:"Michigan Football Articles",description:"Michigan football reporting connected directly to real data, player profiles and team evidence."};

const westernMichiganPreview:MichiganStory={
  slug:"michigan-western-michigan-2026-preview",
  eyebrow:"WEEK 1 · GAME PREVIEW",
  title:"Michigan vs. Western Michigan: The Data Says Michigan Should Run First and Make Broc Lowry Throw",
  coverQuestion:"Can Michigan turn its biggest matchup edge into a four-touchdown opener?",
  deck:"Michigan owns a massive offensive edge entering Week 1, but Western Michigan is not a typical MAC opener. The defending conference champions have a legitimate run game, a proven quarterback and a defense that was much better than its name recognition suggests.",
  published:"August 21, 2026",
  readMinutes:9,
  coverImage:"/images/articles/michigan-western-michigan-2026-preview.jpg",
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

const playcallingAudit:MichiganStory={
  slug:"michigan-offense-2025-playcalling-audit",
  eyebrow:"DATA AUDIT · 2025 REGULAR SEASON",
  title:"Michigan's 13.5-Point Offensive Mystery",
  coverQuestion:"How did Jason Beck's Utah score 13.5 more points per game with almost the same offensive foundation?",
  deck:"Michigan and Utah were nearly identical in run share, overall success rate and yards per play. The gap exploded on the scoreboard. This audit shows where the separation actually appeared — and what that does and does not say about Jason Beck in 2026.",
  published:"August 27, 2026",
  readMinutes:10,
  coverImage:"/images/articles/jason-beck.png",
  tags:[
    {type:"UNIT",slug:"offense",label:"Offense"},
    {type:"POSITION",slug:"qb",label:"QB"},
    {type:"TOPIC",slug:"analytics",label:"Analytics"},
    {type:"TOPIC",slug:"coaching",label:"Coaching"}
  ],
  body:[],
  dataLinks:[
    {label:"2025 Michigan offense analytics",href:"/analytics/offense?year=2025",description:"See the full opponent-adjusted efficiency breakdown behind this audit."},
    {label:"Bryce Underwood profile",href:"/players/5141741",description:"Review Underwood's freshman production and 2026 roster profile."}
  ]
};

export default function Articles(){
  const stories=[playcallingAudit,westernMichiganPreview,...michiganStories()];
  return <div className={styles.page}>
    <header className={styles.hero}>
      <div className={`wrap ${styles.heroInner}`}>
        <span className="kicker maize">MICHIGAN FOOTBALL FOCUS</span>
        <div className={styles.heroLayout}>
          <div>
            <h1>THE NOTEBOOK</h1>
            <p>Michigan football news, previews and analysis backed by the numbers that matter.</p>
          </div>
          <div className={styles.heroCount} aria-label={`${stories.length} stories live`}>
            <b>{stories.length}</b>
            <span>STORIES LIVE</span>
          </div>
        </div>
      </div>
    </header>
    <div className={`wrap ${styles.content}`}>
      <ArticleLibrary stories={stories}/>
    </div>
  </div>;
}
