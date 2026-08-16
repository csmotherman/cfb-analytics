# Prediction v2 Early-Season Prior Challenger

**Status:** FROZEN 2026 PROSPECTIVE CANDIDATE  
**Version:** `prediction-v2-early-prior-four-game-linear-v1`

This document freezes the first previous-season carryover experiment. The carryover rule and promotion gate were declared before its game-margin results were inspected. The historical gate subsequently passed in full. The exact rule is now frozen for prospective 2026 use; do not retune the weights against 2026 outcomes.

The feasibility audit showed that immediately adjacent prior seasons provide complete Iterative, Football Mechanisms, MWDR, and site-aware SRS state for 1,754 of 1,781 historical regular-season games through Week 4 (98.5%). That is sufficient to use a full-family prior rather than a partial workaround.

## Scope

The challenger is used only for regular-season games through Week 4 in seasons with an immediately adjacent historical season.

Valid historical carryovers were:

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

For prospective 2026 use, the adjacent prior is 2025.

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

The value `4` was not selected from outcome testing. It is tied to the existing Prediction-v2 min4 stability benchmark so the prior disappears completely once the current team state reaches that established threshold.

No additional shrinkage coefficient is tuned. The early-season OLS fit is responsible for calibrating the predictive strength of the carried state.

### Missing current-season component rule

Before a team has four current-season games, an individual component can legitimately remain undefined because its denominator or state has not occurred yet. In that case, if the adjacent-season prior component is finite, the challenger keeps that prior component unchanged. Missing current evidence is **not** treated as zero and does not cause an otherwise coverable game to be discarded.

Once a team has four or more current-season games, there is no prior fallback: the component must come from the current-season Prediction-v2 state. This exception is therefore an early-sample missing-evidence rule, not a permanent carryover mechanism.

## What is blended

The blend occurs at team-state level **before** matchup edges are reconstructed.

The challenger carries:

- all six Iterative offense and defense rating families;
- site-aware SRS team ratings;
- MWDR offense and defense ratings;
- the Football Mechanisms state required for Success, Explosive, Turnover, and expected-possession volume terms.

The site-aware HFA coefficient is blended using the mean of the home and away prior weights. At zero current games this is the prior-season final HFA. If the current-season HFA is not yet estimable before Game 4, the finite prior HFA remains in place. Once both teams have four current games, the HFA and all team-state inputs are current-season Prediction v2 values.

The final feature vector remains the same 19-feature Prediction-v2 architecture.

## Mechanical reversion requirement

For every row where both teams have at least four current-season games, the reconstructed challenger feature vector must match Prediction v2 to numerical tolerance.

Historical audit result:

```text
late v2 reversion rows = 4,462
mismatches             = 0
max absolute difference= 0.000e+00
```

This structural requirement passed exactly.

## Historical outer-season evaluation

Held-out development seasons:

```text
2018
2019
2022
2023
2024
2025
```

For each held-out season, training used only eligible early-prior rows from chronologically earlier seasons. The missing 2020 season remained missing.

The 2023-2025 folds were already heavily used development evidence elsewhere in the project. They are retained here for consistency/stability diagnostics, but this historical pass is therefore a **freeze candidate for prospective 2026 validation**, not pristine unseen confirmation.

## Predeclared comparisons and observed results

Negative deltas are improvements for MAE/RMSE.

### FOUR-GAME BLEND vs PRIOR-ONLY

Exact same train and test game IDs.

```text
ALL 6 FOLDS
mean delta MAE   -0.2207
mean delta RMSE  -0.2789
MAE better         6/6
RMSE better        4/6

RECENT 2023-2025
mean delta MAE   -0.2111
mean delta RMSE  -0.1651
MAE better         3/3
RMSE better        2/3
```

### FOUR-GAME BLEND vs CURRENT-ONLY

Exact common sample where normal current-season Prediction-v2 features were finite.

```text
ALL 6 FOLDS
mean delta MAE   -2.1493
mean delta RMSE  -2.4220

RECENT 2023-2025
mean delta MAE   -1.2744
mean delta RMSE  -1.7578
```

### FOUR-GAME BLEND vs SITE/HFA BASELINE

```text
ALL 6 FOLDS
mean delta MAE   -4.4971
mean delta RMSE  -5.5563

RECENT 2023-2025
mean delta MAE   -4.3290
mean delta RMSE  -5.2736
```

## Week-band diagnostic

This diagnostic was predeclared as descriptive, not a tuning target.

```text
Weeks 0-2 vs PRIOR-ONLY
  delta MAE   -0.0033
  delta RMSE  +0.0441

Weeks 3-4 vs PRIOR-ONLY
  delta MAE   -0.4073
  delta RMSE  -0.5591
```

Interpretation: the fixed blend is essentially tied with prior-only in Weeks 0-2, while most of its historical advantage appears in Weeks 3-4 as current-season evidence accumulates. Do not use this observation to retune the frozen weights against the same historical folds.

## Predeclared promotion gate

Every predeclared condition passed:

```text
STRUCTURAL
  exact reversion to Prediction v2 after both teams have 4+ games        PASS

VS PRIOR-ONLY — all six outer folds
  mean delta MAE < 0                                                     PASS
  mean delta RMSE < 0                                                    PASS
  MAE better in at least 4 of 6 folds                                   PASS (6/6)
  RMSE better in at least 4 of 6 folds                                  PASS (4/6)

VS PRIOR-ONLY — recent 2023-2025
  mean delta MAE <= 0                                                    PASS
  mean delta RMSE <= 0                                                   PASS

VS CURRENT-ONLY — exact common sample, all six folds
  mean delta MAE < 0                                                     PASS
  mean delta RMSE < 0                                                    PASS

VS CURRENT-ONLY — recent 2023-2025 common sample
  mean delta MAE <= 0                                                    PASS
  mean delta RMSE <= 0                                                   PASS

VS SITE/HFA BASELINE — all six folds
  mean delta MAE < 0                                                     PASS
  mean delta RMSE < 0                                                    PASS
```

## Decision

`PASS_2026_FREEZE_CANDIDATE`

Freeze this exact rule and architecture before observing 2026 outcomes. Do not tune the `1.00/0.75/0.50/0.25/0.00` carryover weights against 2026 if 2026 is being used as prospective validation.

Prediction v2 remains the locked mature-season research benchmark. This early-season extension is not renamed Prediction v3 until it receives genuinely prospective evidence or a separate promotion decision.

Historical evaluation command:

```bash
python -m cfb_analytics.analytics.prediction_v2_early_prior_challenger
```
