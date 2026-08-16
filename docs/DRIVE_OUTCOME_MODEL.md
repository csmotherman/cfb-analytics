# Drive Outcome Probability Benchmark

**Status:** RESEARCH ONLY  
**Version:** `drive-outcome-multinomial-v1-expanding-season`

## Purpose

Drive State Research v2 established a trustworthy possession-level contract:

```text
raw drive-start state + leakage-safe pregame team quality -> categorical driveResult
```

The first model benchmark asks two separate questions:

1. Does possession-start football state predict the eventual drive outcome better than unconditional class frequencies?
2. After controlling for that state, does pregame offense/defense quality add stable out-of-sample probability information?

Prediction v1 and the existing historical simulator remain unchanged.

## Full-corpus audit

The regulation-only v2 materialization covers 2014-2019 and 2021-2025. Across those seasons the saved corpus contains about 207k drive rows. Start yards-to-goal, score margin, and clock have complete coverage in every audited season. Pregame quality coverage is about 91% because Week 1 and other zero-history states intentionally remain missing rather than leaking future information.

Raw `driveResult` spellings are not perfectly stable across CFBD seasons. For example, 2021 contains `RUSHING TD`, `PASSING TD`, `FG GOOD`, `FG MISSED`, and `INT RETURN TOUCH`. The benchmark normalizes these exact raw labels at load time to their semantic v2 families. It does not require rewriting the saved drive-state files and does not drop those rows.

`Uncategorized` and other genuinely unresolved source outcomes remain `OTHER` rather than being silently forced into a football class.

## Outcome classes

The benchmark predicts the following fixed probability vector:

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
OTHER
```

Rare classes are retained. No class-weighting is used in the first benchmark because the primary goal is calibrated probability estimation, not balanced classification accuracy.

## Models

### GLOBAL

Training-set class frequencies with light Dirichlet smoothing. This is the minimum probability benchmark.

### STATE

Regularized multinomial logistic regression using only information available when the possession begins:

- period;
- start clock;
- yards to goal with simple nonlinear field-position basis terms;
- offense-minus-defense score margin;
- leading/tied/trailing state;
- home-offense indicator;
- late-half clock pressure.

### FULL

`STATE` plus leakage-safe pregame team quality:

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

Missing pregame quality is imputed using **training-only** field means. A missingness indicator is added for every imputed field, and games played before the current partition are retained so the model can distinguish zero-history/early-season states. No test row is dropped for missing pregame quality.

## Validation

Evaluation is expanding-season walk-forward. For each outer test season, every earlier available season is training data and the entire outer season is untouched test data.

Default outer seasons:

```text
2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025
```

This gives multiple historical regime tests instead of optimizing only against the most recently inspected seasons. The 2020 season remains absent under the repository corpus contract.

Primary metrics:

- multiclass log loss;
- multiclass Brier score.

Secondary diagnostics:

- top-class accuracy;
- pooled observed versus predicted frequency for every outcome class.

Promotion logic is sequential:

```text
STATE must beat GLOBAL
then
FULL must beat STATE
```

Negative metric deltas are improvements. Pregame team quality should not enter the mechanistic simulator unless FULL produces stable proper-score gains across outer seasons and in the pooled result.

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

If the transparent multinomial benchmark works, the next challenger should exploit football structure rather than immediately jumping to a black-box model. A natural hierarchy is:

```text
possession outcome family
  -> offensive score vs non-score vs opponent score vs period end
  -> TD vs FG conditional on offensive score
  -> punt vs turnover vs downs vs missed FG conditional on non-score
  -> return TD vs safety conditional on opponent score
```

That hierarchy is promoted only if it improves walk-forward probability scores and calibration. Game simulation comes after the drive probability model itself is validated.
