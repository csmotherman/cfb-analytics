# 2026 CFP Season Simulator Research

**Status:** EXPLORATORY -- isolated research track, not promoted, not wired into any production pipeline.
**Code:** `src/cfb_analytics/analytics/preseason_power/{conference_structure,season_schedule_2026,resume_scoring,standings,season_simulator_2026,validate_field_selection}.py`
**Outputs:** `data/research/preseason_power/season_2026_full_simulation_team_summary.csv`, `season_2026_simulation_methodology.json`
**Tests:** `tests/analytics/test_season_simulator_2026.py`

This extends the preseason power rating research (`PRESEASON_POWER_RATING_RESEARCH.md`) from "predict Week 1" to "simulate the entire 2026 regular season and CFP field," closing the gap the repo's own product contract (`PREDICTION_2026_PRODUCT_CONTRACT.md`) lists as required before publishing 2026 CFP odds: calibrated game probabilities for every week (not just Week 1), a complete national schedule, conference standings/AQ selection, and a predictive committee/resume model.

## Method

For each of `n_sims` Monte Carlo trials:

1. Every scheduled FBS-vs-FBS 2026 regular-season game (`season_schedule_2026.py`) is drawn once, using the SAME predicted margin as the Week 1 model (recommended preseason power + recruiting + QB continuity + home field, held constant for the whole season -- no in-season updating, same explicit design choice as `season_2026.py`) and one shared residual per game from the validated empirical residual pool, so a trial's game outcomes are internally consistent (if Ohio State beats Michigan in a trial, both teams' records reflect that same result).
2. Conference standings are computed from conference-only records, with a documented, simplified tiebreak chain: conference win% -> head-to-head (only when exactly two teams are tied and played each other) -> overall win% -> a seeded coin flip (`standings.py`). Real per-conference tiebreakers are far more granular (common opponents, etc.) and are not replicated.
3. Each conference's top 2 play one simulated, synthesized, neutral-site championship game (not read from schedule data, since the schedule pull doesn't yet cover championship week -- see Data coverage below).
4. Every team's simulated regular-season resume (win%, strength of schedule, quality wins, scoring margin, conference-champion flag) is scored by the SAME resume model as `historical_cfp_selection.py` (imported, not modified -- that file is retrospective-only by design and stays that way), fit once on all real CFP-era seasons and reused across every trial.
5. The 2026 CFP AQ rule is applied and the field is seeded (`standings.apply_aq_and_seed`).

Aggregated across trials, this produces each team's empirical probability of making the 12-team field, winning its conference, and earning a top-4 bye -- an actual distribution, not a single point projection.

## The AQ rule matters, and it changed for 2026

Confirmed live (Sept 2026): the AQ rule that will govern the actual 2026 field is **not** the same rule used in 2024 or 2025.

