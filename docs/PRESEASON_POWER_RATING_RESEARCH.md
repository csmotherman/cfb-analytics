# Preseason Power Rating Research

**Status:** EXPLORATORY -- isolated research track, not promoted, not wired into any production pipeline.
**Code:** `src/cfb_analytics/analytics/preseason_power/`
**Outputs:** `data/research/preseason_power/`
**Tests:** `tests/analytics/test_preseason_power_leakage.py`
**Extended by:** `docs/CFP_2026_SEASON_SIMULATOR_RESEARCH.md` -- takes this Week 1 model full-season, simulating the whole 2026 schedule and the resulting 12-team CFP field.

This document reports a walk-forward backtest of a true preseason power rating: for target season Y, every input is restricted to information that existed before Y's first game (prior-season results, the recruiting class entering Y, and QB roster continuity between Y-1 and Y). No AP poll, Coaches Poll, SP+, FPI, or betting line was used as a model input anywhere in this track. Betting lines were never consulted at all (this repo's `data/raw/market_lines` only covers 2014-2025 with partial open-line coverage; it was not read by this research).

## Data audit summary

`data/canonical/season=Y/team_games.json` (the leakage-safe FBS-vs-FBS team-game table) exists for 2014-2019 and 2021-2025 -- 11 seasons. 2020 is absent repo-wide (COVID). 2010-2013 have only an `fbs_membership.json` snapshot, no team_games. These 11 seasons (`COMPLETE_SEASONS` in `common.py`) are the entire usable universe for both building a prior and scoring a Week 1 prediction.

| feature family | first available season | notes |
|---|---|---|
| team_games / opponent-adjustable results | 2014 | 2020 hole; 2010-2013 raw-only |
| recruiting (team composite rank/points) | 2010 | 2026 class already published |
| roster snapshot | 2013 | 2026 preseason roster present |
| player_season_stats | 2013 | absent for 2026 (season unplayed) |
| transfer portal | 2021 | 2026 offseason cycle present |
| coaching history (by team-season) | 1890 (identity/tenure); 2014 (established-era offense/defense) | `data/research/coaching_history/`, see Model 7 |
| market lines | 2014 | partial open-line coverage; used only as an external note, never as a feature |

**Model 7 (coaching continuity) is now built** -- see the addendum below. `data/research/coaching_history/` supplies a full FBS head-coach career history (identity/tenure back to 1890) and a coach-season table restricted to established (year3+) tenures, joined to this repo's own leakage-safe points ratings (2014-2025).

## Method

A single mechanism is used throughout: a game-level design matrix (one row per Week 1 FBS-vs-FBS game, columns = home-minus-away diffed predictors, target = actual margin), fit by closed-form ridge regression, walk-forward -- coefficients for the season being predicted are fit only on Week 1 games from strictly earlier `COMPLETE_SEASONS`. Model 0 baselines, Model 1's decay weights, and every Model 3-6 ablation are the same mechanism with a different predictor set. A `home_field` indicator (1 on non-neutral games, 0 on neutral) is included in every set, so HFA is estimated jointly rather than assumed.

Team power itself reuses the repo's existing `iterative_ratings.fit_metric_ratings` solver (the same block-coordinate-descent code already used for success rate / explosiveness / etc.) against a synthetic "Points" spec (`points_for` per game, weight 1), which fits `points_for = league_mean + offense(team) - defense(opponent)`. This gives points-scale offense/defense/overall power by construction, and (with shrinkage=0) reconstructs the same margin structure as the repo's existing `fit_srs` SRS solver -- confirmed empirically (MAE 13.432 vs 13.430 on identical single-year-power backtests).

## Results

### Model 0 -- naive baselines (2018-2025, n=326)

| model | MAE | win% |
|---|---|---|
| raw scoring margin (no opponent adjustment) | 15.91 | -- |
| existing repo SRS (`fit_srs`), single year | 13.72 | -- |
| points-scale power (`fit_metric_ratings`), single year | 13.72 | -- |

Opponent adjustment alone is worth ~2.2 points of MAE over raw margin.

### Model 2 -- regression to the mean

