// Hand-authored matchup preview datasets (numbers-first, narrative-shaped).
// Each export is built the same way: pull from the repo's validated,
// reproducible analytics artifacts, verify the pipeline output against
// known guardrails, then hand-place the resulting numbers into a typed
// shape the UI renders without any inline arithmetic or invented figures.
//
// This file intentionally uses ONLY the schedule-adjusted "validated five"
// opponent-adjusted model (source: darren_data_pack.py, output published to
// data/exports/darren/<season>/<team>/darren-data-pack.md) for matchup
// efficiency claims -- not the separate sitewide Ridge team-rating pipeline
// (data/published/<season>/analytics/ridge-team-ratings.json) that powers
// /games/[gameId] and /rankings. The two pipelines use different math and
// can disagree on the same team's rank; blending them produces exactly the
// kind of self-contradicting numbers this dataset is meant to avoid.

export type StatPoint = { value: string; label: string; detail?: string };

export type CompareValue = { value: string; rank: number };
export type CompareRow = { metric: string; michigan: CompareValue; opponent: CompareValue };

export type ContinuityPositionGroup = { group: string; pct: number };

export type ContinuitySide = {
  overallPct: number;
  positions: ContinuityPositionGroup[];
};

export type MatchupPreviewData = {
  slug: string;
  season: number;
  week: number;
  opponent: string;
  opponentTeamId: number;
  michiganTeamId: number;
  kickoffISO: string;
  venue: string;
  record: string;

  heroThesis: string;
  oneSentence: string;

  opponentOffense: { numbers: StatPoint[]; takeaway: string };
  opponentDefense: { numbers: StatPoint[]; takeaway: string };
  michiganOffenseTakeaway: string;
  michiganDefenseTakeaway: string;

  compositeComparison: {
    michigan: { offense: CompareValue; defense: CompareValue; overall: CompareValue };
    opponent: { offense: CompareValue; defense: CompareValue; overall: CompareValue };
    overallEdge: string;
  };
  offenseCompareRows: CompareRow[];
  defenseCompareRows: CompareRow[];

  blueprint: {
    michiganRecord2025: string;
    opponentRecord2025: string;
    winProbMichiganPct: number;
    winProbOpponentPct: number;
    projectedMargin: string;
    projectedMarginRange: string;
    projectionSource: string;
    michiganOffenseVsOpponentDefense: CompareRow[];
    opponentOffenseVsMichiganDefense: CompareRow[];
    michiganSeason: { offense: CompareValue; defense: CompareValue; overall: CompareValue; offenseContinuityPct: number; defenseContinuityPct: number };
    opponentSeason: { offense: CompareValue; defense: CompareValue; overall: CompareValue; offenseContinuityPct: number; defenseContinuityPct: number };
  };

  continuity: {
    methodologyNote: string;
    michigan: { offense: ContinuitySide; defense: ContinuitySide };
    opponent: { offense: ContinuitySide; defense: ContinuitySide };
    opponentExternal: {
      source: string;
      offenseOverallPct: number;
      defenseOverallPct: number;
      offensePositions: ContinuityPositionGroup[];
      defensePositions: ContinuityPositionGroup[];
    };
    divergenceNote: string;
  };

  matchups: Array<{
    id: string;
    kicker: string;
    title: string;
    question: string;
    numbers: StatPoint[];
    narrative: string[];
  }>;

  howOpponentCompetes: string[];
  howMichiganControls: string[];

  numbersThatMatter: Array<{ value: string; label: string; why: string }>;

  market: { spread: string; winChance: string; book: string; asOf: string; source: string; sourceUrl: string } | null;

  methodology: {
    validated: string;
    internal: string;
    external: string;
    market: string;
  };

  sources: Array<{ label: string; url: string }>;
};

