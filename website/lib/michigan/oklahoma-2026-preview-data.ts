// Hand-authored matchup preview dataset for Michigan vs. Oklahoma, Week 2, 2026.
//
// Evidence is deliberately separated by type so a one-game box score is not
// blended into a full-season opponent-adjusted rating or a preseason model.
//
// Sources, by section:
// - 2025 opponent-adjusted baseline: data/exports/darren/2025/oklahoma/darren-data-pack.md
//   (schedule-adjusted-ratings-v1, ridge 40 / home-field ridge 20). The pack
//   contains a 12-game FBS sample for Oklahoma; Illinois State is excluded.
// - Week 1, 2026: official Michigan and Oklahoma box scores/play-by-play.
// - Current personnel: official participation charts plus dated reporting cited
//   in the sources list. Availability language is intentionally qualified.
// - 2025 head-to-head: official Michigan/Oklahoma box score from Sept. 6, 2025.
// - Preseason simulation: data/published/2026/michigan/preseason-2026-projection.json.
// - Market: data/published/2026/michigan/market-lines.json plus Action Network,
//   checked Sept. 10, 2026.

export type StatPoint = { value: string; label: string; detail?: string };
export type CompareValue = { value: string; rank: number };
export type CompareRow = { metric: string; michigan: CompareValue; opponent: CompareValue };

export type OklahomaPreviewData = {
  slug: string;
  season: number;
  week: number;
  opponent: string;
  opponentTeamId: number;
  michiganTeamId: number;
  kickoffISO: string;
  venue: string;

  heroThesis: string;

  scoutCards: Array<{ kicker: string; value: string; title: string; body: string }>;

  compositeComparison: {
    michigan: { offense: CompareValue; defense: CompareValue; overall: CompareValue };
    opponent: { offense: CompareValue; defense: CompareValue; overall: CompareValue };
    overallEdge: string;
  };

  baseline: {
    intro: string;
    michiganOffenseVsOpponentDefense: CompareRow[];
    opponentOffenseVsMichiganDefense: CompareRow[];
    takeaway: string;
  };

  week1: {
    intro: string;
    oklahoma: { line: string; opponent: string; qb: string; rb: string; rows: StatPoint[] };
    michigan: { line: string; opponent: string; qb: string; rb: string; rows: StatPoint[] };
    takeaway: string;
    caveat: string;
  };

  matchups: Array<{
    id: string;
    kicker: string;
    title: string;
    question: string;
    numbers: StatPoint[];
    narrative: string[];
  }>;

  howOklahomaWins: string[];
  howMichiganWins: string[];

  numbersThatMatter: Array<{ value: string; label: string; why: string }>;
  verdict: string;

  market: { spread: string; winChance: string; book: string; asOf: string; source: string; sourceUrl: string; openedAt: string };
  preseasonModel: { winProbMichiganPct: number; projectedMargin: string; projectedMarginRange: string; source: string };

  methodology: {
    validated: string;
    week1: string;
    market: string;
    preseason: string;
  };

  sources: Array<{ label: string; url: string }>;
};