A shrinkage sweep on the single-season power fit found **shrinkage=0 is best** (MAE rises monotonically from 13.43 at shrinkage=0 to 15.39 at shrinkage=34): the game-level ridge regression already regularizes team power, so an additional shrinkage-to-FBS-mean step at the per-season fit stage double-penalizes and hurts. Adding a 5-year program-average predictor alongside the tuned 3-year weights made MAE **worse** (13.38 -> 13.79); adding a conference-average predictor was a wash (13.38 -> 13.38). Neither survived; both were dropped.

### Model 1 -- multi-year decay weights

Ridge-fit coefficients on `power_y1/y2/y3 + home_field`, refit at every walk-forward step. The most recent fit (predicting 2025, i.e. the weights that would be used for 2026):

| lag | normalized weight |
|---|---|
| Y-1 | 0.569 |
| Y-2 | 0.241 |
| Y-3 | 0.190 |

`w1 > w2 > w3` held in 6 of 7 walk-forward steps (the 2018 step, trained on only 38 games, produced a small negative w2 -- a small-sample artifact, not a pattern). A constrained grid search (simplex, step 0.1) cross-check, evaluated on the same 7 seasons, independently found **w1=0.6, w2=0.3, w3=0.1** as the MAE-minimizing point -- consistent with the ridge result. **Home-field advantage was jointly estimated at ~4.0-4.4 points** in the more recent, larger-sample walk-forward steps (not the traditional assumed 3).

Multi-year power (2018-2025 matched sample) beat single-year: MAE 13.72 -> 13.38, win% 75.2% -> 76.9%.

### Model 3-6 -- personnel-era ablation (2018-2025 matched sample, n=312-316; portal on 2022-2025, n=180)

| model | MAE | win% | Brier |
|---|---|---|---|
| Track A base: power_y1+y2+y3 + HFA | 13.38 | 76.9 | .1653 |
| + recruiting (3yr class avg) | 12.92 | 78.5 | .1599 |
| + returning offense production share | 13.03 | 75.3 | .1653 |
| + returning defense production share | 13.24 | 77.2 | .1651 |
| + QB returning flag | 12.94 | 76.6 | .1628 |
| **+ recruiting_3yr + QB returning flag (RECOMMENDED)** | **12.46** | **77.9** | **.1574** |
| + also adding returning off/def shares on top | 12.50 | 77.2 | .1596 |
| Track A base, portal-comparable seasons only (2022-2025) | 13.15 | 76.7 | .1595 |
| + portal net production (offense+defense) | 14.17 | 73.9 | .1676 |

**Recruiting and QB continuity both earn their place; returning production does not add anything beyond them.** The full "kitchen sink" (recruiting + QB flag + both returning shares) scores 12.50 -- *worse* than the 2-feature combination alone (12.46). The two-feature model is both simpler and better and is the recommendation.

**Portal made every variant worse and was excluded.** This is very likely a measurement artifact rather than evidence that transfer activity doesn't matter: `portal.json` has no player ID, so incoming/outgoing transfers were matched to `player_season_stats` by normalized name + team, which only matched 40-70% of transfers in spot checks. The unmatched half is silently scored as zero prior production, which is systematically wrong for real transfers. A future revisit needs an ID-based join (or CFBD's athlete-ID-bearing transfer endpoint, if available) before portal value can be fairly tested.

### Addendum -- transfer-QB-specific test (`transfer_qb_features`, `Model 5b`)

The generic portal ablation above bundles all positions together with a noisy name join. A narrower, cleaner version was tested separately: for a team whose own prior-season starter did *not* return, look up the incoming QB transfer (if any) via `portal.json`, and use his actual prior-season production at his old school (`transfer_qb_incoming_flag` = 1 if he threw >=100 attempts, `transfer_qb_prior_passing_yards` continuous) -- e.g. this correctly identifies Miami's 2026 incoming QB Darian Mensah (500 att / 3,973 yds at Duke in 2025) as a productive transfer, not an unknown.

On the 4 portal-available seasons (2022-2025, n=180, of which 63 games had a nonzero home-vs-away transfer-QB differential -- not a sparse sample):

| model | MAE | win% | Brier |
|---|---|---|---|
| RECOMMENDED (recruiting_3yr + QB returning flag) | 12.06 | 80.0 | .1451 |
| + transfer_qb_incoming_flag | 12.62 | 76.7 | .1539 |
| + transfer_qb_prior_passing_yards | 13.00 | 77.2 | .1606 |
| + both | 13.04 | 76.1 | .1615 |

