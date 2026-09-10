// Michigan 13, Western Michigan 12 — Week 1, September 5, 2026, Michigan Stadium.
// Every number here is derived directly from this repo's play-by-play and
// canonical team-game data (data/raw/cfbd/season=2026/.../week=01, gameId
// 401858428, and data/canonical/season=2026/team_games.json). Field-position,
// success-rate and explosiveness figures use the site's locked definitions
// (field-position-v1, success-v1, explosiveness-v1). Drive results, penalty
// text, third-down outcomes and turnover detail are read off the canonical
// play log's own flags (isPenalty, isTurnover, hasNoPlayContext, etc.).
//
// EPA figures use this repo's independent, from-scratch EPA v2 model
// ("epa-v2-research-next-score" — realized next-score-before-halftime value,
// never trained on CFBD's ppa) — the same model backing the site's
// fourth-down-decision grading. Fit on 1,544,257 plays across 11 seasons
// (2014–2025, excluding 2020), applied to gameId 401858428. "EPA negated by
// a penalty" = EP(the hypothetical down/distance/field position had the
// penalty not been called) − EP(the actual down/distance/field position that
// resulted), holding the pre-snap state fixed across both branches.

export type DriveRow = {
  seq: number;
  quarter: number;
  result: "TD" | "PUNT" | "INT" | "FUMBLE";
  startYardsToGoal: number;
  deepestYardsToGoal: number;
  plays: number;
  epa: number;
  note?: string;
};

