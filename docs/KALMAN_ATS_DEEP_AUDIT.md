# Kalman ATS Deep Audit

Status: exploratory diagnosis of an already-discovered row. This is **not** independent confirmation evidence and does not modify the frozen 2026 ATS logistic challenger.

## Candidate under audit

The dynamic model zoo produced one potentially interesting Kalman row:

- model: `KALMAN`
- eligibility: `minGames=4`
- direct ATS confidence threshold: `0.55`
- historical screen: 67-56-3, 54.47% ATS, +3.99% flat -110 ROI

The corresponding `minGames=3` result was poor, so this audit is specifically designed to determine whether the difference is tied to current-season information depth or simply noise.

## Frozen audit settings

No parameter is tuned here. The audit reuses the exact dynamic-zoo settings:

- offseason carry: 50%
- initial variance: 100
- process variance per rating period: 4
- observation variance: `14^2`
- non-neutral HFA: 2.5 points
- ATS layer: `StandardScaler + LogisticRegression(C=0.5, max_iter=2000, random_state=42)`
- primary threshold: 0.55

## Diagnostics

The report includes:

- pooled min3 and min4 performance at 0.55
- season-by-season min4 stability
- Wilson 95% intervals and one-sided test versus the 52.381% -110 break-even rate
- home vs away selections
- favorite vs underdog selections
- spread buckets
- week buckets
- neutral/non-neutral splits
- confidence and probability calibration
- eligibility-depth buckets
- max drawdown and longest losing streak
- standardized logistic coefficient stability across outer folds

### Critical min3-depth decomposition

The audit also holds the **min3-fitted model fixed** and divides its 0.55-confidence bets into:

- `MIN3_ONLY_EXACTLY_3`: at least one team had exactly three prior current-season games
- `MIN3_MODEL_ON_4PLUS`: both teams already had four or more prior games

That test distinguishes a genuine information-depth issue from a trivial comparison of two separately fitted min3/min4 logistic models.

## Run

```bash
python -m cfb_analytics.analytics.kalman_ats_deep_audit --overwrite
```

Outputs:

```text
data/processed/market_benchmark/kalman-ats-deep-audit.json
data/processed/market_benchmark/kalman-ats-deep-audit-games.json
```

Do not promote or tune a Kalman strategy based solely on this audit. If the signal survives, the next step is a separately named challenger, preferably testing one predeclared `FULL ATS logistic + Kalman strength + Kalman uncertainty` architecture.
