// Hand-authored matchup preview dataset for Michigan vs. Oklahoma, Week 2, 2026.
// Built the same way as lib/michigan/matchup-preview-data.ts: pull from the
// repo's validated, reproducible analytics artifacts, verify against known
// guardrails, then hand-place the resulting numbers into a typed shape the
// UI renders without inline arithmetic or invented figures.
//
// Sources, by section:
// - "2025 opponent-adjusted baseline": data/exports/darren/2025/oklahoma/darren-data-pack.md
//   (schedule-adjusted-ratings-v1, ridge 40 / home-field ridge 20). Michigan's
//   matching figures are the comparison column inside that same export.
// - "Week 1, 2026": data/processed/derived/games/season=2026/season_type=regular/week=01/team_games.json
//   (team-game-v7-tfl, raw single-game numbers, not opponent-adjusted) plus a
//   manual sack count from the canonical 2026 play log for both games.
// - Preseason simulation win prob/margin: data/published/2026/michigan/preseason-2026-projection.json,
//   generated before Week 1 was played -- kept in its own labeled block.
// - Market line: data/published/2026/michigan/market-lines.json, sourced from
//   Action Network / FanDuel as of Sept. 10, 2026.

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
    "The nation's most efficient defense, by the 2025 numbers, is walking into Michigan Stadium. The question underneath both Week 1 tapes is whether either offense has actually shown anything yet.",

  scoutCards: [
    {
      kicker: "OKLAHOMA'S IDENTITY",
      value: "#2",
      title: "The best defense in the country, on paper.",
      body: "Oklahoma's defense finished 2025 as the #2 opponent-adjusted unit in FBS -- #1 against the run, #6 in explosive-play rate allowed, #3 in yards per play allowed. This is the standard Michigan's offense has to clear.",
    },
    {
      kicker: "THE REAL QUESTION MARK",
      value: "46.7/100",
      title: "The offense was never the strength.",
      body: "Oklahoma's offense ranked just #76 nationally in 2025. John Mateer's Week 1 line -- 14-for-19, 247 yards, 3 TD -- was sharp, but it came against UTEP, a bottom-tier FBS defense.",
    },
    {
      kicker: "THE 2026 TENSION",
      value: "51-0 / 13-12",
      title: "Two openers, two different tapes.",
      body: "Oklahoma routed UTEP by 51. Michigan needed a walk-off touchdown to beat a MAC team by one point at home. Neither result erases the 2025 baseline below -- it's the only in-season evidence either team has generated.",
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
      "This is the closest matchup on paper Michigan has played all year -- a +3.2 overall composite gap, not the +25.3 gap in the Western Michigan preview. But the gap is lopsided by side of the ball: Michigan's offense is the better unit, Oklahoma's defense is the better unit, and they're about to play each other directly.",
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
      "Read the two boards together and the picture is asymmetric. Michigan's offense (#19 nationally) runs directly into the best defense in the country by these numbers -- a top-8 unit in every one of the five validated categories. Oklahoma's offense (a middling #54-to-#96 unit across the board) runs into a Michigan defense that's good (#18-#58) but not dominant. If both units play to their 2025 baseline, Michigan's defense should have the easier night than Michigan's offense does.",
  },

  week1: {
    intro:
      "Both teams have exactly one 2026 data point, and it isn't the same kind of data point. Oklahoma beat UTEP by 51. Michigan needed a touchdown as time expired to beat Western Michigan by one. Neither result overrides the 2025 baseline above -- it's simply the only in-season evidence either team has generated, kept labeled separately on purpose.",
    oklahoma: {
      line: "Oklahoma 51, UTEP 0",
      opponent: "UTEP",
      qb: "John Mateer: 14-for-19, 247 yards, 3 TD",
      rb: "Lloyd Avant: 15 carries, 79 yards, 1 TD",
      rows: [
        { value: "56.1%", label: "Success rate" },
        { value: "60.0%", label: "Pass success rate" },
        { value: "54.1%", label: "Rush success rate" },
        { value: "17.5%", label: "Explosive-play rate" },
        { value: "7.3", label: "Yards per play" },
        { value: "+2", label: "Turnover margin" },
      ],
    },
    michigan: {
      line: "Michigan 13, Western Michigan 12",
      opponent: "Western Michigan",
      qb: "Bryce Underwood: 12-for-23, 128 yards passing, 1 rush TD, walk-off 47-yard TD pass to JJ Buchanan",
      rb: "Jordan Marshall: 11 carries, 44 yards",
      rows: [
        { value: "47.6%", label: "Success rate" },
        { value: "45.5%", label: "Pass success rate" },
        { value: "50.0%", label: "Rush success rate" },
        { value: "11.9%", label: "Explosive-play rate" },
        { value: "5.7", label: "Yards per play" },
        { value: "-1", label: "Turnover margin" },
      ],
    },
    takeaway:
      "Michigan's defense was, if anything, the sharper unit of the two by Week 1's own numbers: a 31.3% success rate allowed and a 3.1% explosive-play rate allowed, both better than what Oklahoma's defense allowed UTEP (34.0% / 8.0%). Oklahoma also had to work for its pressure -- 4 sacks on UTEP's 22 dropbacks -- while Michigan's defense got there twice. The gap between 51-0 and 13-12 is almost entirely an offensive story on both sides, not a defensive one.",
    caveat:
      "One important asterisk: UTEP and Western Michigan are not equivalent openers. UTEP is a bottom-tier FBS team; Western Michigan is the reigning MAC champion that pushed Michigan to the final play. Treat Week 1 as noisy, single-game evidence sitting on top of the validated 2025 baseline above -- not a replacement for it.",
  },

  matchups: [
    {
      id: "protect-the-freshman",
      kicker: "MATCHUP 1",
      title: "Protect a true freshman center",
      question: "Can a rebuilt Michigan line hold up behind a true freshman making just his second career start?",
      numbers: [
        { value: "3", label: "Projected Michigan OL starters out (Maikkula, Fodje, Fasusi)" },
        { value: "4 sacks", label: "Oklahoma's defensive line, Week 1 vs. UTEP" },
      ],
      narrative: [
        "Michigan is down three projected offensive line starters, which pushed true freshman Noah Best into the starting center job for just his second career start -- in Michigan Stadium, against a Big Ten-caliber crowd, facing a defensive front that just produced 4 sacks and consistently disrupted UTEP's pocket.",
        "Oklahoma's front isn't dependent on one player to generate that pressure, either -- Adepoju Adebawore made his first career start after Danny Okoye's injury and factored directly into it. This is the single most direct danger in the matchup: Michigan's most inexperienced protector against the group that made Oklahoma's defense the #2 opponent-adjusted unit in the country a year ago.",
      ],
    },
    {
      id: "run-funnel",
      kicker: "MATCHUP 2",
      title: "Oklahoma's defense is built to stop exactly what Michigan does best",
      question: "What happens when the #1 adjusted run defense in the country (2025) meets a Michigan offense that ran for the #4 adjusted rush-success rate?",
      numbers: [
        { value: "32.0%", label: "Oklahoma rush success allowed, #1 of 136" },
        { value: "49.0%", label: "Michigan rush success rate, #4 of 136" },
      ],
      narrative: [
        "This is the sharpest contradiction on either team's statistical profile. Michigan's offense wants to establish Jordan Marshall and stay ahead of the chains on the ground -- the same approach that made the Wolverines the #4 adjusted rushing offense in the country last season. Oklahoma's defense was allowed the lowest opponent rush-success rate in the country running that exact defense.",
        "Neither number is a guess about scheme; both are opponent-adjusted results from a full season. Something has to give, and whichever side wins that specific battle -- Michigan staying on schedule on early downs, or Oklahoma forcing Michigan into obvious passing situations against a defense that also ranked #8 against the pass -- will do a lot to decide the game inside the game.",
      ],
    },
    {
      id: "balance-test",
      kicker: "MATCHUP 3",
      title: "Is Oklahoma's offense actually more balanced in 2026?",
      question: "The Oklahoma staff has made a more balanced offense an explicit offseason goal. Did Week 1 back that up?",
      numbers: [
        { value: "47.4%", label: "Oklahoma's 2025 rush decision rate (vs. Michigan's 57.1%)" },
        { value: "15-79-1", label: "Lloyd Avant's Week 1 rushing line" },
      ],
      narrative: [
        "Oklahoma was already less run-heavy than Michigan in 2025 (47.4% rush decision rate vs. Michigan's 57.1%), and this year's staff has talked openly about wanting more balance with Tory Blaylock sidelined and Avant establishing himself as the clear lead back in Week 1.",
        "The stakes: if Oklahoma can stay balanced and keep Mateer off obvious passing downs, it neutralizes the one lever Michigan's defense has to generate pressure. If Michigan's front -- which already got to the quarterback twice against Western Michigan -- can force Oklahoma into predictable passing situations, that's where the game turns least in Oklahoma's favor.",
      ],
    },
  ],

  howOklahomaWins: [
    "Feed Lloyd Avant and stay balanced. Oklahoma's offense was never the elite half of this team; the path to winning is controlling the clock and not needing 30 empty possessions to complement the nation's #2 defense.",
    "Let the front seven -- 4 sacks and the country's #1 adjusted rush defense in 2025 -- dictate the terms against a patchwork Michigan line anchored by a true freshman center.",
    "Don't get sloppy with the football. Oklahoma is already +2 on turnover margin for the season; Michigan is -1, including two Bryce Underwood giveaways that directly set up Western Michigan points.",
  ],
  howMichiganWins: [
    "Give Underwood's line real help -- chip protection and quick-game answers against a front that already produced 4 sacks in Week 1, rather than asking Noah Best to win every rep in isolation.",
    "Establish the run behind Jordan Marshall early to avoid the long-yardage, obvious-passing situations where Oklahoma's defense (#1 adjusted rush D, #8 adjusted pass D) is most dangerous.",
    "Cash the possessions Michigan does get. Michigan's offense reached Western Michigan's territory only once all night in Week 1 -- against a defense this good, that number has to move.",
    "Make Oklahoma one-dimensional. Michigan's front already got home twice against Western Michigan; testing whether Oklahoma's 'more balanced' 2026 plan survives real pressure is the clearest lever Michigan's defense controls.",
  ],

  numbersThatMatter: [
    { value: "72.3 vs 75.5", label: "2025 overall composite, Oklahoma vs. Michigan", why: "The tightest matchup gap Michigan has played all year -- a 3.2-point edge, not a blowout." },
    { value: "#2", label: "Oklahoma's 2025 defense composite rank", why: "By the site's validated opponent-adjusted model, only one FBS defense graded better." },
    { value: "#76", label: "Oklahoma's 2025 offense composite rank", why: "The unit that has to prove Week 1's 51-0 over UTEP wasn't just about the opponent." },
    { value: "51-0 / 13-12", label: "Week 1 final scores", why: "Two very different tapes walking into the same Saturday." },
    { value: "+5.5 to +6.5", label: "Current market line (Michigan getting points)", why: "Moved from Michigan -2.5 preseason -- an 8-to-9-point swing in three weeks, driven almost entirely by Week 1." },
    { value: "24-13", label: "Oklahoma won this exact game last September", why: "The only true head-to-head data point between these two rosters." },
  ],
  verdict:
    "The 2025 baseline says this should be close, decided by whether Michigan's offense can find answers against the best defense it will face all year. The market has already made its decision. The tape says neither offense has proven much of anything yet.",

  market: {
    spread: "Oklahoma -5.5",
    winChance: "36.3%",
    book: "FanDuel",
    asOf: "Sept. 10, 2026",
    source: "Action Network odds tracker",
    sourceUrl: "https://www.actionnetwork.com/ncaaf-game/oklahoma-michigan-score-odds-september-12-2026/287974",
    openedAt: "Opened Michigan -2.5 in the preseason market (mid-August)",
  },
  preseasonModel: {
    winProbMichiganPct: 67,
    projectedMargin: "Michigan by 4.3 (median +6.1)",
    projectedMarginRange: "range: Oklahoma by 16.4 to Michigan by 24.6",
    source: "Michigan Football Focus 2026 preseason simulation (50,000 runs), generated before Week 1",
  },

  methodology: {
    validated:
      "All 2025 opponent-adjusted efficiency claims and composite rankings (success rate, rush/pass success, explosive-play rate, yards per play, and the composites built from them) come from the repository's schedule-adjusted model (schedule-adjusted-ratings-v1, ridge 40 / home-field ridge 20), via the Darren Data Pack export for Oklahoma (data/exports/darren/2025/oklahoma/darren-data-pack.md), which carries Michigan's matching figures as the built-in comparison column.",
    week1:
      "The Week 1, 2026 tape (success rate, rush/pass success, explosive-play rate, yards per play, turnover margin) comes directly from the repository's canonical 2026 team-game dataset (team-game-v7-tfl), plus a manual sack count from the canonical 2026 play log for both games. These are raw, single-game numbers with no opponent adjustment applied, and are labeled as such throughout this piece rather than blended into the validated 2025 rows.",
    market:
      "The FanDuel spread and Action Network market read are a sourced market price as of Sept. 10, 2026, not a Michigan Football Focus prediction. The win-chance figure applies the site's own spread-to-win-probability calibration (logistic, fit on 2018-2025 clean closing spreads) to that spread.",
    preseason:
      "The 67% win probability and +4.3 (median +6.1) projected margin are the site's preseason simulation (50,000 runs), generated before Week 1 was played. It has not been updated with in-season results and is presented here as a preseason data point, not a current prediction.",
  },

  sources: [
    { label: "4 players to watch: Oklahoma vs. Michigan (Yahoo Sports)", url: "https://sports.yahoo.com/articles/4-players-watch-oklahoma-takes-120215933.html" },
    { label: "Way Too Early Michigan Opponent Preview: Week 2 vs. Oklahoma (SI)", url: "https://www.si.com/college/michigan/football/way-too-early-michigan-football-opponent-preview-week-2-vs-oklahoma" },
    { label: "Oklahoma vs. Michigan: market overreaction in favor of the Sooners (NBC Sports)", url: "https://www.nbcsports.com/watch/college-football/oklahoma-vs-michigan-preview-market-overreaction-in-favor-of-sooners" },
    { label: "Oklahoma vs. Michigan odds tracker (Action Network)", url: "https://www.actionnetwork.com/ncaaf-game/oklahoma-michigan-score-odds-september-12-2026/287974" },
    { label: "Oklahoma @ Michigan odds (FanDuel)", url: "https://sportsbook.fanduel.com/football/ncaa-football-games/oklahoma-@-michigan-35170578" },
    { label: "2026 official Michigan roster", url: "https://mgoblue.com/sports/football/roster/2026" },
  ],
};
