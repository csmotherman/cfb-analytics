# Prediction v2 vs CFBD Market Spread Benchmark

**Status:** retrospective benchmark utility  
**Model status:** frozen; this analysis must not mutate Prediction v2  
**Version:** `prediction-v2-vs-cfbd-market-v1`

## Purpose

Compare the locked Prediction v2 game-margin benchmark against historical CFBD
betting spreads without giving the model in-sample information.

The benchmark has two distinct coverage concepts:

1. **Market coverage:** download every CFBD line returned for 2014-2025,
   regular season and postseason.
2. **Official model comparison:** join market lines only to Prediction v2's
   already-locked outer-season OOS folds:
   `2018, 2019, 2021, 2022, 2023, 2024, 2025`.

The report must not relabel 2014-2017 as official Prediction-v2 OOS evidence.
The model corpus intentionally omits 2020.

## Spread sign convention

Everything is normalized to signed expected **home scoring margin**:

```text
+7.0  => home team favored by 7
 0.0  => pick'em
-7.0  => away team favored by 7
```

This is the same orientation as Prediction v2's `target_margin` and predicted
margin.

For CFBD provider lines:

- parse `formattedSpread` when possible;
- numeric `spread` is converted to expected home margin by negating it;
- when both are available they must agree or the provider line is rejected.

Example:

```text
home = Georgia Tech
away = Florida State
formattedSpread = "Florida State -10.5"
spread = 10.5

marketHomeMargin = -10.5
```

## Provider rule

Do not use whichever provider happens to appear first in the API response.

Default selection:

1. use provider `consensus` when available;
2. otherwise use the median normalized spread across all parseable providers.

Use `--consensus-only` during evaluation to disable the median fallback.

The selected provider/method and provider count are retained per matched game.

## API-key handling

Never hard-code or commit the CFBD token.

```bash
export CFBD_API_KEY='REDACTED'
```

The downloaded market snapshot lives under `data/raw/**`, which is already
ignored by Git.

## Download historical lines

This performs 24 sequential requests: regular + postseason for each year
2014-2025.

```bash
python -m cfb_analytics.analytics.prediction_v2_market_benchmark download
```

Default output:

```text
data/raw/market_lines/cfbd-lines-2014-2025.json
```

The command refuses to overwrite an existing snapshot unless `--overwrite` is
supplied intentionally.

## Evaluate the locked model

```bash
python -m cfb_analytics.analytics.prediction_v2_market_benchmark evaluate
```

Default outputs:

```text
data/processed/market_benchmark/prediction-v2-vs-market.json
data/processed/market_benchmark/prediction-v2-vs-market-games.json
```

Both output directories are ignored by Git.

## Primary metrics

For each locked `minGames` setting (3 and 4), report pooled and per-season:

```text
Model MAE
Market MAE
Model - Market MAE delta

Model RMSE
Market RMSE
Model - Market RMSE delta

Model winner accuracy
Market winner accuracy

Mean absolute model-market disagreement
```

Negative MAE/RMSE deltas mean Prediction v2 beat the market on final-margin
error for the matched sample.

## Against-the-spread diagnostic

For each matched game:

```text
modelMarketEdge
  = modelHomeMargin - marketHomeMargin

actualCoverMargin
  = actualHomeMargin - marketHomeMargin
```

If `modelMarketEdge > 0`, the model prefers the home side relative to the
market. If it is negative, the model prefers the away side.

ATS accuracy is descriptive. Market pushes and exact zero model-market edges
are excluded from ATS decisions.

The report also summarizes ATS performance at minimum absolute disagreement
thresholds:

```text
0, 1, 2, 3, 5, 7, 10 points
```

These thresholds are diagnostics only and must not be selected after looking at
results and then described as a predeclared betting strategy.

## Integrity rules

The benchmark hard-fails on:

- duplicate market game IDs;
- model/market home-away identity disagreement for the same `gameId`;
- formatted/numeric line sign conflicts at the provider-line level.

The join key is CFBD `gameId`. Team-name fuzzy matching is not used.

## What this analysis can and cannot prove

A strong market comparison is useful because the closing/consensus spread is a
high-quality pregame benchmark. It does not make Prediction v2 a profitable
betting system by itself.

Do not use this retrospective comparison to mutate the already-frozen 2026
Prediction v2 architecture, coefficients, or early-prior weights. Any future
model change inspired by this benchmark must be a separately named challenger
with a new predeclared evaluation contract.