**Worse in every variant -- not added to the recommended model.** The interesting part is *why*: the fitted coefficient's sign was correctly positive in all 4 walk-forward steps (a productive transfer QB genuinely correlates with outperforming), but its size was unstable year to year (+5.35, +2.59, +1.34, +3.59), and that instability cost more out-of-sample accuracy than the correct-direction signal recovered. This reads as a real, underlying football effect (transfer QB integration -- new receivers, new line, new scheme, no guarantee of even winning the job -- is inherently higher-variance than same-team continuity) rather than a data problem, unlike the generic portal result above. Current verdict: the Week 1 model does not have statistical grounds to credit a team extra for a productive incoming transfer QB beyond what recruiting and the (absence of a) returning-starter flag already capture -- Miami's 2026 rank reflects that.

**Model 7 (coaching continuity) -- see the dedicated addendum below for the full result; the short version: continuity flags add nothing, but a coach's imported track record from his prior job is a real, if coverage-limited, signal.**

### Recommended model -- full walk-forward evaluation (2018-2025, n=312)

`power_y1 (0.57) + power_y2 (0.24) + power_y3 (0.19) + recruiting_3yr + qb_returning_flag + HFA(~4.1 pts, 0 on neutral)`

| metric | value |
|---|---|
| MAE | 12.46 |
| RMSE | 16.18 |
| Median AE | 9.70 |
| Winner accuracy | 77.9% |
| Brier score | 0.157 |
| Log loss | 0.482 |

