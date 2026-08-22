import type {Metadata} from "next";
import Link from "next/link";

export const metadata:Metadata={
  title:"Michigan vs. Western Michigan: The Data Says Michigan Should Run First and Make Broc Lowry Throw",
  description:"Michigan owns a massive offensive edge entering Week 1, but Western Michigan is not a typical MAC opener. The defending conference champions have a legitimate run game, a proven quarterback and a defense that was much better than its name recognition suggests."
};

const sources=[
  ["Michigan coaching staff","https://mgoblue.com/sports/football/coaches"],
  ["Jason Beck Michigan profile","https://mgoblue.com/sports/football/roster/coaches/jason-beck/6855"],
  ["Bryce Underwood Michigan profile","https://mgoblue.com/sports/football/roster/bryce-underwood/28012"],
  ["Jay Hill Michigan profile","https://mgoblue.com/sports/football/roster/coaches/jay-hill/6865"],
  ["Western Michigan promotes Greer Martini","https://wmubroncos.com/news/2026/2/11/greer-martini-promoted-to-defensive-coordinator.aspx"],
  ["Western Michigan staff additions","https://wmubroncos.com/news/2026/3/27/football-announces-staff-additions.aspx"],
  ["Nadame Tucker Senior Bowl announcement","https://wmubroncos.com/news/2025/12/29/football-after-historic-season-nadame-tucker-accepts-invitation-to-the-2026-panini-senior-bowl.aspx"],
  ["Broc Lowry Western Michigan profile","https://wmubroncos.com/sports/football/roster/broc-lowry/15874"],
  ["Lowry and Buckley Maxwell watch list","https://wmubroncos.com/news/2026/8/3/football-lowry-and-buckley-named-to-maxwell-award-watch-list.aspx"]
] as const;

