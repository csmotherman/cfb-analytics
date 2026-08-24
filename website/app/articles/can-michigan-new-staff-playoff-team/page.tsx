import type {Metadata} from "next";
import Link from "next/link";

const articleUrl="https://cfb-analytics-two.vercel.app/articles/can-michigan-new-staff-playoff-team";
const articleImage="https://cfb-analytics-two.vercel.app/images/articles/staff-article.png";

export const metadata:Metadata={
  title:"Can Michigan’s New Staff Turn the Wolverines Into a Playoff Team?",
  description:"A fan-first look at what changed from Michigan’s 2025 staff to Kyle Whittingham’s 2026 staff — and what actually has to improve for the Wolverines to reach the CFP.",
  openGraph:{type:"article",url:articleUrl,siteName:"Michigan Football Focus",title:"Can Michigan’s New Staff Turn the Wolverines Into a Playoff Team?",description:"What changes on Saturdays under Kyle Whittingham, Jason Beck and Jay Hill — and whether it can move Michigan from 9-4 to the playoff.",images:[{url:articleImage,alt:"Michigan football coaching staff"}]},
  twitter:{card:"summary_large_image",title:"Can Michigan’s New Staff Turn the Wolverines Into a Playoff Team?",description:"What changes on Saturdays under Kyle Whittingham, Jason Beck and Jay Hill — and whether it can move Michigan from 9-4 to the playoff.",images:[articleImage]}
};

const paragraphs=[
  "Michigan does not need a complete rebuild to become a playoff team. It needs to turn a good 2025 team into one that is more dependable against elite opponents. The Wolverines finished 9-4 and 7-2 in the Big Ten, but three of the four losses came against ranked opponents: Oklahoma, Ohio State and Texas. That is the gap the new staff has to close. Michigan already proved it could beat most of its schedule. The next step is becoming good enough — and consistent enough — to beat the teams that decide playoff seasons.",
  "The biggest change is at the top. Kyle Whittingham replaces the 2025 Sherrone Moore/Biff Poggi setup and arrives with decades of head-coaching experience, a reputation for physical football and a much more established program identity. For fans, that matters less because of résumé lines and more because Michigan now has a head coach whose teams have spent years living in close, high-leverage games. The expectation should be fewer weeks where Michigan looks like a different team from one Saturday to the next.",
  "Whittingham also did not come to Ann Arbor alone. Michigan’s 2026 staff includes Jason Beck at offensive coordinator, Jay Hill at defensive coordinator, Jim Harding coaching the offensive line, Micah Simon at wide receiver, Freddie Whittingham at tight end and several other assistants with direct ties to Whittingham’s Utah program. That creates something Michigan did not have entering 2025: a large group of coaches who already know how the head coach wants practice, game-planning and weekly preparation to operate.",
  "That continuity should show up first on offense. Michigan averaged 27.5 points per game in 2025 and was good enough on the ground to win nine games, but the offense too often became predictable when it needed answers through the air. Beck’s 2025 Utah offense averaged 41.3 points and 482.9 yards per game. Nobody should expect Michigan to instantly copy those numbers, but the philosophical difference is meaningful: Beck’s offense uses quarterback run threats, RPOs, motion and horizontal stress to make the defense wrong more often. If Bryce Underwood makes the normal Year 1-to-Year 2 jump, Michigan should be much harder to load the box against.",
  "That is probably the single biggest reason the staff change can move Michigan’s ceiling. The 2025 Wolverines were already competitive because they could run the ball and play defense. What they lacked was an offense that consistently punished good defenses for overplaying those strengths. Against Oklahoma, USC and Ohio State, Michigan scored 13, 13 and 9 points. A playoff team cannot survive that kind of offensive floor. Beck does not need to create the best offense in America. He needs to make Michigan much less likely to disappear for entire stretches against top teams.",
  "The defensive transition is different because Michigan is not trying to escape a bad unit. The Wolverines are trying to preserve a defensive identity while changing coordinators. Jay Hill’s recent BYU defenses give fans a clear picture of what to watch: third downs, takeaways, red-zone defense and quarterback discomfort. BYU’s 2025 defense allowed 19.1 points per game, intercepted 17 passes and forced 24 takeaways while holding opponents to roughly one-third on third down. Michigan does not need those exact numbers; it needs those same game-changing moments.",
  "The most encouraging part of the transition is that the new staff is not forcing Michigan to abandon what already works. Tony Alford remains with the running backs and run-game structure, Kerry Coombs remains on special teams, and the roster still has veteran leadership such as Rod Moore. At the same time, Whittingham imported coaches he trusts for the areas he clearly wanted to change. That balance matters. Wholesale change sounds exciting in January, but playoff teams usually improve because they keep their strengths and fix the parts opponents can exploit.",
  "There is still real risk. New terminology can slow down a defense early. A new offensive system can look great in camp and clunky once Big Ten opponents start disguising coverages. Michigan also cannot coach its way around every roster issue. The offensive line has to protect, receivers have to separate and the secondary has to hold up against top quarterbacks. Staff reputation raises the floor of preparation; it does not remove the need for players to win matchups.",
  "The schedule will tell us quickly whether the transition is working. Michigan does not need to look perfect in September, but by the time conference play reaches its biggest games, fans should see three obvious differences: the offense should have more answers when the run game is crowded, the defense should get off the field more reliably on third down, and Michigan should look calmer in the moments where one possession decides the game.",
  "So can the new staff make Michigan a playoff team? Yes — because the 2025 team was closer than a 9-4 record can make it feel. But the path is not magic. Michigan has to turn its existing physical identity into a more complete team. If Beck raises the offensive floor, Hill preserves the defense’s ability to control games and Whittingham gives the program week-to-week consistency, the Wolverines do not need a massive leap everywhere. They need a few important weaknesses to stop being weaknesses. That is a realistic playoff formula."
];

