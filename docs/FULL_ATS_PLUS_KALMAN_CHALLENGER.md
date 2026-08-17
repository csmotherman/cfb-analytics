# FULL ATS Logistic + Kalman Challenger

Status: exploratory post-discovery challenger. This does **not** modify the frozen 2026 ATS logistic artifact.

## Research question

Does adding only two leakage-safe state-space features improve the already-selected FULL ATS logistic model?

Baseline:

- Prediction v2 football features + market/context features
- `StandardScaler + LogisticRegression(C=0.5, max_iter=2000, random_state=42)`
- `minGames=3`
- confidence threshold `0.575`

Challenger:

- exact same baseline features and architecture
- plus `KALMAN_strength`
- plus `KALMAN_uncertainty`
- same `minGames=3`
- same confidence threshold `0.575`

No Kalman parameter, logistic hyperparameter, eligibility threshold, or betting threshold is tuned in this experiment.

## Baseline reproduction guard

The script refuses to compare models unless the historical baseline reproduces the already-observed discovery record exactly:

- 495 bets
- 265 wins
- 220 losses
- 10 pushes

This prevents an accidental sample or market-data shift from being mistaken for a Kalman improvement.

## Leakage contract

Kalman signals come from `dynamic_market_edge_zoo.build_dynamic_signals`.

For every rating period, all games are scored before any result from that period updates the Kalman state. The outer ATS logistic fold for each official test season is then fit only on eligible seasons strictly earlier than the target season.

Baseline and challenger are trained and evaluated on the exact same rows.

## Evaluation

The report includes:

- pooled baseline vs challenger ATS accuracy and flat -110 ROI
- pooled Brier score and calibration
- season-by-season 2018, 2019, 2021-2025 results
- recent 2023-2025 results
- bet-selection overlap
  - both models bet
  - same side vs opposite side
  - baseline-only bets
  - challenger-only bets
- standardized Kalman coefficient stability across the seven outer folds

Negative `deltaBrier` means the Kalman challenger improves probabilistic accuracy. Positive `deltaAccuracyPP` / `deltaRoiPP` means the challenger improves the selected betting rule.

## Run

```bash
python -m cfb_analytics.analytics.full_ats_plus_kalman_challenger --overwrite
```

Outputs:

```text
data/processed/market_benchmark/full-ats-plus-kalman-challenger.json
data/processed/market_benchmark/full-ats-plus-kalman-challenger-games.json
```

Because 2018-2025 outcomes were already used during earlier discovery, even a positive result here is not untouched confirmation evidence. The frozen 2026 ATS model remains unchanged regardless of this result.
