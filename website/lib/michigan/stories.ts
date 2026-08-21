export type StoryTagType = "POSITION"|"UNIT"|"TOPIC";
export type StoryTag = {type:StoryTagType;slug:string;label:string};
export type StoryDataLink = {label:string;href:string;description:string};
export type MichiganStory = {
  slug:string;
  eyebrow:string;
  title:string;
  deck:string;
  body:string[];
  playerIds?:string[];
  published?:string;
  readMinutes?:number;
  tags:StoryTag[];
  dataLinks:StoryDataLink[];
  coverQuestion?:string;
  coverLabel?:string;
  coverTheme?:string;
  sources?:{label:string;url:string}[];
};

const tag=(type:StoryTagType,slug:string,label:string):StoryTag=>({type,slug,label});

export function michiganStories(): MichiganStory[] {
  return [
    {
      slug:"what-to-expect-michigan-offense-2026",
      eyebrow:"2026 OFFENSE · SEASON PREVIEW",
      title:"What to Expect From Michigan’s Offense in 2026",
      deck:"Michigan already had a productive running game in 2025. Jason Beck’s challenge is to make the offense harder to defend horizontally, more dangerous through Bryce Underwood, and far better at turning good drives into points.",
      published:"August 21, 2026",
      readMinutes:9,
      playerIds:["5141741","5079574","5141572"],
      coverQuestion:"Can Jason Beck turn Michigan’s foundation into a playoff offense?",
      coverLabel:"OFFENSE PREVIEW",
      coverTheme:"offense",
      tags:[
        tag("POSITION","qb","QB"),
        tag("UNIT","offense","Offense"),
        tag("TOPIC","season-preview","Season Preview"),
        tag("TOPIC","coaching","Coaching"),
        tag("TOPIC","analytics","Analytics")
      ],
      dataLinks:[
        {label:"Michigan offense analytics",href:"/analytics/offense?year=2025",description:"See Michigan’s opponent-adjusted 2025 offensive efficiency and national context."},
        {label:"Bryce Underwood profile",href:"/players/5141741",description:"Review Underwood’s freshman production and 2026 roster profile."},
        {label:"Michigan roster",href:"/team/roster",description:"Explore the 2026 personnel that will operate Jason Beck’s offense."}
      ],
      body:[
        "Michigan does not need to reinvent its offense in 2026. It needs to make the offense it already had much harder to defend. The 2025 Wolverines finished 9-4 while averaging 27.5 points and 396.9 yards per game. They ran for 210.2 yards per game, 14th nationally according to Michigan’s season review, and averaged 5.4 yards per rushing attempt. That is not a broken foundation. The problem was that Michigan’s ability to control games on the ground never consistently became an offense that could stress every blade of grass or finish enough drives with touchdowns.",
        "The contrast with Jason Beck’s 2025 Utah offense is the reason the coordinator change matters. Utah averaged 41.3 points, 482.9 total yards and 6.6 yards per play while finishing 11-2. The Utes rushed for 266.3 yards per game and still produced 216.6 passing yards per game. They converted 52.6 percent of third downs, went 16-for-25 on fourth down and scored on 54 of 59 red-zone trips, with 47 of those possessions ending in touchdowns. Michigan, by comparison, converted 43.6 percent of third downs and scored touchdowns on 32 of 52 red-zone trips. The gap was not simply talent or rushing volume. Utah was better at keeping the defense in conflict and better at finishing possessions.",
        "That difference is visible in how Beck builds an offense. When he installed the system at Utah in 2025, Kyle Whittingham described it as no-huddle and somewhat faster, but not a pure tempo offense. The bigger change was structural: quarterback run game, RPOs, horizontal spacing and multiple answers attached to the same look. Michigan tight end Zack Marshall described the system this spring as an offense built around horizontal stress, jet action, perimeter screens and second options rather than asking every concept to win in one predetermined way. That matters because the 2025 Michigan offense could run the ball even when opponents expected the run. In 2026, Beck’s goal should be to punish the defense for overcommitting to that expectation.",
        "Bryce Underwood is the fulcrum. As a true freshman, he started all 13 games and completed 202 of 335 passes for 2,428 yards, 11 touchdowns and nine interceptions. He also ran 88 times for 392 yards and six touchdowns. Michigan’s official 2025 team totals show only 11 passing touchdowns all season despite 33 rushing scores. Underwood flashed the arm talent and improvisational ability that made him one of the nation’s most important recruits, but the passing game never became as consistently threatening as the run game. Beck now inherits a quarterback with a full Big Ten season behind him and a skill set that fits the offense he just ran at Utah.",
        "The Utah comparison is especially useful here because Beck’s 2025 quarterback, Devon Dampier, was also a true dual threat. Dampier completed 63.5 percent of his passes for 2,490 yards and 24 touchdowns while adding value as a runner. Utah’s offense did not ask the quarterback to choose between being a passer and being part of the run game. It used his legs to manipulate numbers, create RPO access throws and force defenses to defend the quarterback after the handoff fake. Underwood’s 392 rushing yards as a freshman suggest Michigan can present the same mathematical problem without turning him into a running back.",
        "Fall camp has reinforced that this will be Underwood’s offense in more than name. Michigan opened camp on August 5, its first under Whittingham, and Underwood was voted one of four team captains less than two weeks later alongside Jordan Marshall, Rod Moore and Trey Pierce. Underwood is also on the Walter Camp Player of the Year and Maxwell Award watch lists. Those honors do not guarantee a sophomore leap, but the captain vote matters: Michigan’s teammates are signaling that the quarterback is no longer simply the talented young player learning on the job. He is one of the players expected to drive the team.",
        "The skill-position structure should help him. Andrew Marsh returns after 45 catches for 651 yards and four touchdowns as a freshman, including a 12-catch, 189-yard game at Northwestern. Michigan named him its 2025 Offensive Skill Player of the Year. Jordan Marshall returns after helping anchor one of the nation’s better rushing attacks, and Beck’s system creates ways to make backs, receivers and tight ends threats before the snap rather than only after it. That is the subtle but important change Michigan fans should watch: motion that changes leverage, quick throws that punish soft boxes, quarterback keeps that punish crashing edges and formations that make the same personnel look different from snap to snap.",
        "The offensive line is the part of the equation that should not be reduced to a single preseason grade. Michigan used six different starting combinations in 2025 and still became a Joe Moore Award semifinalist while producing 12 individual 100-yard rushing performances. Jim Harding, who coached Utah’s line before coming with Whittingham, now takes over a unit that already proved it can create movement. The question is whether the line can adapt from Michigan’s familiar downhill menu to Beck’s wider collection of RPO, perimeter and quarterback-run concepts without losing the physical identity that made the 2025 run game successful.",
        "There is also a warning in the Utah numbers. Utah’s offense was excellent over the full season, but it was not invulnerable. The Utes scored only 10 points in a loss to Texas Tech and 21 in a three-point loss at BYU. A new scheme does not erase protection problems, receiver separation issues or bad decisions against elite defenses. Michigan should not expect to copy Utah’s 41.3 points per game simply because Beck is calling the plays. Personnel, conference environment and quarterback development all change the equation.",
        "The realistic target is more specific. Michigan needs to preserve the 2025 run-game floor while moving closer to Utah’s ability to stay alive on third down and finish red-zone possessions with touchdowns. Michigan’s own opponent-adjusted model rated the 2025 offense 24th nationally overall, with adjusted points per drive ranked 22nd, yards per drive 29th, success rate 20th and scoring-drive rate 23rd. That profile says the Wolverines were already above average on a snap-to-snap basis. They were not an elite offense because too many drives produced less than the underlying efficiency suggested they should.",
        "That is why the 2026 offense is one of the most interesting units in the Big Ten. Michigan is not starting from zero, and Beck is not arriving with a theoretical résumé. His 2024 New Mexico offense finished fourth nationally in total offense, and his first Utah offense followed with 482.9 yards and 41.3 points per game. The 2025 Wolverines already supplied the run game, a year of Underwood experience and a young receiver in Marsh who has shown he can handle volume. If Beck can add horizontal stress, create easier answers for Underwood and turn a few more promising drives into seven points instead of three or zero, Michigan does not need a miraculous offensive transformation to become a playoff-level team. It needs a more complete version of what was already there."
      ],
      sources:[
        {label:"Michigan 2025 cumulative statistics",url:"https://mgoblue.com/sports/football/stats/2025"},
        {label:"Michigan 2025 season review",url:"https://mgoblue.com/news/2026/1/7/season-review-2025-michigan-football"},
        {label:"Michigan 2026 fall camp hub",url:"https://app.mgoblue.com/2026FallCamp"},
        {label:"Michigan 2026 captains announcement",url:"https://mgoblue.com/news/2026/8/17/football-announces-captains-leadership-council-for-team-147"},
        {label:"Michigan 2026 preseason honors",url:"https://mgoblue.com/news/2026/5/26/2026-michigan-football-preseason-honors"},
        {label:"Zack Marshall on Jason Beck’s offense",url:"https://mgoblue.com/news/2026/5/13/mgoblue-podcasts-in-the-trenches-586-zack-marshall-and-freddie-whittingham-transcript"},
        {label:"Utah 2025 cumulative statistics",url:"https://utahutes.com/sports/football/stats/2025"},
        {label:"Utah 2025 fall camp on Beck’s offense",url:"https://utahutes.com/news/2025/7/30/fall-camp-begins-for-utah-football"}
      ]
    }
  ];
}

export function storyBySlug(slug:string): MichiganStory | null {
  return michiganStories().find(story=>story.slug===slug)??null;
}