- **2024-2025 (real, completed seasons):** all conference champions were pooled and ranked by the committee; only the top 5 by rank auto-qualified. This could -- and once did -- shut out a Power-conference champion entirely: Duke won the 2025 ACC championship at 8-5 and was left out of the 12-team field because 5 other conference champions outranked it ([abc11.com](https://abc11.com/post/college-football-playoff-2025-acc-champion-duke-left-off-12-team-bracket/18261044/), [Yahoo Sports](https://sports.yahoo.com/college-football/breaking-news/article/heres-why-duke-didnt-make-the-college-football-playoff-after-winning-the-acc-title-182059864.html)).
- **2026 (the season this simulator targets):** the rule was changed specifically in response to that outcome. The ACC, Big Ten, Big 12, and SEC champions are now GUARANTEED an automatic bid regardless of rank; only the 5th AQ slot (highest-ranked champion among the other six conferences) is rank-contested ([Yahoo Sports](https://sports.yahoo.com/articles/college-football-playoff-format-slightly-090000081.html), [SI.com](https://www.si.com/college/boise-state/football/college-football-playoff-changes-format-for-group-of-six-representation)). Seeding is separately by rank regardless of championship status, unchanged from the May 2025 seeding revision. Notre Dame carries a special provision (automatic bid if ranked top 12) that is not separately implemented, since ranking Notre Dame in the ordinary at-large pool already produces the same outcome under this simulator's ranking-based selection.

`standings.apply_aq_and_seed(..., season=)` implements both rules, selected by season, so the same code validates against real pre-2026 seasons and simulates the actual 2026 rule.

## Validation (`validate_field_selection.py`)

The AQ + seeding + resume-ranking machinery was checked against the real, completed 2024 and 2025 seasons (using the pre-2026 pooled-top-5 rule, ground-truth conference champions, and the real 12-team fields) -- this isolates bugs in the field-selection RULE from noise in either the rating model or the conference-standings simulation.

| season | field-size match | teams matched (of 12) | missed by model | false positives |
|---|---|---|---|---|
| 2024 | yes | 10 | SMU, Tennessee | Alabama, Army |
| 2025 | yes | 9 | Alabama, Miami, Texas A&M | BYU, Boise State, Notre Dame |

The resume model here is fit on all historical seasons INCLUDING the one being scored (not leave-one-out), so this checks selection *machinery*, not out-of-sample predictive accuracy -- that's already validated in `HISTORICAL_CFP_SELECTION_MODEL.md`'s leave-one-season-out evaluation (86.7% top-field accuracy, pure ranking, no AQ rule applied). The 75-83% machinery-check accuracy here is in the same range and expected to run slightly below the pure-ranking number, since applying the real AQ rule can seat a conference champion whose resume score alone wouldn't have ranked them in the top 12 (exactly the dynamic that produced the Duke exception in the first place). The 2026 rule itself cannot be historically validated the same way -- no completed season has used it yet.

## Data coverage

The 2026 schedule pull (`data/raw/cfbd/season=2026/season_type=regular/week=NN/games.json`) was refreshed (2026-09-03) after the initial 2026-08-27 pull. Weeks 14-15 -- rivalry week and every real conference championship game -- are still empty after the refresh: CFBD's own calendar (`cfb-raw calendar --season 2026`) confirms 15 regular-season weeks exist, so this is a genuine current gap in CFBD's own published schedule, not a stale local cache. This simulator does not depend on that data for championship games (synthesized instead, see Method) -- but per-team schedule coverage in the current pull is 10-12 of an expected 12 games (`schedule_coverage` in the methodology output), so some late-season/rivalry games are still missing from a handful of teams' simulated resumes. A future refresh (closer to conference championship weekend) is the natural way to close this gap.

The refresh did surface one thing worth incorporating: the 2026 season had already started (Week 1 ran Aug 29 - Sept 7), and 8 Week 1 games were complete by the Sept 3 refresh. `season_schedule_2026.py` now carries each game's `completed`/`actual_margin` fields, and `season_simulator_2026.py` holds those games fixed at their real result in every trial instead of simulating them (6 of the 8 involve two rated FBS teams and are covered; the other 2 involve a team outside the simulation's rated universe). Re-running this simulator closer to any given week will naturally lock in more real results and simulate less of the season.

## 2026 result (`n_sims=2000`, seed=17, refreshed schedule, 6 Week 1 games locked to their real result)

Top of the field-probability table (`season_2026_full_simulation_team_summary.csv`), consistent with the Week 1 preseason power ranking (Ohio State/Oregon/Notre Dame/Georgia at the top):

| team | conference | field % | conference title % | bye % | avg seed when in |
|---|---|---|---|---|---|
| Notre Dame | FBS Independents | 94.8 | -- | 73.5 | 3.18 |
| Ohio State | Big Ten | 91.0 | 47.2 | 64.9 | 3.54 |
| Oregon | Big Ten | 90.3 | 31.6 | 59.5 | 3.87 |
| Miami | ACC | 81.7 | 67.1 | 24.7 | 6.72 |
| Georgia | SEC | 74.6 | 41.3 | 36.2 | 5.11 |

Field probabilities sum to exactly 1200 (12 slots x 100%) across all FBS teams in every configuration checked, confirming the AQ+seeding rule always produces a valid 12-team field.

## What this does not do

- Does not modify `prospective/2026/`, `historical_cfp_selection.py`, or any production pipeline.
- Does not update team power in-season -- every trial uses the same fixed preseason rating for every week (see `PRESEASON_POWER_RATING_RESEARCH.md` for why that rating is trusted: 0.799 average Spearman rho against actual end-of-season power).
- Does not fully replicate real conference tiebreakers, or read real conference-championship-game matchups (synthesizes them instead).
- Does not yet reflect a complete 2026 schedule (weeks 14-15 gap, see Data coverage).