export default function MichiganWesternMichiganPreview(){
  return <article className="focus-article">
    <div className="focus-article-shell">
      <header className="focus-article-hero">
        <div className="focus-article-hero-fade"/>
        <div className="focus-article-hero-copy">
          <span className="focus-article-eyebrow">WEEK 1 · GAME PREVIEW</span>
          <h1>Michigan vs. Western Michigan: The Data Says Michigan Should Run First and Make Broc Lowry Throw</h1>
          <p>Michigan owns a massive offensive edge entering Week 1, but Western Michigan is not a typical MAC opener. The defending conference champions have a legitimate run game, a proven quarterback and a defense that was much better than its name recognition suggests.</p>
          <div className="focus-article-meta"><span>August 21, 2026</span><span>9 MIN READ</span></div>
        </div>
      </header>

      <div className="focus-article-body">
        <p className="focus-article-lede">Michigan opens the 2026 season against Western Michigan on Sept. 5 at 7:30 p.m. in Michigan Stadium. It will also be the first game of the Kyle Whittingham era, with Jason Beck taking over the offense and Jay Hill running the defense. Western enters as the defending MAC champion and was picked first in the conference's 2026 preseason coaches poll. The Broncos officially finished 10-4 last season after beating Kennesaw State 41-6 in the Myrtle Beach Bowl.</p>
        <p>BetMGM currently has Michigan favored by <strong>26.5 points</strong>. Our spread-based market calibration translates that into roughly a <strong>95.9% straight-up win probability</strong> for the Wolverines.</p>
        <p>But the underlying matchup is more interesting than the spread suggests.</p>

        <h2>The biggest number: Michigan's 24.5-point offensive advantage</h2>
        <p>Our opponent-adjusted Ridge model rates Michigan as the No. 25 team nationally based on its 2025 baseline, compared with No. 70 Western Michigan.</p>
        <p>The gap becomes much larger when isolating offense. Michigan's offense checks in at No. 24 with a 114.2 rating, while Western Michigan's offense ranks No. 106 at 89.7. Michigan's defense is No. 36 at 109.7 and Western Michigan's defense is No. 41 at 107.9. A rating of 100 represents roughly an average FBS team.</p>
        <p>The interesting part isn't Michigan's 13.2-point overall advantage. It's the shape of it. Michigan's offense rates <strong>24.5 points higher</strong> than Western's offense. The two defenses, however, are separated by only 1.8 rating points.</p>
        <p>That suggests a fairly simple thesis for Week 1: <strong>Michigan should have significantly more ways to move the football, but Western's defense may be capable of making the game uglier than a 26.5-point spread implies.</strong></p>

        <h2>Michigan should test Western on the ground immediately</h2>
        <p>This is the clearest matchup advantage in the entire dataset.</p>
        <p>Michigan's 2025 offense finished No. 6 nationally in rush success rate at 50.9%, No. 10 in rushing yards per attempt at 6.01 and No. 29 in explosive rushing rate. Western Michigan's defense finished only No. 89 in rushing yards allowed per attempt and No. 89 in explosive rushing rate allowed.</p>
        <p>And that was before Michigan hired Jason Beck.</p>
        <p>Beck's 2025 Utah offense finished second nationally in rushing offense at 266.3 yards per game, fourth in total offense and fifth in scoring. Utah also converted 52.6% of its third downs, third-best nationally.</p>
        <p>He inherits a backfield built for that style.</p>
        <p>Jordan Marshall rushed for 932 yards and 10 touchdowns on 150 carries last season — 6.2 yards per attempt — despite starting only four games. Bryce Underwood added 392 rushing yards and six touchdowns while starting all 13 games as a true freshman. Both were voted captains for 2026.</p>
        <p>If Beck's offense translates quickly, there is little statistical reason for Michigan to make this opener unnecessarily complicated.</p>
        <p><strong>Run the football. Force Western to commit additional bodies. Then ask Underwood to punish the response.</strong></p>

        <h2>But Western's defense deserves respect</h2>
        <p>Calling Western Michigan a 26.5-point underdog can obscure what the Broncos actually did defensively last year.</p>
        <p>Our numbers put Western's defense at <strong>No. 41 nationally in opponent-adjusted Ridge rating</strong>, just five spots behind Michigan.</p>
        <p>More importantly, several areas of the defense were legitimately strong: No. 9 in points allowed per resolved possession, No. 10 in scoring rate allowed per possession, No. 10 in pass explosive rate allowed, No. 11 in net passing yards allowed per dropback and No. 10 in third-down conversion rate allowed.</p>
        <p>Western's official numbers tell the same story. The defense finished ninth nationally in scoring defense and played a major role in the program's MAC championship.</p>
        <p>That creates one of the game's more important questions: <strong>Can Michigan turn successful drives into touchdowns?</strong></p>
        <p>That wasn't always automatic last season. Michigan ranked only No. 78 in points per scoring opportunity and No. 70 in red-zone touchdown rate. Western's defense ranked No. 35 in points allowed per scoring opportunity and No. 30 in red-zone touchdown rate allowed.</p>
        <p>Michigan can dominate the yardage battle and still make covering a four-touchdown spread uncomfortable if drives repeatedly end in field goals.</p>
        <p>Beck's arrival could matter there too. Utah finished 12th nationally in red-zone offense last season.</p>

        <h2>The Western pass rush is the matchup to watch</h2>
        <p>There is one especially clear concern for Michigan's offense in the baseline numbers.</p>
        <p>Michigan ranked only <strong>No. 76 in sack rate allowed</strong>. Western's defense ranked <strong>No. 13 in defensive sack rate</strong>.</p>
        <p>Last year's version of that pass rush was led by Nadame Tucker, who produced 14.5 sacks and 21 tackles for loss, led the nation in both categories, won MAC Defensive Player of the Year and accepted a Senior Bowl invitation after the season. He is no longer on Western's 2026 roster.</p>
        <p>That's a major loss.</p>
        <p>Western also changed defensive coordinators. Greer Martini was promoted after serving as linebackers coach in 2025, while longtime Furman defensive coordinator Duane Vaughn joined the staff as co-defensive coordinator and outside linebackers coach.</p>
        <p>So the 2025 Western pass-rush numbers need context. The underlying defense was excellent. The single most disruptive player from that defense is gone, and the staff responsible for replacing his production has changed.</p>
        <p>If Michigan's rebuilt offensive line controls that front, Western loses one of its most realistic ways to derail drives.</p>

        <h2>Western's offense has one obvious path</h2>
        <p>Western Michigan isn't going to want a throwing contest with Michigan.</p>
        <p>The Broncos ran the ball on approximately <strong>65% of their offensive snaps</strong> last season, and there is no reason for that identity to change.</p>
        <p>Quarterback <strong>Broc Lowry</strong> returns after winning MAC Offensive Player of the Year. He threw for 1,803 yards and nine touchdowns but was even more dangerous as a runner, setting a Western Michigan quarterback record with <strong>963 rushing yards and 14 rushing touchdowns</strong>.</p>
        <p>Running back <strong>Jalen Buckley</strong> is back too. He rushed for 1,003 yards and nine touchdowns in 2025, then exploded for 193 yards in the MAC Championship Game and another 174 in the Myrtle Beach Bowl. Lowry and Buckley are both on the 2026 Maxwell Award watch list.</p>
        <p>That's Western's formula.</p>
        <p>Keep Michigan's offense standing on the sideline. Let Lowry create an extra gap in the running game. Stay ahead of the chains. Shorten the game.</p>
        <p>Because when Western is forced to throw, the matchup changes dramatically.</p>
        <p>Its 2025 offense ranked <strong>No. 124</strong> in net passing yards per dropback, <strong>No. 120</strong> in passing explosive rate, <strong>No. 122</strong> in passing-down success rate and No. 112 in overall pass success rate. Michigan's defense ranked No. 20 in net passing yards allowed per dropback and No. 36 in passing explosive rate allowed.</p>
        <p><strong>If Michigan consistently gets Lowry into obvious passing situations, the numbers tilt heavily toward the Wolverines.</strong></p>

        <h2>Jay Hill's first assignment is stopping the QB run game</h2>
        <p>This won't be the same Michigan defense that produced the 2025 numbers.</p>
        <p>Jay Hill takes over after three seasons as BYU's defensive coordinator. His 2025 BYU defense ranked in the top 25 nationally in seven categories, including No. 5 in red-zone defense, No. 7 in interceptions and No. 19 on third down.</p>
        <p>His first Michigan game presents a useful test of discipline.</p>
        <p>Western's traditional rushing attack is good, but Lowry is what changes the math. Michigan cannot simply fit the run as if it's defending an ordinary handoff offense. A quarterback who ran for nearly 1,000 yards can punish an undisciplined edge or a linebacker flowing too aggressively toward Buckley.</p>
        <p>Western actually owns two intriguing statistical advantages from last season: its offense ranked No. 32 nationally in standard-down success, while Michigan's defense ranked No. 60 in standard-down success allowed. Western also ranked No. 10 in red-zone success while Michigan's defense was only No. 73 in preventing it.</p>
        <p>Those are the situations where the Broncos could make this interesting.</p>
        <p>They cannot live in third-and-eight.</p>
        <p>They might be able to live in second-and-four.</p>

        <h2>What the 26.5-point spread is really asking</h2>
        <p>The question isn't whether Michigan is better.</p>
        <p>Almost every broad measure says it is.</p>
        <p>Michigan played the significantly tougher 2025 schedule. The average opponent in our Ridge ratings scored <strong>106.5</strong> for Michigan compared with only <strong>92.5</strong> for Western.</p>
        <p>Michigan's offense is rated 24.5 points better. Western's passing offense has a brutal matchup. And Michigan gets the game at the Big House.</p>
        <p>But a point spread this large requires more than simply being better.</p>
        <p>Michigan needs touchdowns. It needs to prevent Western from shortening the game with Lowry and Buckley. And it needs to avoid letting Western's defense create sacks and negative plays that turn promising possessions into punts.</p>
        <p>That's what makes this opener useful.</p>
        <p>The Wolverines aren't merely trying to start 1-0. They're debuting a new head coach, a new offensive system and a new defensive system around a sophomore quarterback who already has a full season of experience.</p>
        <p>Underwood threw for 2,428 yards as a freshman, while Andrew Marsh emerged as his leading receiver with 651 yards. Now Beck gets to build on that foundation rather than starting from scratch.</p>
        <p>Western isn't walking into Ann Arbor as an anonymous Group of Five opponent, either. It is the defending MAC champion, returns the conference's reigning Offensive Player of the Year and its 1,000-yard running back, and enters 2026 as the coaches' favorite to win the league again.</p>
        <p>That makes the opener a good first measurement of what Michigan has become.</p>
        <p><strong>The data favors Michigan heavily. The most convincing version of the win would be Michigan controlling the line of scrimmage, leaning into its rushing advantage and forcing Lowry to become a dropback passer.</strong></p>
        <p>If that happens, the 26.5-point spread starts to make sense.</p>
        <p>If Western can instead turn the night into a slow, physical, possession-by-possession game, it has enough on both sides of the ball to make Michigan work much harder than the market expects.</p>
      </div>

      <section className="focus-article-explore">
        <div className="focus-article-section-heading"><span>KEEP EXPLORING</span><h2>See the numbers behind the story.</h2></div>
        <div className="focus-article-link-grid">
          <Link href="/games/401858428"><strong>Michigan vs. Western Michigan game hub</strong><p>View the Ridge comparison, matchup details and current market spread.</p><span>VIEW →</span></Link>
          <Link href="/analytics"><strong>Michigan analytics</strong><p>Explore the opponent-adjusted ratings behind the preview.</p><span>VIEW →</span></Link>
          <Link href="/team/roster"><strong>2026 Michigan roster</strong><p>Review the personnel entering the first game of the Whittingham era.</p><span>VIEW →</span></Link>
        </div>
      </section>

      <section className="focus-article-sources">
        <strong>REPORTING &amp; DATA SOURCES</strong>
        <div>{sources.map(([label,url])=><a href={url} rel="noreferrer" target="_blank" key={url}>{label} ↗</a>)}</div>
      </section>

      <footer className="focus-article-footer"><Link href="/articles">← ALL ARTICLES</Link></footer>
    </div>
  </article>;
}
