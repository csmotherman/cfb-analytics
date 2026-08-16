# Prediction v1 Lean Challenger

**Status:** RESEARCH CHALLENGER — DEVELOPMENT/VALIDATION SPLIT  
**Version:** `prediction-v1-lean-challenger-v1-development-selected`

## Purpose

After correcting historical game targets and recomputing SRS from authoritative CFBD `games.json` results, the Prediction v1 integrity audit found that the corrected FULL model contains several weak or redundant terms.

The goal of this challenger is not to search arbitrary feature combinations. It asks one narrower question:

> Can a feature-pruned version of the corrected Prediction v1 architecture improve out-of-sample stability while retaining the clearly useful SRS and MWDR families?

## Corrected-data prerequisite

Run this challenger only after the authoritative-target feature-store rebuild and a passing target-integrity audit.

The corrected feature store uses:

```text
raw CFBD games.json final result
  -> target_homeScore
  -> target_awayScore
  -> target_margin
  -> target_homeWin
  -> recomputed leakage-safe SRS
```

The non-score Iterative ratings and saved Football Mechanisms matchups are reused.

## Incumbent architecture

```text
BASE
  Iterative matchup features
  SRS

MWDR
  home_MWDR_OffenseEdge
  home_MWDR_DefenseEdge
  mwdrXExpectedPossessions

VOLUME
  successVolumeEdge
  explosiveVolumeEdge
  turnoverVolumeEdge

FULL = BASE + MWDR + VOLUME
```

The integrity audit on corrected data showed:

- SRS was the strongest drop-one feature and had the expected coefficient sign in all 14 stability folds;
- removing the entire MWDR family worsened recent MAE in all 6 min3/min4 2023–2025 folds;
- the MWDR x expected-possessions interaction was also strongly supported by the 14-fold drop-one screen;
- several weaker terms improved mean MAE and RMSE when removed in the pooled 14-fold diagnostic.

Because MWDR components are highly correlated with `mwdrXExpectedPossessions`, individual MWDR coefficient signs are not interpreted causally. Family-level OOS ablation is the decision mechanism.

## Development-only pruning rule

Feature selection uses only these outer test seasons:

```text
2018
2019
2021
2022
```

at both minimum-prior-games thresholds 3 and 4, for **8 development folds** total.

For every FULL feature, fit the same model with exactly that one feature removed. A feature enters the frozen prune set only if all of the following are true on those development folds:

1. mean drop-model MAE delta vs FULL is negative;
2. mean drop-model RMSE delta vs FULL is negative;
3. dropping the feature improves MAE in at least 5 of 8 folds;
4. dropping the feature improves RMSE in at least 5 of 8 folds.

No 2023–2025 fold is used by this pruning rule.

All qualifying features are removed together to create exactly one LEAN challenger. There is no combinatorial subset search.

## Recent validation gate

The frozen LEAN feature set is then evaluated on:

```text
2023
2024
2025
```

at minimum-prior-games 3 and 4, for **6 recent validation folds**.

LEAN is promotion-eligible only if:

1. mean MAE delta vs FULL is negative;
2. mean RMSE delta vs FULL is negative;
3. LEAN improves MAE in at least 4 of 6 folds;
4. LEAN improves RMSE in at least 4 of 6 folds.

Winner accuracy remains secondary context.

These recent seasons have been inspected elsewhere in the project, so this is not a claim that they are a pristine never-seen final test set. The purpose of the split is narrower: they are not allowed to choose the prune set in this challenger.

## Volume-engine revalidation

The same command also rechecks the corrected FULL model against STABLE on the six recent folds:

```text
STABLE = BASE + MWDR
FULL   = STABLE + success/explosive/turnover volume
```

This is necessary because the original volume-engine selection was performed before the authoritative target correction. If corrected FULL no longer improves both recent mean MAE and RMSE relative to STABLE, the VOLUME + OLS architecture requires reconsideration even if the lean-pruning experiment is interesting.

## Runtime contract

The challenger is saved-data only.

For each of the 14 development/validation folds it prepares the standardized cross-product matrix and FULL baseline once. All drop-one fits reuse those cached fold matrices. The script does not replay PBP, rebuild profiles, regenerate sandbox components, or fit drive-outcome models.

Run:

```bash
python -m cfb_analytics.analytics.prediction_v1_lean_challenger
```

## Interpretation

A passing LEAN result does not silently replace Prediction v1. It advances the lean feature contract to a formal corrected-benchmark comparison and documentation step.

A failing LEAN result means the corrected FULL architecture remains the incumbent candidate and the project should move to a structurally different challenger rather than tuning arbitrary prune combinations against recent holdouts.

One high-priority structural challenger after this screen is a symmetry-oriented parameterization of paired home/away matchup features (for example net matchup edges) to reduce redundancy and coefficient instability without adding model complexity.
