# Prediction v2 Early-Season Prior Challenger

**Status:** PREDECLARED DEVELOPMENT CHALLENGER  
**Version:** `prediction-v2-early-prior-four-game-linear-v1`

This document freezes the first previous-season carryover experiment **before any game-margin results from the challenger are inspected**.

The feasibility audit showed that immediately adjacent prior seasons provide complete Iterative, Football Mechanisms, MWDR, and site-aware SRS state for 1,754 of 1,781 historical regular-season games through Week 4 (98.5%). That is sufficient to test a full-family prior rather than a partial workaround.

## Scope

The challenger is used only for regular-season games through Week 4 in seasons with an immediately adjacent historical season.

Valid carryovers are:

```text
2015 <- 2014
2016 <- 2015
2017 <- 2016
2018 <- 2017
2019 <- 2018
2022 <- 2021
2023 <- 2022
2024 <- 2023
2025 <- 2024
```

There is no 2021 prior because 2020 is absent from the project corpus. The experiment must not silently reach back to 2019.

## Fixed carryover rule

The immediately previous season supplies the missing share of a four-game evidence window.

```text
current games played before matchup   prior weight   current-season weight
0                                     1.00           0.00
1                                     0.75           0.25
2                                     0.50           0.50
3                                     0.25           0.75
4+                                    0.00           1.00
```

The weight is applied independently to each team based on that team's current-season games played before the matchup.

The value `4` is not selected from outcome testing. It is tied to the existing Prediction-v2 min4 stability benchmark so the prior disappears completely once the current team state reaches that established threshold.

No additional shrinkage coefficient is tuned. The early-season OLS fit is responsible for calibrating the predictive strength of the carried state.

## What is blended

The blend occurs at team-state level **before** matchup edges are reconstructed.

The challenger carries:

- all six Iterative offense and defense rating families;
- site-aware SRS team ratings;
- MWDR offense and defense ratings;
- the Football Mechanisms state required for Success, Explosive, Turnover, and expected-possession volume terms.

The site-aware HFA coefficient is blended using the mean of the home and away prior weights. At zero current games this is the prior-season final HFA. Once both teams have four current games, the HFA and all team-state inputs are current-season Prediction v2 values.

The final feature vector remains the same 19-feature Prediction-v2 architecture.

## Mechanical reversion requirement

For every row where both teams have at least four current-season games, the reconstructed challenger feature vector must match Prediction v2 to numerical tolerance.

This is a structural requirement, not a predictive result. If it fails, the challenger is invalid regardless of MAE/RMSE.

## Outer-season evaluation

Primary held-out development seasons are:

```text
2018
2019
2022
2023
2024
2025
```

For each held-out season, train only on eligible early-prior rows from chronologically earlier seasons. The missing 2020 season remains missing.

The 2023-2025 folds are already heavily used development evidence elsewhere in the project. They are retained here for consistency/stability diagnostics, but a historical pass makes this only a **candidate to freeze for prospective 2026 validation**.

## Predeclared comparisons

### 1. FOUR-GAME BLEND vs PRIOR-ONLY

Use the exact same train and test game IDs. The prior-only ablation keeps the previous-season state at 100% through the full early window and ignores current-season state.

This tests whether the fixed decay successfully incorporates new-season evidence instead of merely benefiting from stale prior-year strength.

### 2. FOUR-GAME BLEND vs CURRENT-ONLY

Use the exact common sample where the normal current-season Prediction-v2 feature vector is already finite. Fit both early models on the exact same historical common rows.

This tests whether adding the previous-season information improves on simply trusting one to three current-season games.

### 3. FOUR-GAME BLEND vs SITE/HFA BASELINE

Fit a simple early-game baseline using only intercept plus non-neutral home-site status.

This is a sanity check that the 19-feature early model adds meaningful team-strength information.

## Predeclared promotion gate

The four-game blend is a **2026 freeze candidate** only if every condition below passes:

```text
STRUCTURAL
  challenger reverts exactly to Prediction v2 once both teams have 4+ games

VS PRIOR-ONLY — all six outer folds
  mean delta MAE < 0
  mean delta RMSE < 0
  MAE better in at least 4 of 6 folds
  RMSE better in at least 4 of 6 folds

VS PRIOR-ONLY — recent 2023-2025 folds
  mean delta MAE <= 0
  mean delta RMSE <= 0

VS CURRENT-ONLY — exact common sample, all six folds
  mean delta MAE < 0
  mean delta RMSE < 0

VS CURRENT-ONLY — recent 2023-2025 common sample
  mean delta MAE <= 0
  mean delta RMSE <= 0

VS SITE/HFA BASELINE — all six folds
  mean delta MAE < 0
  mean delta RMSE < 0
```

Negative deltas are improvements.

Week 0-2 and Week 3-4 results are reported separately as stability diagnostics. They are not additional tuning targets for this first fixed challenger.

## Interpretation policy

If the gate passes, do not tune the weights further. Freeze this exact rule and architecture before observing 2026 outcomes.

If the gate fails, do not alter `1.00/0.75/0.50/0.25/0.00` after looking at the same holdouts and call the retuned version independent evidence. A follow-up must be a materially new, explicitly predeclared hypothesis.

The command is saved-data-only:

```bash
python -m cfb_analytics.analytics.prediction_v2_early_prior_challenger
```
