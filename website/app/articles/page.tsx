import type {Metadata} from "next";
import {ArticleLibrary} from "../../components/articles/ArticleLibrary";
import {michiganStories,type MichiganStory} from "../../lib/michigan/stories";
import styles from "../../styles/articles.module.css";

export const metadata:Metadata={title:"Michigan Football Articles",description:"Michigan football reporting connected directly to real data, player profiles and team evidence."};

const howMichiganBeatsOklahoma:MichiganStory={
  slug:"how-michigan-beats-oklahoma-2026",
  eyebrow:"WEEK 2 · GAME PREVIEW",
  title:"How Michigan Beats Oklahoma — and How Oklahoma Makes Sure It Doesn't",
  coverQuestion:"Can Michigan's offense find answers against the best defense it will see all year?",
  deck:"Oklahoma's defense graded as the #2 opponent-adjusted unit in the country last season. Michigan needed a walk-off touchdown to beat a MAC team at home. Both facts are true. Here's how each team actually wins Saturday, and the metrics that separate signal from noise.",
  published:"September 10, 2026",
  readMinutes:12,
  tags:[
    {type:"UNIT",slug:"offense",label:"Offense"},
    {type:"UNIT",slug:"defense",label:"Defense"},
    {type:"POSITION",slug:"qb",label:"QB"},
    {type:"TOPIC",slug:"game-preview",label:"Game Preview"},
    {type:"TOPIC",slug:"analytics",label:"Analytics"}
  ],
  body:[],
  dataLinks:[
    {label:"Michigan vs. Oklahoma data preview",href:"/articles/michigan-oklahoma-2026-preview",description:"The full 2025 baseline, Week 1 tape and market context behind this story."},
    {label:"Michigan vs. Oklahoma game hub",href:"/games/401856679",description:"Model projection, matchup details and market context."}
  ]
};

const oklahomaPreview:MichiganStory={
  slug:"michigan-oklahoma-2026-preview",
  eyebrow:"WEEK 2 · GAME PREVIEW",
  title:"Michigan vs. Oklahoma: The Week 2 Matchup Story",
  coverQuestion:"Oklahoma's defense graded #2 nationally last season. Is this the closest matchup Michigan has played all year?",
  deck:"A +3.2-point overall composite gap, not a blowout. The validated 2025 baseline, the Week 1 2026 tape and the market, kept labeled separately on purpose.",
  published:"September 10, 2026",
  readMinutes:9,
  tags:[
    {type:"UNIT",slug:"offense",label:"Offense"},
    {type:"UNIT",slug:"defense",label:"Defense"},
    {type:"TOPIC",slug:"game-preview",label:"Game Preview"},
    {type:"TOPIC",slug:"analytics",label:"Analytics"}
  ],
  body:[],
  dataLinks:[
    {label:"Michigan vs. Oklahoma game hub",href:"/games/401856679",description:"View the model comparison and current market spread."},
    {label:"Michigan analytics",href:"/analytics",description:"Explore the opponent-adjusted ratings behind the preview."}
  ]
};

const dontJumpTheGun:MichiganStory={
  slug:"dont-jump-the-gun-michigan-football-2026",
  eyebrow:"WEEK 1 · PERSPECTIVE",
  title:"Don't Jump the Gun: Why Michigan Is in a Better Spot Than It Looks",
  coverQuestion:"What should one terrible Saturday actually change about how we see Michigan?",
  deck:"Michigan's 13-12 escape against Western Michigan was unacceptable. It was also one game. The evidence says downgrade the Wolverines after Week 1 — don't reclassify them.",
  published:"September 8, 2026",
  readMinutes:14,
  coverImage:"/images/articles/michigan-western.png",
  tags:[
    {type:"UNIT",slug:"offense",label:"Offense"},
    {type:"UNIT",slug:"defense",label:"Defense"},
    {type:"POSITION",slug:"qb",label:"QB"},
    {type:"TOPIC",slug:"analytics",label:"Analytics"},
    {type:"TOPIC",slug:"coaching",label:"Coaching"}
  ],
  body:[],
  dataLinks:[
    {label:"Michigan's 2025 offensive audit",href:"/articles/michigan-offense-2025-playcalling-audit",description:"See the larger Jason Beck baseline that one 2026 game cannot erase."},
    {label:"SOAR analytics",href:"/analytics",description:"Explore the team efficiency data behind Michigan's broader outlook."}
  ]
};

