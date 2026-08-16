# Drive Outcome Probability Benchmark

**Status:** VALIDATED RESEARCH BASELINE  
**Version:** `drive-outcome-multinomial-v1-convergence-verified`

## Purpose

Drive State Research v2 established a possession-level contract:

```text
raw drive-start state + leakage-safe pregame team quality -> categorical driveResult
```

This benchmark asks two sequential questions:

1. Does possession-start football state predict the eventual drive outcome better than unconditional class frequencies?
2. After controlling for that state, does pregame offense/defense quality add stable out-of-sample probability information?

Prediction v1 and the existing historical simulator remain unchanged. This model is a validated **research baseline** for the new mechanistic simulator, not a production-locked game model.

## Corpus and target contract

The regulation-only v2 materialization covers 2014-2019 and 2021-2025 and contains about 207k drive rows. Start yards-to-goal, score margin, and clock have complete coverage in every audited season. Pregame quality coverage is about 91% because Week 1 and other zero-history states intentionally remain missing rather than leaking future information.

Known cross-season raw `driveResult` aliases are normalized at model load time, including:

- `RUSHING TD`, `PASSING TD`, `END OF HALF TD`, `END OF GAME TD` -> `TOUCHDOWN`;
- `FG GOOD` -> `FIELD_GOAL`;
- `FG MISSED` -> `MISSED_FIELD_GOAL`;
- `INT RETURN TOUCH` -> `RETURN_TOUCHDOWN`.

`Uncategorized` and other genuinely unresolved raw outcomes remain preserved in the research corpus but are excluded from model fitting and proper-score evaluation. Missing **predictors** are handled differently: no row with a resolved target is dropped for missing pregame quality.

## Modeled outcome classes

```text
TOUCHDOWN
FIELD_GOAL
PUNT
TURNOVER
DOWNS
MISSED_FIELD_GOAL
PERIOD_END
RETURN_TOUCHDOWN
SAFETY
```

Rare but valid football outcomes are retained. No class weighting is used because the goal is calibrated probability estimation rather than balanced classification accuracy.

## Models

### GLOBAL

Training-set class frequencies with light Dirichlet smoothing.

### STATE

Regularized multinomial logistic regression using only information known at possession start:

- period;
- start clock;
- yards to goal with nonlinear field-position basis terms;
- offense-minus-defense score margin;
- leading/tied/trailing state;
- home-offense indicator;
- late-half clock pressure.

### FULL

`STATE` plus leakage-safe pregame team quality.

Offense:

- yards per possession;
- success rate;
- explosive rate;
- scoring-opportunity rate;
- points per opportunity;
- early-down success;
- giveaway rate.

Defense:

- yards per possession allowed;
- success rate allowed;
- explosive rate allowed;
- scoring-opportunity rate allowed;
- points per opportunity allowed;
- early-down success allowed;
- takeaway rate.

Missing quality is imputed using **training-only** field means. A missingness indicator is added for every imputed field, and games played before the current partition are retained so the model can distinguish early-season states.

## Optimizer and convergence contract

The verified benchmark uses:

```text
solver = newton-cholesky
C = 1.0
max_iter = 200
tol = 1e-7
```

The repository model dependency requires scikit-learn >=1.6. Any `ConvergenceWarning` is fatal; proper scores are never reported from an explicitly unconverged fit.

The earlier `lbfgs` execution hit its iteration ceiling and was treated as preliminary only. The converged rerun reproduced the same signal essentially unchanged.

## Validation design

Evaluation is expanding-season walk-forward. For each outer test season, every earlier available season is training data and the entire outer season is untouched test data.

Outer seasons:

```text
2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025
```

Primary metrics:

- multiclass log loss;
- multiclass Brier score.

Secondary diagnostics:

- top-class accuracy;
- semantic target coverage;
- alias normalization counts;
- pooled observed versus predicted frequency by class.

## Converged walk-forward result

The verified run passed the sequential promotion test in every outer season.

```text
STATE vs GLOBAL
  pooled LogLoss delta = -0.218779
  pooled Brier delta   = -0.070117
  better seasons       = 8/8 on LogLoss
  better seasons       = 8/8 on Brier

FULL vs STATE
  pooled LogLoss delta = -0.009612
  pooled Brier delta   = -0.006070
  better seasons       = 8/8 on LogLoss
  better seasons       = 8/8 on Brier
```

Interpretation:

- possession-start state contains large, repeatable probability information;
- broad leakage-safe offense/defense quality adds smaller but highly consistent incremental information after state is controlled;
- pregame team quality is therefore justified in the mechanistic drive model.

The FULL model's pooled class-frequency calibration was also close:

```text
TOUCHDOWN          observed 26.67% | predicted 26.34% | gap -0.33 pp
FIELD_GOAL         observed  9.53% | predicted  8.72% | gap -0.81 pp
PUNT               observed 37.30% | predicted 38.34% | gap +1.03 pp
TURNOVER           observed  9.20% | predicted  9.52% | gap +0.32 pp
DOWNS              observed  6.76% | predicted  5.96% | gap -0.80 pp
MISSED_FIELD_GOAL  observed  3.04% | predicted  2.99% | gap -0.04 pp
PERIOD_END         observed  6.26% | predicted  6.72% | gap +0.46 pp
RETURN_TOUCHDOWN   observed  1.09% | predicted  1.23% | gap +0.14 pp
SAFETY             observed  0.15% | predicted  0.17% | gap +0.02 pp
```

These are aggregate calibration checks, not a substitute for conditional calibration diagnostics later.

## Command

```bash
python -m cfb_analytics.analytics.drive_outcome_model
```

Optional outer-season override:

```bash
python -m cfb_analytics.analytics.drive_outcome_model --test-seasons 2021,2022,2023,2024,2025
```

## What comes next

The flat FULL multinomial model is now the baseline to beat. The next challenger exploits football structure without changing the information set or tuning regularization:

```text
root
  -> offensive score
  -> non-scoring end
  -> opponent score
  -> period end

conditional branches
  offensive score -> TD vs FG
  non-scoring end -> punt vs turnover vs downs vs missed FG
  opponent score  -> return TD vs safety
```

The hierarchical model must beat the **same flat FULL baseline on the same outer-season rows** using log loss and Brier score. If it does not, the flat model remains the mechanistic probability baseline.