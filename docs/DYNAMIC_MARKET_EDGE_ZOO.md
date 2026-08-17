# Dynamic Market Edge Model Zoo

Status: exploratory model-family screen. It does not modify Prediction v2 or the frozen ATS logistic challenger.

## Predeclared families

- `ELO`: classic win/loss Elo, K=20, 55 Elo-point non-neutral home advantage
- `MOV_ELO`: same Elo system with a bounded log margin-of-victory update multiplier
- `GLICKO`: Glicko-1-style rating plus rating deviation, updated by rating period
- `KALMAN`: Gaussian latent team strength with process variance and margin observations

Common offseason carry is fixed at 50% toward the population mean before results are seen.

## Leakage boundary

For every season partition/week:

1. uncertainty/state drift is applied,
2. every game in the partition receives a pregame dynamic signal,
3. only after every prediction is recorded are the partition results allowed to update states.

Therefore a target game cannot update its own rating input, and one game in a partition cannot alter another prediction from the same partition.

Dynamic states use all completed historical games. Evaluation still uses the project's locked chronological outer test seasons. For each outer test season, any margin calibration or ATS logistic layer is fit only on earlier seasons.

## Two questions per dynamic family

### Calibrated margin

A fixed `StandardScaler + Ridge(alpha=10)` maps each model's pregame strength/uncertainty signal to final home margin. It is compared with the historical CFBD reference spread on MAE, RMSE and ATS disagreement.

### Direct ATS probability

A fixed `StandardScaler + LogisticRegression(C=0.5)` predicts home-cover probability from:

- dynamic strength,
- dynamic uncertainty,
- market spread,
- absolute spread,
- home-favorite indicator,
- week,
- neutral-site indicator.

The predeclared confidence thresholds are 0.55, 0.575 and 0.60.

## Run

```bash
python -m cfb_analytics.analytics.dynamic_market_edge_zoo --overwrite
```

Outputs:

```text
data/processed/market_benchmark/dynamic-market-edge-zoo.json
data/processed/market_benchmark/dynamic-market-edge-zoo-games.json
```

The terminal report prints pooled margin performance, pooled ATS results, and season stability at the 0.575 threshold.

Any attractive row remains discovery evidence. A survivor must be frozen under a new name before it can be treated as a confirmation/prospective challenger.