export const michiganOklahoma2026: OklahomaPreviewData = {
  slug: "michigan-oklahoma-2026",
  season: 2026,
  week: 2,
  opponent: "Oklahoma",
  opponentTeamId: 201,
  michiganTeamId: 130,
  kickoffISO: "2026-09-12T16:00:00.000Z",
  venue: "Michigan Stadium",

  heroThesis:
    "Oklahoma's 2025 defense is the most trustworthy unit in this matchup. Michigan's Week 1 offense is the least trustworthy. But the 51-0 and 13-12 scoreboards exaggerate the defensive gap, and Oklahoma arrives with offensive-line uncertainty of its own.",

  scoutCards: [
    {
      kicker: "THE PROVEN UNIT",
      value: "#2",
      title: "Oklahoma's defense is elite. Full stop.",
      body: "In the site's validated 2025 FBS sample, Oklahoma finished #2 in the defensive composite, #1 in adjusted success rate allowed, #1 in adjusted rush success allowed and #3 in adjusted yards per play allowed. This is the strongest unit on the field Saturday.",
    },
    {
      kicker: "MICHIGAN'S RED FLAG",
      value: "3/10",
      title: "The offense could not stay on the field.",
      body: "Michigan went 3-for-10 on third down, punted six times, turned it over three times and possessed the ball for only 19:52 against Western Michigan. The concern is bigger than one ugly quarterback stat line: the offense repeatedly lost possession leverage.",
    },
    {
      kicker: "THE HIDDEN COUNTER",
      value: "0 TD",
      title: "Michigan's defense never broke.",
      body: "Western Michigan had the ball for 40:08 and still finished with 221 yards, 3.3 yards per play and zero touchdowns. Michigan's opener was a major offensive failure, not evidence that every part of the team collapsed.",
    },
  ],

  compositeComparison: {
    michigan: {
      offense: { value: "83.4/100", rank: 19 },
      defense: { value: "67.6/100", rank: 38 },
      overall: { value: "75.5/100", rank: 19 },
    },
    opponent: {
      offense: { value: "46.7/100", rank: 76 },
      defense: { value: "97.9/100", rank: 2 },
      overall: { value: "72.3/100", rank: 25 },
    },
    overallEdge: "+3.2",
  },

  baseline: {
    intro:
      "The strongest prior we have is the 2025 opponent-adjusted evidence, not one Week 1 final score. Michigan holds a 75.5-to-72.3 edge in the site's validated composite, but that 3.2-point rating gap is not a projected point spread. The matchup is asymmetrical: Michigan's #19 offense runs into Oklahoma's #2 defense, while Oklahoma's #76 offense faces Michigan's #38 defense.",
    michiganOffenseVsOpponentDefense: [
      { metric: "Success rate", michigan: { value: "46.8%", rank: 19 }, opponent: { value: "32.1%", rank: 1 } },
      { metric: "Rush success", michigan: { value: "49.0%", rank: 4 }, opponent: { value: "32.0%", rank: 1 } },
      { metric: "Pass success", michigan: { value: "42.0%", rank: 54 }, opponent: { value: "35.7%", rank: 8 } },
      { metric: "Explosive-play rate", michigan: { value: "13.0%", rank: 19 }, opponent: { value: "8.9%", rank: 6 } },
      { metric: "Yards per play", michigan: { value: "6.55", rank: 21 }, opponent: { value: "4.20", rank: 3 } },
    ],
    opponentOffenseVsMichiganDefense: [
      { metric: "Success rate", michigan: { value: "41.8%", rank: 58 }, opponent: { value: "41.7%", rank: 75 } },
      { metric: "Rush success", michigan: { value: "41.3%", rank: 47 }, opponent: { value: "40.9%", rank: 96 } },
      { metric: "Pass success", michigan: { value: "42.8%", rank: 79 }, opponent: { value: "41.8%", rank: 57 } },
      { metric: "Explosive-play rate", michigan: { value: "9.9%", rank: 22 }, opponent: { value: "11.2%", rank: 70 } },
      { metric: "Yards per play", michigan: { value: "4.83", rank: 18 }, opponent: { value: "5.80", rank: 67 } },
    ],
    takeaway:
      "The stable evidence points to one dominant unit, not a dominant Oklahoma team. Oklahoma's defense owns a top-eight rank in all five validated categories. Oklahoma's 2025 offense does not. Michigan's path is therefore less about outgunning the Sooners and more about refusing to give their defense extra leverage through turnovers, third-and-long and short fields.",
  },

  week1: {
    intro:
      "Use Week 1 to identify problems, not to rewrite a full year of priors. The official box scores tell a cleaner story than the two final scores by themselves.",
    oklahoma: {
      line: "Oklahoma 51, UTEP 0",
      opponent: "UTEP",
      qb: "John Mateer: 11-for-17, 225 yards, 3 TD, 0 INT; exited late in the third quarter",
      rb: "Lloyd Avant: 15 carries, 79 yards, 1 TD",
      rows: [
        { value: "401", label: "Total yards" },
        { value: "6.9", label: "Yards per play" },
        { value: "6/11", label: "Third down" },
        { value: "5/5", label: "Red-zone scores" },
        { value: "4", label: "Sacks by OU" },
        { value: "+1", label: "Turnover margin" },
      ],
    },
    michigan: {
      line: "Michigan 13, Western Michigan 12",
      opponent: "Western Michigan",
      qb: "Bryce Underwood: 12-for-22, 170 yards, 1 TD, 1 INT; 9 carries, 47 yards, 1 rush TD",
      rb: "Jordan Marshall: 11 carries, 44 yards; Michigan tailbacks combined for 59 yards on 16 carries",
      rows: [
        { value: "276", label: "Total yards" },
        { value: "5.8", label: "Yards per play" },
        { value: "3/10", label: "Third down" },
        { value: "19:52", label: "Time of possession" },
        { value: "6", label: "Punts" },
        { value: "-3", label: "Turnover margin" },
      ],
    },
    takeaway:
      "Oklahoma was clearly the better Week 1 offense, but 51 points was not 51 points of offense: Isaiah Sategna III returned a punt 88 yards for a touchdown, and the Sooners repeatedly benefited from field position while scoring on their first eight possessions. Michigan created the opposite environment for itself with two lost fumbles, an interception and six punts. Defensively, both teams were stingy by conventional box-score measures: Michigan allowed 3.3 yards per play and no touchdowns; Oklahoma allowed 3.5 yards per play and no points. The largest Week 1 separation was offense, ball security and hidden yards.",
    caveat:
      "The opponents were not equivalent. Michigan Football Focus's preseason model ranked UTEP #122 and Western Michigan #79, and Western entered 2026 as the reigning MAC champion. This section intentionally uses official box-score data rather than unpublished single-game advanced rates; the 2025 opponent-adjusted rows above remain the validated analytics baseline.",
  },

  matchups: [
    {
      id: "oklahoma-line-vs-michigan-rush",
      kicker: "MATCHUP 1",
      title: "The offensive-line injury story belongs to Oklahoma",
      question: "Does Oklahoma get healthy enough up front to neutralize the best thing Michigan showed in Week 1?",
      numbers: [
        { value: "2 expected back", label: "Jake Maikkula and Ryan Fodje practiced at full speed this week" },
        { value: "1 uncertain", label: "Michael Fasusi's availability remained less certain in midweek reporting" },
        { value: "1.5 sacks", label: "Dom Nichols vs. Western Michigan" },
      ],
      narrative: [
        "Michigan is not starting a true freshman center. Its Week 1 line was Blake Frazier, Evan Link, Jake Guarnera, Brady Norton and Andrew Sprague, a group loaded with prior starting experience. The reshuffled line in this matchup is Oklahoma's. True freshman Noah Best started in the opener while veteran center Jake Maikkula and Ryan Fodje were unavailable, and Michael Fasusi started at left tackle.",
        "The picture has improved for Oklahoma since Friday. Midweek reporting had Maikkula and Fodje back at full speed and expected to return, while Fasusi's status was less certain. That makes this a moving matchup, not a blanket Oklahoma weakness. Michigan still has a real pressure lever: Dom Nichols had 1.5 sacks in the opener, and Carter Meadows practiced this week with hopes of joining the edge rotation. The catch is John Mateer turns undisciplined pressure into rushing yards, so Michigan has to compress the pocket without opening escape lanes.",
      ],
    },
    {
      id: "run-funnel",
      kicker: "MATCHUP 2",
      title: "Michigan cannot run on reputation",
      question: "Can the Wolverines repair a Week 1 run-game execution problem against the best adjusted rush defense in the 2025 sample?",
      numbers: [
        { value: "32.0%", label: "Oklahoma adjusted rush success allowed, #1 of 136" },
        { value: "49.0%", label: "Michigan 2025 adjusted rush success, #4 of 136" },
        { value: "16-59", label: "Michigan tailbacks vs. Western Michigan" },
      ],
      narrative: [
        "This was supposed to be strength on strength. Michigan's 2025 offense ranked #4 in adjusted rush success. Oklahoma's 2025 defense ranked #1 in adjusted rush success allowed. Then Michigan's tailbacks opened 2026 with 59 yards on 16 carries, and the film showed missed assignments and poor execution in the new gap-scheme menu.",
        "The answer is not simply to hand Jordan Marshall the ball 25 times. Against a defense this good, volume without efficiency creates exactly the third-and-long game Brent Venables wants. Michigan needs cleaner combination blocks, better answers to movement and enough quarterback-run stress from Underwood to make Oklahoma defend all 11 players. If early downs repeatedly become second-and-eight and third-and-six, the Sooners own the matchup.",
      ],
    },
    {
      id: "underwood-vs-venables",
      kicker: "MATCHUP 3",
      title: "Bryce Underwood has already seen this exam once",
      question: "Can Michigan keep Venables from turning every important snap into a pre-snap test for its quarterback?",
      numbers: [
        { value: "9/24, 142", label: "Underwood passing at Oklahoma in 2025" },
        { value: "3/14", label: "Michigan third downs in that 24-13 loss" },
        { value: "6-126-1", label: "JJ Buchanan's Week 1 receiving line" },
      ],
      narrative: [
        "Last September in Norman, Oklahoma held Underwood to 9-of-24 passing for 142 yards and no touchdowns, and Michigan converted only 3 of 14 third downs. One week into 2026, the same structural problem is still visible: Michigan was 3 of 10 on third down against Western Michigan and turned the ball over three times.",
        "Michigan has to reduce the number of snaps where Underwood is asked to diagnose Venables' pressure and coverage movement with the play clock bleeding. Quick-game throws, movement passes, designed quarterback runs and early-down play action can all change the geometry. JJ Buchanan gave Michigan a legitimate Week 1 answer with six catches for 126 yards, but Oklahoma can make life much harder if no second receiver forces the coverage to widen.",
      ],
    },
    {
      id: "mateer-contain",
      kicker: "MATCHUP 4",
      title: "Pressure John Mateer without giving him the escape hatch",
      question: "Can Michigan turn Oklahoma's line uncertainty into negative plays without repeating last year's scramble problem?",
      numbers: [
        { value: "344", label: "Mateer's total yards vs. Michigan in 2025" },
        { value: "3 TD", label: "Mateer touchdowns in that game: 1 pass, 2 rush" },
        { value: "3.3", label: "Michigan yards per play allowed in Week 1" },
      ],
      narrative: [
        "Mateer was the difference in Norman: 270 passing yards, 74 rushing yards and three total touchdowns. His legs did not have to matter against UTEP -- he ran only three times for seven yards -- but Michigan should expect them to matter Saturday if the pocket gets muddy.",
        "This is where Michigan's encouraging opener on defense meets its hardest test. The Wolverines held Western Michigan to 221 yards and no touchdowns, and Nichols repeatedly affected the pocket. Against Mateer, edge discipline matters as much as sack totals. Let him step through pressure and Oklahoma can turn a good rush into a broken-play explosive to Isaiah Sategna III, Trell Harris or Rocky Beers.",
      ],
    },
  ],

  howOklahomaWins: [
    "Win first down and let the defense create third-and-long. Michigan went 3-for-14 on third down in Norman last year and 3-for-10 against Western Michigan. Venables does not need to manufacture chaos if Michigan keeps volunteering obvious passing situations.",
    "Make Underwood prove he has more than one reliable receiving answer. JJ Buchanan produced 126 of Michigan's 170 passing yards in Week 1; forcing the ball elsewhere makes every coverage disguise more valuable.",
    "Use Mateer's legs when Michigan's rush gets greedy. He produced 74 rushing yards and two rushing touchdowns in last year's meeting, and the threat of the escape changes how aggressively Michigan can chase the pocket.",
    "Own the hidden yards. Isaiah Sategna III already has an 88-yard punt-return touchdown in 2026, and reigning Lou Groza Award winner Tate Sandell gives Oklahoma a major weapon if this turns into the low-possession game the market total of 43.5 suggests.",
  ],
  howMichiganWins: [
    "Stay on the field. Michigan cannot pair another 3-for-10 third-down day with six punts and expect its defense to survive 40 minutes against Oklahoma. Even modest improvement in early-down efficiency changes the entire game script.",
    "Run efficiently, not stubbornly. Oklahoma's adjusted rush defense ranked #1 in the 2025 FBS sample; Michigan needs movement, quarterback-run stress and cleaner execution rather than assuming its 2025 rushing identity will reappear on command.",
    "Get the turnover margin back to neutral. Michigan was minus-three against Western Michigan: Underwood threw an interception and lost a fumble, and Andrew Marsh lost a punt-return fumble. That is not survivable against a defense built to shorten the field.",
    "Make Oklahoma drive the field. Attack any remaining offensive-line uncertainty with Nichols and a deeper edge rotation, but keep rush-lane integrity against Mateer. If Oklahoma has to string together 10-play drives rather than live on explosives and short fields, Michigan's defense gives the Wolverines a chance.",
  ],

  numbersThatMatter: [
    { value: "#2", label: "Oklahoma 2025 defense composite", why: "The strongest and most stable unit-level signal in the matchup." },
    { value: "3/14 -> 3/10", label: "Michigan third downs: 2025 at OU -> 2026 opener", why: "A recurring possession problem, not just one bad final score." },
    { value: "-3", label: "Michigan Week 1 turnover margin", why: "One interception and two lost fumbles gave Western short-field chances and starved Michigan's own offense of possessions." },
    { value: "3.3", label: "Michigan Week 1 yards per play allowed", why: "The defense allowed no touchdowns despite spending 40:08 on the field." },
    { value: "344", label: "John Mateer total yards vs. Michigan in 2025", why: "The returning quarterback has already shown he can stress Michigan with both his arm and his legs." },
    { value: "8 pts", label: "Market move: Oklahoma +2.5 to -5.5", why: "Action Network shows an eight-point flip from the opener; the current total is 43.5." },
  ],
  verdict:
    "Oklahoma deserves to be favored because its best unit attacks Michigan's biggest Week 1 weakness: staying on schedule without giving the ball away. But the current spread asks the Sooners to separate in a matchup whose strongest evidence still points toward defense and limited possessions. Michigan's defense is good enough to keep this live; its offense has to stop making the game harder than the opponent does. Editorial lean: Oklahoma 20, Michigan 17.",

  market: {
    spread: "Oklahoma -5.5",
    winChance: "36.3%",
    book: "FanDuel",
    asOf: "Sept. 10, 2026",
    source: "Action Network odds tracker",
    sourceUrl: "https://www.actionnetwork.com/ncaaf-game/oklahoma-michigan-score-odds-september-12-2026/287974",
    openedAt: "Opened Oklahoma +2.5 (Michigan -2.5); current total 43.5",
  },
  preseasonModel: {
    winProbMichiganPct: 67,
    projectedMargin: "Michigan by 4.3 (median +6.1)",
    projectedMarginRange: "10th-90th percentile: Oklahoma by 16.4 to Michigan by 24.6",
    source: "Michigan Football Focus 2026 preseason simulation, generated before Week 1",
  },

  methodology: {
    validated:
      "The 2025 opponent-adjusted efficiency claims and composite rankings come from the repository's schedule-adjusted-ratings-v1 model (ridge 40 / home-field ridge 20) through the Oklahoma Darren Data Pack. Its Oklahoma sample contains 12 FBS games, excluding the Illinois State FCS game. Primary strength claims use only the five metrics marked validated in that artifact: success rate, rush success rate, pass success rate, explosive-play rate and yards per play. The 3.2-point composite difference is a rating difference, not a predicted scoring margin.",
    week1:
      "Week 1 facts in this preview come from the official University of Michigan Western Michigan box score/play-by-play and the official University of Oklahoma UTEP box score/play-by-play. Total yards, yards per play, third downs, red-zone results, sacks, punts, time of possession and turnovers are official box-score values. No unpublished single-game success-rate estimate is presented as a validated 2026 metric.",
    market:
      "Action Network listed Oklahoma -5.5 with a 43.5 total on Sept. 10 after opening Oklahoma +2.5. The site's market file stores Michigan +5.5 and converts that spread to a 36.3% straight-up Michigan win chance using its 2018-2025 closing-spread logistic calibration. That is a market-derived probability, not the site's football prediction model.",
    preseason:
      "The 67% Michigan win probability and +4.3 projected margin (median +6.1) come from the site's independent preseason simulation and were generated before either team played Week 1. They are intentionally preserved as a preseason prior, not relabeled as a current prediction after Michigan-Western Michigan and Oklahoma-UTEP.",
  },

  sources: [
    { label: "Michigan Monday: Game 2 vs. Oklahoma (official Michigan)", url: "https://mgoblue.com/sports/2026/9/7/michigan-monday-game-2-vs-oklahoma" },
    { label: "Michigan vs. Western Michigan official box score", url: "https://mgoblue.com/sports/football/stats/2026/western-michigan/boxscore/30374" },
    { label: "Oklahoma vs. UTEP official box score", url: "https://soonersports.com/sports/football/stats/2026/utep/boxscore/11371" },
    { label: "Oklahoma 51, UTEP 0 official recap", url: "https://soonersports.com/news/2026/9/4/football-sooners-defeat-utep-to-open-the-season" },
    { label: "Michigan at Oklahoma 2025 official box score", url: "https://mgoblue.com/sports/football/stats/2025/oklahoma/boxscore/29134" },
    { label: "Oklahoma offensive-line availability update (Yahoo / Sooners On SI)", url: "https://sports.yahoo.com/articles/breaking-oklahoma-gets-o-line-145018611.html" },
    { label: "Michigan injury updates before Oklahoma (Maize n Brew)", url: "https://www.maizenbrew.com/football/122238/michigan-football-injury-updates-carter-meadows-andrew-babalola-hogan-hansen-oklahoma" },
    { label: "Michigan run-game film review vs. Western Michigan (Maize n Brew)", url: "https://www.maizenbrew.com/football/121968/michigan-football-western-michigan-film-study-run-game-blake-frazier-jake-guarnera-jordan-marshall-savion-hiter" },
    { label: "Tate Sandell wins 2025 Lou Groza Award (official Oklahoma)", url: "https://soonersports.com/news/2025/12/12/football-sandell-wins-lou-groza-award" },
    { label: "Oklahoma vs. Michigan odds tracker (Action Network)", url: "https://www.actionnetwork.com/ncaaf-game/oklahoma-michigan-score-odds-september-12-2026/287974" },
  ],
};