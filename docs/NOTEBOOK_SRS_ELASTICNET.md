# CFB Sandbox Notebook SRS + ElasticNet Model

## Purpose

This module reproduces the predictive model used in the supplied `CFB_Sandbox.ipynb` notebook as a separate model in the repository, then compares it with Prediction v2 on historical out-of-sample seasons.

Implementation:

```text
src/cfb_analytics/analytics/notebook_srs_elasticnet.py
```

Version:

```text
cfb-sandbox-notebook-srs-elasticnet-v1
```

Prediction v2 is not modified.

## Notebook model definition

The notebook creates four offensive game metrics for both teams, then takes home minus away:

- `SR_diff`: success rate difference, using 50% of yards-to-go on first down, 70% on second down, and 100% on third/fourth down.
- `EPA_diff`: mean CFBD `ppa` per play difference.
- `PPD_diff`: mean points-per-drive difference; drive points are `endOffenseScore - startOffenseScore`, clipped to `[0, 8]`.
- `DriveConv_diff`: difference in the fraction of offensive drives scoring more than zero points.

The fifth metric is final home scoring margin:

- `spread = home_score - away_score`.

The notebook then fits its custom SRS algorithm independently to:

```text
spread
SR_diff
EPA_diff
PPD_diff
DriveConv_diff
```

For each metric and each iteration, a team's rating is:

```text
average metric margin + mean(current SRS of distinct opponents)
```

The opponent mean is intentionally unweighted by repeat meetings, matching the notebook. The complete rating vector is centered after each iteration. Convergence uses `tol=1e-6` with `max_iter=1000`.

Each of the five SRS vectors is then standardized across teams with population standard deviation (`ddof=0`). `SRS_Overall` is the simple average of the five standardized SRS ratings.

The six regression features are exactly:

```text
SRSdiff_spread
SRSdiff_SR_diff
SRSdiff_EPA_diff
SRSdiff_PPD_diff
SRSdiff_DriveConv_diff
SRSdiff_Overall
```

where every feature is `home rating - away rating`.

The supplied notebook searched LinearRegression, Ridge, Lasso, and ElasticNet candidates using an 80/20 random split with `random_state=42`. The winning model in the notebook was:

```text
ElasticNet(alpha=0.1, l1_ratio=0.2, max_iter=5000)
```

That selected model is treated as frozen before the repository backtest. The six features are standardized with `StandardScaler` before the ElasticNet fit, matching the notebook's model-training cell.

## Historical evaluation boundary

The notebook's displayed 2025 model was built from the season's completed data as a whole. Reusing that exact full-season feature construction to score games from the same season would leak the target game's result into its own SRS ratings.

For the Prediction-v2 comparison, the model mathematics above are unchanged, but every historical target partition is materialized from strictly earlier completed partitions. This is the only timing change required to make the head-to-head backtest legitimate.

The later notebook cell that predicts the current week passes unscaled feature values to an estimator that was fit on scaled values. The repository comparison does not copy that inference mismatch; it applies the fitted `StandardScaler` at prediction time, consistent with the notebook's train/test and full-fit model cells.

## Head-to-head protocol

The comparison uses the same outer test seasons used by Prediction v2:

```text
2018
2019
2021
2022
2023
2024
2025
```

Both `minGames=3` and `minGames=4` are evaluated.

For every test season:

1. notebook-model rows are built only from information available before each target partition;
2. the notebook ElasticNet is trained only on prior seasons;
3. Prediction v2 is independently trained using its existing expanding-season protocol;
4. the two models are scored on the exact intersection of eligible game IDs;
5. target margins are required to match exactly before a game enters the comparison.

The report includes per-season and pooled common-sample:

- MAE;
- RMSE;
- straight-up winner accuracy;
- notebook-minus-v2 deltas;
- notebook and Prediction-v2 eligible counts;
- exact common-sample count.

## Run

```bash
python -m cfb_analytics.analytics.notebook_srs_elasticnet --overwrite
```

Outputs:

```text
data/processed/notebook_srs_elasticnet_vs_prediction_v2.json
data/processed/notebook_srs_elasticnet_vs_prediction_v2_games.json
```

Interpretation:

```text
dMAE < 0   notebook model has lower MAE than Prediction v2
dRMSE < 0  notebook model has lower RMSE than Prediction v2
dWin > 0   notebook model has higher winner accuracy
```

Do not alter Prediction v2 based on this experiment. This is a separately named retrospective challenger/comparator.
