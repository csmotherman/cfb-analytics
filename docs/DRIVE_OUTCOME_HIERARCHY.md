# Hierarchical Drive Outcome Challenger

**Status:** SCREENED — NOT PROMOTED  
**Version:** `drive-outcome-hierarchy-v1-full-features`

## Why this exists

The converged flat FULL drive-outcome model is a validated research baseline. Across outer seasons 2017, 2018, 2019, 2021, 2022, 2023, 2024, and 2025:

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

The hierarchy asked a narrower structural question:

> Does explicitly modeling football outcome families improve probability estimation enough to justify replacing one flat 9-class multinomial model?

## Hierarchy

The root classifier predicts four broad families:

```text
OFFENSIVE_SCORE
NON_SCORING_END
OPPONENT_SCORE
PERIOD_END
```

Conditional branches predict:

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

Final leaf probabilities are products of root and conditional probabilities. For example:

```text
P(TD) = P(OFFENSIVE_SCORE) * P(TD | OFFENSIVE_SCORE)
```

## Fair comparison contract

The hierarchy was not allowed a richer information set or tuned regularization.

Both FLAT and HIER use:

- identical semantic target rows;
- identical expanding-season training windows;
- identical possession-start features;
- identical pregame offense/defense quality fields;
- identical training-only quality imputation;
- identical missingness indicators;
- identical `C=1.0` regularization;
- identical `newton-cholesky` solver contract;
- fatal convergence warnings.

This makes the experiment a test of factorization/football structure, not a feature or hyperparameter search.

## Screening result

A full eight-season hierarchy run is computationally expensive because each outer season fits the flat baseline plus four hierarchy classifiers. Rather than spend that cost before establishing useful effect size, the experiment used an early-era and late-era screen.

### 2017

```text
FLAT
  LogLoss 1.42700
  Brier   0.67392
  Accuracy 47.47%

HIER
  LogLoss 1.42677
  delta   -0.000239
  Brier   0.67367
  delta   -0.000244
  Accuracy 47.56%
  delta   +0.10 pp
```

### 2025

```text
FLAT
  LogLoss 1.47602
  Brier   0.69406
  Accuracy 45.11%

HIER
  LogLoss 1.47593
  delta   -0.000087
  Brier   0.69389
  delta   -0.000171
  Accuracy 45.12%
  delta   +0.02 pp
```

Both screens are directionally positive, but the gains are microscopic relative to the already-validated FULL-vs-STATE improvement and do not justify the extra model complexity or repeated training cost.

The hierarchy therefore is **not promoted**. This is not evidence that football factorization is wrong; it is evidence that, with this feature set and logistic specification, the structural decomposition adds too little operational value to replace the simpler flat FULL model.

No additional outer-season hierarchy runs are required unless the implementation is later made substantially cheaper or the hierarchy changes in a scientifically meaningful way.

## Decision

The selected possession-outcome probability engine remains:

```text
FLAT FULL 9-class multinomial logistic regression
```

The hierarchy remains useful as a documented research branch and may be revisited later if the simulator gains richer state, branch-specific features, or cached model matrices. It should not block simulator development now.

## Command

The existing research command remains available:

```bash
python -m cfb_analytics.analytics.drive_outcome_hierarchy --test-seasons 2017
```

or any explicit subset of outer seasons. A full eight-season run is not part of the current required workflow.

## What comes next

Move to the missing simulator mechanisms using the validated flat FULL probability engine:

```text
selected drive-outcome probabilities
  -> points assignment
  -> possession sequencing / next possession state
  -> period endings and game clock handling
  -> regulation game simulation
  -> separate overtime treatment
  -> game-level validation against Prediction v1
```

Future experiments should prefer cached/reused transformed matrices and baseline predictions so research iterations do not repeatedly pay the full fitting cost.