const westernMichiganRecap:MichiganStory={
  slug:"michigan-western-michigan-2026-recap",
  eyebrow:"WEEK 1 RECAP · EPA & PENALTY AUDIT",
  title:"Michigan vs. Western Michigan by EPA: What the Turnovers and Penalties Actually Cost",
  coverQuestion:"Success rate liked Michigan's offense. Full-value EPA doesn't. And the defense that \"couldn't get off the field\" actually dominated per snap.",
  deck:"An independent, from-scratch EPA model — trained on 1.5M+ plays across 11 seasons — prices every snap of both units. Michigan's two turnovers were worth more than every other offensive snap combined. Its defense allowed −0.34 EPA per play and zero touchdowns, then gave back 5.6 expected points on one series to two of its own penalties — including a flag that erased a real interception.",
  published:"September 8, 2026",
  readMinutes:10,
  coverImage:"/images/articles/michigan-western.png",
  tags:[
    {type:"UNIT",slug:"offense",label:"Offense"},
    {type:"UNIT",slug:"defense",label:"Defense"},
    {type:"POSITION",slug:"qb",label:"QB"},
    {type:"TOPIC",slug:"game-recap",label:"Game Recap"},
    {type:"TOPIC",slug:"analytics",label:"Analytics"}
  ],
  body:[],
  dataLinks:[
    {label:"Michigan vs. Western Michigan game hub",href:"/games/401858428",description:"Full game data, model comparison and market context."},
    {label:"Michigan analytics",href:"/analytics",description:"Explore the opponent-adjusted ratings behind the recap."}
  ]
};

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

const bigGameGapAudit:MichiganStory={
  slug:"michigan-2025-big-game-gap",
  eyebrow:"DATA AUDIT · 2025 SEASON",
  title:"Michigan's Big-Game Gap, and the Fourth Downs That Made It Worse",
  coverQuestion:"How much of Michigan's marquee-game struggle was really about the opponent — and how many points did conservative fourth-down calls cost along the way?",
  deck:"Opponent-adjusted with full-season ratings, Michigan's offense still collapsed in its three marquee games — and it was a passing problem, not a run-game one. A from-scratch expected-points model, trained on eleven seasons of play-by-play, grades every fourth-down decision the coaching staff made against what has actually worked at that distance and field position.",
  published:"September 2, 2026",
  readMinutes:12,
  tags:[
    {type:"UNIT",slug:"offense",label:"Offense"},
    {type:"POSITION",slug:"qb",label:"QB"},
    {type:"TOPIC",slug:"analytics",label:"Analytics"},
    {type:"TOPIC",slug:"coaching",label:"Coaching"}
  ],
  body:[],
  dataLinks:[
    {label:"2025 Michigan offense analytics",href:"/analytics/offense?year=2025",description:"See the full opponent-adjusted efficiency breakdown behind this audit."},
    {label:"Bryce Underwood profile",href:"/players/5141741",description:"Review Underwood's freshman production and 2026 roster profile."},
    {label:"The 13.5-point mystery",href:"/articles/michigan-offense-2025-playcalling-audit",description:"The earlier down/distance audit this piece builds on."}
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
  const stories=[howMichiganBeatsOklahoma,oklahomaPreview,dontJumpTheGun,westernMichiganRecap,bigGameGapAudit,playcallingAudit,westernMichiganPreview,...michiganStories()];
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
