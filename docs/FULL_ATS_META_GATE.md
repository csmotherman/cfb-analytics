# FULL ATS Bet-Quality Meta Gate v1

Status: exploratory/post-discovery research. This branch does **not** modify the frozen 2026 ATS logistic artifact.

## Research question

Can the complete set of currently validated, leakage-safe pregame feature families identify **which existing FULL ATS candidate bets deserve action**?

The first-stage FULL model still chooses the side. The second-stage gate has only two actions:

- `BET` the exact side chosen by FULL
- `PASS`

It is never allowed to reverse the side.

## First-stage contract

The candidate universe is intentionally fixed to the already-selected FULL ATS rule:

```text
minGames = 3
FULL ATS confidence >= 0.575
StandardScaler + LogisticRegression(C=0.5)
```

The historical official OOS baseline must reproduce exactly:

```text
495 bets
265 wins
220 losses
10 pushes
```

The experiment fails closed if that record changes.

## Gate target

For each non-push FULL candidate bet:

```text
1 = FULL's selected side covered
0 = FULL's selected side failed to cover
```

Pushes are excluded from gate fitting but may be accepted/passed during evaluation and are graded as pushes in betting metrics.

## Gate features

"All features" means all **currently validated pregame-safe feature families**, not every stored column. IDs, targets, final scores, result fields, duplicate aliases, and arbitrary raw columns are intentionally excluded.

The gate receives:

1. all 26 existing FULL ATS inputs:
   - the 19 frozen Prediction-v2 football features
   - the 7 market/context features
2. all 9 predeclared dynamic offense/defense state features:
   - POINTS_OD home matchup / away matchup / uncertainty
   - YPP_OD home matchup / away matchup / uncertainty
   - SUCCESS_OD home matchup / away matchup / uncertainty
3. Kalman latent strength and uncertainty
4. first-stage outputs and information depth:
   - cross-fitted FULL home-cover probability
   - FULL confidence
   - FULL picked-side sign
   - home games played before
   - away games played before

Total: 42 gate inputs.

## Double cross-fitting / leakage contract

This is the critical part of the architecture.

A gate-training row may never contain an in-sample first-stage prediction.

For each source season `S`:

1. fit FULL only on eligible seasons `< S`,
2. predict season `S`,
3. retain only FULL candidates at confidence >= 0.575,
4. attach the pregame-safe state/context features,
5. save whether FULL's selected side ultimately covered.

Then, for each official gate test season `T`:

1. train the gate only on saved candidate rows from seasons `< T`,
2. score candidates in season `T`,
3. gate chooses BET/PASS,
4. the original FULL side is immutable.

2015-2017 cross-fitted FULL candidate predictions are used as warm-up gate-training examples. Official evaluation remains 2018, 2019, 2021-2025.

## Predeclared gate models

Only two models are tested:

### META_LOGISTIC

```text
StandardScaler
+
LogisticRegression(C=0.5, max_iter=2000, random_state=42)
```

### META_HIST_GB

```text
HistGradientBoostingClassifier(
    learning_rate=0.05,
    max_iter=150,
    max_leaf_nodes=15,
    min_samples_leaf=30,
    l2_regularization=1.0,
    random_state=42,
)
```

No model zoo and no hyperparameter search are performed in this experiment.

## Fixed BET/PASS threshold

The gate accepts a candidate only when:

```text
P(FULL pick covers | pregame features) >= 110 / 210
                                     >= 0.5238095238
```

This is the -110 break-even probability. It is economically defined and fixed before the historical evaluation. No gate threshold sweep is used for the primary decision rule.

## Diagnostics

For each gate model the report includes:

- pooled accepted ATS / ROI
- pooled passed ATS / ROI
- candidate retention rate
- season-by-season accepted/pass results
- 2023-2025 results
- gate Brier score for predicting whether the FULL pick is correct
- bankroll / maximum drawdown / losing streak for accepted bets
- fixed score buckets
- cumulative top-ranked bet-quality curve, diagnostic only
- standardized META_LOGISTIC coefficient stability across outer folds

The top-ranked cumulative curve is **not** a set of alternative betting thresholds. It is diagnostic evidence about whether higher gate scores actually rank better FULL candidates.

## Run

```bash
python -m cfb_analytics.analytics.full_ats_meta_gate --overwrite
```

Outputs:

```text
data/processed/market_benchmark/full-ats-meta-gate.json
data/processed/market_benchmark/full-ats-meta-gate-games.json
```

## Interpretation boundary

2018-2025 outcomes have already been used repeatedly in research. Even a strong result is post-discovery historical evidence, not untouched confirmation evidence. The committed 2026 ATS logistic model remains frozen regardless of this experiment. Any meta-gate survivor must be separately named and prospectively frozen before it can be treated as confirmation evidence.
