# Prediction v1 Integrity & Stability Audit

**Status:** ACTIVE RESEARCH GATE  
**Version:** `prediction-v1-integrity-audit-v1`

## Why this exists

Prediction v1 remains the locked research benchmark, but recent drive-state forensics exposed two reasons to re-audit the current game model before adding more features:

1. the oriented model target is reconstructed from canonical play score state, while raw CFBD `games.json` already contains the authoritative final game result;
2. MWDR is built from the legacy `_points(d)` derived-drive score-delta helper, whose score semantics are now known to require caution.

The correct response is not to discard Prediction v1. It is to quantify whether either dependency materially affects the benchmark and to measure which current features are actually stable out of sample.

## Cheap-data contract

This audit reads only saved artifacts:

- raw CFBD `games.json` partitions;
- saved model feature stores;
- saved Football Mechanisms matchup files.

It does **not** replay play-by-play, rebuild profiles, rebuild snapshots, or fit the drive-outcome model.

## Gate 1 — target integrity

For every stored model row, compare:

```text
model target_homeScore
model target_awayScore
model target_margin
```

against the final score in raw CFBD `games.json`.

The raw score extractor supports the known/candidate score-field spellings and reports which schema is actually present rather than silently assuming one.

The audit reports:

- raw game count;
- stored model-row count;
- scored games matched by game ID;
- exact final-score matches;
- exact margin matches;
- missing raw final scores;
- conflicting duplicate raw game IDs;
- mismatch examples by season.

The default all-in-one audit stops before model-selection work if the target-margin contract fails. A target problem must be fixed before feature optimization.

## Gate 2 — MWDR dependency

On the exact current Prediction-v1 common sample, compare:

```text
CURRENT FULL
  Iterative + SRS
  + MWDR offense/defense edges
  + MWDR x expected possessions
  + Success/Explosive/Turnover volume edges

NO_MWDR
  Iterative + SRS
  + Success/Explosive/Turnover volume edges

MWDR_NO_INTERACTION
  Iterative + SRS
  + MWDR offense/defense edges
  + Success/Explosive/Turnover volume edges
```

Evaluation uses the same six recent holdouts already used by Prediction-v1 research:

```text
2023, 2024, 2025 x minimum prior games 3 and 4
```

The reported delta is challenger minus CURRENT FULL, so negative MAE/RMSE means the simpler challenger is better.

This isolates two questions before any corrected-MWDR rebuild is attempted:

1. does the MWDR family still earn its place in the current model?
2. does the possessions interaction add anything beyond the raw MWDR matchup edges?

If MWDR does not add stable value, there is no reason to spend time rebuilding it. If it does add stable value, then a score-clean replacement becomes a high-priority challenger.

## Gate 3 — feature stability and pruning screen

Prediction v1 contains 19 modeled features. The stability screen uses expanding-season holdouts from 2018 onward at both min-3 and min-4 eligibility thresholds, producing 14 folds.

For each feature it records:

- standardized OLS coefficient in each fold;
- coefficient sign consistency;
- near-zero coefficient frequency;
- held-out MAE change when that feature is removed;
- held-out RMSE change when that feature is removed;
- number of folds where removal makes MAE/RMSE worse.

The drop-one delta is:

```text
reduced model - FULL model
```

so a positive value means the feature helped the full model.

The audit also reports the largest pooled pairwise feature correlations on the min-3 common sample. This is a collinearity diagnostic, not a promotion test.

A feature is printed as a **prune-screen candidate** only when removing it improves both mean MAE and mean RMSE across the stability folds. Nothing is automatically removed. Any candidate must then face a dedicated same-sample lean-model walk-forward challenger.

## Command

Run the complete gated audit:

```bash
python -m cfb_analytics.analytics.prediction_v1_integrity_audit
```

Target contract only:

```bash
python -m cfb_analytics.analytics.prediction_v1_integrity_audit --section targets
```

MWDR + stability diagnostics only, after the target contract is already known to pass:

```bash
python -m cfb_analytics.analytics.prediction_v1_integrity_audit --section model
```

## Decision sequence after the output

```text
TARGET fails
  -> fix authoritative game target first
  -> rebuild only the affected downstream target/model artifacts
  -> rerun Prediction v1 benchmark

TARGET passes + MWDR weak/harmful
  -> challenge a lean no-MWDR Prediction v1 candidate

TARGET passes + MWDR helpful
  -> build a score-clean semantic/authoritative MWDR challenger
  -> compare current MWDR vs replacement on the exact same sample

STABILITY identifies redundant features
  -> build one predeclared lean/core challenger
  -> do not delete features one by one based on outer holdout peeking

No strong pruning signal
  -> retain Prediction v1 feature set
  -> move next to site-aware/HFA and early-season priors
```

## Promotion discipline

This audit is diagnostic. It cannot itself create Prediction v2.

Any replacement must still satisfy the locked benchmark policy: leakage-safe walk-forward evaluation, identical common samples, paired MAE/RMSE as primary metrics, per-holdout reporting, recent-era stability, and no tuning against the held-out season.