const sources=[
  ["Michigan 2025 season review","https://mgoblue.com/news/2026/1/7/season-review-2025-michigan-football"],
  ["Michigan 2025 coaching staff","https://mgoblue.com/sports/football/coaches/2025"],
  ["Michigan 2026 coaching staff","https://mgoblue.com/sports/football/coaches"],
  ["Whittingham announces offensive staff","https://mgoblue.com/news/2026/1/7/football-whittingham-announces-offensive-coaching-staff"],
  ["Whittingham announces defensive staff","https://mgoblue.com/news/2026/1/3/football-whittingham-announces-coaching-staff-for-defense-special-teams"],
  ["Michigan 2025 schedule/results","https://mgoblue.com/sports/football/schedule/text/2025"]
] as const;

export default function StaffArticle(){
  return <article className="focus-article">
    <div className="focus-article-shell">
      <header className="focus-article-hero">
        <img src="/images/articles/staff-article.png" alt="Michigan football coaching staff"/>
        <div className="focus-article-hero-shade"/>
        <div className="focus-article-hero-copy">
          <span className="focus-article-eyebrow">2026 STAFF · BIG PICTURE</span>
          <h1>Can Michigan’s New Staff Turn the Wolverines Into a Playoff Team?</h1>
          <p>Michigan won nine games in 2025. The new staff’s job is not to start over — it is to fix the few things that kept a good team from becoming a playoff team.</p>
          <div className="focus-article-meta"><span>August 21, 2026</span><span>8 MIN READ</span></div>
        </div>
      </header>

      <div className="focus-article-body">
        {paragraphs.map((paragraph,index)=><p className={index===0?"focus-article-lede":undefined} key={index}>{paragraph}</p>)}
      </div>

      <section className="focus-article-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>See what changes under the new staff.</h2></div>
        <div className="focus-article-link-grid">
          <Link href="/analytics/staff"><strong>Staff analytics</strong><p>Explore the coaching transition, tendencies and staff context.</p><span>VIEW →</span></Link>
          <Link href="/analytics/offense?year=2025"><strong>2025 offense</strong><p>See the baseline Jason Beck inherits and where Michigan needs to improve.</p><span>VIEW →</span></Link>
          <Link href="/analytics/defense?year=2025"><strong>2025 defense</strong><p>See the unit Jay Hill is trying to preserve and sharpen.</p><span>VIEW →</span></Link>
        </div>
      </section>

      <section className="focus-article-sources"><strong>REPORTING & DATA SOURCES</strong><div>{sources.map(([label,url])=><a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div></section>
      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}
