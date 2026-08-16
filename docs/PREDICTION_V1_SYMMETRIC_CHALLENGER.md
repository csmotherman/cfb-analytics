# Prediction v1 Symmetric Net Challenger

**Status:** RESEARCH CHALLENGER — FIXED STRUCTURAL REPARAMETERIZATION  
**Version:** `prediction-v1-symmetric-net-v1`

## Why this test exists

The corrected Prediction v1 integrity audit showed that several paired Iterative features are strongly correlated:

```text
home YPP <> home yards/possession       r ~= 0.85
away YPP <> away yards/possession       r ~= 0.85
home success <> home yards/possession   r ~= 0.83
away success <> away yards/possession   r ~= 0.83
```

The MWDR family is also highly collinear with its expected-possession interaction:

```text
home MWDR defense <> MWDR x possessions r ~= 0.90
home MWDR offense <> MWDR x possessions r ~= 0.89
```

A development-selected four-feature LEAN model failed recent validation, so the project will not continue tuning arbitrary prune combinations against inspected holdouts.

This challenger instead asks a structural question:

> Can Prediction v1 represent the same football information with fewer redundant degrees of freedom by using net matchup edges?

## Fixed transformation

The six paired Iterative families are transformed from separate home and away matchup edges into one net edge each:

```text
netIterativeSuccessEdge
  = home_iterativeSuccessEdge
  - away_iterativeSuccessEdge

netIterativeExplosiveEdge
  = home_iterativeExplosiveEdge
  - away_iterativeExplosiveEdge

netIterativeYardsPerPlayEdge
  = home_iterativeYardsPerPlayEdge
  - away_iterativeYardsPerPlayEdge

netIterativeYardsPerPossessionEdge
  = home_iterativeYardsPerPossessionEdge
  - away_iterativeYardsPerPossessionEdge

netIterativeFinishingEdge
  = home_iterativeFinishingEdge
  - away_iterativeFinishingEdge

netIterativeFieldPositionEdge
  = home_iterativeFieldPositionEdge
  - away_iterativeFieldPositionEdge
```

Higher net values favor the home team under the existing Iterative matchup-direction contract.

MWDR is collapsed from two raw matchup edges into one net home advantage:

```text
netMwdrEdge
  = home_MWDR_OffenseEdge
  + home_MWDR_DefenseEdge
```

The already-supported possessions interaction remains:

```text
mwdrXExpectedPossessions
```

The volume engine is retained unchanged because corrected FULL revalidated against STABLE on recent mean MAE and RMSE.

## Candidate feature contract

```text
6 net Iterative matchup edges
srsEdge
netMwdrEdge
mwdrXExpectedPossessions
successVolumeEdge
explosiveVolumeEdge
turnoverVolumeEdge
```

Total:

```text
FULL       19 features
SYMMETRIC  12 features
```

No feature selection, hyperparameter search, or holdout-driven combination search is performed.

## Evaluation protocol

The challenger uses the corrected authoritative-target feature stores and identical FULL-eligible game rows.

Estimator and walk-forward protocol remain unchanged:

- OLS;
- equal game weights;
- all prior available seasons for each holdout;
- min-prior-games 3 and 4;
- same signed home-margin target;
- same corrected SRS;
- same 2020 omission;
- same season-reset behavior.

Outer evaluation seasons:

```text
2018
2019
2021
2022
2023
2024
2025
```

at min3 and min4, for 14 folds.

The recent forward-facing subset is 2023–2025 at min3/min4, for 6 folds.

## Promotion gate

SYMMETRIC advances only if all of the following hold:

1. mean MAE vs FULL improves across all 14 folds;
2. mean RMSE vs FULL improves across all 14 folds;
3. MAE improves in at least 8 of 14 folds;
4. RMSE improves in at least 8 of 14 folds;
5. mean MAE improves on the 6 recent folds;
6. mean RMSE improves on the 6 recent folds;
7. MAE improves in at least 4 of 6 recent folds;
8. RMSE improves in at least 4 of 6 recent folds.

Winner accuracy is secondary context.

The script also reports standardized coefficient sign stability for the 12 symmetric features and pairwise correlation diagnostics. These are interpretability/stability diagnostics, not substitutes for OOS error improvement.

## Runtime

This is a saved-data-only linear-model experiment. It does not rebuild PBP, profiles, sandbox components, drive models, or feature stores.

Run:

```bash
python -m cfb_analytics.analytics.prediction_v1_symmetric_challenger
```

## Interpretation

If SYMMETRIC passes, it becomes a strong Prediction-v2 candidate because it would improve OOS accuracy while reducing the model from 19 to 12 terms and making the matchup structure more interpretable.

If it fails, retain corrected FULL and stop trying to solve the remaining error with algebraic reshuffling of the same information. The next research step should introduce a genuinely different information source, with home-field/neutral-site context and early-season priors among the highest-priority candidates.