export const wmu2026Recap = {
  gameId: "401858428",
  michiganTeamId: 130,
  opponentTeamId: 2711,
  finalScore: { michigan: 13, westernMichigan: 12 },
  kickoffLabel: "September 5, 2026 · Michigan Stadium",

  quarterback: {
    name: "Bryce Underwood",
    completions: 12,
    attempts: 24,
    passYards: 170,
    passTDs: 1,
    interceptions: 1,
    carries: 23,
    rushYards: 95,
    rushTDs: 1,
  },

  totalOffenseYards: 265,
  sacksAllowed: 1,

  fieldPosition: {
    michiganAvgStart: 23.8,
    opponentAvgStart: 40.2,
  },

  thirdDown: {
    // Every 3rd down Michigan actually snapped, excluding the final
    // game-winning drive and the one first down gifted by a Western
    // Michigan pre-snap penalty (no Michigan snap occurred on that down).
    realAttempts: 9,
    realConversions: 2,
    // Same window, but counting the penalty-gifted first down and the two
    // conversions on the final drive — the "flattering" box-score version.
    boxScoreAttempts: 12,
    boxScoreConversions: 4,
  },

  drives: [
    { seq: 1, quarter: 1, result: "TD", startYardsToGoal: 75, deepestYardsToGoal: 1, plays: 11, epa: 8.45, note: "Opening drive. Stuffed on 3rd-and-goal from the 1, then Underwood punched it in on 4th down." },
    { seq: 2, quarter: 1, result: "PUNT", startYardsToGoal: 75, deepestYardsToGoal: 53, plays: 4, epa: -0.83, note: "A 16-yard 3rd-and-5 conversion was wiped by an Illegal Formation penalty. The replayed down stalled two plays later." },
    { seq: 3, quarter: 2, result: "PUNT", startYardsToGoal: 80, deepestYardsToGoal: 78, plays: 3, epa: -2.62, note: "Three-and-out. Net gain: 2 yards." },
    { seq: 4, quarter: 2, result: "PUNT", startYardsToGoal: 84, deepestYardsToGoal: 77, plays: 3, epa: -3.16, note: "Included a negative pass play on 3rd-and-3." },
    { seq: 5, quarter: 2, result: "PUNT", startYardsToGoal: 92, deepestYardsToGoal: 89, plays: 3, epa: -2.35, note: "Started at the 8. A sack on 3rd-and-7 ended it." },
    { seq: 6, quarter: 2, result: "INT", startYardsToGoal: 98, deepestYardsToGoal: 73, plays: 5, epa: -3.21, note: "Two-minute drill from the Michigan 2. Never left Michigan's own side of the field before Underwood was picked off near the 27." },
    { seq: 7, quarter: 3, result: "PUNT", startYardsToGoal: 73, deepestYardsToGoal: 44, plays: 7, epa: 1.80, note: "The one drive that reached Western Michigan territory (to the 44) — despite two more holding penalties, one erasing a 20-yard run." },
    { seq: 8, quarter: 4, result: "PUNT", startYardsToGoal: 82, deepestYardsToGoal: 75, plays: 3, epa: -1.91, note: "Three-and-out." },
    { seq: 9, quarter: 4, result: "FUMBLE", startYardsToGoal: 93, deepestYardsToGoal: 78, plays: 3, epa: -2.95, note: "Marshall's 15-yard run set up 1st-and-10 at the 22. Two plays later, Underwood fumbled on a scramble near the 31; Western Michigan recovered." },
    { seq: 10, quarter: 4, result: "TD", startYardsToGoal: 75, deepestYardsToGoal: 47, plays: 6, epa: 1.95, note: "Down 12-7 with 35 seconds left, no timeouts. Underwood to Buchanan for 47 and the win, as time expired." },
  ] as DriveRow[],

  penalties: [
    { drive: 1, type: "Illegal Formation", yards: 5, effect: "Wiped a 3-yard Jordan Marshall run.", magnitude: "minor" as const },
    { drive: 2, type: "Illegal Formation", yards: 5, effect: "Wiped a 16-yard completion that had converted 3rd-and-5.", magnitude: "major" as const, epaNegated: 2.45 },
    { drive: 7, type: "Holding (interior)", yards: 10, effect: "Turned a stuffed 2nd-and-5 run into 2nd-and-15.", magnitude: "minor" as const },
    { drive: 7, type: "Holding (Underwood, run-blocking)", yards: 10, effect: "Wiped a 20-yard Broderick Kuzdzal run that would have reached the Western Michigan 30.", magnitude: "major" as const, epaNegated: 2.22 },
    { drive: 9, type: "Illegal Substitution", yards: 5, effect: "Accepted for yardage on 1st down; part of the same drive that ended in the fumble.", magnitude: "minor" as const },
  ],

  turnovers: [
    { drive: 6, type: "Interception", detail: "Thrown from Michigan's own 27 late in the 2nd quarter.", result: "Western Michigan field goal on the ensuing short field.", epa: -3.37 },
    { drive: 9, type: "Fumble", detail: "Underwood fumble on a scramble near the Michigan 31 in the 4th quarter.", result: "Western Michigan field goal on the ensuing short field.", epa: -2.35 },
  ],

  efficiency: [
    { metric: "Success rate", michigan: 0.476, opponent: 0.313, unit: "pct" as const },
    { metric: "Explosive-play rate", michigan: 0.119, opponent: 0.031, unit: "pct" as const },
    { metric: "Yards per successful play", michigan: 11.5, opponent: 7.7, unit: "num" as const },
    { metric: "Points per scoring opportunity", michigan: 7.0, opponent: 1.7, unit: "num" as const },
  ],

  // EPA v2, full game, both directions. "Michigan offense" = every Michigan
  // snap (48, including the interception and fumble rows themselves — a
  // turnover's value swing is exactly what next-score EPA is built to
  // price). "Michigan defense allowed" = the same accounting applied to
  // every Western Michigan offensive snap (67).
  epaSummary: {
    michiganOffense: { totalEpa: -4.83, plays: 48, drives: 10, epaPerPlay: -0.101, epaPerDrive: -0.483 },
    michiganDefenseAllowed: { totalEpa: -22.57, plays: 67, drives: 11, epaPerPlay: -0.337, epaPerDrive: -2.052 },
    michiganOffenseCleanSnapsOnly: { totalEpa: 0.88, plays: 46, epaPerPlay: 0.019 },
  },

  defensivePenalties: [
    {
      drive: "WMU drive, 2nd quarter",
      type: "Pass Interference",
      detail: "Erased a live Jyaire Hill interception at the Michigan 37. Western Michigan kept the ball and gained an automatic first down instead of losing it.",
      epaNegated: 4.07,
    },
    {
      drive: "Same WMU drive, next snap",
      type: "Personal foul (15 yards, on top of a stopped 6-yard gain)",
      detail: "Turned a manageable 2nd-and-4 into a fresh set of downs 21 yards downfield.",
      epaNegated: 1.54,
    },
  ],

  westernMichiganThirdDown: { attempts: 17, conversions: 7 },

  longestWmuDrive: { plays: 19, yards: 71, result: "FG", epa: -1.76, quarter: 3 },

  sources: [
    { label: "Michigan vs. Western Michigan game hub", url: "/games/401858428" },
    { label: "College Football Data play-by-play, gameId 401858428", url: "https://collegefootballdata.com" },
  ],
} as const;
