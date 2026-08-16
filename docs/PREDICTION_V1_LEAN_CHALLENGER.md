# Prediction v1 Lean Challenger

**Status:** SCREENED — NOT PROMOTED  
**Version:** `prediction-v1-lean-challenger-v1-development-selected`

## Purpose

After correcting historical game targets and recomputing SRS from authoritative CFBD `games.json` results, the Prediction v1 integrity audit found that the corrected FULL model contains several weak or redundant terms.

The goal of this challenger was not to search arbitrary feature combinations. It asked one narrower question:

> Can a feature-pruned version of the corrected Prediction v1 architecture improve out-of-sample stability while retaining the clearly useful SRS and MWDR families?

## Corrected-data prerequisite

The challenger ran only after the authoritative-target feature-store rebuild and a passing target-integrity audit.

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

Feature selection used only these outer test seasons:

```text
2018
2019
2021
2022
```

at both minimum-prior-games thresholds 3 and 4, for **8 development folds** total.

For every FULL feature, fit the same model with exactly that one feature removed. A feature entered the frozen prune set only if all of the following were true on those development folds:

1. mean drop-model MAE delta vs FULL was negative;
2. mean drop-model RMSE delta vs FULL was negative;
3. dropping the feature improved MAE in at least 5 of 8 folds;
4. dropping the feature improved RMSE in at least 5 of 8 folds.

No 2023–2025 fold was used by this pruning rule.

All qualifying features were removed together to create exactly one LEAN challenger. There was no combinatorial subset search.

## Volume-engine revalidation result

The corrected FULL model was rechecked against STABLE on the six recent 2023–2025 min3/min4 folds.

```text
STABLE - FULL
mean MAE delta   +0.0053
mean RMSE delta  +0.0067
winner delta     +0.00 pp
STABLE MAE wins   2/6
STABLE RMSE wins  1/6
```

Positive `STABLE - FULL` deltas mean FULL was better. The volume engine therefore survived the corrected-target revalidation: FULL improved recent mean MAE and RMSE, and beat STABLE on RMSE in 5 of 6 folds. The gain is small, so the volume block remains part of the incumbent architecture but should not be treated as a large effect.

## Frozen development prune set

The development-only rule selected:

```text
away_iterativeFieldPositionEdge
away_iterativeFinishingEdge
home_iterativeYardsPerPossessionEdge
turnoverVolumeEdge
```

This reduced the model from 19 to 15 features.

## Recent validation result

The frozen LEAN model was evaluated once on the six recent 2023–2025 min3/min4 folds.

```text
LEAN - FULL
mean MAE delta   +0.0205
mean RMSE delta  +0.0217
winner delta     +0.35 pp
MAE better        2/6
RMSE better       1/6
worst MAE delta  +0.0556
worst RMSE delta +0.0517
```

The 2024 and 2025 folds were consistently worse under LEAN. The small winner-accuracy increase did not compensate for worse proper margin-error metrics.

## Decision

**LEAN is not promoted.**

Do not remove the four development-selected features from the corrected FULL benchmark and do not tune alternate prune combinations against the already-inspected recent folds.

The corrected FULL VOLUME + OLS architecture remains the incumbent candidate.

The failure is informative: apparent drop-one redundancy on older folds did not combine into a more stable recent model. This points away from ad hoc deletion and toward a structural reparameterization that represents the same football information with fewer redundant degrees of freedom.

## Next structural challenger

The next predeclared experiment is a symmetry-oriented parameterization:

```text
paired home/away Iterative edges
  -> one net matchup edge per football family

home_MWDR_OffenseEdge + home_MWDR_DefenseEdge
  -> one net MWDR edge

keep
  srsEdge
  mwdrXExpectedPossessions
  successVolumeEdge
  explosiveVolumeEdge
  turnoverVolumeEdge
```

This directly tests whether reducing collinearity by construction can preserve or improve OOS accuracy without adding model complexity.
