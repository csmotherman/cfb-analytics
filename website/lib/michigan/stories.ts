import { currentRoster } from "./roster";
import { currentRecruitingClass } from "./recruiting";

export type MichiganStory = { slug:string; eyebrow:string; title:string; deck:string; body:string[]; playerId?:string; published?:string; sources?:{label:string;url:string}[] };

export function michiganStories(): MichiganStory[] {
  const roster = currentRoster();
  const score = {"S+":7,S:6,A:5,B:4,C:3,D:2,F:1};
  const featured = roster.filter(p=>p.prospectGrade).sort((a,b)=>(score[b.prospectGrade!]??0)-(score[a.prospectGrade!]??0)).slice(0,4);
  const playerStories = featured.map((player):MichiganStory=>({
    slug:`player-${player.id}`, playerId:player.id, eyebrow:`${player.position ?? "PLAYER"} NOTEBOOK · 2026`,
    title:`The ${player.firstName} ${player.lastName} question`,
    deck:`Where Michigan's ${player.position ?? "roster"} profile meets the opportunity ahead.`,
    body:[
      `${player.firstName} ${player.lastName} enters the 2026 preseason wearing No. ${player.jersey ?? "—"} at ${player.position ?? "an unlisted position"}. At ${player.height ? `${Math.floor(player.height/12)}-foot-${player.height%12}` : "an unlisted height"} and ${player.weight ? `${player.weight} pounds` : "an unlisted weight"}, the roster profile sets the frame—not the conclusion.`,
      player.compositeRating ? `The recruiting record supplies a ${player.compositeRating.toFixed(4)} composite and a ${player.prospectGrade} Michigan display grade. That is useful context for pedigree, but it is not a claim about present performance or a promise about the depth chart.` : `No recruiting composite matched the current roster identity, so the profile stays unrated rather than filling the gap with a guess.`,
      `The story to follow is role: how Michigan deploys this skill set, what the weekly workload becomes, and how the production changes against Big Ten competition. Those answers will be added from observed games.`
    ]
  }));
  const recruiting = currentRecruitingClass();
  return [{
    slug:"2026-coaching-staff", eyebrow:"THE NEW STAFF · 2026", title:"What Michigan's new coaching staff is built to do", deck:"Kyle Whittingham brings an experienced, physical program to Ann Arbor. Jason Beck and Jay Hill give it a clear football plan on both sides.", published:"August 18, 2026",
    body:[
      "Michigan did not hire Kyle Whittingham to reinvent what winning football looks like in Ann Arbor. It hired a coach whose Utah teams were known for being hard to move, strong up front and comfortable winning games that required patience. Whittingham arrived after 21 seasons as Utah's head coach, a 177–88 record, three conference championships and eight seasons with at least 10 wins.",
      "The first thing Michigan fans should expect is a connected staff. Offensive coordinator Jason Beck worked under Whittingham at Utah in 2025, while defensive coordinator Jay Hill previously spent 12 years on Whittingham's Utah staff before leading Weber State and coordinating BYU's defense. This is not a collection of unfamiliar coaches learning one another on the fly. The head coach and both coordinators already share a working football language.",
      "Beck's offense is the most interesting change. His recent teams have paired quarterback development with a real running game instead of treating balance as a slogan. New Mexico ranked fourth nationally in total offense and fifth in rushing offense in 2024. At Michigan, Beck also coaches quarterbacks, Jim Harding handles the offensive line, Micah Simon coaches receivers and Freddie Whittingham works with tight ends. Tony Alford staying as run-game coordinator and running backs coach gives the room valuable Michigan continuity.",
      "The likely offensive identity is straightforward: make the quarterback comfortable, create movement in the run game and force defenses to defend the whole field. That does not guarantee instant production. It does give Michigan a sensible structure for developing a young offense without asking one player to carry every Saturday.",
      "Hill's defense should look just as familiar to Big Ten fans: physical, organized and difficult to score against. His BYU defenses finished among the nation's top 21 in scoring defense in both 2024 and 2025. Lewis Powell brings more than a decade of Utah defensive-line experience to the edge group, while Jernaro Gilford arrives after 10 seasons coaching BYU's cornerbacks.",
      "Special teams should remain a real part of the plan. Kerry Coombs stayed as coordinator, with Garrett Clawson continuing on staff. That continuity matters because Whittingham has never treated kicking and coverage units like an afterthought. Hill also spent nine seasons coordinating special teams at Utah.",
      "The honest preseason read is that Michigan has a coherent staff, not a finished product. Whittingham supplies the program standard. Beck must turn the offensive pieces into dependable points. Hill must make the defense play fast without losing discipline. If those three parts connect, Michigan should look like Michigan: strong at the line of scrimmage, prepared for close games and difficult to beat late in the season."
    ],
    sources:[
      {label:"Michigan names Kyle Whittingham head coach",url:"https://mgoblue.com/news/2025/12/27/kyle-whittingham-named-michigans-j-ira-and-nicki-harris-family-head-football-coach"},
      {label:"Michigan announces offensive staff",url:"https://mgoblue.com/news/2026/1/7/football-whittingham-announces-offensive-coaching-staff"},
      {label:"Jason Beck named offensive coordinator",url:"https://mgoblue.com/news/2026/1/2/football-jason-beck-named-michigans-sanford-robertson-offensive-coordinator"},
      {label:"Jay Hill named defensive coordinator",url:"https://mgoblue.com/news/2026/1/2/football-jay-hill-named-u-ms-lester-family-defensive-coordinator"},
      {label:"Michigan's 2026 coaching staff",url:"https://mgoblue.com/sports/football/coaches"}
    ]
  },{slug:"2026-class-blueprint",eyebrow:"RECRUITING · 2026",title:"Inside Michigan's 2026 class blueprint",deck:`${recruiting?.recruits.length ?? 0} commitments, one class identity, and the position map behind the national ranking.`,body:[`Michigan's current 2026 class snapshot contains ${recruiting?.recruits.length ?? 0} commitments and sits No. ${recruiting?.ranking?.rank ?? "—"} nationally in the published source.`,"The star and composite columns describe recruiting consensus. The F–S+ display grade translates that composite without changing the underlying order.","The next layer is roster fit: where each player enters the position room, which future needs remain open, and how development changes the original recruiting expectation."]},...playerStories];
}

export function storyBySlug(slug:string){return michiganStories().find(story=>story.slug===slug)??null;}
