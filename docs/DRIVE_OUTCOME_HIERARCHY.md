# Hierarchical Drive Outcome Challenger

**Status:** RESEARCH ONLY  
**Version:** `drive-outcome-hierarchy-v1-full-features`

## Why this exists

The converged flat FULL drive-outcome model is now a validated research baseline. Across outer seasons 2017, 2018, 2019, 2021, 2022, 2023, 2024, and 2025:

```text
STATE vs GLOBAL
  pooled LogLoss delta = -0.218779
  pooled Brier delta   = -0.070117
  better seasons       = 8/8 on both metrics

FULL vs STATE
  pooled LogLoss delta = -0.009612
  pooled Brier delta   = -0.006070
  better seasons       = 8/8 on both metrics
```

That establishes two things: possession-start state is strongly predictive, and leakage-safe pregame offense/defense quality adds stable incremental information.

The next question is structural:

> Does explicitly modeling football outcome families improve probability estimation beyond one flat 9-class multinomial model?

## Hierarchy

The root classifier predicts four broad families:

```text
OFFENSIVE_SCORE
NON_SCORING_END
OPPONENT_SCORE
PERIOD_END
```

Conditional branches then predict:

```text
OFFENSIVE_SCORE
  -> TOUCHDOWN
  -> FIELD_GOAL

NON_SCORING_END
  -> PUNT
  -> TURNOVER
  -> DOWNS
  -> MISSED_FIELD_GOAL

OPPONENT_SCORE
  -> RETURN_TOUCHDOWN
  -> SAFETY

PERIOD_END
  -> PERIOD_END
```

Final leaf probabilities are products of the root and conditional probabilities. For example:

```text
P(TD) = P(OFFENSIVE_SCORE) * P(TD | OFFENSIVE_SCORE)
```

The resulting vector is evaluated in the exact same 9-class order as the flat baseline.

## Fair comparison contract

The hierarchy is not allowed a richer information set or tuned regularization.

Both FLAT and HIER use:

- identical semantic target rows;
- identical outer seasons;
- identical expanding-season training windows;
- identical possession-start features;
- identical pregame offense/defense quality fields;
- identical training-only quality imputation;
- identical missingness indicators;
- identical `C=1.0` regularization;
- identical `newton-cholesky` solver contract;
- fatal convergence warnings.

This makes the experiment a test of **factorization/football structure**, not a feature or hyperparameter search.

## Why the hierarchy might help

The flat model must estimate all nine outcomes simultaneously even though some outcomes are naturally conditional on a higher-level event.

The hierarchy can share statistical structure at the family level and can give rare outcomes a more sensible conditional problem. For example, `SAFETY` is extremely rare unconditionally, but the opponent-score branch only needs to distinguish safety from return touchdown after the root has already estimated the probability of an opponent score.

The hierarchy is not assumed to be better. If the factorization introduces avoidable error, the validated flat FULL model remains the baseline.

## Evaluation

Primary metrics:

- multiclass log loss;
- multiclass Brier score.

Secondary diagnostics:

- top-class accuracy;
- outer-season win counts;
- pooled class-frequency calibration.

Promotion rule:

```text
HIER must improve pooled LogLoss and pooled Brier versus FLAT FULL,
with gains that are not driven by one isolated outer season.
```

A negative HIER-minus-FLAT delta is better.

## Command

The benchmark reads the already-materialized Drive State v2 files. No PBP replay, profile rebuild, or drive-state regeneration is required.

```bash
python -m cfb_analytics.analytics.drive_outcome_hierarchy
```

Optional recent-season subset:

```bash
python -m cfb_analytics.analytics.drive_outcome_hierarchy --test-seasons 2021,2022,2023,2024,2025
```

## What comes after this

If HIER beats the flat baseline, it becomes the preferred possession-outcome probability engine for the simulator research path.

If HIER does not beat FLAT, that is still useful evidence: keep the simpler validated flat FULL model and move on to the next missing simulator mechanism rather than forcing football structure that does not improve out-of-sample probabilities.

Only after the possession-outcome engine is selected should the project translate these probabilities into game simulation, including possession sequencing, points assignment, period endings, and a separate overtime treatment.