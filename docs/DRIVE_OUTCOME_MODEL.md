# Drive Outcome Probability Benchmark

**Status:** RESEARCH ONLY  
**Version:** `drive-outcome-multinomial-v1-convergence-verified`

## Purpose

Drive State Research v2 established a trustworthy possession-level contract:

```text
raw drive-start state + leakage-safe pregame team quality -> categorical driveResult
```

The first model benchmark asks two questions:

1. Does possession-start football state predict the eventual drive outcome better than unconditional class frequencies?
2. After controlling for that state, does pregame offense/defense quality add stable out-of-sample probability information?

Prediction v1 and the existing historical simulator remain unchanged.

## Full-corpus audit

The regulation-only v2 materialization covers 2014-2019 and 2021-2025 and contains about 207k drive rows. Start yards-to-goal, score margin, and clock have complete coverage in every audited season. Pregame quality coverage is about 91% because Week 1 and other zero-history states intentionally remain missing rather than leaking future information.

Raw `driveResult` spellings are not perfectly stable across CFBD seasons. The benchmark therefore normalizes known semantic aliases at load time, including:

- `RUSHING TD`, `PASSING TD`, `END OF HALF TD`, `END OF GAME TD` -> `TOUCHDOWN`;
- `FG GOOD` -> `FIELD_GOAL`;
- `FG MISSED` -> `MISSED_FIELD_GOAL`;
- `INT RETURN TOUCH` -> `RETURN_TOUCHDOWN`.

This uses the exact preserved raw label and does not require regenerating the saved drive-state corpus.

## Unresolved targets

`Uncategorized` and other genuinely unresolved raw outcomes are not a football outcome class. They stay preserved in the research corpus, but are excluded from model fitting and proper-score evaluation and are reported explicitly as semantic-target coverage loss.

This matters because unresolved labels are not stationary across seasons: for example, 2018 contains a much larger `Uncategorized` block than most seasons. Treating that source-quality artifact as a football class would distort log loss and Brier score.

Missing **predictors** are handled differently: no test row with a resolved outcome is dropped because of missing pregame quality.

## Modeled outcome classes

The fixed probability vector is:

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

Rare but valid football outcomes are retained. No class weighting is used in the first benchmark because the primary goal is calibrated probability estimation, not balanced classification accuracy.

## Models

### GLOBAL

Training-set class frequencies with light Dirichlet smoothing.

### STATE

Regularized multinomial logistic regression using only information known at possession start:

- period;
- start clock;
- yards to goal with simple nonlinear field-position basis terms;
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

Missing pregame quality is imputed using **training-only** field means. A missingness indicator is added for every imputed field, and games played before the current partition are retained so the model can distinguish early-season states.

## Optimizer and convergence contract

The first full walk-forward execution used `lbfgs` with sparse standardization and hit the configured 1,200-iteration ceiling for every STATE and FULL fit. The resulting outer-season signal was directionally strong, but those exact scores are not eligible for promotion because the optimizer explicitly failed to converge.

The benchmark now uses:

```text
solver = newton-cholesky
C = 1.0
max_iter = 200
tol = 1e-7
```

The repository model dependency requires scikit-learn >=1.6, where `newton-cholesky` supports the full multinomial objective. This dataset has many more observations than encoded feature-by-class parameters, which makes that solver appropriate for the benchmark geometry.

Any `ConvergenceWarning` is now fatal. The benchmark stops instead of printing proper scores from an unconverged model.

The optimizer change is a verification step, not a hyperparameter search. `C=1.0`, features, outer seasons, imputation logic, and evaluation metrics remain unchanged so the rerun can determine whether the earlier signal survives a converged fit.

## Preliminary unconverged run

The first execution produced the following directional outer-season result before convergence verification was added:

```text
STATE vs GLOBAL
  pooled LogLoss delta = -0.218756
  pooled Brier delta   = -0.070116
  better seasons       = 8/8 on both primary metrics

FULL vs STATE
  pooled LogLoss delta = -0.009659
  pooled Brier delta   = -0.006081
  better seasons       = 8/8 on both primary metrics
```

Pooled FULL class-frequency calibration was also close in aggregate, with the largest displayed gap about +1.03 percentage points for PUNT. These results are promising but remain **preliminary/unpromoted** until reproduced by converged fits.

## Validation

Evaluation is expanding-season walk-forward. For each outer test season, every earlier available season is training data and the entire outer season is untouched test data.

Default outer seasons:

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
- pooled observed versus predicted frequency for every modeled outcome class.

Promotion logic is sequential:

```text
STATE must beat GLOBAL
then
FULL must beat STATE
```

Negative metric deltas are improvements. Pregame team quality should not enter the mechanistic simulator unless FULL produces stable proper-score gains across outer seasons and in the pooled result **from converged fits**.

## Command

The benchmark reads the already-materialized drive-state corpus. It does not replay play-by-play, regenerate profiles, or rebuild snapshots.

```bash
python -m cfb_analytics.analytics.drive_outcome_model
```

Optional outer-season override:

```bash
python -m cfb_analytics.analytics.drive_outcome_model --test-seasons 2021,2022,2023,2024,2025
```

The optional model dependencies are required:

```bash
pip install -e ".[models]"
```

## What comes next

If the converged transparent multinomial benchmark reproduces the signal, the next challenger should exploit football structure rather than immediately jumping to a black-box model:

```text
possession outcome family
  -> offensive score vs non-score vs opponent score vs period end
  -> TD vs FG conditional on offensive score
  -> punt vs turnover vs downs vs missed FG conditional on non-score
  -> return TD vs safety conditional on opponent score
```

That hierarchy is promoted only if it improves walk-forward probability scores and calibration. Game simulation comes after the drive probability model itself is validated.