export const michiganWesternMichigan2026: MatchupPreviewData = {
  slug: "michigan-western-michigan-2026",
  season: 2026,
  week: 1,
  opponent: "Western Michigan",
  opponentTeamId: 2711,
  michiganTeamId: 130,
  kickoffISO: "2026-09-05T23:30:00.000Z",
  venue: "Michigan Stadium",
  record: "Western Michigan enters 10-4, the reigning MAC Champion, off a Myrtle Beach Bowl win",

  heroThesis:
    "Western brings its quarterback and its offensive backfield back almost intact. The defense that carried the Broncos in 2025 is rebuilding most of its front seven -- but not from scratch.",

  oneSentence:
    "Western wants to lean on Broc Lowry, a nearly-intact backfield and a run-first identity to shorten the game; Michigan's clearest opening is a defensive front that looks far less familiar than the secondary behind it.",

  opponentOffense: {
    numbers: [
      { value: "65.1%", label: "Rush decision rate", detail: "one of the most run-heavy offenses in FBS" },
      { value: "42.7%", label: "Adjusted rush success", detail: "#65 of 136 -- roughly average" },
      { value: "38.3%", label: "Adjusted pass success", detail: "#118 of 136 -- bottom quarter nationally" },
      { value: "#100", label: "Overall offense composite", detail: "of 136 FBS teams" },
    ],
    takeaway: "Western was comfortable winning without asking its passing game to carry the offense.",
  },
  opponentDefense: {
    numbers: [
      { value: "#34", label: "Overall defense composite", detail: "of 136 FBS teams" },
      { value: "38.4%", label: "Adjusted pass success allowed", detail: "#23 of 136" },
      { value: "41.1%", label: "Adjusted rush success allowed", detail: "#43 of 136" },
    ],
    takeaway: "The defense was the stronger half of the team and made Western difficult to play cleanly against.",
  },
  michiganOffenseTakeaway: "Michigan's offense was elite in exactly the way Western's wasn't -- an explosive, efficient unit on the ground and through the air.",
  michiganDefenseTakeaway: "Michigan's defense was very good but not as dominant relative to the field as Western's -- the closest thing to an even matchup on this page.",

  compositeComparison: {
    michigan: {
      offense: { value: "83.4/100", rank: 19 },
      defense: { value: "67.6/100", rank: 38 },
      overall: { value: "75.5/100", rank: 19 },
    },
    opponent: {
      offense: { value: "30.1/100", rank: 100 },
      defense: { value: "70.4/100", rank: 34 },
      overall: { value: "50.2/100", rank: 67 },
    },
    overallEdge: "+25.3", // 75.5 - 50.2, Michigan's overall composite minus Western's
  },
  offenseCompareRows: [
    { metric: "Success rate", michigan: { value: "46.8%", rank: 19 }, opponent: { value: "40.3%", rank: 95 } },
    { metric: "Rush success", michigan: { value: "49.0%", rank: 4 }, opponent: { value: "42.7%", rank: 65 } },
    { metric: "Pass success", michigan: { value: "42.0%", rank: 54 }, opponent: { value: "38.3%", rank: 118 } },
    { metric: "Explosive-play rate", michigan: { value: "13.0%", rank: 19 }, opponent: { value: "10.9%", rank: 80 } },
    { metric: "Yards per play", michigan: { value: "6.55", rank: 21 }, opponent: { value: "4.91", rank: 119 } },
  ],
  defenseCompareRows: [
    { metric: "Success rate allowed", michigan: { value: "41.8%", rank: 58 }, opponent: { value: "39.8%", rank: 35 } },
    { metric: "Rush success allowed", michigan: { value: "41.3%", rank: 47 }, opponent: { value: "41.1%", rank: 43 } },
    { metric: "Pass success allowed", michigan: { value: "42.8%", rank: 79 }, opponent: { value: "38.4%", rank: 23 } },
    { metric: "Explosive-play rate allowed", michigan: { value: "9.9%", rank: 22 }, opponent: { value: "10.9%", rank: 52 } },
    { metric: "Yards per play allowed", michigan: { value: "4.83", rank: 18 }, opponent: { value: "5.57", rank: 52 } },
  ],

  blueprint: {
    // 2025 final records: Michigan 9-4 (data/published/2025/teams/michigan/games.json),
    // Western Michigan 10-4 (wmubroncos.com, MAC Champion).
    michiganRecord2025: "9-4",
    opponentRecord2025: "10-4",
    // Win prob / margin: data/published/2026/michigan/preseason-2026-projection.json,
    // game 401858428 -- the site's calibrated preseason simulation model (50,000 sims),
    // NOT the validated-five opponent-adjusted model used everywhere else on this page.
    // Kept in its own labeled block rather than blended into the adjusted-stat rows.
    winProbMichiganPct: 95.6,
    winProbOpponentPct: 4.4,
    projectedMargin: "Michigan by 27.6",
    projectedMarginRange: "range: Michigan by 7.3 to 47.9",
    projectionSource: "Michigan Football Focus 2026 preseason simulation (50,000 runs)",
    // Cross-matchup: each team's own offense against the other's defense,
    // same validated-five metrics used throughout this page.
    michiganOffenseVsOpponentDefense: [
      { metric: "Success rate", michigan: { value: "46.8%", rank: 19 }, opponent: { value: "39.8%", rank: 35 } },
      { metric: "Rush success", michigan: { value: "49.0%", rank: 4 }, opponent: { value: "41.1%", rank: 43 } },
      { metric: "Pass success", michigan: { value: "42.0%", rank: 54 }, opponent: { value: "38.4%", rank: 23 } },
      { metric: "Explosive-play rate", michigan: { value: "13.0%", rank: 19 }, opponent: { value: "10.9%", rank: 52 } },
      { metric: "Yards per play", michigan: { value: "6.55", rank: 21 }, opponent: { value: "5.57", rank: 52 } },
    ],
    opponentOffenseVsMichiganDefense: [
      { metric: "Success rate", michigan: { value: "41.8%", rank: 58 }, opponent: { value: "40.3%", rank: 95 } },
      { metric: "Rush success", michigan: { value: "41.3%", rank: 47 }, opponent: { value: "42.7%", rank: 65 } },
      { metric: "Pass success", michigan: { value: "42.8%", rank: 79 }, opponent: { value: "38.3%", rank: 118 } },
      { metric: "Explosive-play rate", michigan: { value: "9.9%", rank: 22 }, opponent: { value: "10.9%", rank: 80 } },
      { metric: "Yards per play", michigan: { value: "4.83", rank: 18 }, opponent: { value: "4.91", rank: 119 } },
    ],
    michiganSeason: {
      offense: { value: "83.4/100", rank: 19 },
      defense: { value: "67.6/100", rank: 38 },
      overall: { value: "75.5/100", rank: 19 },
      offenseContinuityPct: 63.0,
      defenseContinuityPct: 61.1,
    },
    opponentSeason: {
      offense: { value: "30.1/100", rank: 100 },
      defense: { value: "70.4/100", rank: 34 },
      overall: { value: "50.2/100", rank: 67 },
      offenseContinuityPct: 56.2,
      defenseContinuityPct: 42.9,
    },
  },

  continuity: {
    methodologyNote:
      "This is our own headcount continuity, not a snap-weighted number: every 2025 roster player who is also on the 2026 roster counts once, regardless of how much he played. We don't have per-player snap-count data in our pipeline (CFBD exposes season stats and Predicted Points Added, not participation/snap counts), so a true snap-weighted \"returning snaps\" figure isn't something we can calculate ourselves -- see the methodology note below for how that gap is handled.",
    michigan: {
      offense: {
        overallPct: 63.0,
        positions: [
          { group: "QB", pct: 40.0 },
          { group: "RB", pct: 62.5 },
          { group: "WR", pct: 57.1 },
          { group: "TE", pct: 75.0 },
          { group: "OL", pct: 68.4 },
        ],
      },
      defense: {
        overallPct: 61.1,
        positions: [
          { group: "DL", pct: 63.2 },
          { group: "LB", pct: 42.9 },
          { group: "DB", pct: 71.4 },
        ],
      },
    },
    opponent: {
      offense: {
        overallPct: 56.2,
        positions: [
          { group: "QB", pct: 50.0 },
          { group: "RB", pct: 71.4 },
          { group: "WR", pct: 50.0 },
          { group: "TE", pct: 44.4 },
          { group: "OL", pct: 61.1 },
        ],
      },
      defense: {
        overallPct: 42.9,
        positions: [
          { group: "DL", pct: 40.0 },
          { group: "LB", pct: 50.0 },
          { group: "DB", pct: 42.1 },
        ],
      },
    },
    opponentExternal: {
      source: "CBS Sports returning-snap research (published Aug. 22, 2026)",
      offenseOverallPct: 52,
      defenseOverallPct: 33,
      offensePositions: [
        { group: "QB", pct: 89 },
        { group: "RB", pct: 70 },
        { group: "WR", pct: 61 },
        { group: "TE", pct: 2 },
        { group: "OL", pct: 52 },
      ],
      defensePositions: [
        { group: "DL", pct: 20 },
        { group: "LB", pct: 12 },
        { group: "DB", pct: 55 },
      ],
    },
    divergenceNote:
      "Our headcount numbers and CBS's snap-weighted numbers measure different things, and the gap between them is itself informative. Western's DL/LB headcount continuity (40% / 50%) looks far less severe than CBS's snap-weighted continuity (20% / 12%) -- meaning the players who left were disproportionately the ones who played the most, while several of the bodies still on the roster were lightly used in 2025. The opposite is true at DB: our headcount (42%) undersells it next to CBS's snap number (55%), because the defensive backs who stayed were disproportionately the ones who played heavy snaps. Same story at tight end for the offense: our headcount continuity is a modest 44%, but CBS's snap-weighted number is just 2% -- several bodies return, but almost none of the players who caught passes.",
  },

  matchups: [
    {
      id: "force-passing",
      kicker: "MATCHUP 1",
      title: "Force Western out of its comfort zone",
      question: "Can Michigan get Western behind schedule and make Broc Lowry win consistently through the air?",
      numbers: [
        { value: "42.7%", label: "Adjusted rush success", detail: "#65 -- roughly average" },
        { value: "38.3%", label: "Adjusted pass success", detail: "#118 -- the weak point" },
      ],
      narrative: [
        "Western's 2025 identity wasn't just run-heavy by volume (65.1% rush decision rate) -- it was run-heavy because the running game was the more efficient half of the offense. The gap between an average adjusted rush success rate (#65) and a bottom-quarter adjusted pass success rate (#118) is the single widest split in Western's statistical profile.",
        "Michigan doesn't need to shut Western's offense down entirely. It needs to take away the option of staying on schedule on the ground and make Lowry win with his arm consistently, not just occasionally.",
      ],
    },
    {
      id: "rebuilt-front",
      kicker: "MATCHUP 2",
      title: "Test the rebuilt front seven",
      question: "How much of the unit responsible for Western's 2025 defensive performance is actually still there?",
      numbers: [
        { value: "20% / 12%", label: "DL / LB snap continuity", detail: "CBS Sports, snap-weighted" },
        { value: "8 of 20", label: "DL who are college-experience newcomers", detail: "our roster audit" },
      ],
      narrative: [
        "Western's defense was the strength of the team in 2025. The relevant question for 2026 isn't whether that defense was good -- it's how much of the group that produced it is actually back. By CBS's snap-weighted numbers, Western returns only 20% of defensive-line snaps and 12% of linebacker snaps.",
        "But low continuity doesn't automatically mean a bad unit. Western didn't try to replace its departed front seven with freshmen -- it imported older, experienced bodies: DE DeJuan Echoles Jr. (Ball State), DE Scoop Gardner Jr. (Long Island, 14.5 TFL in 2025), DE Austin Alexander (North Carolina, former four-star), DT Ahmed Tounkara (Ohio State) and DT Zavian Tibbs (Houston) among them. Michigan isn't facing the same defensive front that fueled Western's 2025 success, but Western isn't simply starting over, either.",
      ],
    },
    {
      id: "back-end-stability",
      kicker: "MATCHUP 3",
      title: "Don't confuse front-seven turnover with an entirely new defense",
      question: "Does the back end give Western enough stability to survive while its new front settles in?",
      numbers: [
        { value: "55%", label: "DB snap continuity", detail: "CBS Sports, the highest of any defensive group" },
        { value: "38.4%", label: "Adjusted pass success allowed", detail: "#23 of 136" },
      ],
      narrative: [
        "Western returns far more experience in the secondary than up front, and the coaching staff transition is a continuation rather than a reset: Greer Martini coached linebackers in the 2025 defense before being promoted to coordinator, and players have described the 2026 install as \"different person, same scheme.\"",
        "That combination -- a stable back end and a scheme that survives the coordinator change -- is why Western's #23 adjusted pass defense shouldn't be assumed to collapse just because the defensive front is largely new. The correct read is a defense that's reloaded inside a familiar system, not one that's starting from zero.",
      ],
    },
  ],

  howOpponentCompetes: [
    "Stay ahead of the chains with Lowry and the run game -- Western's 65.1% rush decision rate isn't going to change, and Lowry (963 rush yards, 14 rush TD in 2025) and Jalen Buckley account for 82% of Western's returning offensive value by our PPA audit.",
    "Shorten the game. Western averaged 10.69 possessions per game in 2025, fewer than Michigan's 11.23 -- fewer possessions means fewer chances for a talent gap to compound.",
    "Lean on the defensive back end (55% snap continuity, #23 adjusted pass defense) to prevent the explosive passing plays that would turn a competitive game into a rout.",
    "Get immediate competence from the rebuilt defensive front -- not dominance, just enough to keep Michigan from finishing drives cheaply behind a line that returns only 20% of its snaps.",
  ],
  howMichiganControls: [
    "Force obvious passing downs early and often. The #65-vs-#118 rush/pass split is the single clearest exploitable gap in Western's profile -- make Lowry beat Michigan through the air, not just occasionally but as the primary plan.",
    "Attack the reconstructed front seven directly, not just statistically. 20% DL and 12% LB snap continuity is the lowest continuity number on either roster in this preview -- that unit is the one still finding its footing under game speed.",
    "Don't let the game compress into a low-possession, methodical script. Western's whole competitive path depends on keeping possessions limited; Michigan controls that by playing fast and finishing drives rather than trading empty possessions.",
    "Respect that Western's pass defense (#23 adjusted) is real. A shootout isn't guaranteed just because the front seven is inexperienced -- ball security and finishing drives still matter against a defensive back end that didn't lose much.",
  ],

  numbersThatMatter: [
    { value: "65.1%", label: "Western's 2025 rush decision rate", why: "One of the most run-heavy offenses in the country, and there's no reason for that identity to change in 2026." },
    { value: "#118", label: "Adjusted pass-success rank", why: "The clearest exploitable weakness in Western's statistical profile -- the widest gap between run and pass efficiency on either roster." },
    { value: "#34", label: "Adjusted defense composite", why: "Western's defense was legitimately good in 2025, particularly against the pass (#23) -- the question is how much of it returns, not whether it was real." },
    { value: "20% / 12%", label: "DL / LB snap continuity (CBS)", why: "The single lowest-continuity position pairing in this whole preview -- Michigan's most direct point of attack." },
    { value: "82%", label: "Share of returning offensive PPA that's just Lowry + Buckley", why: "Western's offense isn't merely run-first -- it's built around two specific players staying on the field and staying effective." },
    { value: "63% / 61%", label: "Michigan's own offense / defense continuity", why: "Our same headcount methodology run on Michigan's roster -- Michigan returns more of both sides of the ball than Western does." },
    { value: "-26.5", label: "BetMGM spread (Michigan)", why: "The market's read, not our model's -- included for context, labeled separately from every opponent-adjusted claim on this page." },
  ],

  market: {
    spread: "Michigan -26.5",
    winChance: "95.9%",
    book: "BetMGM",
    asOf: "Aug. 19, 2026",
    source: "MLive preseason odds roundup",
    sourceUrl: "https://www.mlive.com/sports-betting/michigan-wolverines-football-odds/",
  },

  methodology: {
    validated:
      "All opponent-adjusted efficiency claims (success rate, rush/pass success, explosive-play rate, yards per play, and the composite ratings built from them) come from the repository's schedule-adjusted model (schedule-adjusted-ratings-v1, ridge 40 / home-field ridge 20), fit on the full 2025 FBS schedule graph with strict leave-one-game-out validation. Re-run live for this piece and confirmed to reproduce every published figure exactly.",
    internal:
      "Roster headcount continuity (both teams) and PPA retention (Western Michigan) are calculated directly from official team rosters plus CFBD's prior-season player Predicted Points Added, matched by name. Michigan's continuity used the same code path as Western's, adapted for the fact that mgoblue.com's official roster does not publish a \"Previous School\" column the way wmubroncos.com does -- so Michigan's non-returning players are grouped as unclassified newcomers rather than split into transfer/first-time-college buckets. Western's PPA figures were regenerated live for this piece; CFBD's underlying rushing-PPA computation has been revised upstream since the original pull (verified by diff -- roster classification and receiving/passing PPA were unchanged, only rushing PPA moved), so the numbers on this page are the current, corrected figures.",
    external:
      "ESPN's returning-production percentage and CBS Sports' returning-snap percentages are production-weighted and snap-weighted respectively -- different methodologies from our own headcount continuity, kept clearly labeled rather than blended together.",
    market:
      "The BetMGM spread and implied win probability are a sourced market price, not a Michigan Football Focus prediction.",
  },

  sources: [
    { label: "WMU 2026 coaching staff", url: "https://wmubroncos.com/sports/football/coaches" },
    { label: "Greer Martini promoted to DC (Feb. 11, 2026)", url: "https://wmubroncos.com/news/2026/2/11/greer-martini-promoted-to-defensive-coordinator.aspx" },
    { label: "21-transfer announcement (Feb. 9, 2026)", url: "https://wmubroncos.com/news/2026/2/9/football-welcomes-21-transfers-to-the-bronco-brotherhood.aspx" },
    { label: "2026 official Western Michigan roster", url: "https://wmubroncos.com/sports/football/roster/2026" },
    { label: "2026 official Michigan roster", url: "https://mgoblue.com/sports/football/roster/2026" },
    { label: "ESPN 2026 returning production (Bill Connelly, Mar. 23, 2026)", url: "https://www.espn.com/college-football/story/_/id/48259759/college-football-returning-production-2026-notre-dame-texas" },
    { label: "CBS 2026 returning snaps (Aug. 22, 2026)", url: "https://www.cbssports.com/college-football/news/college-football-returning-snap-percentages-2026/" },
    { label: "BetMGM spread via MLive (Aug. 19, 2026)", url: "https://www.mlive.com/sports-betting/michigan-wolverines-football-odds/" },
  ],
};