No single season dominates: year-by-year MAE ranges 11.25 (2019) to 14.42 (2021), the latter plausibly the most roster-chaotic post-COVID season in the sample. Segment behavior is sane and un-gamed: P4-vs-P4 win% 64.5% (closest games, hardest to call), P4-vs-G5 win% 87.3% (correctly the easiest bucket, Brier 0.107), and winner accuracy rises monotonically from 52.5% (0-3 pt predicted margin) to 96.4% (21+ pt predicted margin) -- exactly the shape a well-behaved model should have. Calibration is reasonable but not perfect: the 70-80% confidence bucket is overconfident (74.9% predicted vs 63.6% actual, n=44); other buckets track closely. The 15 biggest misses are recognizable real upsets/blowouts (Texas State over Baylor 2023, Marshall over Navy 2021, Vanderbilt over Hawai'i 2022, Temple over Rutgers 2021), not obvious model bugs.

Conference-specific HFA was tested (P4-home residual +1.4, G5-home residual -1.5) but the split is within ~1 standard error given sample size (n=190/84) -- kept as a single constant HFA rather than fragmenting.

### Preseason ranking validity (secondary diagnostic, not the fitting objective)

Preseason power (the recommended model, computed before any Y game) vs. that same season's *actual* end-of-season opponent-adjusted power, across all 7 backtested seasons:

| metric | average | range |
|---|---|---|
| Spearman rho | 0.799 | 0.746 - 0.850 |
| Kendall tau | 0.606 | 0.543 - 0.661 |
| Pairwise concordance | 80.3% | 77.2% - 83.1% |

Stable across seasons -- the preseason ordering is a genuinely strong (not just Week-1-lucky) predictor of full-season team quality.

### Residual distribution (for Monte Carlo)

Out-of-sample residual std = **16.15 points** (not an assumed 14). Train/test split by season (2018-2022 fit, 2023-2025 held out): Normal, Student-t (fitted df=15, i.e. already near-Gaussian), and an empirical KDE score within noise of each other (held-out NLL 4.184 / 4.180 / 4.190). Recommendation: empirical bootstrap, per the brief's preference -- but a Normal(mu=-1.1, sigma=16.4) approximation would give essentially identical simulation output.

## 2026 demonstration (`demo_2026.py`)

Applying the recommended model to the real 2026 preseason (2023-2025 priors, the 2026 recruiting class, 2026 vs. 2025 roster QB continuity -- nothing from any 2026 game, since none have been played) produced a Top 25 with Ohio State, Oregon, Notre Dame, and Georgia at the top and Michigan at #9 -- an unforced result of the model, not a manually chosen placement. Outputs: `data/research/preseason_power/preseason_2026_top25.csv`, `preseason_2026_ratings.csv` (full FBS field), and `week1_2026_predictions.csv` (48 games, with Monte Carlo win probability / median margin / 10th-90th percentile / upset probability using the validated empirical residual pool). The Week 1 schedule was read *read-only* from `prospective/2026/features/week-01.json` (team names and neutral-site flag only -- no feature or rating value from that file was reused, keeping this track fully independent of the production model).

### Addendum -- experience-weighted individual roster talent (Model 8)

`recruiting_3yr` (the feature in the recommended model) is a **team-level class composite**: it only knows the incoming class entering season Y, not which of those recruits (or earlier classes) are still on the roster, or how far along they are. A 5-star true freshman and a 5-star senior are indistinguishable to it. Tested whether joining CFBD's roster (`recruitIds`) to individual recruit ratings (`recruiting/players`, field `rating`) and weighting each player's rating by `roster.year` (1=fr .. 4=sr) produces a better predictor -- the hypothesis being that a proven senior blue-chip should count for more than an unproven freshman one.

New feature `experience_weighted_talent_features` (`features.py`), registered as `talent_flat` / `talent_linear` / `talent_senior_boost` (weight schemes `{1,1,1,1}`, `{1,2,3,4}`, `{1.0,1.4,1.8,2.2}` by class), aggregated two ways (average-per-rated-player, and sum-across-roster):

| model | MAE | win% | Brier |
|---|---|---|---|
| Track A base: power_y1+y2+y3 + HFA | 13.95 | 75.9 | .1724 |
| + recruiting_3yr (team composite, baseline) | 12.99 | 77.8 | .1607 |
| + talent_flat (avg, unweighted control) | 13.88 | 75.9 | .1717 |
| + talent_linear (avg, 1-4 weight) | 13.70 | 76.6 | .1692 |
| + talent_senior_boost (avg, 1.0-2.2 weight) | 13.72 | 76.6 | .1700 |
| + talent_sum_senior_boost (sum instead of average) | 13.99 | 75.9 | .1704 |
| recruiting_3yr + talent_senior_boost + qb_returning_flag | 12.60 | 78.2 | .1588 |
| recruiting_3yr + qb_returning_flag (RECOMMENDED, unchanged) | **12.60** | **78.2** | **.1584** |

**Result: negative.** Every weighting scheme and both aggregations underperform the plain team-composite `recruiting_3yr` on its own (13.7-14.0 vs 12.99 MAE), and adding the best variant (`talent_senior_boost`) on top of the recommended model doesn't beat it -- MAE ties at 12.60 while Brier gets very slightly worse (.1588 vs .1584). The recommended model is unchanged.

**Root cause, not just a null result:** `recruitIds` -> `recruiting/players.id` coverage is real but incomplete, and gets worse the further back a signing class is. Spot check (`rated_player_count / roster_count`): Ohio State 2025 70.2%, Toledo 2025 65.5%, Alabama 2025 59.1%, Alabama 2019 54.3%, Georgia 2015 44.3%. In the walk-forward, half the training seasons (2018-2021) are built on rosters with under ~55% of players resolving to a rated recruit -- unrated players (walk-ons, JUCO, missed joins) are silently scored as zero talent, which is systematically noisier the further back the season, exactly the same failure mode that sank the generic portal feature (Model 3-6 above) for the same name/ID-join reason. This reads as **the same underlying idea (seniority should matter) not yet supported by data plumbing precise enough to test it fairly** -- not evidence that experience-weighting recruiting talent is a bad idea in principle. A future revisit needs either better `recruitIds` coverage validation per season, or a coverage-aware weighting (e.g. discount low-coverage team-seasons rather than silently zeroing missing players).

### Addendum -- coaching continuity (Model 7)

The original report above (and the product contract's own gap list) named this as the one preseason signal that could not be tested at all: no historical coach-by-team-season table existed anywhere in the repo. `data/research/coaching_history/` closes that gap with two files: `fbs_coaches_full_history.json` (every FBS head coach's full career, `school`+`year` back to 1890 -- identity/tenure only; a season entry's own wins/losses/srs/spOverall are that season's outcome, or for the unplayed 2026 stub rows, CFBD's SP+ preseason projection, so neither is read as a feature) and `coach_year3plus_records_2014_2025.json` (coach-seasons restricted to `yearAtSchool>=3`, i.e. an established system past the honeymoon/transition years, with `offense`/`defense` fields that were spot-checked to match this repo's own `season_points_ratings(year, shrinkage=0.0)` exactly -- not SP+).

Three features (`features.py`, registered in `model.py`):

- `coach_new_flag` -- 1 if `target_season` is the coach's first year at this school.
- `coach_tenure_years` -- consecutive years (present in the corpus) at this school entering `target_season`.
- `coach_prior_overall` -- the career-average established (year3+) offense+defense of the coach currently on the sideline, from seasons strictly before `target_season` at ANY school he's coached. This is the one designed to matter for a coaching change: it imports the new hire's proven track record from his last job, rather than leaving the team scored only on the outgoing coach's `power_y1/y2/y3`.

| model | MAE | win% | Brier | n |
|---|---|---|---|---|
| BASE: power_y1+y2+y3 + HFA (full sample) | 13.38 | 76.9 | .1653 | 316 |
| + coach_new_flag (on BASE) | 13.43 | 76.6 | .1630 | 316 |
| + coach_tenure_years (on BASE) | 13.43 | 76.9 | .1661 | 316 |
| RECOMMENDED + coach_new_flag | 12.50 | 77.6 | .1550 | 312 |
| RECOMMENDED + coach_tenure_years | 12.51 | 78.2 | .1569 | 312 |
| RECOMMENDED, same subsample as coach_prior_overall below (fair baseline) | **12.38** | 78.6 | **.1516** | 56 |
| RECOMMENDED + coach_prior_overall | **11.86** | 78.6 | .1580 | 56 |

**Continuity flags add nothing** -- `coach_new_flag` and `coach_tenure_years` both tie or slightly worsen MAE/Brier on top of the recommended model (12.50/12.51 vs 12.46 baseline), same null pattern as the failed Model 8 talent weighting: knowing a coach is new, on its own, isn't informative without knowing whether he's any good.

**`coach_prior_overall` is a real, coverage-limited positive signal.** Its coverage is only 46.6% of Week 1 team-games (a coach needs an established year3+ stint anywhere in the corpus before `target_season` -- most often missing for a coach in his first ever FBS head-coaching job), so the fair comparison is RECOMMENDED evaluated on the *same* 56-game subsample where the feature is defined, not the full 312-game sample. On that matched subsample the feature earns a real MAE improvement (12.38 -> 11.86, -0.52) with win% unchanged and Brier slightly worse (.1516 -> .1580). The fitted coefficient is positive and stable across every one of the 5 walk-forward steps it produces (2021: 0.437, 2022: 0.295, 2023: 0.500, 2024: 0.494, 2025: 0.432) -- not a small-sample fluke in one direction one year and the other the next.

**Not folded into the primary model.** Naive full-sample imputation (0 when either team's coach has no established record, plus a companion availability-diff flag) was tested to try to recover the gain across all 312 games -- it does not survive: MAE goes to 12.51-12.59, worse than the unmodified recommended model. Diluting the signal with zeros for the majority-missing rows costs more than the true signal recovers, and folding `coach_prior_overall` in as a hard-required feature (the alternative to imputing) would cut the recommended model's production coverage roughly in half, which is unacceptable for a full-FBS 2026 field. Recommended model is unchanged. This reads as a genuine, real coaching-quality-import effect not yet supported by wide enough data coverage to use unconditionally -- the same shape of finding as the Model 8 talent root cause, but on the positive side of the ledger rather than the negative one. A future revisit needs either deeper coach-history coverage (more pre-2014 established seasons per coach) or a smarter coverage-aware blend (e.g. shrink toward 0 in proportion to games of established evidence, rather than an all-or-nothing gate).

## What this does not do

- Does not modify `prospective/2026/` or any production pipeline.
- Does not use AP/Coaches/SP+/FPI/betting lines as inputs.
- Coaching continuity is measured (Model 7, above): continuity flags don't help; a coach's imported prior track record does, on the ~47% of games where it's defined, but isn't part of the recommended model due to that coverage gap.
- Portal is measured but excluded from the recommendation (net negative, likely a name-matching artifact -- see above).
