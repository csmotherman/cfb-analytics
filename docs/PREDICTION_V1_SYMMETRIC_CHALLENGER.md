# Prediction v1 Symmetric Net Challenger

**Status:** SCREENED — NOT PROMOTED  
**Version:** `prediction-v1-symmetric-net-v1`

## Purpose

After the authoritative target repair and corrected-SRS rebuild, the Prediction v1 stability audit showed substantial redundancy among the paired home/away Iterative features and the MWDR family. A development-selected LEAN deletion experiment failed recent validation, so the next test used a fixed structural reparameterization rather than more holdout-driven pruning.

The challenger asked:

> Can Prediction v1 represent the same football information with fewer redundant degrees of freedom by using net matchup edges?

## Fixed transformation

The six paired Iterative families were transformed from separate home and away matchup edges into one net edge each:

```text
netIterativeSuccessEdge
  = home_iterativeSuccessEdge - away_iterativeSuccessEdge

netIterativeExplosiveEdge
  = home_iterativeExplosiveEdge - away_iterativeExplosiveEdge

netIterativeYardsPerPlayEdge
  = home_iterativeYardsPerPlayEdge - away_iterativeYardsPerPlayEdge

netIterativeYardsPerPossessionEdge
  = home_iterativeYardsPerPossessionEdge - away_iterativeYardsPerPossessionEdge

netIterativeFinishingEdge
  = home_iterativeFinishingEdge - away_iterativeFinishingEdge

netIterativeFieldPositionEdge
  = home_iterativeFieldPositionEdge - away_iterativeFieldPositionEdge
```

MWDR was collapsed to:

```text
netMwdrEdge
  = home_MWDR_OffenseEdge + home_MWDR_DefenseEdge
```

The candidate retained:

```text
srsEdge
mwdrXExpectedPossessions
successVolumeEdge
explosiveVolumeEdge
turnoverVolumeEdge
```

Feature count:

```text
FULL       19
SYMMETRIC  12
```

No feature selection or hyperparameter search was performed.

## Evaluation protocol

The challenger used the corrected authoritative-target feature stores and the exact FULL-eligible game rows.

Estimator and walk-forward protocol remained unchanged:

- OLS;
- equal game weights;
- all prior available seasons for each holdout;
- minimum-prior-games 3 and 4;
- authoritative signed home-margin target;
- corrected leakage-safe SRS;
- 2020 omitted;
- season reset preserved.

Outer seasons were 2018, 2019, 2021, 2022, 2023, 2024, and 2025 at min3/min4, for 14 folds total. The recent subset was 2023–2025 at min3/min4, for 6 folds.

## Predeclared promotion gate

SYMMETRIC required all of the following:

1. lower mean MAE across all 14 folds;
2. lower mean RMSE across all 14 folds;
3. at least 8/14 MAE wins;
4. at least 8/14 RMSE wins;
5. lower recent mean MAE;
6. lower recent mean RMSE;
7. at least 4/6 recent MAE wins;
8. at least 4/6 recent RMSE wins.

Winner accuracy was secondary context.

## Result

```text
ALL 14
  mean MAE delta     -0.0246
  mean RMSE delta    -0.0143
  winner delta       +0.13 pp
  MAE better          10/14
  RMSE better          7/14

RECENT 6
  mean MAE delta     -0.0141
  mean RMSE delta    -0.0108
  winner delta       +0.50 pp
  MAE better           4/6
  RMSE better          3/6
```

The candidate improved pooled average MAE and RMSE, including the recent pooled averages, but failed the stability gate because RMSE improved in only 7/14 overall folds and 3/6 recent folds. Both 2025 MAE folds were worse under SYMMETRIC.

## Coefficient / correlation diagnostic

Most net Iterative features had cleaner directional coefficient behavior than the original paired parameterization. However, MWDR remained structurally redundant:

```text
netMwdrEdge <> mwdrXExpectedPossessions
r = +0.997
```

The coefficient on `netMwdrEdge` was negative in 13/14 folds while the interaction was positive in 14/14 folds. Given their near-perfect correlation, those individual signs are not interpreted causally.

## Decision

**SYMMETRIC is not promoted.**

The corrected FULL VOLUME + OLS architecture remains the incumbent candidate.

Do not tune alternate net definitions, relax the gate, or search combinations against the already-inspected holdouts. The symmetric experiment was useful because it showed that algebraic compression can improve pooled error while still failing year-to-year stability. That is not enough evidence for a benchmark replacement.

## Next direction

Stop rearranging the same information. The next challenger should add a genuinely different pregame information source.

The first candidate is site context:

```text
home-field game
vs
neutral-site game
```

Before fitting a site-aware model, audit the actual raw CFBD `games.json` schema and historical neutral-site coverage. If coverage is adequate, the preferred next test is a leakage-safe site-aware SRS / home-field model rather than merely adding another arbitrary feature to the final OLS.
