# Prediction Model v2 Research Benchmark Contract

**Status:** LOCKED RESEARCH BENCHMARK  
**Version:** `prediction-v2-site-aware-srs-hfa-v1`  
**Purpose:** forward reference model for future game-margin challengers after authoritative-target repair and site-aware SRS promotion. This is a research benchmark, not a claim of production optimality.

## What changed from Prediction v1

Prediction v2 keeps the corrected Prediction-v1 VOLUME + OLS architecture and changes exactly one feature:

```text
Prediction v1
  srsEdge

Prediction v2
  siteAwareSrsMargin
```

All other model terms, target definitions, training weights, outer-season protocol, and eligibility rules remain unchanged.

## Feature contract

Prediction v2 uses 19 features:

```text
ITERATIVE RATINGS
  home_iterativeSuccessEdge
  away_iterativeSuccessEdge
  home_iterativeExplosiveEdge
  away_iterativeExplosiveEdge
  home_iterativeYardsPerPlayEdge
  away_iterativeYardsPerPlayEdge
  home_iterativeYardsPerPossessionEdge
  away_iterativeYardsPerPossessionEdge
  home_iterativeFinishingEdge
  away_iterativeFinishingEdge
  home_iterativeFieldPositionEdge
  away_iterativeFieldPositionEdge

SITE-AWARE SRS
  siteAwareSrsMargin

MWDR
  home_MWDR_OffenseEdge
  home_MWDR_DefenseEdge
  mwdrXExpectedPossessions

VOLUME ENGINE
  successVolumeEdge
  explosiveVolumeEdge
  turnoverVolumeEdge
```

## Site-aware SRS / HFA

Within each season and before each partition, fit strictly prior games to:

```text
margin ~= rating(home)
          - rating(away)
          + HFA * nonNeutral
```

where `nonNeutral=1` for true home/away games and `0` for neutral-site games.

The feature used by Prediction v2 is:

```text
siteAwareSrsMargin
  = siteAwareSrsEdge
    + siteAwareSrsHfaBefore * nonNeutral
```

The current game's result is never used in its own SRS or HFA estimate. Team ratings are centered within disconnected schedule components. Site coverage is complete for all 8,510 corrected model rows.

## Target contract

Targets come only from authoritative raw CFBD `games.json` final scores:

```text
target_homeScore
target_awayScore
target_margin
target_homeWin
```

The corrected corpus passes exact reconciliation for all 8,510 model rows.

## Estimator / training contract

- ordinary least squares;
- signed final home margin target;
- equal weight by game;
- all prior available seasons for each outer holdout;
- identical common sample for ablations;
- minimum prior games 3 and 4 for benchmark evaluation;
- 2020 omitted from the historical corpus;
- season reset preserved;
- regular-season partitions ordered before postseason partitions;
- no current/future game information in pregame features.

## Promotion evidence

Prediction v2 was promoted from the fixed site-aware challenger under a predeclared gate.

```text
ALL 14 FOLDS
Prediction v2 - corrected Prediction v1
  mean MAE delta     -0.0021
  mean RMSE delta    -0.0024
  winner delta       +0.13 pp
  MAE better           8/14
  RMSE better          8/14

RECENT 6 FOLDS (2023-2025 x min3/min4)
  mean MAE delta     -0.0035
  mean RMSE delta    -0.0174
  winner delta       +0.38 pp
  MAE better           4/6
  RMSE better          6/6
```

The challenger passed all predeclared broad and recent MAE/RMSE requirements.

The improvement is **small**. Prediction v2 is promoted because it adds a football-valid, fully observed context variable, preserves model size and sample, corrects a structural limitation of legacy SRS, and met the predefined OOS stability gate. It should not be described as a large accuracy jump.

## Pre-promotion alternatives that were rejected

After the authoritative target correction:

```text
LEAN pruning
  recent MAE delta   +0.0205
  recent RMSE delta  +0.0217
  -> not promoted

SYMMETRIC / net model
  all-14 MAE delta   -0.0246
  all-14 RMSE delta  -0.0143
  recent MAE delta   -0.0141
  recent RMSE delta  -0.0108
  recent RMSE wins     3/6
  -> failed stability gate; not promoted
```

Do not reopen those exact formulations by tuning against the already-inspected holdouts.

## Benchmark policy moving forward

Prediction v2 is now the comparison baseline for new game-margin research.

A challenger does not replace it because it is football-plausible or improves pooled error. Future work should preserve:

1. identical leakage-safe samples;
2. paired MAE and RMSE as primary metrics;
3. winner accuracy as secondary context;
4. per-season results;
5. recent-era stability;
6. predeclared promotion rules before inspecting challenger holdout results.

If a future challenger earns promotion, create Prediction v3 rather than silently mutating v2.

## 2026 prospective validation

Historical 2023–2025 folds have now been inspected repeatedly during development. They should not be treated as pristine unseen evidence indefinitely.

For 2026, freeze Prediction v2 before evaluating outcomes and save each weekly pregame prediction. Do not retune v2 against 2026 results during the season if the goal is to use 2026 as a prospective validation year.

## Early-season 2026 freeze candidate

The adjacent-season feasibility audit passed: complete prior state was available for 1,754 of 1,781 historical regular-season games through Week 4 (98.5%). The first outcome-bearing challenger then used the predeclared four-game carryover:

```text
0 current games -> prior weight 1.00
1 current game  -> prior weight 0.75
2 current games -> prior weight 0.50
3 current games -> prior weight 0.25
4+ games        -> prior weight 0.00
```

The historical challenger passed every predeclared gate and is now frozen as `prediction-v2-early-prior-four-game-linear-v1` for prospective 2026 use. It is documented in `docs/PREDICTION_V2_EARLY_PRIOR_CHALLENGER.md`.

Key historical results:

```text
VS PRIOR-ONLY — ALL 6
  mean delta MAE   -0.2207
  mean delta RMSE  -0.2789
  MAE wins            6/6
  RMSE wins           4/6

VS CURRENT-ONLY — COMMON SAMPLE
  mean delta MAE   -2.1493
  mean delta RMSE  -2.4220

EXACT MATURE-SEASON REVERSION
  4,462 rows checked
  0 mismatches
  max abs diff 0.000e+00
```

Week-band diagnostics showed essentially no advantage over prior-only in Weeks 0-2 (`MAE -0.0033`, `RMSE +0.0441`) and a clearer advantage in Weeks 3-4 (`MAE -0.4073`, `RMSE -0.5591`). Those diagnostics are descriptive only; the frozen weights must not be retuned against the same historical folds.

This does **not** rename the model Prediction v3. Prediction v2 remains the locked mature-season benchmark, while the early-prior rule is a frozen 2026 prospective extension. A future Prediction-v3 decision should require genuinely prospective evidence or a separate predeclared promotion decision.
