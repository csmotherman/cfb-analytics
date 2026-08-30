// Hand-authored opponent scouting outlooks for creators (numbers-first,
// built to be read straight into a video). Not a generated pipeline artifact
// like game-story.ts -- each report is audited against the repository's
// published data pack + roster-overview export before being added here.
// Source: data/research/darren/<slug>.md, cross-checked against
// data/exports/darren/... and data/research/roster-overview/....

export type ScoutingTable = {
  caption?: string;
  columns: string[];
  rows: string[][];
};

export type ScoutingSection = {
  id: string;
  title: string;
  intro?: string[];
  bullets?: string[];
  tables?: ScoutingTable[];
};

export type ScoutingSource = { label: string; url: string };

export type ScoutingReport = {
  slug: string;
  opponent: string;
  opponentTeamId: number | null;
  michiganTeamId: number | null;
  season: number;
  matchupContext: string;
  record: string;
  overview: string[];
  sections: ScoutingSection[];
  guardrails: string[];
  sources: ScoutingSource[];
};

const westernMichigan2026: ScoutingReport = {
  slug: "western-michigan-2026",
  opponent: "Western Michigan",
  opponentTeamId: 2711,
  michiganTeamId: 130,
  season: 2026,
  matchupContext: "Michigan's Week 1 opponent · Sept. 5 · Michigan Stadium",
  record: "2025: 10-4 · MAC Champion · Myrtle Beach Bowl winner",
  overview: [
    "The repository's FBS-only model sample is 9-4 over 13 games (Rhode Island FCS game excluded).",
    "2025 identity: extremely run-oriented offense (65.1% rush decision rate, 42.85 rush attempts/game) carried by a defense that finished #34 nationally on our validated-five composite, well ahead of the #100 offense.",
    "2026 continuity: ESPN has WMU returning 51% overall production. CBS has 43% of snaps returning. Our own official-roster audit finds 51 of 104 players (49.0%) are back from 2025.",
    "Where continuity lives: the offensive backfield/WR core is stable (89% QB snaps, 70% RB, 61% WR returning per CBS); TE (2%) and the defensive front seven (20% DL, 12% LB) are being rebuilt.",
    "Staff: Lance Taylor (HC, Year 4) and Walt Bell (OC) both return. Greer Martini was promoted from LBs coach to DC after Chris O'Leary left for the LA Chargers; Duane Vaughn joined as co-DC/OLBs.",
  ],
  sections: [
    {
      id: "how-to-read",
      title: "How to read this page",
      intro: [
        "Every stat below comes in two flavors: \"raw\" and \"opponent-adjusted.\" Raw is just what actually happened on the field. Adjusted accounts for who they played — beating up on a bad team counts for less, and playing well against a great team counts for more. The model looks at every FBS team's full schedule at once, figures out how good each opponent really was, and slides each team's raw numbers up or down accordingly. That's why a team's adjusted numbers can look different from the box score — it's not a different stat, it's the same stat corrected for schedule strength.",
        "National rank is out of 136 FBS teams. #1 is the best in that stat nationally, #136 is the worst.",
        "Quick glossary for the terms used throughout — everything below is defined once here so the tables can stay clean.",
      ],
      tables: [
        {
          columns: ["Term", "What it means"],
          rows: [
            ["Success rate", "A play \"stays on schedule\" if it gains enough yards to keep the offense ahead of the chains — about half the needed yards on 1st down, 70% on 2nd, and the full distance on 3rd or 4th. Success rate is just the share of plays that do that."],
            ["Explosive play", "A run of 10+ yards or a pass of 20+ yards — a chunk gain, not just incremental yardage."],
            ["Havoc rate", "How often the defense blows up a play before it develops — a tackle for loss, a sack, or forcing a turnover."],
            ["Rush decision rate", "Run plays as a share of every called run-or-pass decision, where a sack still counts as a \"pass decision.\" Cleaner than \"run-play percentage\" because it isn't skewed by how often the QB got sacked."],
            ["PPA (Predicted Points Added)", "A per-play scoring-value number from our outside data provider (CFBD), not something we calculate ourselves. It credits a player or play for how much closer it got the team to scoring, so a game-changing catch and a 3-yard checkdown don't just get lumped together as \"receptions.\""],
            ["Performance over expectation (POE)", "For one specific game, we hide that game from the model, let it predict how the team should have performed based on everything else both teams did that season, then compare the real result to that prediction. Positive = they beat their own expectation. Negative = they underperformed it."],
            ["Composite rating", "We turn a team's national rank on each of the five core adjusted stats into a percentile, then average those — separately for offense and defense, then average those two for one overall grade."],
            ["Validated vs. research-only", "\"Validated\" stats are the five we've stress-tested over time and trust as headline evidence. \"Research-only\" stats use the same model but haven't been checked the same way yet — good supporting color, not something to hang a strong claim on by itself."],
          ],
        },
      ],
    },
    {
      id: "quick-numbers",
      title: "Quick numbers for the video",
      intro: ["The fastest version of this report. Everything here is repeated with full context further down the page."],
      tables: [
        {
          caption: "Team / roster",
          columns: ["Metric", "Value"],
          rows: [
            ["2025 record", "10-4"],
            ["2025 result", "MAC Champion + Myrtle Beach Bowl winner"],
            ["ESPN returning production", "51% overall / 60% offense / 42% defense"],
            ["CBS returning snaps", "43% overall / 52% offense / 33% defense"],
            ["Official-roster audit", "51 of 104 players return (49.0%)"],
            ["College-experience newcomers", "30 (11 offense / 17 defense)"],
          ],
        },
        {
          caption: "2025 play calling",
          columns: ["Metric", "Value"],
          rows: [
            ["Rush decision rate", "65.1%"],
            ["Dropback rate", "34.9%"],
            ["Rush attempts/game", "42.85"],
            ["Dropbacks/game", "23.00"],
          ],
        },
        {
          caption: "2025 opponent-adjusted offense (validated)",
          columns: ["Metric", "Value", "Rank"],
          rows: [
            ["Success rate", "40.3%", "#95"],
            ["Rush success", "42.7%", "#65"],
            ["Pass success", "38.3%", "#118"],
            ["Explosive rate", "10.9%", "#80"],
            ["Yards/play", "4.91", "#119"],
            ["Offense composite", "30.1/100", "#100"],
          ],
        },
        {
          caption: "2025 opponent-adjusted defense (validated)",
          columns: ["Metric", "Value", "Rank"],
          rows: [
            ["Success rate allowed", "39.8%", "#35"],
            ["Rush success allowed", "41.1%", "#43"],
            ["Pass success allowed", "38.4%", "#23"],
            ["Explosive rate allowed", "10.9%", "#52"],
            ["Yards/play allowed", "5.57", "#52"],
            ["Defense composite", "70.4/100", "#34"],
          ],
        },
      ],
    },
    {
      id: "staff",
      title: "2026 staff",
      tables: [
        {
          columns: ["Role", "Name", "Note"],
          rows: [
            ["Head coach", "Lance Taylor", "Year 4. 2025 MAC Coach of the Year. Extended through 2030 after the title."],
            ["Offensive coordinator", "Walt Bell", "Year 3 running the offense. Was with QB Broc Lowry at Indiana before both landed at WMU."],
            ["Defensive coordinator", "Greer Martini", "Promoted Feb. 11, 2026 from 2025 LBs coach. Replaces Chris O'Leary (now LA Chargers DC)."],
            ["Co-DC / OLBs", "Duane Vaughn", "Added Mar. 27, 2026. 13 seasons at Furman, 5 as DC."],
          ],
        },
      ],
      bullets: [
        "Darren shorthand: \"New defensive playcaller, but not a clean-sheet install — Martini coached in the 2025 system, and Vaughn adds experienced DC support.\"",
        "O'Leary's 2025 WMU defense allowed 17.4 points/game (#9 FBS) and 305.5 yards/game (#19 FBS), per the Chargers' own announcement.",
      ],
    },
    {
      id: "continuity",
      title: "Returning production & roster continuity",
      intro: ["Three different methodologies answer three different questions — keep the labels attached to their numbers, don't blend them."],
      tables: [
        {
          caption: "Overall continuity by source",
          columns: ["Source", "Overall", "Offense", "Defense"],
          rows: [
            ["ESPN returning production (Bill Connelly)", "51% — #71", "60% — #48", "42% — #103"],
            ["CBS returning snaps (Aug. 22, 2026)", "43% — #55", "52% — #31", "33% — #94"],
            ["Our audited roster headcount", "49.0% (51/104)", "56.2% (27/48)", "42.9% (21/49)"],
          ],
        },
        {
          caption: "CBS returning snaps by position group",
          columns: ["Offense", "Returning", "Defense", "Returning"],
          rows: [
            ["QB", "89%", "DL", "20%"],
            ["RB", "70%", "LB", "12%"],
            ["WR", "61%", "DB", "55%"],
            ["TE", "2%", "", ""],
            ["OL", "52%", "", ""],
          ],
        },
        {
          caption: "Our audited roster breakdown",
          columns: ["Group", "Count", "Share"],
          rows: [
            ["Total current players", "104", "—"],
            ["Returned from 2025 roster", "51", "49.0%"],
            ["College-experience newcomers", "30", "28.8%"],
            ["First-time college newcomers", "22", "21.2%"],
            ["Rejoining after missing 2025", "1", "1.0%"],
            ["Upperclassmen", "45", "43.3%"],
            ["Seniors / graduate players", "24", "23.1%"],
          ],
        },
        {
          caption: "Player-PPA retention (garbage time excluded, matched to the 2026 roster)",
          columns: ["Metric", "Retained"],
          rows: [
            ["Overall signed player PPA", "79.6%"],
            ["Positive player PPA", "72.1%"],
            ["Positive QB passing PPA", "100.0%"],
            ["Positive rushing PPA", "95.9%"],
            ["Positive non-QB pass-play PPA", "38.8%"],
          ],
        },
      ],
      bullets: [
        "Plain-English read: the quarterback/rushing engine is largely intact, but a large amount of receiver/TE pass-game value has to be replaced.",
      ],
    },
    {
      id: "transfers",
      title: "Incoming roster movement",
      intro: [
        "WMU officially announced 21 transfers on Feb. 9, 2026: 12 defense, 8 offense, 1 special teams — 10 with Power-conference experience, 6 from FCS programs.",
        "Our broader \"30 college-experience newcomers\" figure also includes JUCO/other college additions outside that specific announcement — don't call all 30 \"portal transfers.\"",
      ],
      tables: [
        {
          caption: "Notable defensive additions",
          columns: ["Player", "Position", "Previous school", "2025 line"],
          rows: [
            ["DeJuan Echoles Jr.", "DE", "Ball State", "28 tackles, 3 sacks in 10 games"],
            ["Scoop Gardner Jr.", "DE", "Long Island", "52 tackles, 14.5 TFL, 7 sacks"],
            ["Austin Alexander", "DE", "North Carolina", "10 games as a freshman; former 4-star recruit"],
            ["Ahmed Tounkara", "DT", "Ohio State", "Two seasons at Ohio State"],
            ["Zavian Tibbs", "DT", "Houston", "Prior JUCO + Houston experience"],
            ["Daeh McCullough / Tahj Owens / Kouri Crump / Willard Ferrell", "DB", "—", "Additional secondary depth"],
          ],
        },
        {
          caption: "Notable offensive additions",
          columns: ["Player", "Position", "Previous school", "2025 line"],
          rows: [
            ["AJ Green Jr.", "RB", "Arkansas", "962 career rushing yards at Arkansas"],
            ["Nate Levicki", "TE", "Presbyterian", "34 catches, 471 yards, 6 TD"],
            ["Adam Parks", "TE", "New Mexico State", "Physical blocking tight end"],
            ["Emazon Littlejohn", "WR", "South Carolina", "—"],
            ["Trey Petty", "QB", "Illinois", "Experienced QB depth"],
            ["Ben Roebuck", "OL", "Michigan", "—"],
            ["Brandon Smith", "OL", "Illinois State", "—"],
          ],
        },
      ],
      bullets: [
        "Roster thesis: WMU did not try to replace its departed front seven with freshmen — it imported older bodies and prior-college experience (8 of 20 DL and 4 of 10 LB are college-experience newcomers).",
        "TE additions matter because CBS has WMU returning only 2% of 2025 TE snaps.",
      ],
    },
    {
      id: "personnel",
      title: "Key returning offensive personnel",
      tables: [
        {
          columns: ["Player", "Pos", "2025 line", "PPA note"],
          rows: [
            ["Broc Lowry", "QB", "1,803 pass yds / 9 pass TD · 963 rush yds / 14 rush TD", "84.35 total PPA — 71.5% of returning signed player PPA. MAC Offensive Player of the Year."],
            ["Jalen Buckley", "RB", "Primary established RB · 2026 Maxwell Award watch list", "6.00 total PPA, incl. 9.34 rushing PPA"],
            ["Baylin Brooks", "WR", "—", "19.90 returning total PPA"],
            ["Aveion Chenault", "WR", "—", "11.64 returning total PPA"],
          ],
        },
        {
          caption: "Notable 2025 pass-game production that did NOT return",
          columns: ["Player", "Pos", "PPA lost"],
          rows: [
            ["Tailique Williams", "WR", "17.76"],
            ["Blake Bosma", "TE", "11.28"],
            ["Michael Brescia", "TE", "9.49"],
            ["Christian Leary", "WR", "5.19"],
          ],
        },
      ],
      bullets: [
        "Offensive line: CBS has 52% of OL snaps returning; our audit shows 11 of 18 OL were on the 2025 roster (Hunter Whitenack, Gavin Dabo, Chad Schuster among returners).",
        "This is why the PPA story splits cleanly: QB/rush continuity is excellent (100% / 95.9%), non-QB pass-play continuity is only 38.8%.",
      ],
    },
    {
      id: "offense-scheme",
      title: "Offensive identity: run-heavy, QB-run-centered",
      intro: [
        "Lowry rushed for 963 yards and 14 TD in 2025 — the most rushing yards by a WMU quarterback in program history. Bell has said the staff will make \"small evolutions\" to fit Lowry and the line, not wholesale changes.",
        "Don't oversell the passing game: the value came from the run-heavy identity and Lowry's legs, not efficient dropback offense.",
      ],
      tables: [
        {
          caption: "2025 play-calling tendency (WMU vs. Michigan for context)",
          columns: ["Metric", "Western Michigan", "Michigan"],
          rows: [
            ["Rush decision rate", "65.1%", "57.1%"],
            ["Dropback rate", "34.9%", "42.9%"],
            ["Rush attempts/game", "42.85", "36.15"],
            ["Dropbacks/game", "23.00", "27.15"],
            ["Offensive plays/game", "62.85", "63.23"],
            ["Possessions/game", "10.69", "11.23"],
          ],
        },
        {
          caption: "2025 opponent-adjusted offense",
          columns: ["Metric", "Value", "Rank", "Tier"],
          rows: [
            ["Success rate", "40.3%", "#95/136", "validated"],
            ["Rush success", "42.7%", "#65/136", "validated"],
            ["Pass success", "38.3%", "#118/136", "validated"],
            ["Explosive-play rate", "10.9%", "#80/136", "validated"],
            ["Yards/play", "4.91", "#119/136", "validated"],
            ["Rush explosive rate", "12.8%", "#84/136", "research-only"],
            ["Pass explosive rate", "8.5%", "#112/136", "research-only"],
            ["Rush YPA", "4.78", "#78/136", "research-only"],
            ["Net pass yards/dropback", "5.22", "#126/136", "research-only"],
            ["Passing-down success", "26.6%", "#126/136", "research-only"],
          ],
        },
      ],
    },
    {
      id: "defense-scheme",
      title: "Defensive identity: same foundation, new playcaller",
      intro: [
        "Not a clean-sheet defensive rebuild scheme-wise — Martini coached LBs in the 2025 system, and players have described 2026 as \"different person, same scheme.\"",
        "But the exact 2025 personnel is not intact: only 21 of 49 defensive roster players return, and 17 defensive players on the current roster are college-experience newcomers. The secondary has the most continuity; the front seven is the rebuild.",
      ],
      tables: [
        {
          caption: "2025 opponent-adjusted defense",
          columns: ["Metric", "Value", "Rank", "Tier"],
          rows: [
            ["Success rate allowed", "39.8%", "#35/136", "validated"],
            ["Rush success allowed", "41.1%", "#43/136", "validated"],
            ["Pass success allowed", "38.4%", "#23/136", "validated"],
            ["Explosive-play rate allowed", "10.9%", "#52/136", "validated"],
            ["Yards/play allowed", "5.57", "#52/136", "validated"],
            ["Pass explosive rate allowed", "8.3%", "#13/136", "research-only"],
            ["Net pass yards/dropback allowed", "5.66", "#28/136", "research-only"],
            ["Third-down conversion allowed", "37.2%", "#11/136", "research-only"],
            ["Rush explosive rate allowed", "13.8%", "#83/136", "research-only"],
            ["Rush YPA allowed", "5.38", "#107/136", "research-only"],
          ],
        },
      ],
    },
    {
      id: "raw-numbers",
      title: "2025 raw season numbers",
      intro: ["Un-adjusted for schedule. Useful for plain box-score talking points; use the adjusted tables above for strength claims."],
      tables: [
        {
          caption: "Offense — tendency & volume",
          columns: ["Metric", "Value"],
          rows: [
            ["Points/game", "23.15"],
            ["Plays/game", "62.85"],
            ["Possessions/game", "10.69"],
            ["Rush attempts/game", "42.85"],
            ["Dropbacks/game", "23.00"],
            ["Third-down conversion", "39.9%"],
            ["Sack rate allowed", "6.4%"],
            ["Havoc rate allowed", "8.8%"],
          ],
        },
        {
          caption: "Offense — efficiency (raw vs. opponent-adjusted)",
          columns: ["Metric", "Raw", "Adjusted", "Rank"],
          rows: [
            ["Success rate", "42.5%", "40.3%", "#95"],
            ["Rush success", "45.1%", "42.7%", "#65"],
            ["Pass success", "37.5%", "38.3%", "#118"],
            ["Yards/play", "5.18", "4.91", "#119"],
          ],
        },
        {
          caption: "Defense — tendency & volume",
          columns: ["Metric", "Value"],
          rows: [
            ["Points allowed/game", "17.62"],
            ["Defensive plays/game", "61.00"],
            ["Third-down conversion allowed", "32.9%"],
            ["Sack rate generated", "7.9%"],
            ["Havoc rate generated", "10.1%"],
          ],
        },
        {
          caption: "Defense — efficiency (raw vs. opponent-adjusted)",
          columns: ["Metric", "Raw", "Adjusted", "Rank"],
          rows: [
            ["Success rate allowed", "38.1%", "39.8%", "#35"],
            ["Rush success allowed", "40.0%", "41.1%", "#43"],
            ["Pass success allowed", "36.1%", "38.4%", "#23"],
            ["Yards/play allowed", "5.30", "5.57", "#52"],
          ],
        },
      ],
      bullets: [
        "Interpretation: schedule adjustment doesn't rescue the offense — it stayed a bottom-quarter-ish efficiency unit, run game clearly stronger than pass game.",
        "Interpretation: the defense was legitimately good after adjustment, especially suppressing pass success — but rush explosiveness/rush YPA were much less impressive in the research-only layer.",
      ],
    },
    {
      id: "game-by-game",
      title: "Game-by-game: better or worse than expected",
      intro: [
        "Positive = performed better than expected after accounting for opponent and venue (see \"Performance over expectation\" above). The target game itself is hidden from the model before that game's expectation is calculated.",
        "The first three FBS games (Michigan State, North Texas, Illinois) were genuinely bad offensive performances — the season average includes an offense that looked different before Lowry became the clear starter. Toledo (14-13) is the cleanest statistical turning point.",
      ],
      tables: [
        {
          caption: "Full schedule with opponent strength + performance vs. expectation",
          columns: ["Wk", "Opponent", "Site", "Score", "Opp rank", "Off success (vs. exp.)", "Off yards/play (vs. exp.)", "Def success (vs. exp.)", "Def yards/play (vs. exp.)"],
          rows: [
            ["1", "Michigan State", "A", "L 6-23", "#76", "-18.3%", "-2.44", "-9.3%", "-0.11"],
            ["2", "North Texas", "H", "L 30-33", "#29", "-8.4%", "-1.60", "+3.0%", "+0.55"],
            ["3", "Illinois", "A", "L 0-38", "#38", "-15.5%", "-0.72", "-10.0%", "+0.14"],
            ["4", "Toledo", "H", "W 14-13", "#16", "+3.5%", "+0.21", "+9.1%", "+2.11"],
            ["6", "Massachusetts", "A", "W 21-3", "#136", "+2.4%", "-0.36", "-1.9%", "-0.44"],
            ["7", "Ball State", "H", "W 42-0", "#135", "+8.5%", "+0.73", "+14.0%", "+1.91"],
            ["9", "Miami (OH)", "A", "L 17-26", "#88", "+2.9%", "+0.06", "-5.5%", "-1.69"],
            ["10", "Central Michigan", "H", "W 24-21", "#111", "+1.9%", "-0.31", "0.0%", "-0.83"],
            ["12", "Ohio", "H", "W 17-13", "#77", "+1.0%", "+0.48", "+0.1%", "+0.30"],
            ["13", "Northern Illinois", "A", "W 35-19", "#131", "+19.4%", "+0.83", "+7.4%", "-0.19"],
            ["14", "Eastern Michigan", "A", "W 31-21", "#101", "+0.7%", "+0.03", "-5.6%", "-2.56"],
            ["15", "Miami (OH) — MAC Champ.", "N", "W 23-13", "#88", "-10.3%", "+1.08", "+9.4%", "+1.02"],
            ["Bowl", "Kennesaw State — Myrtle Beach", "N", "W 41-6", "#73", "+5.0%", "+1.57", "-2.3%", "-0.32"],
          ],
        },
      ],
      bullets: [
        "Run game produced the biggest late-season spikes: +14.9 pp rush-success POE at Miami (OH) in the regular season, +24.2 pp at Northern Illinois — both alongside negative pass-success POE, reinforcing the run-first identity.",
        "MAC Championship vs. Miami (OH): the title-game defense beat expectation across every validated measure (success +9.4 pp, rush success +13.6 pp, pass success +7.2 pp, explosive +4.7 pp, YPP +1.02), while the offense won differently than its normal run-first profile (rush success -17.5 pp, pass success +11.2 pp).",
      ],
    },
    {
      id: "michigan-comparison",
      title: "2025 baseline comparison to Michigan",
      intro: ["Historical 2025 baseline only — not a claim that 2026 Michigan (new staff) reproduces this profile."],
      tables: [
        {
          caption: "Offense",
          columns: ["Metric", "WMU adjusted", "Rank", "Michigan adjusted", "Rank"],
          rows: [
            ["Success rate", "40.3%", "#95", "46.8%", "#19"],
            ["Rush success", "42.7%", "#65", "49.0%", "#4"],
            ["Pass success", "38.3%", "#118", "42.0%", "#54"],
            ["Explosive rate", "10.9%", "#80", "13.0%", "#19"],
            ["Yards/play", "4.91", "#119", "6.55", "#21"],
          ],
        },
        {
          caption: "Defense",
          columns: ["Metric", "WMU adjusted", "Rank", "Michigan adjusted", "Rank"],
          rows: [
            ["Success allowed", "39.8%", "#35", "41.8%", "#58"],
            ["Rush success allowed", "41.1%", "#43", "41.3%", "#47"],
            ["Pass success allowed", "38.4%", "#23", "42.8%", "#79"],
            ["Explosive rate allowed", "10.9%", "#52", "9.9%", "#22"],
            ["Yards/play allowed", "5.57", "#52", "4.83", "#18"],
          ],
        },
        {
          caption: "Validated-five composite (rating / national rank)",
          columns: ["Team", "Offense", "Defense", "Overall"],
          rows: [
            ["Western Michigan", "30.1/100 — #100", "70.4/100 — #34", "50.2/100 — #67"],
            ["Michigan", "83.4/100 — #19", "67.6/100 — #38", "75.5/100 — #19"],
          ],
        },
      ],
      bullets: [
        "Overall, Michigan rates 25.3 rating points and 48 spots ahead of WMU (#19 vs. #67) — driven almost entirely by the offense gap, not the defense.",
        "Don't simplify the defense composite into \"WMU had a better defense than Michigan.\" WMU rated better in success suppression (especially pass); Michigan rated substantially better in YPP and explosiveness prevention.",
      ],
    },
    {
      id: "matchup-angles",
      title: "Matchup angles for the video",
      intro: ["Based on 2025 statistical strengths plus 2026 roster continuity — not a score prediction. Ranks are out of 136 FBS teams."],
      tables: [
        {
          caption: "When Western Michigan has the ball (WMU offense vs. Michigan defense)",
          columns: ["Metric", "WMU offense", "Rank", "Michigan defense", "Rank"],
          rows: [
            ["Success rate", "40.3%", "#95", "41.8%", "#58"],
            ["Rush success", "42.7%", "#65", "41.3%", "#47"],
            ["Pass success", "38.3%", "#118", "42.8%", "#79"],
            ["Explosive rate", "10.9%", "#80", "9.9%", "#22"],
            ["Yards/play", "4.91", "#119", "4.83", "#18"],
          ],
        },
        {
          caption: "When Michigan has the ball (Michigan offense vs. WMU defense)",
          columns: ["Metric", "Michigan offense", "Rank", "WMU defense", "Rank"],
          rows: [
            ["Success rate", "46.8%", "#19", "39.8%", "#35"],
            ["Rush success", "49.0%", "#4", "41.1%", "#43"],
            ["Pass success", "42.0%", "#54", "38.4%", "#23"],
            ["Explosive rate", "13.0%", "#19", "10.9%", "#52"],
            ["Yards/play", "6.55", "#21", "5.57", "#52"],
          ],
        },
      ],
      bullets: [
        "1. Force WMU to win through the air. Adjusted rush success #65 vs. adjusted pass success #118 (net pass yards/dropback #126, research-only). Control Lowry's designed/option run value and Buckley, then make WMU sustain drives through conventional dropback passing.",
        "2. The one metric where WMU's defense doesn't trail Michigan: pass success. WMU's pass defense ranks #23; Michigan's own passing offense ranks only #54. It's the single closest matchup cell in either table above — if Michigan is forced into obvious passing downs, this is Western's best individual answer, not just a fallback plan.",
        "3. WMU's defense is more trustworthy on the back end (DB 55% snaps returning, pass defense #23 adjusted) than in the rebuilt front seven (DL 20% / LB 12% returning; rush YPA defense #107, rush explosive defense #83, both research-only). The ground game is the most natural way to test whether 2026 reproduces 2025 results.",
        "4. Lowry is the whole offense by a huge margin: reigning MAC Offensive Player of the Year, 963 rush yds/14 rush TD, 84.35 total PPA, 71.5% of returning signed player PPA. Making him inefficient as a runner attacks the central mechanism, not just one skill position.",
        "5. Don't assume the 2025 defense simply carries over. Scheme foundation carries over; personnel does not — ESPN defense returning production 42% (#103), CBS defensive snaps 33% (#94), 17 defensive college-experience newcomers. Call it \"reloaded inside the same system,\" not \"the same defense.\"",
      ],
    },
    {
      id: "names",
      title: "Personnel names to know",
      tables: [
        {
          columns: ["Side", "Names"],
          rows: [
            ["Offense", "Broc Lowry (QB), Jalen Buckley (RB), Baylin Brooks / Aveion Chenault (WR); TE newcomers Nate Levicki / Adam Parks; OL additions Ben Roebuck / Brandon Smith"],
            ["Defense", "Returning DB core has the most continuity; front-seven transfer names: DeJuan Echoles Jr., Scoop Gardner Jr., Austin Alexander, Ahmed Tounkara, Zavian Tibbs"],
          ],
        },
      ],
    },
  ],
  guardrails: [
    "Say \"rush decision rate,\" not official run-play percentage. The denominator is rush attempts + dropbacks, and dropbacks include sacks.",
    "Don't call the 30 college-experience newcomers \"30 portal transfers.\" The official February transfer class is 21; 30 is our broader roster classification of newcomers with prior college experience.",
    "Don't call 51/104 \"returning production.\" It's roster headcount continuity.",
    "ESPN, CBS and our roster audit answer different questions — keep the labels attached to their numbers.",
    "2025 Michigan comparisons are historical baselines only. Michigan's 2026 staff/scheme is different.",
  ],
  sources: [
    { label: "WMU 2026 coaching staff", url: "https://wmubroncos.com/sports/football/coaches" },
    { label: "Greer Martini promoted to DC (Feb. 11, 2026)", url: "https://wmubroncos.com/news/2026/2/11/greer-martini-promoted-to-defensive-coordinator.aspx" },
    { label: "WMU staff additions / Duane Vaughn (Mar. 27, 2026)", url: "https://wmubroncos.com/news/2026/3/27/football-announces-staff-additions.aspx" },
    { label: "Chris O'Leary to Chargers + 2025 defense national stats", url: "https://www.chargers.com/news/agree-to-terms-chris-oleary-defensive-coordinator-2026" },
    { label: "Walt Bell bio", url: "https://wmubroncos.com/sports/football/roster/coaches/walt-bell/4870" },
    { label: "Lowry / Bell 2025 offensive-system comments", url: "https://wmubroncos.com/news/2025/9/27/lowry-takes-the-reins-to-the-wmu-offense.aspx" },
    { label: "Lance Taylor contract extension", url: "https://wmubroncos.com/news/2025/12/8/western-michigan-university-extends-contract-of-head-football-coach-lance-taylor.aspx" },
    { label: "21-transfer announcement (Feb. 9, 2026)", url: "https://wmubroncos.com/news/2026/2/9/football-welcomes-21-transfers-to-the-bronco-brotherhood.aspx" },
    { label: "2026 official roster", url: "https://wmubroncos.com/sports/football/roster/2026" },
    { label: "ESPN 2026 returning production (Bill Connelly, Mar. 23, 2026)", url: "https://www.espn.com/college-football/story/_/id/48259759/college-football-returning-production-2026-notre-dame-texas" },
    { label: "CBS 2026 returning snaps (Aug. 22, 2026)", url: "https://www.cbssports.com/college-football/news/college-football-returning-snap-percentages-2026/" },
    { label: "Martini continuity/scheme interview", url: "https://mitten-football.ghost.io/how-greer-martini-is-shaping-western-michigan-broncos-defense-different-person-same-scheme/" },
    { label: "2025 MAC awards sweep", url: "https://wmubroncos.com/news/2025/12/4/football-broncos-sweep-major-mac-awards-earn-7-all-mac-selections.aspx" },
    { label: "2026 Maxwell watch list (Lowry/Buckley)", url: "https://wmubroncos.com/news/2026/8/3/football-lowry-and-buckley-named-to-maxwell-award-watch-list.aspx" },
  ],
};

const SCOUTING_REPORTS: ScoutingReport[] = [westernMichigan2026];

export function getAllScoutingReports(): ScoutingReport[] {
  return SCOUTING_REPORTS;
}

export function findScoutingReport(slug: string): ScoutingReport | null {
  return SCOUTING_REPORTS.find((r) => r.slug === slug) ?? null;
}
