# Do Weeks 1–2 mislead?

Across 11 completed seasons (2014–2019, 2021–2025), early efficiency contains moderate signal, but situational rates are much less stable. The main cohort contains 1,399 eligible team-seasons; 1,438 team-seasons were screened. FBS-versus-FBS regular-season games only. Early and later opponent-adjusted models are fit separately; later means source Week 3 onward.

| Opponent-adjusted net metric | Week 1 correlation | Week 2 correlation | Weeks 1–2 correlation |
|---|---:|---:|---:|
| yardsPerPlay | 0.437 | 0.419 | 0.508 |
| pointsPerResolvedPossession | 0.428 | 0.424 | 0.493 |
| successRate | 0.409 | 0.414 | 0.487 |
| passSuccessRate | 0.331 | 0.320 | 0.395 |
| explosivePlayRate | 0.314 | 0.334 | 0.385 |
| rushSuccessRate | 0.305 | 0.301 | 0.359 |
| pointsPerOpportunity | 0.246 | 0.243 | 0.282 |
| havocRateAllowed | 0.258 | 0.210 | 0.270 |
| thirdDownConversionRate | 0.240 | 0.189 | 0.225 |
| sackRate | 0.210 | 0.146 | 0.192 |
| redZonePossessionTouchdownRate | 0.098 | 0.123 | 0.129 |

These are Spearman rank correlations, not accuracy percentages. Net combines offense and defense. Week-specific cohorts differ, so differences across columns are descriptive rather than a matched estimate of the value of adding a game.

For net success rate, 33.2% switch halves, median movement is 18.5 percentile points, and only 47.6% of early top-quartile teams remain top-quartile. Another 24.6% of the early top quartile fall below the later median. Year-specific correlations range from 0.370 to 0.563.

Raw early net success rate correlates 0.510 with later adjusted net success rate, compared with 0.487 for early adjusted net success rate. Raw early net yards per play scores 0.520 versus 0.508 adjusted. This does not establish that opponent adjustment is generally harmful; the early-only graph and untuned research shrinkage have little evidence to work with.

In the subset with exactly two eligible early games (583 team-seasons), net success-rate percentile correlation is 0.561. This subset has different schedule selection and does not isolate the causal value of a second game.

The 2025 all-team table covers 136 FBS teams, with 135 eligible estimates. Example success-rate percentile reversals: Michigan 20→89, Ohio State 16→100, Maryland 69→9, Rice 77→5. Percentiles rank eligible teams in this research metric, not overall football power. Sparse early opponent knowledge can itself cause reversals.

Coverage caveat: 798 main-cohort team-seasons have one eligible early FBS game, 583 have two, and 18 have three because some opening-week games share source Week 1 labels. Explicit Week 0 labels, FCS games and postseason are excluded. These are not uniformly first-two-game samples.

Validation: all 484 metric/window/season fits converged; early/later game-ID disjointness asserted for every season; output uniqueness, sample eligibility and 1,438-team-season coverage checked; existing schedule-adjustment tests: 9 passed.

Methodology: `docs/EARLY_SEASON_SIGNAL_RESEARCH.md`. Full metric and team results: `results.json`. Latest complete season: `all-teams-2025.md`.
